# auto_classifier.py
# =========================================================
# Dual-base classification (HGB + XGB) with learned λ(x)
# + K-point integral-delta logits correction (FiLM)
# Keras-3 safe; gate responsibility regularizer + entropy anti-collapse
# Early stopping on val NLL; temperature scaling calibration
# fit/predict style; seed-stable; no duplicate arrays in split
# =========================================================

from __future__ import annotations
import numpy as np, gc, warnings, random
from typing import Dict, Any, Optional, Tuple

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.model_selection import KFold, train_test_split
from sklearn.utils.validation import check_X_y, check_array
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, accuracy_score

# Optional deps
try:
    from xgboost import XGBClassifier  # type: ignore
    HAS_XGB = True
except Exception:
    HAS_XGB = False

try:
    import tensorflow as tf
    from tensorflow.keras import layers, regularizers, optimizers, Model
    HAS_TF = True
except Exception:
    HAS_TF = False


def _require_tf():
    if not HAS_TF:
        raise ImportError('TensorFlow is required for NovaAutoClassifier. '
                          'Install with: pip install "novatium[tensorflow]"')


# -------------- small utils --------------
def _dense32(a): return np.asarray(a, dtype=np.float32)

def _one_hot(y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    y_oh = enc.fit_transform(y.reshape(-1, 1)).astype(np.float32)
    classes = enc.categories_[0].astype(y.dtype)
    return y_oh, classes

def _softmax(z: np.ndarray, axis=-1):
    z = z - np.max(z, axis=axis, keepdims=True)
    ez = np.exp(z)
    return ez / np.sum(ez, axis=axis, keepdims=True)

def _logit_clip(p: tf.Tensor, eps: float = 1e-6) -> tf.Tensor:
    p = tf.clip_by_value(p, eps, 1.0 - eps)
    return tf.math.log(p)

def set_all_seeds(seed: int):
    np.random.seed(seed)
    random.seed(seed)
    if HAS_TF:
        tf.random.set_seed(seed)


# -------------- Gauss–Legendre quadrature --------------
def gauss_legendre_nodes_weights(K=12):
    t, w = np.polynomial.legendre.leggauss(K)
    a = (t + 1.0) / 2.0
    w = w / 2.0
    return a.astype("float32"), w.astype("float32")


# -------------- OOF base learners --------------
def _make_hgb(seed, params=None):
    params = params or {}
    return HistGradientBoostingClassifier(
        max_depth=params.get("max_depth", None),
        learning_rate=params.get("learning_rate", 0.1),
        max_iter=params.get("max_iter", 400),
        l2_regularization=params.get("l2_regularization", 0.0),
        random_state=seed
    )

def _make_xgb(seed, params=None):
    params = params or {}
    return XGBClassifier(
        n_estimators=params.get("n_estimators", 800),
        max_depth=params.get("max_depth", 6),
        learning_rate=params.get("learning_rate", 0.05),
        subsample=params.get("subsample", 0.8),
        colsample_bytree=params.get("colsample_bytree", 0.8),
        reg_lambda=params.get("reg_lambda", 1.0),
        tree_method=params.get("tree_method", "hist"),
        n_jobs=params.get("n_jobs", -1),
        random_state=seed,
        objective="multi:softprob",
        eval_metric="mlogloss",
        verbosity=0,
    )

def _fit_oof_proba_single(X_tr, y_tr, X_te, seed, kind="hgb", n_splits=5, params=None):
    y1d = y_tr.astype(np.int64).ravel()
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    base = _make_xgb(seed, params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, params)
    base.fit(X_tr, y1d)  # fit once to infer n_classes
    C = base.predict_proba(X_tr[:2]).shape[1]
    del base

    oof = np.zeros((len(X_tr), C), np.float32)
    te_preds = []
    for tr, va in kf.split(X_tr):
        if kind == "xgb" and HAS_XGB:
            base = _make_xgb(seed, params)
        else:
            if kind == "xgb" and not HAS_XGB:
                warnings.warn("XGBoost not installed, falling back to HGB.", RuntimeWarning)
            base = _make_hgb(seed, params)
        base.fit(X_tr[tr], y1d[tr])
        oof[va] = base.predict_proba(X_tr[va]).astype(np.float32)
        te_preds.append(base.predict_proba(X_te).astype(np.float32))
    te = np.mean(te_preds, axis=0).astype(np.float32)

    base_full = _make_xgb(seed, params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, params)
    base_full.fit(X_tr, y1d)
    return {"proba_train_oof": oof, "proba_test": te, "base_full": base_full}


def fit_bases_oof(X_train, y_train, X_test, seed=42, n_splits=5, xgb_params=None, hgb_params=None):
    oof_hgb = _fit_oof_proba_single(X_train, y_train, X_test, seed, "hgb", n_splits, hgb_params)
    oof_xgb = _fit_oof_proba_single(X_train, y_train, X_test, seed, "xgb", n_splits, xgb_params) if HAS_XGB else oof_hgb
    return oof_xgb, oof_hgb


# -------------- Keras models --------------
class BasePlusIntegralDeltaLogits(Model):
    """
    Integral-delta correction on *logits* space.
    Produces K per-alpha deltas of size C, integrates with weights -> z (B,C),
    then adds scaled correction g(x)*z to base logits log(p0).
    """
    def __init__(self, alphas, weights, n_classes: int, hidden=64, fourier_m=6, weight_decay=1e-4):
        super().__init__()
        self.K = len(alphas)
        self.C = int(n_classes)
        self.A = tf.constant(alphas[None, :, None])   # (1,K,1)
        self.W = tf.constant(weights[None, :, None])  # (1,K,1)
        self.fourier_m = fourier_m

        reg = regularizers.l2(weight_decay)
        self.enc_x = tf.keras.Sequential([
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
        ])
        self.enc_a = tf.keras.Sequential([
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
        ])
        self.film_gamma = layers.Dense(hidden, kernel_regularizer=reg)
        self.film_beta  = layers.Dense(hidden, kernel_regularizer=reg)

        self.delta_head = tf.keras.Sequential([
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(self.C, kernel_regularizer=reg)  # per-alpha logits delta
        ])
        self.gate_mag = tf.keras.Sequential([
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.softplus)             # nonnegative scalar per sample
        ])

    def call(self, x, p0, training=False, return_delta=False):
        # x: (B,Ds), p0: (B,C) base probabilities mixed by λ
        B = tf.shape(x)[0]
        # Build per-alpha features
        xT = tf.tile(tf.reshape(x, (B, 1, -1)), [1, self.K, 1])    # (B,K,Ds)
        aT = tf.tile(self.A, [B, 1, 1])                            # (B,K,1)
        k  = tf.range(1, self.fourier_m+1, dtype=tf.float32)[None, None, :]
        a_feats = tf.concat([tf.sin(aT*np.pi*k), tf.cos(aT*np.pi*k)], axis=-1)  # (B,K,2m)

        hx = self.enc_x(xT)                                        # (B,K,H)
        ha = self.enc_a(tf.concat([aT, a_feats], axis=-1))         # (B,K,H)
        h  = self.film_gamma(ha) * hx + self.film_beta(ha)         # (B,K,H)

        delta = self.delta_head(h)                                 # (B,K,C)
        integ = tf.reduce_sum(delta * tf.tile(self.W, [B,1,self.C]), axis=1)  # (B,C)

        g = self.gate_mag(x)                                       # (B,1)
        base_logits = _logit_clip(p0)                              # (B,C) log-prob (works for softmax if normalized)
        logits = base_logits + g * integ                           # (B,C)

        if return_delta:
            return logits, integ, g, delta
        return logits, integ, g


class LambdaGate(Model):
    """Per-sample λ(x) in (0,1). Input is [x_scaled, p_xgb, p_hgb] flattened."""
    def __init__(self, hidden=32, weight_decay=1e-4):
        super().__init__()
        reg = regularizers.l2(weight_decay)
        self.net = tf.keras.Sequential([
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.sigmoid)
        ])
    def call(self, x, training=False):
        return self.net(x)  # (B,1)


# -------------- Estimator --------------
class NovaAutoClassifier(BaseEstimator, ClassifierMixin):
    def __init__(
        self,
        use_xgb: bool = True,
        hgb_params: Optional[Dict[str, Any]] = None,
        xgb_params: Optional[Dict[str, Any]] = None,
        seed: int = 42,
        n_splits: int = 5,
        scale_inputs: bool = True,      # scale X for gate/delta
        K: int = 8,
        hidden: int = 64,
        fourier_m: int = 6,
        lr: float = 3e-3,
        max_epochs: int = 200,
        patience: int = 12,
        gate_bce_weight: float = 1e-3,
        gate_tau: float = 8.0,
        gate_entropy_weight: float = 5e-4,
        lambda_center: float = 0.5,
        lam_alpha_smooth: float = 3e-3,
        lam_alpha_curv: float = 2e-3,
        lam_ortho: float = 3e-3,
        lam_gate_pen: float = 5e-4,
        lam_lambda_reg: float = 1e-4,
        progress_bar: bool = True,
        calibrate_logits: bool = True,
    ):
        # expose ALL params as attributes (sklearn requirement)
        self.use_xgb = use_xgb
        self.hgb_params = hgb_params
        self.xgb_params = xgb_params
        self.seed = seed
        self.n_splits = n_splits
        self.scale_inputs = scale_inputs
        self.K = K
        self.hidden = hidden
        self.fourier_m = fourier_m
        self.lr = lr
        self.max_epochs = max_epochs
        self.patience = patience
        self.gate_bce_weight = gate_bce_weight
        self.gate_tau = gate_tau
        self.gate_entropy_weight = gate_entropy_weight
        self.lambda_center = lambda_center
        self.lam_alpha_smooth = lam_alpha_smooth
        self.lam_alpha_curv = lam_alpha_curv
        self.lam_ortho = lam_ortho
        self.lam_gate_pen = lam_gate_pen
        self.lam_lambda_reg = lam_lambda_reg
        self.progress_bar = progress_bar
        self.calibrate_logits = calibrate_logits

        # fitted attrs will be created in fit()
        # self.scaler_ : StandardScaler
        # self._delta_model_ : tf.Model
        # self._lam_gate_ : tf.Model
        # self._base_hgb_, self._base_xgb_
        # self.classes_ : ndarray
        # self.n_features_in_ : int
        # self.temp_T_ : float

    # ---------- helpers ----------
    def _concat_gate_inputs(self, Xs, pxgb, phgb):
        # Xs: scaled X; probs are (N,C)
        return np.concatenate([_dense32(Xs), _dense32(pxgb), _dense32(phgb)], axis=1).astype(np.float32)

    # ---------- core fit ----------
    def fit(self, X, y):
        _require_tf()
        set_all_seeds(self.seed)

        X, y = check_X_y(X, y, accept_sparse=False, ensure_2d=True, dtype=None)
        y = np.asarray(y)
        y_oh, classes = _one_hot(y)
        C = y_oh.shape[1]

        # scale inputs for gate/delta (bases trained on raw)
        if self.scale_inputs:
            self.scaler_ = StandardScaler()
            Xs = self.scaler_.fit_transform(X).astype(np.float32)
        else:
            self.scaler_ = None
            Xs = _dense32(X)

        # OOF bases on train; get fully-fitted models too
        X_te_shadow = X[: min(64, len(X))]
        oof_xgb, oof_hgb = fit_bases_oof(
            X, y, X_te_shadow, seed=self.seed, n_splits=self.n_splits,
            xgb_params=self.xgb_params if (self.use_xgb and HAS_XGB) else None,
            hgb_params=self.hgb_params
        )
        pxgb_tr, phgb_tr = oof_xgb["proba_train_oof"], oof_hgb["proba_train_oof"]

        # persist full bases
        self._base_hgb_ = oof_hgb["base_full"]
        self._has_xgb_ = bool(HAS_XGB and self.use_xgb)
        self._base_xgb_ = oof_xgb["base_full"] if self._has_xgb_ else None

        # ---------- train/val split (indices to avoid duplicates confusion) ----------
        idx = np.arange(len(X), dtype=np.int64)
        tr_idx, va_idx = train_test_split(idx, test_size=0.15, random_state=self.seed, shuffle=True, stratify=y)

        X_tr, X_va = Xs[tr_idx], Xs[va_idx]
        Y_tr, Y_va = y[tr_idx], y[va_idx]
        YOH_tr, YOH_va = y_oh[tr_idx], y_oh[va_idx]
        PX_tr, PX_va = pxgb_tr[tr_idx], pxgb_tr[va_idx]
        PH_tr, PH_va = phgb_tr[tr_idx], phgb_tr[va_idx]

        # ---------- Keras heads ----------
        alphas, weights = gauss_legendre_nodes_weights(K=self.K)
        delta_model = BasePlusIntegralDeltaLogits(
            alphas, weights, n_classes=C, hidden=self.hidden, fourier_m=self.fourier_m, weight_decay=1e-4
        )
        lam_gate = LambdaGate(hidden=32)

        # ---------- build models BEFORE optimizers ----------
        X_boot = tf.constant(X_tr[:2], tf.float32)
        px_boot = tf.constant(0.5 * (PX_tr[:2] + PH_tr[:2]), tf.float32)
        _ = lam_gate(tf.concat([X_boot, px_boot, px_boot], axis=1), training=False)
        _ = delta_model(X_boot, px_boot, training=False)

        opt_delta = optimizers.Adam(self.lr)
        opt_gate  = optimizers.Adam(self.lr)
        # make sure optimizers see current variables
        _ = opt_delta.iterations
        _ = opt_gate.iterations

        eps = tf.constant(1e-6, dtype=tf.float32)

        def ce_loss(y_true_oh, probs):
            probs = tf.clip_by_value(probs, eps, 1.0)
            return -tf.reduce_mean(tf.reduce_sum(y_true_oh * tf.math.log(probs), axis=1))

        # tensors for training
        X_tr_tf   = tf.constant(X_tr, tf.float32)
        Y_tr_oh_t = tf.constant(YOH_tr, tf.float32)
        PX_tr_tf  = tf.constant(PX_tr, tf.float32)
        PH_tr_tf  = tf.constant(PH_tr, tf.float32)

        def train_step():
            with tf.GradientTape(persistent=True) as tape:
                # λ-gate input: [X_s, p_xgb, p_hgb]
                lam_in = tf.concat([X_tr_tf, PX_tr_tf, PH_tr_tf], axis=1)
                lam = lam_gate(lam_in)                       # (B,1)
                p0 = lam * PX_tr_tf + (1.0 - lam) * PH_tr_tf # (B,C)

                logits, integ, g = delta_model(X_tr_tf, p0, training=True)
                probs = tf.nn.softmax(logits, axis=1)

                nll = ce_loss(Y_tr_oh_t, probs)

                # alpha smoothness/curvature penalties require per-alpha deltas
                # Re-run with return_delta for penalties only (no extra grads issues)
                logits2, integ2, g2, delta = delta_model(X_tr_tf, p0, training=True, return_delta=True)
                # delta: (B,K,C)
                diff = delta[:, 1:, :] - delta[:, :-1, :]
                l_smooth = tf.reduce_mean(tf.square(diff))
                l_curv = tf.reduce_mean(tf.square(delta[:, 2:, :] - 2.0*delta[:, 1:-1, :] + delta[:, :-2, :])) if self.lam_alpha_curv > 0 else 0.0

                # orthogonality to base logits
                base_logits = _logit_clip(p0)
                base_z = base_logits - tf.reduce_mean(base_logits, axis=0, keepdims=True)
                integ_z = integ2 - tf.reduce_mean(integ2, axis=0, keepdims=True)
                l_ortho = tf.reduce_mean(tf.square(tf.reduce_mean(base_z * integ_z, axis=1)))

                # small penalties
                l_gate = tf.reduce_mean(g2)  # positive magnitude
                l_lam  = tf.reduce_mean(tf.square(lam - self.lambda_center))

                # responsibility regularizer on λ: use CE of bases
                # Ex = CE(y, p_xgb), Eh = CE(y, p_hgb), p = sigmoid(-tau*(Ex - Eh))
                ex = -tf.reduce_sum(Y_tr_oh_t * tf.math.log(tf.clip_by_value(PX_tr_tf, eps, 1.0)), axis=1, keepdims=True)
                eh = -tf.reduce_sum(Y_tr_oh_t * tf.math.log(tf.clip_by_value(PH_tr_tf, eps, 1.0)), axis=1, keepdims=True)
                p = tf.sigmoid(-self.gate_tau * (ex - eh))
                gate_bce = -tf.reduce_mean(p * tf.math.log(lam + eps) + (1.0 - p) * tf.math.log(1.0 - lam + eps))

                # anti-collapse entropy on λ
                l_entropy = tf.reduce_mean(lam * tf.math.log(lam + eps) + (1.0 - lam) * tf.math.log(1.0 - lam + eps))

                loss = (nll
                        + self.lam_alpha_smooth * l_smooth
                        + self.lam_alpha_curv * l_curv
                        + self.lam_ortho * l_ortho
                        + self.lam_gate_pen * l_gate
                        + self.lam_lambda_reg * l_lam
                        + self.gate_bce_weight * gate_bce
                        + self.gate_entropy_weight * l_entropy)

            g_delta = tape.gradient(loss, delta_model.trainable_variables)
            g_gate  = tape.gradient(loss, lam_gate.trainable_variables)
            del tape
            g_delta = [(g,v) for g,v in zip(g_delta, delta_model.trainable_variables) if g is not None]
            g_gate  = [(g,v) for g,v in zip(g_gate,  lam_gate.trainable_variables)  if g is not None]
            opt_delta.apply_gradients(g_delta)
            opt_gate.apply_gradients(g_gate)
            return float(nll.numpy())

        # training loop with early stopping (val NLL)
        best = 1e9; bad = 0; best_w_delta = None; best_w_gate = None
        for epoch in range(self.max_epochs):
            _ = train_step()

            # validation
            # build inputs for λ on val
            px_va_tf = tf.constant(PX_va, tf.float32)
            ph_va_tf = tf.constant(PH_va, tf.float32)
            x_va_tf  = tf.constant(X_va, tf.float32)

            lam_va = lam_gate(tf.concat([x_va_tf, px_va_tf, ph_va_tf], axis=1), training=False)
            p0_va  = lam_va * px_va_tf + (1.0 - lam_va) * ph_va_tf
            logits_va, _, _ = delta_model(x_va_tf, p0_va, training=False)
            probs_va = tf.nn.softmax(logits_va, axis=1).numpy()
            nll_va = log_loss(Y_va, probs_va, labels=np.arange(C))

            # simple logging of λ stats on val
            lam_m, lam_s = float(np.mean(lam_va.numpy())), float(np.std(lam_va.numpy()))
            # (optional) print every 10 epochs to keep quiet
            if self.progress_bar and (epoch % 10 == 0 or epoch == self.max_epochs - 1):
                print(f"epoch {epoch:03d} | val NLL={nll_va:.4f} | lam_m={lam_m:.3f} lam_s={lam_s:.3f}")

            if nll_va + 1e-4 < best:
                best, bad = nll_va, 0
                best_w_delta = delta_model.get_weights()
                best_w_gate  = lam_gate.get_weights()
            else:
                bad += 1
                if bad >= self.patience:
                    break

        if best_w_delta is not None: delta_model.set_weights(best_w_delta)
        if best_w_gate  is not None: lam_gate.set_weights(best_w_gate)

        # ---------- temperature calibration on val ----------
        self.temp_T_ = 1.0
        if self.calibrate_logits:
            # grid search a few T values around 1.0
            Ts = np.concatenate([np.linspace(0.5, 2.0, 16), np.array([0.33, 3.0], dtype=np.float32)])
            best_T, best_nll = 1.0, 1e9
            lam_va = lam_gate(tf.concat([x_va_tf, px_va_tf, ph_va_tf], axis=1), training=False)
            p0_va  = lam_va * px_va_tf + (1.0 - lam_va) * ph_va_tf
            logits_va, _, _ = delta_model(x_va_tf, p0_va, training=False)
            logits_va = logits_va.numpy()
            for T in Ts:
                probs = _softmax(logits_va / float(T), axis=1)
                nllT = log_loss(Y_va, probs, labels=np.arange(C))
                if nllT < best_nll:
                    best_nll, best_T = nllT, float(T)
            self.temp_T_ = best_T

        # persist
        self._delta_model_ = delta_model
        self._lam_gate_ = lam_gate
        self.classes_ = classes
        self.n_features_in_ = X.shape[1]
        return self

    # ---------- inference ----------
    def _base_proba(self, X) -> Tuple[np.ndarray, np.ndarray]:
        """Return (p_xgb, p_hgb) for given raw X."""
        phgb = self._base_hgb_.predict_proba(X).astype(np.float32)
        if getattr(self, "_has_xgb_", False) and (self._base_xgb_ is not None):
            pxgb = self._base_xgb_.predict_proba(X).astype(np.float32)
        else:
            pxgb = phgb
        return pxgb, phgb

    def predict_proba(self, X):
        _require_tf()
        X = check_array(X, ensure_2d=True, dtype=None)
        X = np.asarray(X)
        Xs = self.scaler_.transform(X).astype(np.float32) if (self.scale_inputs and self.scaler_ is not None) else _dense32(X)

        pxgb, phgb = self._base_proba(X)
        # gate input
        lam_in = np.concatenate([Xs, pxgb, phgb], axis=1).astype(np.float32)
        lam = self._lam_gate_(tf.constant(lam_in, tf.float32), training=False).numpy()
        p0  = lam * pxgb + (1.0 - lam) * phgb

        logits, _, _ = self._delta_model_(tf.constant(Xs, tf.float32), tf.constant(p0, tf.float32), training=False)
        logits = logits.numpy()
        if hasattr(self, "temp_T_") and self.temp_T_ is not None:
            logits = logits / float(self.temp_T_)
        probs = _softmax(logits, axis=1)
        return probs

    def predict(self, X):
        probs = self.predict_proba(X)
        idx = np.argmax(probs, axis=1)
        return self.classes_[idx]

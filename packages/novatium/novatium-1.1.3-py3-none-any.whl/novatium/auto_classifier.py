# auto_classifier.py
# =========================================================
# NovaAutoClassifier
# Dual-base classification (HGB + XGB) with learned λ(x) + integral-delta residual
# Keras-3 safe; includes gate responsibility regularizer + anti-collapse entropy
# Early stopping on val NLL; calibrated evaluation (delta scale + temperature)
# =========================================================

from __future__ import annotations
import numpy as np
import gc
import warnings
from typing import Dict, Any, Optional, Tuple

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import log_loss, accuracy_score
from sklearn.utils.validation import check_X_y, check_array
from sklearn.ensemble import HistGradientBoostingClassifier

# Optional deps: XGBoost
try:
    from xgboost import XGBClassifier  # type: ignore
    HAS_XGB = True
except Exception:
    HAS_XGB = False

# Optional deps: TensorFlow
try:
    import tensorflow as tf
    from tensorflow.keras import layers, regularizers, optimizers, Model
    HAS_TF = True
except Exception:
    HAS_TF = False


def _require_tf():
    if not HAS_TF:
        raise ImportError(
            'TensorFlow is required for NovaAutoClassifier. '
            'Install with: pip install "novatium[tensorflow]"'
        )

def _dense32(a): return np.asarray(a, dtype=np.float32)

def _as_2d(a):
    a = _dense32(a)
    return a.reshape(-1, 1) if a.ndim == 1 else a

def _onehot(y: np.ndarray, n_classes: int) -> np.ndarray:
    y = y.astype(np.int64).ravel()
    oh = np.zeros((y.shape[0], n_classes), dtype=np.float32)
    oh[np.arange(y.shape[0]), y] = 1.0
    return oh

def gauss_legendre_nodes_weights(K=12):
    t, w = np.polynomial.legendre.leggauss(K)
    a = (t + 1.0) / 2.0
    w = w / 2.0
    return a.astype("float32"), w.astype("float32")

def concat_gate_inputs(X, f_xgb, f_hgb):
    # f_* are predicted PROBABILITIES (B, C)
    return np.concatenate([_dense32(X), _dense32(f_xgb), _dense32(f_hgb)], axis=1).astype(np.float32)

# ---------- base learners (OOF) ----------
def _make_hgb(seed, params=None):
    params = params or {}
    return HistGradientBoostingClassifier(
        max_depth=params.get("max_depth", 6),
        learning_rate=params.get("learning_rate", 0.05),
        max_iter=params.get("max_iter", 400),
        random_state=seed
    )

def _make_xgb(seed, params=None):
    params = params or {}
    # Use 'hist' and reasonable defaults for tabular
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
        objective="multi:softprob"  # works for binary & multi-class
    )

def _fit_oof_single(X_tr, y_tr, X_te, seed, n_classes: int, kind="hgb", n_splits=5, params=None):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    f0_oof = np.zeros((len(X_tr), n_classes), np.float32)
    te_preds = []
    for tr, va in kf.split(X_tr):
        if kind == "xgb" and HAS_XGB:
            base = _make_xgb(seed, params)
        else:
            if kind == "xgb" and not HAS_XGB:
                warnings.warn("XGBoost not installed, falling back to HGB.", RuntimeWarning)
            base = _make_hgb(seed, params)
        base.fit(X_tr[tr], y_tr[tr])
        f0_oof[va] = base.predict_proba(X_tr[va]).astype(np.float32)
        te_preds.append(base.predict_proba(X_te).astype(np.float32))
    f0_te = np.mean(te_preds, axis=0).astype(np.float32)
    base_full = _make_xgb(seed, params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, params)
    base_full.fit(X_tr, y_tr)
    return {"f0_train_oof": f0_oof, "f0_test": f0_te, "base_full": base_full}

def fit_bases_oof(
    X_train, y_train, X_test, seed=42, n_splits=5,
    n_classes: int = 2, xgb_params=None, hgb_params=None
):
    oof_hgb = _fit_oof_single(X_train, y_train, X_test, seed, n_classes, "hgb", n_splits, hgb_params)
    oof_xgb = _fit_oof_single(X_train, y_train, X_test, seed, n_classes, "xgb", n_splits, xgb_params) if HAS_XGB else oof_hgb
    return oof_xgb, oof_hgb

# ---------- TF helpers ----------
def ce_from_logits(y_onehot: tf.Tensor, logits: tf.Tensor) -> tf.Tensor:
    # y_onehot: (B,C), logits: (B,C)
    return tf.nn.softmax_cross_entropy_with_logits(labels=y_onehot, logits=logits)

def to_logits_from_probs(p: tf.Tensor, eps: float = 1e-7) -> tf.Tensor:
    # Multiclass "log-softmax inverse": logits = log(p) (unnormalized), ok since softmax(log p)=p
    return tf.math.log(tf.clip_by_value(p, eps, 1.0))

def softmax_np(logits: np.ndarray) -> np.ndarray:
    m = logits.max(axis=1, keepdims=True)
    e = np.exp(logits - m)
    return e / e.sum(axis=1, keepdims=True)

# ---------- Models ----------
class BasePlusIntegralDeltaCE(Model):
    """
    Classification variant:
      inputs: x, f0_logits (B,C)
      computes: logits = f0_logits + g(x) * z(x) where z is integral over K nodes of delta(x, a)
      loss: cross-entropy + regularizers (smoothness, curvature, ortho vs f0)
    """
    def __init__(self, alphas, weights, n_classes: int, hidden=48, fourier_m=6, weight_decay=1e-4):
        super().__init__()
        self.K = len(alphas)
        self.C = n_classes
        self.A = tf.constant(alphas[None, :, None])   # (1,K,1)
        self.W = tf.constant(weights[None, :, None])  # (1,K,1)
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
            layers.Dense(self.C, kernel_regularizer=reg)  # per-class correction
        ])
        # small positive scalar gate g(x) >= 0 to modulate residual strength
        self.gate = tf.keras.Sequential([
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.softplus)
        ])
        self.fourier_m = fourier_m

    def call(self, x, f0_logits, training=False, return_delta=False):
        B = tf.shape(x)[0]
        xT = tf.tile(tf.reshape(x, (B, 1, -1)), [1, self.K, 1])  # (B,K,D)
        aT = tf.tile(self.A, [B, 1, 1])                          # (B,K,1)
        k  = tf.range(1, self.fourier_m+1, dtype=tf.float32)[None, None, :]
        a_feats = tf.concat([tf.sin(aT*np.pi*k), tf.cos(aT*np.pi*k)], axis=-1)

        hx = self.enc_x(xT)  # (B,K,H)
        ha = self.enc_a(tf.concat([aT, a_feats], axis=-1))  # (B,K,H)
        h  = self.film_gamma(ha) * hx + self.film_beta(ha)  # (B,K,H)

        delta = self.delta_head(h)                           # (B,K,C)
        wT = tf.tile(self.W, [B, 1, self.C])                # (B,K,C)
        integ = tf.reduce_sum(delta * wT, axis=1)           # (B,C)
        g = self.gate(x)                                     # (B,1)
        logits = f0_logits + g * integ                      # (B,C)

        if return_delta:
            return logits, integ, g, delta
        return logits, integ, g

class LambdaGate(Model):
    """Per-sample λ(x) in (0,1). Input is [x, p_xgb, p_hgb] concatenated."""
    def __init__(self, in_hidden=32, weight_decay=1e-4):
        super().__init__()
        reg = regularizers.l2(weight_decay)
        self.net = tf.keras.Sequential([
            layers.Dense(in_hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(in_hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.sigmoid)
        ])
    def call(self, x, training=False):
        return self.net(x)  # (B,1)

# ---------- Estimator ----------
class NovaAutoClassifier(BaseEstimator, ClassifierMixin):
    def __init__(
        self,
        use_xgb: bool = True,
        hgb_params: Optional[Dict[str, Any]] = None,
        xgb_params: Optional[Dict[str, Any]] = None,
        seed: int = 42,
        n_splits: int = 5,

        # TF head
        K: int = 8,
        hidden: int = 48,
        fourier_m: int = 6,
        lr: float = 3e-3,
        max_epochs: int = 300,
        patience: int = 12,

        # regularizers (alpha grid & gates)
        lam_alpha_smooth: float = 3e-3,
        lam_alpha_curv: float = 2e-3,
        lam_ortho: float = 3e-3,
        lam_gate_pen: float = 5e-4,
        lam_lambda_reg: float = 1e-4,
        lambda_center: float = 0.5,
        gate_bce_weight: float = 1e-3,
        gate_tau: float = 8.0,
        gate_entropy_weight: float = 5e-4,

        # preprocessing
        scale_X: bool = True,
        progress_bar: bool = True
    ):
        self.use_xgb = use_xgb
        self.hgb_params = hgb_params
        self.xgb_params = xgb_params
        self.seed = seed
        self.n_splits = n_splits

        self.K = K
        self.hidden = hidden
        self.fourier_m = fourier_m
        self.lr = lr
        self.max_epochs = max_epochs
        self.patience = patience

        self.lam_alpha_smooth = lam_alpha_smooth
        self.lam_alpha_curv = lam_alpha_curv
        self.lam_ortho = lam_ortho
        self.lam_gate_pen = lam_gate_pen
        self.lam_lambda_reg = lam_lambda_reg
        self.lambda_center = lambda_center
        self.gate_bce_weight = gate_bce_weight
        self.gate_tau = gate_tau
        self.gate_entropy_weight = gate_entropy_weight

        self.scale_X = scale_X
        self.progress_bar = progress_bar

    # ----------- sklearn API -----------
    def fit(self, X, y):
        _require_tf()
        X, y = check_X_y(X, y, accept_sparse=False, ensure_2d=True, multi_output=False, y_numeric=False)
        X = _dense32(X)
        y = np.asarray(y).astype(np.int64).ravel()

        # set random seeds for determinism
        np.random.seed(self.seed)
        tf.random.set_seed(self.seed)

        # optional scaling (standardize features)
        if self.scale_X:
            from sklearn.preprocessing import StandardScaler
            self._scaler_ = StandardScaler()
            Xs = self._scaler_.fit_transform(X).astype(np.float32)
        else:
            self._scaler_ = None
            Xs = X

        n_classes = int(np.max(y)) + 1
        self.classes_ = np.arange(n_classes, dtype=np.int64)
        y_oh = _onehot(y, n_classes)

        # small shadow test slice for OOF shape
        X_te_shadow = X[: min(64, len(X))]

        # ---------- OOF base proba ----------
        oof_xgb, oof_hgb = fit_bases_oof(
            X, y, X_te_shadow, seed=self.seed, n_splits=self.n_splits,
            n_classes=n_classes, xgb_params=self.xgb_params if (self.use_xgb and HAS_XGB) else None,
            hgb_params=self.hgb_params
        )
        p_xgb_tr, p_xgb_te = oof_xgb["f0_train_oof"], oof_xgb["f0_test"]
        p_hgb_tr, p_hgb_te = oof_hgb["f0_train_oof"], oof_hgb["f0_test"]

        # persist base models for inference
        self._base_hgb_ = oof_hgb["base_full"]
        self._has_xgb_ = bool(HAS_XGB and self.use_xgb)
        self._base_xgb_ = oof_xgb["base_full"] if self._has_xgb_ else None

        # ---------- train/val split (for TF head & calibration) ----------
        X_tr, X_va, Y_tr, Y_va, PX_tr, PX_va, PH_tr, PH_va, YOH_tr, YOH_va = train_test_split(
            Xs, Xs, y, y, p_xgb_tr, p_xgb_tr, p_hgb_tr, p_hgb_tr, y_oh,  # keep Xs twice to keep API consistent
            test_size=0.15, random_state=self.seed
        )

        # gate inputs
        X_tr_gate = concat_gate_inputs(X_tr, PX_tr, PH_tr)
        X_va_gate = concat_gate_inputs(X_va, PX_va, PH_va)

        # f0 logits = log(prob) (safe inverse to softmax)
        def to_logits_np(p: np.ndarray) -> np.ndarray:
            eps = 1e-7
            return np.log(np.clip(p, eps, 1.0))

        # ---------- Build TF models ----------
        alphas, weights = gauss_legendre_nodes_weights(K=self.K)
        delta_model = BasePlusIntegralDeltaCE(alphas, weights, n_classes=n_classes, hidden=self.hidden, fourier_m=self.fourier_m, weight_decay=1e-4)

        lam_gate = LambdaGate(in_hidden=32, weight_decay=1e-4)

        # Boot build (forward once)
        _ = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        lam_boot = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        f0_boot_probs = lam_boot * tf.constant(PX_tr[:2], tf.float32) + (1.0 - lam_boot) * tf.constant(PH_tr[:2], tf.float32)
        f0_boot_logits = to_logits_from_probs(f0_boot_probs)
        _ = delta_model(tf.constant(X_tr[:2], tf.float32), f0_boot_logits, training=False)

        # Fresh optimizers
        opt_delta = optimizers.Adam(self.lr)
        opt_gate  = optimizers.Adam(self.lr)
        # Build optimizers with current variable sets
        opt_delta.build(delta_model.trainable_variables)
        opt_gate.build(lam_gate.trainable_variables)

        eps = tf.constant(1e-7, dtype=tf.float32)

        # ---------- training step (eager) ----------
        def train_step(x_gate_in, x_raw, p_xgb, p_hgb, y_onehot):
            with tf.GradientTape(persistent=True) as tape:
                lam = lam_gate(x_gate_in)                                   # (B,1)
                p0 = lam * p_xgb + (1.0 - lam) * p_hgb                      # (B,C)
                f0_logits = to_logits_from_probs(p0)                        # (B,C)

                logits, z, g, delta = delta_model(x_raw, f0_logits, training=True, return_delta=True)
                # CE loss
                ce = tf.reduce_mean(ce_from_logits(y_onehot, logits))

                # alpha smoothness/curvature along K (operate on delta over K)
                diff = delta[:, 1:, :] - delta[:, :-1, :]
                l_smooth = tf.reduce_mean(tf.square(diff))
                l_curv = tf.reduce_mean(tf.square(delta[:, 2:, :] - 2.0*delta[:, 1:-1, :] + delta[:, :-2, :])) if self.lam_alpha_curv > 0 else 0.0

                # orthogonality (per-class, zero-mean across batch)
                f0_z = f0_logits - tf.reduce_mean(f0_logits, axis=0, keepdims=True)  # (B,C)
                z_z  = z - tf.reduce_mean(z, axis=0, keepdims=True)                  # (B,C)
                l_ortho = tf.reduce_mean(tf.reduce_sum(f0_z * z_z, axis=1)**2)

                # small penalties
                l_gate = tf.reduce_mean(g)  # encourage small magnitude residual scale
                l_lam  = tf.reduce_mean(tf.square(lam - self.lambda_center))

                # Responsibility regularizer for λ using base CE
                # p ~ probability XGB is better (smaller CE)
                ce_xgb = tf.reduce_mean(ce_from_logits(y_onehot, to_logits_from_probs(p_xgb)), axis=0, keepdims=False)  # scalar per-sample? we want per-sample
                ce_xgb = ce_from_logits(y_onehot, to_logits_from_probs(p_xgb))  # (B,)
                ce_hgb = ce_from_logits(y_onehot, to_logits_from_probs(p_hgb))  # (B,)
                p_resp = tf.sigmoid(-self.gate_tau * (ce_xgb - ce_hgb))         # (B,)
                p_resp = tf.reshape(p_resp, (-1, 1))                            # (B,1)
                gate_bce = -tf.reduce_mean(p_resp * tf.math.log(lam + eps) + (1.0 - p_resp) * tf.math.log(1.0 - lam + eps))

                # Anti-collapse entropy on λ
                l_entropy = tf.reduce_mean(lam * tf.math.log(lam + eps) + (1.0 - lam) * tf.math.log(1.0 - lam + eps))

                loss = (ce
                        + self.lam_alpha_smooth * l_smooth + self.lam_alpha_curv * l_curv + self.lam_ortho * l_ortho
                        + self.lam_gate_pen * l_gate + self.lam_lambda_reg * l_lam
                        + self.gate_bce_weight * gate_bce
                        + self.gate_entropy_weight * l_entropy)

            g_delta = tape.gradient(loss, delta_model.trainable_variables)
            g_gate  = tape.gradient(loss, lam_gate.trainable_variables)
            del tape
            g_delta = [(g,v) for g,v in zip(g_delta, delta_model.trainable_variables) if g is not None]
            g_gate  = [(g,v) for g,v in zip(g_gate,  lam_gate.trainable_variables)  if g is not None]
            opt_delta.apply_gradients(g_delta)
            opt_gate.apply_gradients(g_gate)

            return float(ce), float(l_smooth), float(l_ortho)

        # tensors
        X_tr_tf  = tf.constant(X_tr,  tf.float32)
        X_va_tf  = tf.constant(X_va,  tf.float32)
        PX_tr_tf = tf.constant(PX_tr, tf.float32)
        PX_va_tf = tf.constant(PX_va, tf.float32)
        PH_tr_tf = tf.constant(PH_tr, tf.float32)
        PH_va_tf = tf.constant(PH_va, tf.float32)
        YOH_tr_tf= tf.constant(_dense32(YOH_tr), tf.float32)
        YOH_va_tf= tf.constant(_dense32(YOH_va), tf.float32)
        X_tr_gate_tf = tf.constant(X_tr_gate, tf.float32)
        X_va_gate_tf = tf.constant(X_va_gate, tf.float32)

        # training loop with early stopping on val CE/NLL
        best = 1e9
        bad = 0
        best_w_delta = None
        best_w_gate = None

        rng = range(self.max_epochs)
        if self.progress_bar:
            try:
                from tqdm import tqdm
                rng = tqdm(rng)
            except Exception:
                pass

        for epoch in rng:
            ce_tr, l_s, l_o = train_step(X_tr_gate_tf, X_tr_tf, PX_tr_tf, PH_tr_tf, YOH_tr_tf)

            # compute val CE & lambda stats
            lam_va = lam_gate(X_va_gate_tf, training=False)                       # (B,1)
            p0_va  = lam_va * PX_va_tf + (1.0 - lam_va) * PH_va_tf               # (B,C)
            f0l_va = to_logits_from_probs(p0_va)                                  # (B,C)
            logits_va, _, _, _ = delta_model(X_va_tf, f0l_va, training=False, return_delta=True)
            ce_va = tf.reduce_mean(ce_from_logits(YOH_va_tf, logits_va)).numpy().item()

            if self.progress_bar and hasattr(rng, "set_postfix"):
                lam_m, lam_s = float(tf.reduce_mean(lam_va).numpy()), float(tf.math.reduce_std(lam_va).numpy())
                rng.set_postfix(ce=f"{ce_tr:.3f}", val_ce=f"{ce_va:.3f}", lam_m=f"{lam_m:.3f}", lam_s=f"{lam_s:.3f}")

            if ce_va + 1e-4 < best:
                best, bad = ce_va, 0
                best_w_delta = delta_model.get_weights()
                best_w_gate  = lam_gate.get_weights()
            else:
                bad += 1
                if bad >= self.patience:
                    break

        if best_w_delta is not None: delta_model.set_weights(best_w_delta)
        if best_w_gate  is not None: lam_gate.set_weights(best_w_gate)

        # ------ Post-hoc calibration on validation ------
        # Build f0 & z (integrated delta) without g; then optimize:
        #   logits_c = f0_logits + c * z   (c >= 0)
        #   and a temperature T > 0: logits_out = logits_c / T
        with tf.device("/CPU:0"):
            lam_va = lam_gate(X_va_gate_tf, training=False)
            p0_va = lam_va * PX_va_tf + (1.0 - lam_va) * PH_va_tf
            f0l_va = to_logits_from_probs(p0_va)
            _, z_va, _, _ = delta_model(X_va_tf, f0l_va, training=False, return_delta=True)  # z: (B,C)
            # convert tensors to numpy
            f0l_va_np = f0l_va.numpy()
            z_va_np   = z_va.numpy()
            y_va_np   = Y_va.copy()

        def val_ce_for(c: float, T: float) -> float:
            logits = f0l_va_np + c * z_va_np
            logits = logits / T
            p = softmax_np(logits)
            return float(log_loss(y_va_np, p, labels=self.classes_))

        # grid search small ranges (fast & stable)
        c_candidates = np.linspace(0.0, 2.0, 21)  # scale of residual
        T_candidates = np.linspace(0.5, 3.0, 21)  # temperature
        best_ce = 1e9
        best_c = 0.0
        best_T = 1.0
        for c in c_candidates:
            for T in T_candidates:
                ce_try = val_ce_for(c, T)
                if ce_try < best_ce:
                    best_ce = ce_try
                    best_c, best_T = c, T

        # persist artifacts
        self._delta_model_ = delta_model
        self._lam_gate_ = lam_gate
        self.n_features_in_ = X.shape[1]
        self.n_classes_ = n_classes
        self._cal_c_ = float(best_c)
        self._cal_T_ = float(best_T)

        return self

    # ---------- inference helpers ----------
    def _preprocess_X(self, X: np.ndarray) -> np.ndarray:
        X = check_array(X)
        X = _dense32(X)
        if getattr(self, "_scaler_", None) is not None:
            X = self._scaler_.transform(X).astype(np.float32)
        return X

    def _base_proba(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        # HGB
        ph = self._base_hgb_.predict_proba(X).astype(np.float32)
        # XGB if available
        if getattr(self, "_has_xgb_", False) and (self._base_xgb_ is not None):
            px = self._base_xgb_.predict_proba(X).astype(np.float32)
        else:
            px = ph
        return px, ph

    def _forward_logits(self, Xs: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # build gate inputs
        px, ph = self._base_proba(Xs)
        X_gate = concat_gate_inputs(Xs, px, ph)
        lam = self._lam_gate_(tf.constant(X_gate, tf.float32), training=False).numpy()  # (B,1)
        p0 = lam * px + (1.0 - lam) * ph                                                # (B,C)
        f0l = np.log(np.clip(p0, 1e-7, 1.0))                                            # (B,C)
        # z from delta_model (without g)
        f0l_tf = tf.constant(f0l, tf.float32)
        X_tf   = tf.constant(Xs, tf.float32)
        _, z, _, _ = self._delta_model_(X_tf, f0l_tf, training=False, return_delta=True)
        z = z.numpy()
        return f0l, z, lam

    # ---------- sklearn predict API ----------
    def predict_proba(self, X):
        _require_tf()
        Xs = self._preprocess_X(X)
        f0l, z, _ = self._forward_logits(Xs)
        # calibrated logits
        logits = (f0l + self._cal_c_ * z) / self._cal_T_
        p = softmax_np(logits)
        return p

    def predict(self, X):
        p = self.predict_proba(X)
        return np.argmax(p, axis=1)

    def evaluate(self, X, y, calibrated: bool = True) -> Dict[str, float]:
        """Return dict with {'nll': cross_entropy, 'acc': accuracy} on provided (X,y)."""
        _require_tf()
        Xs = self._preprocess_X(X)
        px, ph = self._base_proba(Xs)
        # forward f0 & residual
        X_gate = concat_gate_inputs(Xs, px, ph)
        lam = self._lam_gate_(tf.constant(X_gate, tf.float32), training=False)
        p0 = lam.numpy() * px + (1.0 - lam.numpy()) * ph
        f0l = np.log(np.clip(p0, 1e-7, 1.0))
        X_tf = tf.constant(Xs, tf.float32)
        f0l_tf = tf.constant(f0l, tf.float32)
        logits, z, _, _ = self._delta_model_(X_tf, f0l_tf, training=False, return_delta=True)
        logits = logits.numpy()
        z = z.numpy()

        if calibrated:
            logits = (f0l + self._cal_c_ * z) / self._cal_T_
        # else use raw logits from model (already includes g*z inside logits)
        p = softmax_np(logits)
        y_true = np.asarray(y).astype(np.int64).ravel()
        return {
            "nll": float(log_loss(y_true, p, labels=self.classes_)),
            "acc": float(accuracy_score(y_true, np.argmax(p, axis=1)))
        }

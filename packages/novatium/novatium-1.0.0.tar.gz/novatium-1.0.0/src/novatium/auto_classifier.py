from __future__ import annotations
import numpy as np, warnings
from typing import Dict, Any, Optional
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.model_selection import KFold, train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.utils.validation import check_X_y, check_array

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


# ---------- utils ----------
def _require_tf():
    if not HAS_TF:
        raise ImportError(
            'TensorFlow is required for NovaAutoClassifier. Install via: pip install "novatium[tensorflow]"'
        )

def _dense32(a): return np.asarray(a, dtype=np.float32)

def _y_bin(y):
    y = _dense32(y).reshape(-1, 1)
    u = np.unique(y)
    if not set(u.tolist()).issubset({0.0, 1.0}):
        raise ValueError("NovaAutoClassifier expects binary labels {0,1}.")
    return y

def _logit(p, eps=1e-6):
    p = np.clip(p, eps, 1.0 - eps)
    return np.log(p / (1.0 - p)).astype(np.float32)

def gauss_legendre_nodes_weights(K=12):
    t, w = np.polynomial.legendre.leggauss(K)
    a = (t + 1.0)/2.0; w = w/2.0
    return a.astype("float32"), w.astype("float32")

def concat_gate_inputs(X, p_xgb, p_hgb):
    return np.concatenate([_dense32(X), _dense32(p_xgb), _dense32(p_hgb)], axis=1).astype(np.float32)


# ---------- base learners (OOF + full) ----------
def _make_hgb(seed, params=None):
    params = params or {}
    return HistGradientBoostingClassifier(
        learning_rate=params.get("learning_rate", 0.06),
        max_depth=params.get("max_depth", 6),
        max_iter=params.get("max_iter", 400),
        random_state=seed
    )

def _make_xgb(seed, params=None):
    params = params or {}
    return XGBClassifier(
        n_estimators=params.get("n_estimators", 800),
        max_depth=params.get("max_depth", 6),
        learning_rate=params.get("learning_rate", 0.06),
        subsample=params.get("subsample", 0.8),
        colsample_bytree=params.get("colsample_bytree", 0.8),
        reg_lambda=params.get("reg_lambda", 1.0),
        tree_method=params.get("tree_method", "hist"),
        n_jobs=params.get("n_jobs", -1),
        random_state=seed,
        eval_metric="logloss",
        use_label_encoder=False,
    )

def _fit_oof_single(X_tr, y_tr, seed, kind="hgb", n_splits=5, params=None):
    y1d = y_tr.ravel().astype(np.int32)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    p_oof = np.zeros((len(X_tr), 1), np.float32)
    for tr, va in kf.split(X_tr):
        if kind == "xgb" and HAS_XGB:
            base = _make_xgb(seed, params)
        else:
            if kind == "xgb" and not HAS_XGB:
                warnings.warn("XGBoost not installed; falling back to HGB.", RuntimeWarning)
            base = _make_hgb(seed, params)
        base.fit(X_tr[tr], y1d[tr])
        p_oof[va] = base.predict_proba(X_tr[va])[:, 1].astype(np.float32).reshape(-1, 1)
    # also fit a full model for inference
    base_full = _make_xgb(seed, params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, params)
    base_full.fit(X_tr, y1d)
    return {"p_train_oof": p_oof, "base_full": base_full}

def fit_bases_oof(X_train, y_train, seed=42, n_splits=5, xgb_params=None, hgb_params=None):
    oof_hgb = _fit_oof_single(X_train, y_train, seed, "hgb", n_splits, hgb_params)
    oof_xgb = _fit_oof_single(X_train, y_train, seed, "xgb", n_splits, xgb_params) if HAS_XGB else oof_hgb
    return oof_xgb, oof_hgb


# ---------- TF heads ----------
class BasePlusIntegralDeltaLogit(Model):
    """
    Input: x, f0_logit (mixture logit). Predicts integ delta and a softplus gate g(x),
    returns prob sigma(f0_logit + g*integ).
    """
    def __init__(self, alphas, weights, hidden=32, fourier_m=6, weight_decay=1e-4):
        super().__init__()
        self.K = len(alphas)
        self.A = tf.constant(alphas[None, :, None])
        self.W = tf.constant(weights[None, :, None])
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
            layers.Dense(1, kernel_regularizer=reg)
        ])
        self.gate = tf.keras.Sequential([
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.softplus)
        ])
        self.fourier_m = fourier_m

    def call(self, x, f0_logit, training=False, return_delta=False):
        B = tf.shape(x)[0]
        xT = tf.tile(tf.reshape(x, (B, 1, -1)), [1, self.K, 1])
        aT = tf.tile(self.A, [B, 1, 1])
        k  = tf.range(1, self.fourier_m+1, dtype=tf.float32)[None, None, :]
        a_feats = tf.concat([tf.sin(aT*np.pi*k), tf.cos(aT*np.pi*k)], axis=-1)

        hx = self.enc_x(xT)
        ha = self.enc_a(tf.concat([aT, a_feats], axis=-1))
        h  = self.film_gamma(ha) * hx + self.film_beta(ha)

        delta = self.delta_head(h)                                    # (B,K,1)
        integ = tf.reduce_sum(delta * tf.tile(self.W, [B,1,1]), axis=1)  # (B,1)
        g = self.gate(x)                                              # (B,1)

        logit = f0_logit + g * integ
        p = tf.sigmoid(logit)
        if return_delta:
            return p, logit, integ, g, delta
        return p, logit, integ, g

class LambdaGate(Model):
    """Per-sample λ(x)∈(0,1). Input is [x, p_xgb, p_hgb]."""
    def __init__(self, hidden=24, weight_decay=1e-4):
        super().__init__()
        reg = regularizers.l2(weight_decay)
        self.net = tf.keras.Sequential([
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.sigmoid)
        ])
    def call(self, x, training=False):
        return self.net(x)


# ---------- Estimator ----------
class NovaAutoClassifier(BaseEstimator, ClassifierMixin):
    """
    Dual-base (HGB + XGB) lambda-gated classifier with integral-delta correction in logit space.
    No args needed; TensorFlow required, XGBoost optional (falls back to HGB if missing).
    """

    def __init__(
        self,
        use_xgb: bool = True,
        hgb_params: Optional[Dict[str, Any]] = None,
        xgb_params: Optional[Dict[str, Any]] = None,
        seed: int = 42,
        n_splits: int = 5,
        K: int = 8,
        hidden: int = 32,
        fourier_m: int = 6,
        lr: float = 3e-3,
        max_epochs: int = 250,
        patience: int = 12,
        gate_tau: float = 8.0,
        gate_entropy_weight: float = 5e-4,
        lambda_center: float = 0.5,
        lam_alpha_smooth: float = 3e-3,
        lam_alpha_curv: float = 2e-3,
        lam_ortho: float = 3e-3,
        lam_gate_pen: float = 5e-4,
        lam_lambda_reg: float = 1e-4,
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
        self.gate_tau = gate_tau
        self.gate_entropy_weight = gate_entropy_weight
        self.lambda_center = lambda_center
        self.lam_alpha_smooth = lam_alpha_smooth
        self.lam_alpha_curv = lam_alpha_curv
        self.lam_ortho = lam_ortho
        self.lam_gate_pen = lam_gate_pen
        self.lam_lambda_reg = lam_lambda_reg

    def fit(self, X, y):
        _require_tf()
        X, y = check_X_y(X, y, accept_sparse=False)
        X = _dense32(X); y = _y_bin(y)

        # OOF probabilities and fully fitted bases (persist for inference)
        oof_xgb, oof_hgb = fit_bases_oof(
            X, y, seed=self.seed, n_splits=self.n_splits,
            xgb_params=self.xgb_params if (self.use_xgb and HAS_XGB) else None,
            hgb_params=self.hgb_params
        )
        PX = oof_xgb["p_train_oof"] if (self.use_xgb and HAS_XGB) else oof_hgb["p_train_oof"]
        PH = oof_hgb["p_train_oof"]

        # persist fitted base models for inference
        self._base_hgb_ = oof_hgb["base_full"]
        self._has_xgb_ = bool(HAS_XGB and self.use_xgb)
        self._base_xgb_ = oof_xgb["base_full"] if self._has_xgb_ else None

        # train/val split
        X_tr, X_va, Y_tr, Y_va, PX_tr, PX_va, PH_tr, PH_va = train_test_split(
            X, y, PX, PH, test_size=0.15, random_state=self.seed
        )
        X_tr_gate = concat_gate_inputs(X_tr, PX_tr, PH_tr)
        X_va_gate = concat_gate_inputs(X_va, PX_va, PH_va)

        # build TF models
        alphas, weights = gauss_legendre_nodes_weights(K=self.K)
        delta_head = BasePlusIntegralDeltaLogit(alphas, weights, hidden=self.hidden, fourier_m=self.fourier_m, weight_decay=1e-4)
        lam_gate   = LambdaGate(hidden=24)

        # boot shapes
        _ = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        lam_boot = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        f0p_boot = tf.clip_by_value(lam_boot * tf.constant(PX_tr[:2], tf.float32) + (1.0 - lam_boot) * tf.constant(PH_tr[:2], tf.float32), 1e-6, 1-1e-6)
        f0log_boot = tf.math.log(f0p_boot / (1.0 - f0p_boot))
        _ = delta_head(tf.constant(X_tr[:2], tf.float32), f0log_boot, training=False)

        opt_delta = optimizers.Adam(self.lr)
        opt_gate  = optimizers.Adam(self.lr)
        eps = tf.constant(1e-7, dtype=tf.float32)

        def train_step(x_gate_in, x_raw, pxgb, phgb, ytrue):
            with tf.GradientTape(persistent=True) as tape:
                lam = lam_gate(x_gate_in)                          # (B,1)
                f0p = tf.clip_by_value(lam * pxgb + (1.0 - lam) * phgb, 1e-6, 1-1e-6)
                f0log = tf.math.log(f0p / (1.0 - f0p))
                p, logit, integ, g, delta = delta_head(x_raw, f0log, training=True, return_delta=True)
                p = tf.clip_by_value(p, 1e-6, 1.0 - 1e-6)

                # Bernoulli NLL
                bce = -tf.reduce_mean(ytrue*tf.math.log(p) + (1.0 - ytrue)*tf.math.log(1.0 - p))

                # alpha regularizers
                diff = delta[:, 1:, :] - delta[:, :-1, :]
                l_smooth = tf.reduce_mean(tf.square(diff))
                l_curv = tf.reduce_mean(tf.square(delta[:, 2:, :] - 2.0*delta[:, 1:-1, :] + delta[:, :-2, :])) if self.lam_alpha_curv > 0 else 0.0

                # orthogonality (logit space)
                logit_z = logit - tf.reduce_mean(logit, axis=0, keepdims=True)
                integ_z = integ - tf.reduce_mean(integ, axis=0, keepdims=True)
                l_ortho = tf.square(tf.reduce_mean(logit_z * integ_z))

                # small penalties
                l_gate = tf.reduce_mean(g)
                l_lam  = tf.reduce_mean(tf.square(lam - self.lambda_center))

                # responsibility: who was better
                ex = - (ytrue*tf.math.log(tf.clip_by_value(pxgb,1e-6,1-1e-6)) + (1.0-ytrue)*tf.math.log(tf.clip_by_value(1.0-pxgb,1e-6,1-1e-6)))
                eh = - (ytrue*tf.math.log(tf.clip_by_value(phgb,1e-6,1-1e-6)) + (1.0-ytrue)*tf.math.log(tf.clip_by_value(1.0-phgb,1e-6,1-1e-6)))
                p_target = tf.sigmoid(-self.gate_tau * (ex - eh))  # prob XGB better
                gate_bce = -tf.reduce_mean(p_target * tf.math.log(lam + eps) + (1.0 - p_target) * tf.math.log(1.0 - lam + eps))

                # anti-collapse entropy
                l_entropy = tf.reduce_mean(lam * tf.math.log(lam + eps) + (1.0 - lam) * tf.math.log(1.0 - lam + eps))

                loss = (bce
                        + self.lam_alpha_smooth*l_smooth + self.lam_alpha_curv*l_curv + self.lam_ortho*l_ortho
                        + self.lam_gate_pen*l_gate + self.lam_lambda_reg*l_lam
                        + 1e-3 * gate_bce
                        + self.gate_entropy_weight * l_entropy)

            g_delta = tape.gradient(loss, delta_head.trainable_variables)
            g_gate  = tape.gradient(loss, lam_gate.trainable_variables)
            del tape
            g_delta = [(g,v) for g,v in zip(g_delta, delta_head.trainable_variables) if g is not None]
            g_gate  = [(g,v) for g,v in zip(g_gate,  lam_gate.trainable_variables)  if g is not None]
            opt_delta.apply_gradients(g_delta)
            opt_gate.apply_gradients(g_gate)

        # tensors
        X_tr_gate_tf = tf.constant(X_tr_gate, tf.float32)
        X_tr_tf      = tf.constant(X_tr, tf.float32)
        PX_tr_tf     = tf.constant(PX_tr, tf.float32)
        PH_tr_tf     = tf.constant(PH_tr, tf.float32)
        Y_tr_tf      = tf.constant(Y_tr, tf.float32)

        best = 1e9; bad = 0; best_w_delta = None; best_w_gate = None
        for epoch in range(self.max_epochs):
            train_step(X_tr_gate_tf, X_tr_tf, PX_tr_tf, PH_tr_tf, Y_tr_tf)

            # simple val BCE
            lam_va = lam_gate(tf.constant(X_va_gate, tf.float32), training=False)
            f0p_va = tf.clip_by_value(lam_va * tf.constant(PX_va, tf.float32) + (1.0 - lam_va) * tf.constant(PH_va, tf.float32), 1e-6, 1-1e-6)
            f0log_va = tf.math.log(f0p_va / (1.0 - f0p_va))
            p_va, _, _, _ = delta_head(tf.constant(X_va, tf.float32), f0log_va, training=False)
            # manual BCE to avoid sklearn dep here
            val_p = np.clip(p_va.numpy().reshape(-1), 1e-6, 1-1e-6)
            val_y = Y_va.reshape(-1)
            val_bce = float(-(val_y*np.log(val_p) + (1-val_y)*np.log(1-val_p)).mean())

            if val_bce + 1e-4 < best:
                best, bad = val_bce, 0
                best_w_delta = delta_head.get_weights()
                best_w_gate  = lam_gate.get_weights()
            else:
                bad += 1
                if bad >= self.patience:
                    break

        if best_w_delta is not None: delta_head.set_weights(best_w_delta)
        if best_w_gate  is not None: lam_gate.set_weights(best_w_gate)

        self._delta_head_ = delta_head
        self._lam_gate_ = lam_gate
        self.n_features_in_ = X.shape[1]
        return self

    def predict_proba(self, X):
        _require_tf()
        X = check_array(X)
        X = _dense32(X)

        # USE PERSISTED BASE MODELS (no refit at inference)
        ph = self._base_hgb_.predict_proba(X)[:, 1].astype(np.float32).reshape(-1, 1)
        if self._has_xgb_ and self._base_xgb_ is not None:
            px = self._base_xgb_.predict_proba(X)[:, 1].astype(np.float32).reshape(-1, 1)
        else:
            px = ph

        X_gate = concat_gate_inputs(X, px, ph)
        lam = self._lam_gate_(tf.constant(X_gate, tf.float32), training=False).numpy()
        f0p = np.clip(lam * px + (1.0 - lam) * ph, 1e-6, 1.0 - 1e-6)
        f0log = _logit(f0p)

        p, _, _, _ = self._delta_head_(tf.constant(X, np.float32), tf.constant(f0log, np.float32), training=False)
        p = np.clip(p.numpy().reshape(-1), 1e-6, 1.0 - 1e-6)
        return np.c_[1.0 - p, p]

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(np.int32)

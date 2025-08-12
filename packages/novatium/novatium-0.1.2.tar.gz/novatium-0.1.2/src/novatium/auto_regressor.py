from __future__ import annotations
import numpy as np, gc, warnings
from typing import Dict, Any, Optional
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.utils.validation import check_X_y, check_array

# Optional deps
try:
    from xgboost import XGBRegressor  # type: ignore
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
        raise ImportError(
            "TensorFlow is required for NovaAutoRegressor. "
            "Install with: pip install novatium[tensorflow]"
        )

def _dense32(a): return np.asarray(a, dtype=np.float32)

def ensure_2d_y(y):
    y = _dense32(y)
    return y.reshape(-1, 1) if y.ndim == 1 else y

def gauss_legendre_nodes_weights(K=12):
    t, w = np.polynomial.legendre.leggauss(K)
    a = (t + 1.0)/2.0; w = w/2.0
    return a.astype("float32"), w.astype("float32")

def concat_gate_inputs(X, f_xgb, f_hgb):
    return np.concatenate([_dense32(X), _dense32(f_xgb), _dense32(f_hgb)], axis=1).astype(np.float32)

# ---------- base learners (OOF) ----------
def _make_hgb(seed, params=None):
    if params is None: params = {}
    return HistGradientBoostingRegressor(
        max_depth=params.get("max_depth", 6),
        learning_rate=params.get("learning_rate", 0.05),
        max_iter=params.get("max_iter", 400),
        random_state=seed
    )

def _make_xgb(seed, params=None):
    if params is None: params = {}
    return XGBRegressor(
        n_estimators=params.get("n_estimators", 800),
        max_depth=params.get("max_depth", 6),
        learning_rate=params.get("learning_rate", 0.05),
        subsample=params.get("subsample", 0.8),
        colsample_bytree=params.get("colsample_bytree", 0.8),
        reg_lambda=params.get("reg_lambda", 1.0),
        tree_method=params.get("tree_method", "hist"),
        n_jobs=params.get("n_jobs", -1),
        random_state=seed,
    )

def _fit_oof_single(X_tr, y_tr, X_te, seed, kind="hgb", n_splits=5, params=None):
    y1d = y_tr.ravel()
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    f0_oof = np.zeros((len(X_tr), 1), np.float32)
    te_preds = []
    for tr, va in kf.split(X_tr):
        if kind == "xgb" and HAS_XGB:
            base = _make_xgb(seed, params)
        else:
            if kind == "xgb" and not HAS_XGB:
                warnings.warn("XGBoost not installed, falling back to HGB.", RuntimeWarning)
            base = _make_hgb(seed, params)
        base.fit(X_tr[tr], y1d[tr])
        f0_oof[va] = base.predict(X_tr[va]).astype(np.float32).reshape(-1, 1)
        te_preds.append(base.predict(X_te).astype(np.float32).reshape(-1, 1))
    f0_te = np.mean(te_preds, axis=0).astype(np.float32)
    # fit full model for potential external use
    base_full = _make_xgb(seed, params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, params)
    base_full.fit(X_tr, y1d)
    return {"f0_train_oof": f0_oof, "f0_test": f0_te, "base_full": base_full}

def fit_bases_oof(X_train, y_train, X_test, seed=42, n_splits=5, xgb_params=None, hgb_params=None):
    oof_hgb = _fit_oof_single(X_train, y_train, X_test, seed, "hgb", n_splits, hgb_params)
    oof_xgb = _fit_oof_single(X_train, y_train, X_test, seed, "xgb", n_splits, xgb_params) if HAS_XGB else oof_hgb
    return oof_xgb, oof_hgb

# ---------- Keras models ----------
def gaussian_nll(y, mu, log_sigma):
    inv_var = tf.exp(-2.0 * log_sigma)
    return 0.5 * (tf.math.log(2.0*np.pi) + 2.0*log_sigma + tf.square(y - mu) * inv_var)

class BasePlusIntegralDeltaNLL(Model):
    def __init__(self, alphas, weights, hidden=32, fourier_m=6, weight_decay=1e-4):
        super().__init__()
        self.K = len(alphas)
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
            layers.Dense(1, kernel_regularizer=reg)
        ])
        self.gate = tf.keras.Sequential([
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.softplus)
        ])
        self.logsig_head = tf.keras.Sequential([
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(1, kernel_regularizer=reg)
        ])
        self.fourier_m = fourier_m

    def call(self, x, f0, training=False, return_delta=False):
        B = tf.shape(x)[0]
        xT = tf.tile(tf.reshape(x, (B, 1, -1)), [1, self.K, 1])  # (B,K,D)
        aT = tf.tile(self.A, [B, 1, 1])                          # (B,K,1)
        k  = tf.range(1, self.fourier_m+1, dtype=tf.float32)[None, None, :]
        a_feats = tf.concat([tf.sin(aT*np.pi*k), tf.cos(aT*np.pi*k)], axis=-1)

        hx = self.enc_x(xT)
        ha = self.enc_a(tf.concat([aT, a_feats], axis=-1))
        h  = self.film_gamma(ha) * hx + self.film_beta(ha)

        delta = self.delta_head(h)                               # (B,K,1)
        integ = tf.reduce_sum(delta * tf.tile(self.W, [B,1,1]), axis=1)  # (B,1)
        g = self.gate(x)                                         # (B,1)
        mu = f0 + g * integ                                      # (B,1)
        log_sigma = tf.clip_by_value(self.logsig_head(x), -6.0, 3.0)

        if return_delta:
            return mu, log_sigma, integ, g, delta
        return mu, log_sigma, integ, g

class LambdaGate(Model):
    """Per-sample λ(x) in (0,1). Input is [x, f_xgb, f_hgb]."""
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
        return self.net(x)  # (B,1)

def _forward(delta_model, lam_gate, X_gate, X_raw, fxgb, fhgb):
    lam = lam_gate(tf.constant(X_gate, tf.float32), training=False).numpy()
    f0  = lam * fxgb + (1.0 - lam) * fhgb
    mu, log_sig, integ, g = delta_model(tf.constant(X_raw, tf.float32),
                                        tf.constant(f0, tf.float32),
                                        training=False)
    return mu.numpy(), log_sig.numpy(), f0, lam

# ---------- Public estimator ----------
class NovaAutoRegressor(BaseEstimator, RegressorMixin):
    """
    Dual-base (HGB + XGB) lambda-gated regressor with integral-delta residual head.
    Defaults require TensorFlow; XGBoost is optional (falls back to HGB if not installed).

    Parameters
    ----------
    use_xgb : bool
        If True and xgboost is installed, use HGB + XGB; else HGB+HGB.
    hgb_params, xgb_params : dict or None
        Optional overrides for base learner hyperparameters.
    seed : int
        Random seed for OOF and models.
    n_splits : int
        KFold splits for OOF predictions.
    K : int
        Gauss-Legendre quadrature nodes.
    hidden : int
        Hidden width in Keras heads.
    fourier_m : int
        Fourier features for alpha encoding.
    lr : float
        Adam learning rate.
    max_epochs : int
        Training epochs.
    patience : int
        Early stopping patience on val NLL.
    gate_bce_weight, gate_tau, gate_entropy_weight : float
        Regularization weights for lambda gate.
    lambda_center, lam_alpha_smooth, lam_alpha_curv, lam_ortho, lam_gate_pen, lam_lambda_reg : float
        Regularization terms for stability.
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
        max_epochs: int = 300,
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

    # ---- sklearn API ----
    def fit(self, X, y):
        _require_tf()
        X, y = check_X_y(X, y, accept_sparse=False, y_numeric=True)
        X = _dense32(X); y = ensure_2d_y(y)

        # Prepare a dummy test split for OOF inference symmetry
        X_tr, X_te = X, X[: min(64, len(X))]
        oof_xgb, oof_hgb = fit_bases_oof(
            X_tr, y, X_te, seed=self.seed, n_splits=self.n_splits,
            xgb_params=self.xgb_params if (self.use_xgb and HAS_XGB) else None,
            hgb_params=self.hgb_params
        )
        
        fxgb_tr, fxgb_te = oof_xgb["f0_train_oof"], oof_xgb["f0_test"]
        fhgb_tr, fhgb_te = oof_hgb["f0_train_oof"], oof_hgb["f0_test"]

        self._base_hgb_ = oof_hgb["base_full"]
        self._has_xgb_ = bool(HAS_XGB and self.use_xgb)
        self._base_xgb_ = oof_xgb["base_full"] if self._has_xgb_ else None

        # Train/val split
        X_tr2, X_va, Y_tr, Y_va, FX_tr, FX_va, FH_tr, FH_va = train_test_split(
            X_tr, y, fxgb_tr, fhgb_tr, test_size=0.15, random_state=self.seed
        )

        # Gate inputs
        X_tr_gate = concat_gate_inputs(X_tr2, FX_tr, FH_tr)
        X_va_gate = concat_gate_inputs(X_va,  FX_va, FH_va)

        # Build models
        alphas, weights = gauss_legendre_nodes_weights(K=self.K)
        delta_model = BasePlusIntegralDeltaNLL(alphas, weights, hidden=self.hidden, fourier_m=self.fourier_m, weight_decay=1e-4)
        lam_gate    = LambdaGate(hidden=24)

        # Boot build
        _ = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        lam_boot = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        f0_boot  = lam_boot * tf.constant(FX_tr[:2], tf.float32) + (1.0 - lam_boot) * tf.constant(FH_tr[:2], tf.float32)
        _ = delta_model(tf.constant(X_tr2[:2], tf.float32), f0_boot, training=False)

        # Optims
        opt_delta = optimizers.Adam(self.lr)
        opt_gate  = optimizers.Adam(self.lr)

        eps = tf.constant(1e-7, dtype=tf.float32)

        def train_step(x_gate_in, x_raw, fxgb, fhgb, ytrue):
            with tf.GradientTape(persistent=True) as tape:
                lam = lam_gate(x_gate_in)
                f0  = lam * fxgb + (1.0 - lam) * fhgb
                mu, log_sig, integ, g, delta = delta_model(x_raw, f0, training=True, return_delta=True)

                nll = tf.reduce_mean(gaussian_nll(ytrue, mu, log_sig))
                diff = delta[:, 1:, :] - delta[:, :-1, :]
                l_smooth = tf.reduce_mean(tf.square(diff))
                l_curv = tf.reduce_mean(tf.square(delta[:, 2:, :] - 2.0*delta[:, 1:-1, :] + delta[:, :-2, :])) if self.lam_alpha_curv > 0 else 0.0

                f0_z = f0 - tf.reduce_mean(f0, axis=0, keepdims=True)
                integ_z = integ - tf.reduce_mean(integ, axis=0, keepdims=True)
                l_ortho = tf.square(tf.reduce_mean(f0_z * integ_z))

                l_gate = tf.reduce_mean(g)
                l_lam  = tf.reduce_mean(tf.square(lam - self.lambda_center))

                ex = tf.square(ytrue - fxgb)
                eh = tf.square(ytrue - fhgb)
                p  = tf.sigmoid(-self.gate_tau * (ex - eh))
                gate_bce = -tf.reduce_mean(p * tf.math.log(lam + eps) + (1.0 - p) * tf.math.log(1.0 - lam + eps))
                l_entropy = tf.reduce_mean(lam * tf.math.log(lam + eps) + (1.0 - lam) * tf.math.log(1.0 - lam + eps))

                loss = (nll
                        + self.lam_alpha_smooth*l_smooth + self.lam_alpha_curv*l_curv + self.lam_ortho*l_ortho
                        + self.lam_gate_pen*l_gate + self.lam_lambda_reg*l_lam
                        + self.gate_bce_weight * gate_bce
                        + self.gate_entropy_weight * l_entropy)

            grads_delta = tape.gradient(loss, delta_model.trainable_variables)
            grads_gate  = tape.gradient(loss, lam_gate.trainable_variables)
            del tape
            grads_delta = [(g,v) for g,v in zip(grads_delta, delta_model.trainable_variables) if g is not None]
            grads_gate  = [(g,v) for g,v in zip(grads_gate,  lam_gate.trainable_variables)  if g is not None]
            opt_delta.apply_gradients(grads_delta)
            opt_gate.apply_gradients(grads_gate)
            return float(nll)

        # tensors
        X_tr_gate_tf = tf.constant(X_tr_gate, tf.float32)
        X_tr_tf      = tf.constant(X_tr2, tf.float32)
        FX_tr_tf     = tf.constant(FX_tr, tf.float32)
        FH_tr_tf     = tf.constant(FH_tr, tf.float32)
        Y_tr_tf      = tf.constant(Y_tr, tf.float32)

        best = 1e9; bad = 0; best_w_delta = None; best_w_gate = None
        iters = range(self.max_epochs)
        for epoch in iters:
            _ = train_step(X_tr_gate_tf, X_tr_tf, FX_tr_tf, FH_tr_tf, Y_tr_tf)

            # val nll
            lam_va = lam_gate(tf.constant(concat_gate_inputs(X_va, FX_va, FH_va), tf.float32), training=False)
            f0_va  = lam_va * tf.constant(FX_va, tf.float32) + (1.0 - lam_va) * tf.constant(FH_va, tf.float32)
            mu_v, log_v, _, _ = delta_model(tf.constant(X_va, tf.float32), f0_va, training=False)
            mu_v = mu_v.numpy(); log_v = log_v.numpy()
            nll_va = 0.5 * np.mean(np.log(2*np.pi) + 2*log_v + ((Y_va - mu_v)**2)/np.exp(2*log_v))

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

        # stash
        self._delta_model_ = delta_model
        self._lam_gate_ = lam_gate
        self._oof_fxgb_tr_ = fxgb_tr; self._oof_fhgb_tr_ = fhgb_tr
        self._oof_fxgb_te_sample_ = fxgb_te; self._oof_fhgb_te_sample_ = fhgb_te
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X):
        _require_tf()
        X = check_array(X)
        X = _dense32(X)

        # Use the persisted base models from fit()
        fhgb = self._base_hgb_.predict(X).astype(np.float32).reshape(-1, 1)
        if self._has_xgb_ and self._base_xgb_ is not None:
            fxgb = self._base_xgb_.predict(X).astype(np.float32).reshape(-1, 1)
        else:
            fxgb = fhgb  # fallback if XGB not used

        # Gate inputs: [X, f_xgb, f_hgb]
        X_gate = concat_gate_inputs(X, fxgb, fhgb)

        # Forward through λ-gate and delta head
        lam = self._lam_gate_(tf.constant(X_gate, tf.float32), training=False).numpy()
        f0  = lam * fxgb + (1.0 - lam) * fhgb
        mu, _, _, _ = self._delta_model_(tf.constant(X, tf.float32),
                                        tf.constant(f0, tf.float32),
                                        training=False)
        return mu.numpy().reshape(-1)


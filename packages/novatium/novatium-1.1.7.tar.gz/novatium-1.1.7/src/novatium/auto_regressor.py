# auto_regressor.py
# =========================================================
# NovaAutoRegressor (restored "Emperor" pipeline)
# - Dual-base: HGB + XGB (optional if xgboost installed)
# - OOF base predictions to avoid leakage
# - Learned λ(x) with BCE responsibility + anti-collapse entropy
# - Integral–delta residual head via K-point Gauss–Legendre quadrature
# - Two optimizers (gate vs delta) to stabilize training
# - Consistent scaling for NN heads (base models fit on raw X)
# - Early stopping on val NLL
# - Uncalibrated & calibrated (c*, temp_s) evaluation with MSE & NLL
# - Eager only (no @tf.function) to avoid SymbolicTensor issues
# - Per-fit fresh optimizers to avoid "unknown variable" errors
# =========================================================

from __future__ import annotations
import numpy as np
import gc, warnings, math, random
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.utils.validation import check_X_y, check_array
from sklearn.preprocessing import StandardScaler

# -------- Optional dependencies --------
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


# ===================== utils =====================
def _require_tf():
    if not HAS_TF:
        raise ImportError('TensorFlow is required. Install with: pip install "novatium[tensorflow]"')

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

def gaussian_nll(y, mu, log_sigma):
    inv_var = tf.exp(-2.0 * log_sigma)
    return 0.5 * (tf.math.log(2.0*np.pi) + 2.0*log_sigma + tf.square(y - mu) * inv_var)

def set_all_seeds(seed: int):
    np.random.seed(seed)
    random.seed(seed)
    try:
        tf.random.set_seed(seed)
    except Exception:
        pass


# ===================== base models (OOF) =====================
def _make_hgb(seed, params=None):
    params = params or {}
    return HistGradientBoostingRegressor(
        max_depth=params.get("max_depth", 6),
        learning_rate=params.get("learning_rate", 0.05),
        max_iter=params.get("max_iter", 400),
        random_state=seed
    )

def _make_xgb(seed, params=None):
    params = params or {}
    return XGBRegressor(
        n_estimators=params.get("n_estimators", 800),
        max_depth=params.get("max_depth", 6),
        learning_rate=params.get("learning_rate", 0.05),
        subsample=params.get("subsample", 0.8),
        colsample_bytree=params.get("colsample_bytree", 0.8),
        reg_lambda=params.get("reg_lambda", 1.0),
        tree_method=params.get("tree_method", "hist"),
        n_jobs=params.get("n_jobs", -1),
        random_state=seed
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
                warnings.warn("XGBoost not installed; falling back to HGB for OOF.", RuntimeWarning)
            base = _make_hgb(seed, params)
        base.fit(X_tr[tr], y1d[tr])
        f0_oof[va] = base.predict(X_tr[va]).astype(np.float32).reshape(-1, 1)
        te_preds.append(base.predict(X_te).astype(np.float32).reshape(-1, 1))
    f0_te = np.mean(te_preds, axis=0).astype(np.float32)
    base_full = _make_xgb(seed, params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, params)
    base_full.fit(X_tr, y1d)
    return {"f0_train_oof": f0_oof, "f0_test": f0_te, "base_full": base_full}

def fit_bases_oof(X_train, y_train, X_test, seed=42, n_splits=5, xgb_params=None, hgb_params=None):
    oof_hgb = _fit_oof_single(X_train, y_train, X_test, seed, "hgb", n_splits, hgb_params)
    oof_xgb = _fit_oof_single(X_train, y_train, X_test, seed, "xgb", n_splits, xgb_params) if HAS_XGB else oof_hgb
    return oof_xgb, oof_hgb


# ===================== Keras models =====================
class BasePlusIntegralDeltaNLL(Model):
    """Integral-delta residual head with K-point Gauss–Legendre quadrature."""
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
    """Per-sample λ(x) in (0,1). Input is [scaled x, f_xgb, f_hgb]."""
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


# ===================== Estimator =====================
@dataclass
class NovaAutoRegressor(BaseEstimator, RegressorMixin):
    # Bases
    use_xgb: bool = True
    hgb_params: Optional[Dict[str, Any]] = None
    xgb_params: Optional[Dict[str, Any]] = None
    n_splits: int = 5

    # Seeds & scaling
    seed: int = 42
    scale_X: bool = True          # scale NN inputs (not base models)

    # Integral–delta head
    K: int = 8
    hidden: int = 32
    fourier_m: int = 6
    weight_decay: float = 1e-4

    # Optim & training
    lr: float = 3e-3
    max_epochs: int = 300
    patience: int = 12
    progress_bar: bool = True

    # Regularizers
    lam_alpha_smooth: float = 3e-3
    lam_alpha_curv: float = 2e-3
    lam_ortho: float = 3e-3
    lam_gate_pen: float = 5e-4
    lam_lambda_reg: float = 1e-4
    lambda_center: float = 0.5
    gate_bce_weight: float = 1e-3
    gate_tau: float = 8.0
    gate_entropy_weight: float = 5e-4

    # ===== public sklearn API =====
    def fit(self, X, y):
        _require_tf()
        tf.keras.backend.clear_session()
        gc.collect()
        set_all_seeds(self.seed)

        # Validate
        X, y = check_X_y(X, y, accept_sparse=False, y_numeric=True)
        X = _dense32(X); y = ensure_2d_y(y)

        # Optionally scale inputs for NN heads (NOT for base models)
        if self.scale_X:
            self._scaler_X_ = StandardScaler().fit(X)
            X_scaled = _dense32(self._scaler_X_.transform(X))
        else:
            self._scaler_X_ = None
            X_scaled = X

        # OOF bases on train (raw X); also keep fully-fitted models
        X_te_shadow = X[: min(64, len(X))]
        oof_xgb, oof_hgb = fit_bases_oof(
            X, y, X_te_shadow,
            seed=self.seed, n_splits=self.n_splits,
            xgb_params=self.xgb_params if (self.use_xgb and HAS_XGB) else None,
            hgb_params=self.hgb_params
        )
        fxgb_tr, fxgb_te = oof_xgb["f0_train_oof"], oof_xgb["f0_test"]
        fhgb_tr, fhgb_te = oof_hgb["f0_train_oof"], oof_hgb["f0_test"]

        # Persist base models for inference
        self._base_hgb_ = oof_hgb["base_full"]
        self._has_xgb_  = bool(HAS_XGB and self.use_xgb)
        self._base_xgb_ = oof_xgb["base_full"] if self._has_xgb_ else None

        # Train/val split for TF head (use scaled X for NN inputs)
        X_tr, X_va, Y_tr, Y_va, FX_tr, FX_va, FH_tr, FH_va = train_test_split(
            X_scaled, y, fxgb_tr, fhgb_tr, test_size=0.15, random_state=self.seed
        )

        # λ-gate inputs: concat [scaled x, f_xgb, f_hgb]
        X_tr_gate = concat_gate_inputs(X_tr, FX_tr, FH_tr)
        X_va_gate = concat_gate_inputs(X_va, FX_va, FH_va)

        # Instantiate models
        alphas, weights = gauss_legendre_nodes_weights(K=self.K)
        delta_model = BasePlusIntegralDeltaNLL(
            alphas, weights, hidden=self.hidden, fourier_m=self.fourier_m, weight_decay=self.weight_decay
        )
        lam_gate = LambdaGate(hidden=24, weight_decay=self.weight_decay)

        # Build BEFORE creating optimizers
        _ = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        lam_boot = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        f0_boot  = lam_boot * tf.constant(FX_tr[:2], tf.float32) + (1.0 - lam_boot) * tf.constant(FH_tr[:2], tf.float32)
        _ = delta_model(tf.constant(X_tr[:2], tf.float32), f0_boot, training=False)

        # Fresh optimizers (per-fit)
        opt_delta = optimizers.Adam(self.lr)
        opt_gate  = optimizers.Adam(self.lr)
        # Ensure they're built on current vars
        opt_delta.build(delta_model.trainable_variables)
        opt_gate.build(lam_gate.trainable_variables)

        eps = tf.constant(1e-7, dtype=tf.float32)

        # tensors
        X_tr_gate_tf = tf.constant(X_tr_gate, tf.float32)
        X_tr_tf      = tf.constant(X_tr, tf.float32)
        FX_tr_tf     = tf.constant(FX_tr, tf.float32)
        FH_tr_tf     = tf.constant(FH_tr, tf.float32)
        Y_tr_tf      = tf.constant(Y_tr, tf.float32)

        # training step
        def train_step(x_gate_in, x_raw, fxgb, fhgb, ytrue):
            with tf.GradientTape(persistent=True) as tape:
                lam = lam_gate(x_gate_in)                       # (B,1) in (0,1)
                f0  = lam * fxgb + (1.0 - lam) * fhgb          # convex mix
                mu, log_sig, integ, g, delta = delta_model(x_raw, f0, training=True, return_delta=True)

                nll = tf.reduce_mean(gaussian_nll(ytrue, mu, log_sig))
                diff = delta[:, 1:, :] - delta[:, :-1, :]
                l_smooth = tf.reduce_mean(tf.square(diff))
                l_curv   = tf.reduce_mean(tf.square(delta[:, 2:, :] - 2.0*delta[:, 1:-1, :] + delta[:, :-2, :])) if self.lam_alpha_curv > 0 else 0.0

                f0_z   = f0 - tf.reduce_mean(f0, axis=0, keepdims=True)
                integ_z= integ - tf.reduce_mean(integ, axis=0, keepdims=True)
                l_ortho= tf.square(tf.reduce_mean(f0_z * integ_z))

                l_gate = tf.reduce_mean(g)
                l_lam  = tf.reduce_mean(tf.square(lam - self.lambda_center))

                # Responsibility target for λ (which base is better per-sample)
                ex = tf.square(ytrue - fxgb)
                eh = tf.square(ytrue - fhgb)
                p  = tf.sigmoid(-self.gate_tau * (ex - eh))  # prob XGB better
                gate_bce = -tf.reduce_mean(p * tf.math.log(lam + eps) + (1.0 - p) * tf.math.log(1.0 - lam + eps))

                # Anti-collapse entropy: add mean(λ log λ + (1-λ) log(1-λ))
                l_entropy = tf.reduce_mean(lam * tf.math.log(lam + eps) + (1.0 - lam) * tf.math.log(1.0 - lam + eps))

                loss = (nll
                        + self.lam_alpha_smooth*l_smooth + self.lam_alpha_curv*l_curv + self.lam_ortho*l_ortho
                        + self.lam_gate_pen*l_gate + self.lam_lambda_reg*l_lam
                        + self.gate_bce_weight * gate_bce
                        + self.gate_entropy_weight * l_entropy)

            g_delta = tape.gradient(loss, delta_model.trainable_variables)
            g_gate  = tape.gradient(loss, lam_gate.trainable_variables)
            del tape
            g_delta = [(g,v) for g,v in zip(g_delta, delta_model.trainable_variables) if g is not None]
            g_gate  = [(g,v) for g,v in zip(g_gate,  lam_gate.trainable_variables)  if g is not None]
            opt_delta.apply_gradients(g_delta)
            opt_gate.apply_gradients(g_gate)
            return float(nll)

        # training loop with early-stopping on val NLL
        best = 1e9; bad = 0; best_w_delta = None; best_w_gate = None
        rng = range(self.max_epochs)
        if self.progress_bar:
            try:
                from tqdm import tqdm
                rng = tqdm(rng)
            except Exception:
                pass

        for epoch in rng:
            _ = train_step(X_tr_gate_tf, X_tr_tf, FX_tr_tf, FH_tr_tf, Y_tr_tf)

            # validation NLL under current gate
            lam_va = lam_gate(tf.constant(X_va_gate, tf.float32), training=False)
            f0_va  = lam_va * tf.constant(FX_va, tf.float32) + (1.0 - lam_va) * tf.constant(FH_va, tf.float32)
            mu_v, log_v, _, _ = delta_model(tf.constant(X_va, tf.float32), f0_va, training=False)
            nll_va = 0.5 * np.mean(np.log(2*np.pi) + 2*log_v.numpy() + ((Y_va - mu_v.numpy())**2)/np.exp(2*log_v.numpy()))

            if self.progress_bar and hasattr(rng, "set_postfix"):
                lam_stats = lam_va.numpy()
                rng.set_postfix(val_nll=f"{nll_va:.3f}", lam_m=f"{lam_stats.mean():.3f}", lam_s=f"{lam_stats.std():.3f}")

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

        # save models
        self._delta_model_ = delta_model
        self._lam_gate_    = lam_gate
        self.n_features_in_ = X.shape[1]

        # ----- post-hoc calibration on validation -----
        def _forward(Xg, Xr, FX, FH):
            lam = lam_gate(tf.constant(Xg, tf.float32), training=False)
            f0  = lam * tf.constant(FX, tf.float32) + (1.0 - lam) * tf.constant(FH, tf.float32)
            mu, log_sig, _, _ = delta_model(tf.constant(Xr, tf.float32), f0, training=False)
            return mu.numpy(), log_sig.numpy(), f0.numpy(), lam.numpy()

        mu_va, log_va, f0_va, lam_va_np = _forward(X_va_gate, X_va, FX_va, FH_va)

        # Integrated correction z on val (recompute with return_delta=True)
        _, _, z_tmp, _, _ = delta_model(tf.constant(X_va, tf.float32),
                                        tf.constant(f0_va, tf.float32),
                                        training=False, return_delta=True)
        z_v = z_tmp.numpy().reshape(-1)
        r_v = (Y_va - f0_va).reshape(-1)
        denom = float(np.dot(z_v, z_v)) + 1e-12
        c_star = float(np.dot(r_v, z_v) / denom) if denom > 0 else 0.0

        res_v = (Y_va.reshape(-1) - mu_va.reshape(-1))
        sig_v = np.exp(log_va.reshape(-1))
        s2 = np.mean((res_v**2) / (sig_v**2 + 1e-12))
        temp_s = float(np.sqrt(max(s2, 1e-12)))

        self._c_star_ = c_star
        self._temp_s_ = temp_s

        # ----- store λ stats for introspection -----
        self._lambda_val_mean_ = float(lam_va_np.mean())
        self._lambda_val_std_  = float(lam_va_np.std())

        return self

    # Helper: forward through calibrated/uncalibrated heads at inference
    def _bases_predict(self, X_raw: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        fhgb = self._base_hgb_.predict(X_raw).astype(np.float32).reshape(-1, 1)
        if getattr(self, "_has_xgb_", False) and (self._base_xgb_ is not None):
            fxgb = self._base_xgb_.predict(X_raw).astype(np.float32).reshape(-1, 1)
        else:
            fxgb = fhgb
        return fxgb, fhgb

    def _nn_inputs(self, X_raw: np.ndarray) -> np.ndarray:
        if self._scaler_X_ is not None:
            return _dense32(self._scaler_X_.transform(X_raw))
        return _dense32(X_raw)

    def _forward(self, X_scaled, fxgb, fhgb):
        # gate inputs: [scaled x, f_xgb, f_hgb]
        X_gate = concat_gate_inputs(X_scaled, fxgb, fhgb)
        lam = self._lam_gate_(tf.constant(X_gate, tf.float32), training=False).numpy()
        f0  = lam * fxgb + (1.0 - lam) * fhgb
        mu, log_sig, _, _ = self._delta_model_(tf.constant(X_scaled, tf.float32),
                                               tf.constant(f0, tf.float32),
                                               training=False)
        return mu.numpy(), log_sig.numpy(), f0, lam

    # ===== sklearn predict API =====
    def predict(self, X) -> np.ndarray:
        """Returns calibrated mean prediction (mu_cal)."""
        X = check_array(X)
        X = _dense32(X)
        X_scaled = self._nn_inputs(X)
        fxgb, fhgb = self._bases_predict(X)
        mu, log_sig, f0, _ = self._forward(X_scaled, fxgb, fhgb)

        # Recompute integrated correction z for current f0
        _, _, z, _, _ = self._delta_model_(tf.constant(X_scaled, tf.float32),
                                           tf.constant(f0, tf.float32),
                                           training=False, return_delta=True)
        z = z.numpy()
        mu_cal = f0 + self._c_star_ * z
        return mu_cal.reshape(-1)

    # Convenience: uncalibrated vs calibrated + NLL pieces
    def predict_with_uncertainty(self, X) -> Dict[str, np.ndarray]:
        X = check_array(X); X = _dense32(X)
        X_scaled = self._nn_inputs(X)
        fxgb, fhgb = self._bases_predict(X)
        mu, log_sig, f0, _ = self._forward(X_scaled, fxgb, fhgb)

        _, _, z, _, _ = self._delta_model_(tf.constant(X_scaled, tf.float32),
                                           tf.constant(f0, tf.float32),
                                           training=False, return_delta=True)
        z = z.numpy()
        mu_cal  = f0 + self._c_star_ * z
        log_cal = np.log(np.exp(log_sig) * self._temp_s_ + 1e-12)

        return {
            "mu_uncal": mu.reshape(-1),
            "log_sigma_uncal": log_sig.reshape(-1),
            "mu_cal":  mu_cal.reshape(-1),
            "log_sigma_cal": log_cal.reshape(-1),
        }

    def evaluate(self, X, y, calibrated: bool = True) -> Dict[str, float]:
        """Return MSE & NLL on (X,y)."""
        X = check_array(X); X = _dense32(X)
        y = ensure_2d_y(y)
        X_scaled = self._nn_inputs(X)
        fxgb, fhgb = self._bases_predict(X)

        mu, log_sig, f0, _ = self._forward(X_scaled, fxgb, fhgb)

        if calibrated:
            _, _, z, _, _ = self._delta_model_(tf.constant(X_scaled, tf.float32),
                                               tf.constant(f0, tf.float32),
                                               training=False, return_delta=True)
            z = z.numpy()
            mu_c  = f0 + self._c_star_ * z
            log_c = np.log(np.exp(log_sig) * self._temp_s_ + 1e-12)
            mse = mean_squared_error(y, mu_c)
            nll = 0.5 * float(np.mean(np.log(2*np.pi) + 2*log_c + ((y - mu_c)**2)/np.exp(2*log_c)))
            return {"mse": float(mse), "nll": nll}
        else:
            mse = mean_squared_error(y, mu)
            nll = 0.5 * float(np.mean(np.log(2*np.pi) + 2*log_sig + ((y - mu)**2)/np.exp(2*log_sig)))
            return {"mse": float(mse), "nll": nll}

    # Introspection helpers
    def lambda_stats(self, X) -> Dict[str, float]:
        X = check_array(X); X = _dense32(X)
        X_scaled = self._nn_inputs(X)
        fxgb, fhgb = self._bases_predict(X)
        X_gate = concat_gate_inputs(X_scaled, fxgb, fhgb)
        lam = self._lam_gate_(tf.constant(X_gate, tf.float32), training=False).numpy()
        return {"lambda_mean": float(lam.mean()), "lambda_std": float(lam.std())}

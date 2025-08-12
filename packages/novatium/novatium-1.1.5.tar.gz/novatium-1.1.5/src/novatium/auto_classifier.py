# auto_classifier.py
# =========================================================
# Dual-base classification (HGB + XGB) with learned λ(x)
# + quadrature integral-delta residual in logit space
# Keras-3 safe; eager training (no @tf.function)
# Regularizers: smooth/curv (delta along K), orthogonality, gate penalties
# Gate responsibility (cross-entropy gap) + anti-collapse entropy
# Stratified OOF for bases; temperature scaling on validation
# =========================================================

from __future__ import annotations

import gc
import numpy as np
from typing import Any, Dict, Optional, Tuple

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.utils.validation import check_X_y, check_array
from sklearn.ensemble import HistGradientBoostingClassifier

try:
    from xgboost import XGBClassifier  # type: ignore
    HAS_XGB = True
except Exception:
    HAS_XGB = False

# --- TensorFlow / Keras imports (optional extra) ---
try:
    import tensorflow as tf
    from tensorflow.keras import layers, regularizers, optimizers, Model
    HAS_TF = True
except Exception:
    HAS_TF = False


# ========================= Utilities =========================

def _require_tf():
    if not HAS_TF:
        raise ImportError(
            'TensorFlow is required for NovaAutoClassifier. '
            'Install with: pip install "novatium[tensorflow]"'
        )

def _dense32(a): return np.asarray(a, dtype=np.float32)

def gauss_legendre_nodes_weights(K=12) -> Tuple[np.ndarray, np.ndarray]:
    t, w = np.polynomial.legendre.leggauss(K)
    a = (t + 1.0) / 2.0
    w = w / 2.0
    return a.astype("float32"), w.astype("float32")

def concat_gate_inputs(X_scaled, logits_xgb, logits_hgb) -> np.ndarray:
    # Gate sees scaled features + both base logits
    return np.concatenate([_dense32(X_scaled), _dense32(logits_xgb), _dense32(logits_hgb)], axis=1).astype(np.float32)

def one_hot(y_int: np.ndarray, num_classes: int) -> np.ndarray:
    Y = np.zeros((len(y_int), num_classes), dtype=np.float32)
    Y[np.arange(len(y_int)), y_int] = 1.0
    return Y

def softmax_np(logits: np.ndarray, axis=-1) -> np.ndarray:
    z = logits - np.max(logits, axis=axis, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=axis, keepdims=True)

# ========================= Bases (OOF) =========================

def _make_hgb(seed: int, params: Optional[Dict[str, Any]] = None) -> HistGradientBoostingClassifier:
    params = params or {}
    return HistGradientBoostingClassifier(
        learning_rate=params.get("learning_rate", 0.1),
        max_depth=params.get("max_depth", None),
        max_iter=params.get("max_iter", 400),
        random_state=seed
    )

def _make_xgb(seed: int, params: Optional[Dict[str, Any]] = None):
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
        eval_metric="logloss",
        use_label_encoder=False
    )

def _fit_oof_single_clf(
    X_tr: np.ndarray, y_tr: np.ndarray, X_te: np.ndarray,
    seed: int, kind: str, n_splits: int, params: Optional[Dict[str, Any]],
    num_classes: int
) -> Dict[str, Any]:
    """OOF probabilities (num_classes), stratified, base trained on RAW X."""
    y1d = y_tr.ravel()
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof = np.zeros((len(X_tr), num_classes), dtype=np.float32)
    te_preds = []
    for tr_idx, va_idx in skf.split(X_tr, y1d):
        if kind == "xgb" and HAS_XGB:
            base = _make_xgb(seed, params)
        else:
            base = _make_hgb(seed, params)
        base.fit(X_tr[tr_idx], y1d[tr_idx])
        oof[va_idx] = base.predict_proba(X_tr[va_idx]).astype(np.float32)
        te_preds.append(base.predict_proba(X_te).astype(np.float32))
    p_te = np.mean(te_preds, axis=0).astype(np.float32)
    base_full = _make_xgb(seed, params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, params)
    base_full.fit(X_tr, y1d)
    return {"p_train_oof": oof, "p_test": p_te, "base_full": base_full}

def fit_bases_oof_clf(
    X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, num_classes: int,
    seed: int = 42, n_splits: int = 5,
    xgb_params: Optional[Dict[str, Any]] = None, hgb_params: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    oof_hgb = _fit_oof_single_clf(X_train, y_train, X_test, seed, "hgb", n_splits, hgb_params, num_classes)
    oof_xgb = _fit_oof_single_clf(X_train, y_train, X_test, seed, "xgb", n_splits, xgb_params, num_classes) if HAS_XGB else oof_hgb
    return oof_xgb, oof_hgb


# ========================= Keras Models =========================

def _classification_ce(labels_onehot: tf.Tensor, logits: tf.Tensor) -> tf.Tensor:
    # mean cross-entropy
    return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=labels_onehot, logits=logits))

class BasePlusIntegralDeltaLogits(Model):
    """
    Integral-delta residual over K quadrature nodes, applied to logits.
    Inputs:
      x: (B, D)
      base_logits: (B, C)  -- this is the mixed base logits (λ-weighted xgb/hgb)
    Outputs:
      logits: (B, C) = base_logits + g(x) * ∫ delta(x, a) w(a) da
      Also returns integ (B, C), gate g(x) (B,1), and raw delta (B,K,C) if requested
    """
    def __init__(self, alphas, weights, hidden=32, fourier_m=6, weight_decay=1e-4, num_classes: int = 2):
        super().__init__()
        self.K = len(alphas)
        self.C = int(num_classes)
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
            layers.Dense(self.C, kernel_regularizer=reg)  # per-class delta
        ])
        self.gate = tf.keras.Sequential([
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.softplus)  # g >= 0
        ])

    def call(self, x, base_logits, training=False, return_delta=False):
        B = tf.shape(x)[0]
        # Expand along quadrature
        xT = tf.tile(tf.reshape(x, (B, 1, -1)), [1, self.K, 1])        # (B,K,D)
        aT = tf.tile(self.A, [B, 1, 1])                                # (B,K,1)
        k  = tf.range(1, self.fourier_m + 1, dtype=tf.float32)[None, None, :]
        a_feats = tf.concat([tf.sin(aT * np.pi * k), tf.cos(aT * np.pi * k)], axis=-1)  # (B,K,2m)

        hx = self.enc_x(xT)                                            # (B,K,H)
        ha = self.enc_a(tf.concat([aT, a_feats], axis=-1))             # (B,K,H)
        h  = self.film_gamma(ha) * hx + self.film_beta(ha)             # (B,K,H)

        delta = self.delta_head(h)                                     # (B,K,C)
        integ = tf.reduce_sum(delta * tf.tile(self.W, [B, 1, self.C]), axis=1)  # (B,C)
        g = self.gate(x)                                               # (B,1)
        logits = base_logits + g * integ                               # (B,C)

        if return_delta:
            return logits, integ, g, delta
        return logits, integ, g


class LambdaGate(Model):
    """Per-sample λ(x) ∈ (0,1) from gate inputs: [X_scaled, logits_xgb, logits_hgb]."""
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


# ========================= Estimator =========================

class NovaAutoClassifier(BaseEstimator, ClassifierMixin):
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
        patience: int = 16,
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
        scaler: Optional[StandardScaler] = None,
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
        self._external_scaler = scaler  # if provided, use this

    # --------- private helpers ---------
    def _set_seeds(self):
        np.random.seed(self.seed)
        if HAS_TF:
            tf.random.set_seed(self.seed)

    def fit(self, X, y):
        _require_tf()
        self._set_seeds()
        tf.keras.backend.clear_session()
        gc.collect()

        # ---------- input checks ----------
        X, y = check_X_y(X, y, accept_sparse=False, dtype=None)
        X = _dense32(X)

        # label encode
        self._le_ = LabelEncoder()
        y_int = self._le_.fit_transform(y).astype(np.int32)
        self.classes_ = self._le_.classes_
        self.n_classes_ = int(len(self.classes_))
        if self.n_classes_ < 2:
            raise ValueError("NovaAutoClassifier needs at least 2 classes.")
        y_oh_full = one_hot(y_int, self.n_classes_)  # (N,C)

        # ---------- scaler (TF heads only) ----------
        if self._external_scaler is None:
            self._scaler_ = StandardScaler()
            Xs = self._scaler_.fit_transform(X).astype(np.float32)
        else:
            self._scaler_ = self._external_scaler
            Xs = self._scaler_.fit_transform(X).astype(np.float32)

        # A small shadow test to drive OOF API (same pattern used in regression)
        X_te_shadow = X[: min(64, len(X))]

        # ---------- OOF base models on RAW X ----------
        oof_xgb, oof_hgb = fit_bases_oof_clf(
            X, y_int, X_te_shadow, num_classes=self.n_classes_,
            seed=self.seed, n_splits=max(3, self.n_splits),  # keep >=3 on tiny sets
            xgb_params=self.xgb_params if (self.use_xgb and HAS_XGB) else None,
            hgb_params=self.hgb_params
        )
        p_xgb_tr, p_hgb_tr = oof_xgb["p_train_oof"], oof_hgb["p_train_oof"]

        # persist trained bases for inference
        self._base_hgb_ = oof_hgb["base_full"]
        self._has_xgb_ = bool(HAS_XGB and self.use_xgb)
        self._base_xgb_ = oof_xgb["base_full"] if self._has_xgb_ else None

        # logits for gate/model inputs
        eps = 1e-7
        logits_xgb_tr = np.log(np.clip(p_xgb_tr, eps, 1 - eps))
        logits_hgb_tr = np.log(np.clip(p_hgb_tr, eps, 1 - eps))

        # ---------- train/val split (stratified) ----------
        X_tr, X_va, y_tr, y_va, Xs_tr, Xs_va, Lx_tr, Lx_va, Lh_tr, Lh_va, YOH_tr, YOH_va = train_test_split(
            X, X, y_int, y_int, Xs, Xs, logits_xgb_tr, logits_xgb_tr, logits_hgb_tr, logits_hgb_tr, y_oh_full,
            test_size=0.15, random_state=self.seed, stratify=y_int
        )

        # gate inputs
        X_tr_gate = concat_gate_inputs(Xs_tr, Lx_tr, Lh_tr)
        X_va_gate = concat_gate_inputs(Xs_va, Lx_va, Lh_va)

        # ---------- Keras models ----------
        alphas, weights = gauss_legendre_nodes_weights(K=self.K)
        delta_model = BasePlusIntegralDeltaLogits(
            alphas, weights, hidden=self.hidden, fourier_m=self.fourier_m,
            weight_decay=1e-4, num_classes=self.n_classes_
        )
        lam_gate = LambdaGate(hidden=24, weight_decay=1e-4)

        # boot-build
        _ = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        lam_boot = lam_gate(tf.constant(X_tr_gate[:2], tf.float32), training=False)
        logits_mix_boot = lam_boot * tf.constant(Lx_tr[:2], tf.float32) + (1.0 - lam_boot) * tf.constant(Lh_tr[:2], tf.float32)
        _ = delta_model(tf.constant(Xs_tr[:2], tf.float32), logits_mix_boot, training=False)

        # optimizers
        opt_delta = optimizers.Adam(self.lr)
        opt_gate  = optimizers.Adam(self.lr)
        eps_tf = tf.constant(1e-7, dtype=tf.float32)

        # tensors
        Xs_tr_tf  = tf.constant(Xs_tr, tf.float32)
        Lx_tr_tf  = tf.constant(Lx_tr, tf.float32)
        Lh_tr_tf  = tf.constant(Lh_tr, tf.float32)
        Y_tr_tf   = tf.constant(YOH_tr, tf.float32)

        # training step
        def train_step():
            with tf.GradientTape(persistent=True) as tape:
                lam = lam_gate(tf.constant(X_tr_gate, tf.float32))           # (B,1)
                logits_mix = lam * Lx_tr_tf + (1.0 - lam) * Lh_tr_tf          # (B,C)
                logits, integ, g = delta_model(Xs_tr_tf, logits_mix, training=True)

                # main CE loss
                nll = _classification_ce(Y_tr_tf, logits)

                # smoothness / curvature on delta along K
                # we need delta => call with return_delta=True
                logits_dbg, integ_dbg, g_dbg, delta_raw = delta_model(Xs_tr_tf, logits_mix, training=True, return_delta=True)
                diff = delta_raw[:, 1:, :] - delta_raw[:, :-1, :]
                l_smooth = tf.reduce_mean(tf.square(diff))
                l_curv = tf.reduce_mean(tf.square(delta_raw[:, 2:, :] - 2.0*delta_raw[:, 1:-1, :] + delta_raw[:, :-2, :])) if self.lam_alpha_curv > 0 else 0.0

                # orthogonality between base mix logits and integral correction
                bmz = logits_mix - tf.reduce_mean(logits_mix, axis=0, keepdims=True)  # (B,C)
                inz = integ - tf.reduce_mean(integ, axis=0, keepdims=True)            # (B,C)
                l_ortho = tf.square(tf.reduce_mean(bmz * inz))

                # small penalties
                l_gate = tf.reduce_mean(g)  # encourage small g
                l_lam  = tf.reduce_mean(tf.square(lam - self.lambda_center))

                # gate responsibility (CE gap)
                ce_xgb = tf.nn.softmax_cross_entropy_with_logits(labels=Y_tr_tf, logits=Lx_tr_tf)  # (B,)
                ce_hgb = tf.nn.softmax_cross_entropy_with_logits(labels=Y_tr_tf, logits=Lh_tr_tf)  # (B,)
                ce_xgb = tf.reshape(ce_xgb, (-1, 1))
                ce_hgb = tf.reshape(ce_hgb, (-1, 1))
                p_target = tf.sigmoid(-self.gate_tau * (ce_xgb - ce_hgb))  # if xgb better => 1
                gate_bce = -tf.reduce_mean(p_target * tf.math.log(lam + eps_tf) + (1.0 - p_target) * tf.math.log(1.0 - lam + eps_tf))

                # anti-collapse entropy on lam
                l_entropy = tf.reduce_mean(lam * tf.math.log(lam + eps_tf) + (1.0 - lam) * tf.math.log(1.0 - lam + eps_tf))

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
            return float(nll)

        # training loop with early stopping on val CE
        best = 1e9; bad = 0; best_w_delta = None; best_w_gate = None

        for epoch in range(self.max_epochs):
            _ = train_step()

            # ----- validation -----
            # base logits on val (already computed): Lx_va, Lh_va
            lam_va = lam_gate(tf.constant(X_va_gate, tf.float32), training=False)     # (Bv,1)
            logits_mix_va = lam_va * tf.constant(Lx_va, tf.float32) + (1.0 - lam_va) * tf.constant(Lh_va, tf.float32)
            logits_va, integ_va, g_va = delta_model(tf.constant(Xs_va, tf.float32), logits_mix_va, training=False)
            nll_va = float(_classification_ce(tf.constant(YOH_va, tf.float32), logits_va).numpy())

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

        # --------- temperature scaling on validation ---------
        with tf.GradientTape() as tape:
            pass  # (placeholder to ensure TF is imported)

        lam_va = lam_gate(tf.constant(X_va_gate, tf.float32), training=False)  # (Bv,1)
        logits_mix_va = lam_va * tf.constant(Lx_va, tf.float32) + (1.0 - lam_va) * tf.constant(Lh_va, tf.float32)
        logits_va, _, _ = delta_model(tf.constant(Xs_va, tf.float32), logits_mix_va, training=False)

        T = tf.Variable(1.0, dtype=tf.float32)
        optT = tf.keras.optimizers.SGD(learning_rate=0.05, momentum=0.0)
        YOH_va_tf = tf.constant(YOH_va, tf.float32)
        for _ in range(200):
            with tf.GradientTape() as tape:
                logits_T = logits_va / T
                loss_T = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=YOH_va_tf, logits=logits_T))
            gT = tape.gradient(loss_T, [T])
            optT.apply_gradients(zip(gT, [T]))
        self._T_ = float(T.numpy())

        # persist pieces
        self._delta_model_ = delta_model
        self._lam_gate_ = lam_gate
        self._Xs_dim_ = Xs.shape[1]
        self.n_features_in_ = X.shape[1]

        return self

    # ----- inference helpers -----
    def _base_logits(self, X_raw: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        # RAW X into trees -> probabilities, then logits
        eps = 1e-7
        p_h = self._base_hgb_.predict_proba(X_raw).astype(np.float32)
        if getattr(self, "_has_xgb_", False) and (self._base_xgb_ is not None):
            p_x = self._base_xgb_.predict_proba(X_raw).astype(np.float32)
        else:
            p_x = p_h
        logits_h = np.log(np.clip(p_h, eps, 1 - eps))
        logits_x = np.log(np.clip(p_x, eps, 1 - eps))
        return logits_x, logits_h

    def predict_proba(self, X):
        _require_tf()
        X = check_array(X)
        X = _dense32(X)
        Xs = self._scaler_.transform(X).astype(np.float32)

        logits_x, logits_h = self._base_logits(X)
        X_gate = concat_gate_inputs(Xs, logits_x, logits_h)
        lam = self._lam_gate_(tf.constant(X_gate, tf.float32), training=False).numpy()
        logits_mix = lam * logits_x + (1.0 - lam) * logits_h

        logits, _, _ = self._delta_model_(tf.constant(Xs, tf.float32), tf.constant(logits_mix, tf.float32), training=False)
        logits = logits.numpy()
        # temperature scaling
        T = getattr(self, "_T_", 1.0)
        probs = softmax_np(logits / max(T, 1e-6), axis=-1)
        return probs

    def predict(self, X):
        probs = self.predict_proba(X)
        preds_int = probs.argmax(axis=1)
        return self._le_.inverse_transform(preds_int)

    def predict_log_proba(self, X):
        probs = self.predict_proba(X)
        eps = 1e-12
        return np.log(np.clip(probs, eps, 1.0))
# =========================================================
# NovaAutoClassifier
# Dual-base classification (HGB + XGB) with learned λ(x)
# + delta-logit residual correction
# - Works for binary & multiclass
# - fit / predict / predict_proba
# - Seed-stable; no optimizer reuse issues
# =========================================================

from __future__ import annotations
import numpy as np
from typing import Optional, Dict, Any, Tuple
import tensorflow as tf
from tensorflow.keras import layers, regularizers, optimizers, Model

from sklearn.model_selection import KFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import log_loss

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except Exception:
    HAS_XGB = False


# ---------------- utils ----------------
def _dense32(a): return np.asarray(a, dtype=np.float32)

def _onehot(y_int: np.ndarray, n_classes: int) -> np.ndarray:
    y_int = y_int.astype(np.int32).ravel()
    Y = np.zeros((len(y_int), n_classes), dtype=np.float32)
    Y[np.arange(len(y_int)), y_int] = 1.0
    return Y

def concat_gate_inputs_cls(X: np.ndarray, p_xgb: np.ndarray, p_hgb: np.ndarray) -> np.ndarray:
    # Ensure probs are 2D
    if p_xgb.ndim == 1: p_xgb = p_xgb[:, None]
    if p_hgb.ndim == 1: p_hgb = p_hgb[:, None]
    return np.concatenate([_dense32(X), _dense32(p_xgb), _dense32(p_hgb)], axis=1).astype(np.float32)

def _clip_probs(p: np.ndarray, eps=1e-7) -> np.ndarray:
    p = np.clip(p, eps, 1.0 - eps)
    p /= p.sum(axis=1, keepdims=True)
    return p


# ---------------- base learners ----------------
def _make_hgb(seed: int, **kw) -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(
        learning_rate=kw.get("learning_rate", 0.05),
        max_depth=kw.get("max_depth", 6),
        max_iter=kw.get("max_iter", 400),
        random_state=seed
    )

def _make_xgb(seed: int, **kw) -> XGBClassifier:
    return XGBClassifier(
        n_estimators=kw.get("n_estimators", 800),
        max_depth=kw.get("max_depth", 6),
        learning_rate=kw.get("learning_rate", 0.05),
        subsample=kw.get("subsample", 0.8),
        colsample_bytree=kw.get("colsample_bytree", 0.8),
        reg_lambda=kw.get("reg_lambda", 1.0),
        tree_method=kw.get("tree_method", "hist"),
        n_jobs=kw.get("n_jobs", -1),
        random_state=seed,
        use_label_encoder=False,
        eval_metric="logloss",
    )

def _fit_oof_single_cls(
    X_tr: np.ndarray,
    y_tr: np.ndarray,
    X_te: np.ndarray,
    seed: int,
    kind: str = "hgb",
    n_splits: int = 5,
    base_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Returns dict with:
      - p_train_oof: (N_train, C) OOF probabilities
      - p_test:      (N_test,  C) mean test probabilities across folds
      - base_full:   fitted model on full training set
      - classes_:    class ordering
    """
    base_params = base_params or {}
    y1d = y_tr.ravel()
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)

    # We need #classes in advance. Fit a small model on a subset just to get classes
    if kind == "xgb" and HAS_XGB:
        tmp = _make_xgb(seed, **base_params)
    else:
        tmp = _make_hgb(seed, **base_params)
    tmp.fit(X_tr[: min(len(X_tr), 256)], y1d[: min(len(y1d), 256)])
    classes_ = np.array(tmp.classes_)
    n_classes = len(classes_)

    p_oof = np.zeros((len(X_tr), n_classes), dtype=np.float32)
    te_preds = []

    for tr, va in kf.split(X_tr):
        base = _make_xgb(seed, **base_params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, **base_params)
        base.fit(X_tr[tr], y1d[tr])
        p_oof[va] = base.predict_proba(X_tr[va]).astype(np.float32)
        te_preds.append(base.predict_proba(X_te).astype(np.float32))

    p_te = np.mean(te_preds, axis=0).astype(np.float32)

    base_full = _make_xgb(seed, **base_params) if (kind == "xgb" and HAS_XGB) else _make_hgb(seed, **base_params)
    base_full.fit(X_tr, y1d)

    return {
        "p_train_oof": p_oof,
        "p_test": p_te,
        "base_full": base_full,
        "classes_": classes_,
    }


# ---------------- Keras heads ----------------
class LambdaGate(Model):
    """Scalar λ(x) ∈ (0,1) to mix XGB vs HGB per sample."""
    def __init__(self, hidden=24, weight_decay=1e-4):
        super().__init__()
        reg = regularizers.l2(weight_decay)
        self.net = tf.keras.Sequential([
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.sigmoid),
        ])

    def call(self, x, training=False):
        return self.net(x)  # (B,1)


class DeltaLogitModel(Model):
    """
    Outputs per-class delta logits and a positive scale g(x) (softplus).
    final_logits = log(p_mix) + g(x) * delta_logits
    """
    def __init__(self, n_classes: int, hidden=64, weight_decay=1e-4):
        super().__init__()
        reg = regularizers.l2(weight_decay)
        self.enc = tf.keras.Sequential([
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
            layers.Dense(hidden, activation="gelu", kernel_regularizer=reg),
        ])
        self.delta_head = layers.Dense(n_classes, kernel_regularizer=reg)
        self.scale_head = tf.keras.Sequential([
            layers.Dense(1, kernel_regularizer=reg),
            layers.Activation(tf.nn.softplus)
        ])

    def call(self, x, base_log_probs, training=False):
        # x: (B,D); base_log_probs: (B,C)
        h = self.enc(x)
        delta_logits = self.delta_head(h)              # (B,C)
        scale = self.scale_head(x)                     # (B,1) >= 0
        final_logits = base_log_probs + scale * delta_logits
        return final_logits, scale, delta_logits


# ---------------- The Classifier ----------------
class NovaAutoClassifier:
    """
    Dual-base classifier (HGB + XGB) with learned per-sample λ(x) and
    delta-logit correction. Supports binary & multiclass.
    """
    def __init__(
        self,
        seed: int = 42,
        n_splits: int = 5,
        gate_hidden: int = 24,
        delta_hidden: int = 64,
        weight_decay: float = 1e-4,
        max_epochs_gate: int = 200,
        max_epochs_delta: int = 300,
        lr_gate: float = 1e-3,
        lr_delta: float = 1e-3,
        gate_entropy_weight: float = 5e-4,    # discourage λ near 0/1
        gate_center_weight: float = 1e-4,     # keep λ around 0.5
        gate_tau: float = 5.0,                # responsibility sharpness
        xgb_params: Optional[Dict[str, Any]] = None,
        hgb_params: Optional[Dict[str, Any]] = None,
    ):
        self.seed = seed
        self.n_splits = n_splits
        self.gate_hidden = gate_hidden
        self.delta_hidden = delta_hidden
        self.weight_decay = weight_decay
        self.max_epochs_gate = max_epochs_gate
        self.max_epochs_delta = max_epochs_delta
        self.lr_gate = lr_gate
        self.lr_delta = lr_delta
        self.gate_entropy_weight = gate_entropy_weight
        self.gate_center_weight = gate_center_weight
        self.gate_tau = gate_tau
        self.xgb_params = xgb_params or {}
        self.hgb_params = hgb_params or {}
        # seeds
        np.random.seed(seed)
        tf.random.set_seed(seed)
        self.is_fitted_ = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        # Encode labels to [0..C-1]
        le = LabelEncoder()
        y_int = le.fit_transform(y)
        self.classes_ = le.classes_
        self.n_classes_ = len(self.classes_)

        X = _dense32(X)
        y_int = y_int.astype(np.int32)
        Y_onehot = _onehot(y_int, self.n_classes_)

        # ---- Base models with OOF ----
        oof_xgb = _fit_oof_single_cls(X, y_int, X, self.seed, "xgb", self.n_splits, self.xgb_params)
        oof_hgb = _fit_oof_single_cls(X, y_int, X, self.seed, "hgb", self.n_splits, self.hgb_params)

        self._base_xgb_ = oof_xgb["base_full"]
        self._base_hgb_ = oof_hgb["base_full"]
        # sanity: same class ordering
        # xgb/hgb should use same class order as LabelEncoder; we’ll just reindex if needed
        # (here we assume sklearn/xgb followed the same order seen in y_int).

        P_xgb_oof = _clip_probs(oof_xgb["p_train_oof"])
        P_hgb_oof = _clip_probs(oof_hgb["p_train_oof"])

        # ---- Gate inputs: concat [X, P_xgb_oof, P_hgb_oof] ----
        X_gate = concat_gate_inputs_cls(X, P_xgb_oof, P_hgb_oof)

        # ---- Build models (call once -> build vars) ----
        self._gate_ = LambdaGate(hidden=self.gate_hidden, weight_decay=self.weight_decay)
        _ = self._gate_(tf.constant(X_gate[:2], tf.float32), training=False)

        self._delta_ = DeltaLogitModel(n_classes=self.n_classes_, hidden=self.delta_hidden, weight_decay=self.weight_decay)
        # base log-probs boot for first call
        lam_boot = self._gate_(tf.constant(X_gate[:2], tf.float32), training=False)
        P_mix_boot = lam_boot.numpy() * P_xgb_oof[:2] + (1.0 - lam_boot.numpy()) * P_hgb_oof[:2]
        P_mix_boot = _clip_probs(P_mix_boot)
        logP_boot = np.log(P_mix_boot).astype(np.float32)
        _ = self._delta_(tf.constant(X[:2], tf.float32), tf.constant(logP_boot, tf.float32), training=False)

        # ---- Optimizers ----
        opt_gate = optimizers.Adam(self.lr_gate)
        opt_delta = optimizers.Adam(self.lr_delta)
        eps = 1e-7

        # ---- Train gate: entropy + center + responsibility targets ----
        X_gate_tf = tf.constant(X_gate, tf.float32)
        X_tf = tf.constant(X, tf.float32)
        Y_tf = tf.constant(Y_onehot, tf.float32)

        P_xgb_tf = tf.constant(P_xgb_oof, tf.float32)
        P_hgb_tf = tf.constant(P_hgb_oof, tf.float32)

        for _ in range(self.max_epochs_gate):
            with tf.GradientTape() as tape:
                lam = self._gate_(X_gate_tf, training=True)       # (N,1)
                # base mixture probs & logits
                P_mix = lam * P_xgb_tf + (1.0 - lam) * P_hgb_tf   # (N,C)
                P_mix = tf.clip_by_value(P_mix, eps, 1.0)
                P_mix = P_mix / tf.reduce_sum(P_mix, axis=1, keepdims=True)
                # responsibility target: prefer base with lower CE on true label
                ce_xgb = -tf.reduce_sum(Y_tf * tf.math.log(tf.clip_by_value(P_xgb_tf, eps, 1.0)), axis=1, keepdims=True)
                ce_hgb = -tf.reduce_sum(Y_tf * tf.math.log(tf.clip_by_value(P_hgb_tf, eps, 1.0)), axis=1, keepdims=True)
                p_target = tf.sigmoid(-self.gate_tau * (ce_xgb - ce_hgb))  # ~1 when XGB better
                gate_bce = -tf.reduce_mean(p_target * tf.math.log(lam + eps) + (1.0 - p_target) * tf.math.log(1.0 - lam + eps))
                # anti-collapse entropy
                l_entropy = tf.reduce_mean(lam * tf.math.log(lam + eps) + (1.0 - lam) * tf.math.log(1.0 - lam + eps))
                # center to 0.5
                l_center = tf.reduce_mean(tf.square(lam - 0.5))
                # total
                loss_gate = self.gate_entropy_weight * l_entropy + self.gate_center_weight * l_center + gate_bce
            grads = tape.gradient(loss_gate, self._gate_.trainable_variables)
            grads = [g for g in grads if g is not None]
            opt_gate.apply_gradients(zip(grads, self._gate_.trainable_variables))

        # ---- Train delta: cross-entropy on final logits ----
        for _ in range(self.max_epochs_delta):
            with tf.GradientTape() as tape:
                lam = self._gate_(X_gate_tf, training=False)
                P_mix = lam * P_xgb_tf + (1.0 - lam) * P_hgb_tf
                P_mix = tf.clip_by_value(P_mix, eps, 1.0)
                P_mix = P_mix / tf.reduce_sum(P_mix, axis=1, keepdims=True)
                logP = tf.math.log(P_mix)
                logits, scale, dlog = self._delta_(X_tf, logP, training=True)
                # CE with logits
                ce = tf.nn.softmax_cross_entropy_with_logits(labels=Y_tf, logits=logits)
                loss_delta = tf.reduce_mean(ce)
            grads = tape.gradient(loss_delta, self._delta_.trainable_variables)
            grads = [g for g in grads if g is not None]
            opt_delta.apply_gradients(zip(grads, self._delta_.trainable_variables))

        # Persist fitted bits
        self._P_train_xgb_ = P_xgb_oof
        self._P_train_hgb_ = P_hgb_oof
        self._X_gate_template_dim_ = X_gate.shape[1]
        self.le_ = le
        self.is_fitted_ = True
        return self

    def _base_proba(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        px = self._base_xgb_.predict_proba(X).astype(np.float32)
        ph = self._base_hgb_.predict_proba(X).astype(np.float32)
        # Ensure class alignment (defensive; assuming same ordering from fit)
        if px.shape[1] != self.n_classes_:
            # try to fix by mapping via observed classes
            # but in normal flow this should not happen
            raise RuntimeError("Class count mismatch between training and inference for XGB.")
        if ph.shape[1] != self.n_classes_:
            raise RuntimeError("Class count mismatch between training and inference for HGB.")
        return _clip_probs(px), _clip_probs(ph)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted_:
            raise RuntimeError("Call fit() before predict_proba().")
        X = _dense32(X)
        px, ph = self._base_proba(X)
        X_gate = concat_gate_inputs_cls(X, px, ph)
        lam = self._gate_(tf.constant(X_gate, tf.float32), training=False).numpy()
        P_mix = lam * px + (1.0 - lam) * ph
        P_mix = _clip_probs(P_mix)
        logP = np.log(P_mix).astype(np.float32)
        logits, _, _ = self._delta_(tf.constant(X, tf.float32), tf.constant(logP, tf.float32), training=False)
        probs = tf.nn.softmax(logits, axis=1).numpy()
        probs = _clip_probs(probs)
        return probs

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        y_int = probs.argmax(axis=1)
        return self.le_.inverse_transform(y_int)

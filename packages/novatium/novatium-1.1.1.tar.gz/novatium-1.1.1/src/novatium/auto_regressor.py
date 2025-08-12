import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, regularizers, optimizers, Model
from sklearn.model_selection import KFold
from sklearn.ensemble import HistGradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error

# ===== Utility Functions =====
def _dense32(a): return np.asarray(a, dtype=np.float32)

def gauss_legendre_nodes_weights(K=12):
    t, w = np.polynomial.legendre.leggauss(K)
    a = (t + 1.0) / 2.0
    w = w / 2.0
    return a.astype("float32"), w.astype("float32")

def concat_gate_inputs(X, f_xgb, f_hgb):
    return np.concatenate([_dense32(X), _dense32(f_xgb), _dense32(f_hgb)], axis=1).astype(np.float32)

def gaussian_nll(y, mu, log_sigma):
    inv_var = tf.exp(-2.0 * log_sigma)
    return 0.5 * (tf.math.log(2.0 * np.pi) + 2.0 * log_sigma + tf.square(y - mu) * inv_var)

# ===== Base Learners =====
def _make_hgb(seed):
    return HistGradientBoostingRegressor(max_depth=6, learning_rate=0.05, max_iter=400, random_state=seed)

def _make_xgb(seed):
    return XGBRegressor(n_estimators=800, max_depth=6, learning_rate=0.05,
                        subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
                        tree_method="hist", n_jobs=-1, random_state=seed)

def _fit_oof_single(X_tr, y_tr, X_te, seed, kind="hgb", n_splits=5):
    y1d = y_tr.ravel()
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    f0_oof = np.zeros((len(X_tr), 1), np.float32)
    te_preds = []
    for tr, va in kf.split(X_tr):
        base = _make_xgb(seed) if kind == "xgb" else _make_hgb(seed)
        base.fit(X_tr[tr], y1d[tr])
        f0_oof[va] = base.predict(X_tr[va]).reshape(-1, 1).astype(np.float32)
        te_preds.append(base.predict(X_te).reshape(-1, 1).astype(np.float32))
    f0_te = np.mean(te_preds, axis=0).astype(np.float32)
    base_full = _make_xgb(seed) if kind == "xgb" else _make_hgb(seed)
    base_full.fit(X_tr, y1d)
    return {"f0_train_oof": f0_oof, "f0_test": f0_te, "base_full": base_full}

# ===== Lambda Gate =====
class LambdaGate(Model):
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

# ===== Delta Correction Model =====
class BasePlusIntegralDeltaNLL(Model):
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
        self.film_beta = layers.Dense(hidden, kernel_regularizer=reg)
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

    def call(self, x, f0, training=False):
        B = tf.shape(x)[0]
        xT = tf.tile(tf.reshape(x, (B, 1, -1)), [1, self.K, 1])
        aT = tf.tile(self.A, [B, 1, 1])
        k = tf.range(1, self.fourier_m + 1, dtype=tf.float32)[None, None, :]
        a_feats = tf.concat([tf.sin(aT * np.pi * k), tf.cos(aT * np.pi * k)], axis=-1)
        hx = self.enc_x(xT)
        ha = self.enc_a(tf.concat([aT, a_feats], axis=-1))
        h = self.film_gamma(ha) * hx + self.film_beta(ha)
        delta = self.delta_head(h)
        integ = tf.reduce_sum(delta * tf.tile(self.W, [B, 1, 1]), axis=1)
        g = self.gate(x)
        mu = f0 + g * integ
        log_sigma = tf.clip_by_value(self.logsig_head(x), -6.0, 3.0)
        return mu, log_sigma

# ===== NovaAutoRegressor =====
class NovaAutoRegressor:
    def __init__(self, seed=42, n_splits=5, hidden=32, weight_decay=1e-4):
        self.seed = seed
        np.random.seed(seed)
        tf.random.set_seed(seed)
        self.n_splits = n_splits
        self.hidden = hidden
        self.weight_decay = weight_decay
        self.is_fitted_ = False

    def fit(self, X, y):
        X = _dense32(X)
        y = _dense32(y).reshape(-1, 1)
        
        # Step 1: Fit base models with OOF
        oof_xgb = _fit_oof_single(X, y, X, self.seed, "xgb", self.n_splits)
        oof_hgb = _fit_oof_single(X, y, X, self.seed, "hgb", self.n_splits)

        self.base_xgb_ = oof_xgb["base_full"]
        self.base_hgb_ = oof_hgb["base_full"]

        # Step 2: Train Lambda gate
        gate_X = concat_gate_inputs(X, oof_xgb["f0_train_oof"], oof_hgb["f0_train_oof"])
        self.gate_model_ = LambdaGate(hidden=self.hidden, weight_decay=self.weight_decay)
        opt_gate = optimizers.Adam(learning_rate=1e-3)
        for _ in range(200):
            with tf.GradientTape() as tape:
                lam = self.gate_model_(gate_X, training=True)
                reg_loss = tf.reduce_mean(lam * (1 - lam))  # anti-collapse
                loss = -reg_loss  # maximize diversity
            grads = tape.gradient(loss, self.gate_model_.trainable_variables)
            opt_gate.apply_gradients(zip(grads, self.gate_model_.trainable_variables))

        # Step 3: Train Delta correction model
        alphas, weights = gauss_legendre_nodes_weights(K=12)
        self.delta_model_ = BasePlusIntegralDeltaNLL(alphas, weights, hidden=self.hidden, weight_decay=self.weight_decay)
        opt_delta = optimizers.Adam(learning_rate=1e-3)

        for _ in range(300):
            with tf.GradientTape() as tape:
                lam = self.gate_model_(gate_X, training=False)
                f0 = lam * oof_xgb["f0_train_oof"] + (1 - lam) * oof_hgb["f0_train_oof"]
                mu, log_sigma = self.delta_model_(X, f0, training=True)
                loss = tf.reduce_mean(gaussian_nll(y, mu, log_sigma))
            grads = tape.gradient(loss, self.delta_model_.trainable_variables)
            opt_delta.apply_gradients(zip(grads, self.delta_model_.trainable_variables))

        self.is_fitted_ = True
        return self

    def predict(self, X):
        if not self.is_fitted_:
            raise ValueError("Model is not fitted yet!")
        X = _dense32(X)
        f0_xgb = self.base_xgb_.predict(X).reshape(-1, 1)
        f0_hgb = self.base_hgb_.predict(X).reshape(-1, 1)
        gate_X = concat_gate_inputs(X, f0_xgb, f0_hgb)
        lam = self.gate_model_(gate_X, training=False).numpy()
        f0 = lam * f0_xgb + (1 - lam) * f0_hgb
        mu, _ = self.delta_model_(X, f0, training=False)
        return mu.numpy().ravel()

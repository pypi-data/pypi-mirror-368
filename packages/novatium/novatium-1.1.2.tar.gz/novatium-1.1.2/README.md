# Novatium
**Cosmic-Grade Machine Learning** — supercharged Base+Delta models for regression and classification.

```
`pip install novatium`

## Quickstart

### NovaRegressor
```python
from novatium import NovaAutoRegressor
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

X, y = load_diabetes(return_X_y=True)
model = NovaAutoRegressor()
model.fit(X, y)
pred = model.predict(X[:5])
print(pred)
```

### NovaClassifier
```python
from novatium import NovaAutoClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingRegressor

X, y = load_breast_cancer(return_X_y=True)
clf = NovaAutoClassifier()
clf.fit(X, y)
proba = clf.predict_proba(X[:5])
print(proba)
```

## Why Novatium?
- Drop-in **Base+Delta** pattern to uplift strong baselines.
- **Sklearn-compatible**: works with pipelines, grid search, etc.
- **Domain-agnostic**: tabular now; CV/NLP-ready APIs.

## License
Apache-2.0 — see `LICENSE`.

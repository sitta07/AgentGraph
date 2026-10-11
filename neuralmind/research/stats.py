"""Small, dependency-free statistics helpers (NumPy only)."""

from __future__ import annotations

import numpy as np


def mean_ci(values, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0) -> dict:
    """Mean with a percentile-bootstrap (1 - alpha) confidence interval."""
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]          # runs with no data for this metric are skipped
    if x.size == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    if x.size == 1:
        return {"mean": float(x[0]), "lo": float(x[0]), "hi": float(x[0]), "n": 1}
    rng = np.random.default_rng(seed)
    boots = rng.choice(x, size=(n_boot, x.size), replace=True).mean(axis=1)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return {"mean": float(x.mean()), "lo": float(lo), "hi": float(hi), "n": int(x.size)}


def paired_diff(a, b, **kw) -> dict:
    """CI of the mean paired difference a - b (same seeds in both conditions)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    return mean_ci(a[ok] - b[ok], **kw)


def gini(values) -> float:
    """Gini coefficient of a non-negative distribution (0 = equal)."""
    x = np.sort(np.clip(np.asarray(values, float), 0, None))
    if x.sum() == 0:
        return 0.0
    n = x.size
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))

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


def mutual_information(table) -> float:
    """Mutual information (bits) of a 2-D contingency table of counts."""
    t = np.asarray(table, float)
    n = t.sum()
    if n == 0:
        return 0.0
    pxy = t / n
    px, py = pxy.sum(1, keepdims=True), pxy.sum(0, keepdims=True)
    nz = pxy > 0
    return float((pxy[nz] * np.log2(pxy[nz] / (px @ py)[nz])).sum())


def g_test_p(table) -> float:
    """p-value of the G-test of independence (G = 2 N MI in nats).

    df = (rows-1)(cols-1) over non-empty rows/columns. Exact for df=1
    (erfc); Wilson-Hilferty normal approximation otherwise."""
    import math
    t = np.asarray(table, float)
    t = t[t.sum(1) > 0][:, t.sum(0) > 0]
    if t.shape[0] < 2 or t.shape[1] < 2:
        return 1.0
    g = 2.0 * t.sum() * mutual_information(t) * math.log(2)
    df = (t.shape[0] - 1) * (t.shape[1] - 1)
    if df == 1:
        return float(math.erfc(math.sqrt(max(g, 0.0) / 2.0)))
    z = ((g / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return float(0.5 * math.erfc(z / math.sqrt(2)))

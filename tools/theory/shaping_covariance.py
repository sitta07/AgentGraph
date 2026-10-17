"""Potential-based shaping and three-factor learning: a check of the sign.

Shaping reward r_t = Phi_{t+1} - Phi_t. For a stationary potential with
lag-1 autocorrelation rho,

    Cov(Phi_t, r_t) = Cov(Phi_t, Phi_{t+1}) - Var(Phi) = -(1 - rho) Var(Phi) <= 0.

If presynaptic activity at decision time rises with Phi_t (eligibility
e_t = g(Phi_t), g increasing), then E[(r_t - b) e_t] < 0 for any constant
baseline b, so a covariance rule dw ~ (r - b) e depresses active synapses on
average, whatever the policy. A state-dependent baseline b(Phi_t) =
E[r_t | Phi_t] removes the term. This script checks both claims on an AR(1)
potential with no agent, no task and no NeuralMind code.
"""

import numpy as np


def run(rho: float, n: int = 400_000, bins: int = 20, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    phi = np.empty(n)
    phi[0] = 0.0
    eps = rng.normal(0.0, np.sqrt(1 - rho ** 2), n)
    for t in range(1, n):
        phi[t] = rho * phi[t - 1] + eps[t]
    r = phi[1:] - phi[:-1]
    p = phi[:-1]
    e = 1.0 / (1.0 + np.exp(-2.0 * p))          # eligibility rises with the potential
    scalar = r - r.mean()                         # scalar critic: one expectation
    edges = np.quantile(p, np.linspace(0, 1, bins + 1)[1:-1])
    k = np.digitize(p, edges)
    cond = np.bincount(k, weights=r) / np.bincount(k)
    state = r - cond[k]                           # state critic: expectation per potential bin
    return {"rho": rho, "cov_phi_r": float(np.cov(p, r)[0, 1]),
            "predicted": -(1 - rho) * float(p.var()),
            "drift_scalar": float((scalar * e).mean()),
            "drift_state": float((state * e).mean())}


if __name__ == "__main__":
    for rho in (0.0, 0.5, 0.9, 0.99):
        print({k: round(v, 4) for k, v in run(rho).items()})

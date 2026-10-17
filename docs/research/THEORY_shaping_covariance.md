# Theory note: potential-based shaping pushes three-factor learning toward depression

**Status:** working note, 2026-10-17. The identity below is elementary and
was checked numerically. Two pre-registered tests bear it out:

- [AM](FINDINGS_AM.md): the predicted fix rescued learning in NeuralMind.
- [AN](FINDINGS_AN.md): the predicted pattern held in a non-spiking forager
  that shares no code with NeuralMind.

Broader generality is untested.

## The identity

Let `Φ_t` be a shaping potential and `r_t = Φ_{t+1} − Φ_t` the shaping reward
(potential-based shaping with γ = 1; Ng, Harada & Russell 1999). If `Φ` is
stationary with variance `σ²` and lag-1 autocorrelation `ρ`, then

```
Cov(Φ_t, r_t) = Cov(Φ_t, Φ_{t+1}) − Var(Φ_t) = −(1 − ρ) σ²  ≤ 0.
```

This is regression to the mean: a high potential now predicts a drop next
step. Nothing about the agent or the task enters.

## Why it matters for three-factor rules

A reward-modulated Hebbian (three-factor) rule changes a weight by
`Δw ∝ (r_t − b) · e_t`, where `e_t` is the synapse's eligibility and `b` a
reward baseline. Frémaux, Sprekeler & Gerstner (2010) showed that such rules
learn the covariance of reward and synaptic activity, and that a baseline
must match the expected reward per stimulus to avoid a bias.

Suppose a synapse's eligibility at decision time rises with the potential,
`e_t = g(Φ_t)` with `g` increasing. One example is a sensor that fires
hardest when food is straight ahead, under a potential equal to alignment
with food. Then, for any constant `b`,

```
E[(r_t − b) e_t] = Cov(r_t, g(Φ_t)) + (E[r] − b) E[e]  →  Cov(r_t, g(Φ_t)) < 0
```

when `b = E[r]`. Under a scalar baseline, those synapses are depressed on
average, whatever the policy. With per-neuron weight normalisation, the lost
weight moves to the less active inputs. The policy invariance of
potential-based shaping is a statement about optimal policies. It does not
constrain these learning dynamics.

**The fix the identity predicts.** A state-dependent baseline,
`b(s_t) = E[r_t | s_t]`, removes the term whenever `s_t` captures `Φ_t`. This
is the per-stimulus critic that Frémaux et al. require, here with a concrete
reason it is needed even when shaping is "safe".

## Numerical check

[`tools/theory/shaping_covariance.py`](../../tools/theory/shaping_covariance.py)
uses an AR(1) potential, eligibility `e = sigmoid(2Φ)`, and no agent or task.

| ρ | Cov(Φ, r) measured | −(1−ρ)σ² | drift, scalar baseline | drift, state baseline (20 bins) |
|---|---|---|---|---|
| 0.0 | −1.005 | −1.003 | −0.304 | −0.001 |
| 0.5 | −0.502 | −0.500 | −0.152 | −0.001 |
| 0.9 | −0.100 | −0.100 | −0.030 | −0.000 |

## Evidence in NeuralMind

- Probe (`tools/probes/rpe_eligibility_probe.py`): under alignment shaping, the reward-prediction error correlated negatively with total eligibility (r ≈ −0.11).
- AE: the learned rise in attacks among social peers lives in the movement neurons' weights.
- AF: approach shaping removed it and rescued learning.

Approach shaping showed a positive correlation in the probe. The identity
alone does not explain this. A likely contributor, unverified: on eating
ticks the shaping term is set to zero and the potential jumps when new food
becomes nearest, so the process is not stationary.

## What is and is not new

**Known:**

- Potential-based shaping preserves optimal policies (Ng et al. 1999).
- Three-factor rules learn reward–activity covariance and need per-stimulus baselines (Frémaux et al. 2010).
- Shaping can bias naive policy-gradient estimates and acts like a state-dependent baseline in actor-critic methods (e.g. [Potential-Based Advice for Stochastic Policy Learning](https://arxiv.org/html/1907.08823v1)).

**Possibly new, not established:**

- The closed-form sign `−(1−ρ)σ²` applied to three-factor rules.
- The resulting drift onto silent inputs under normalisation.
- The downstream effect on action selection seen in AE: actions whose
  neurons learn less win by default.

A more thorough literature search is needed before calling any of this
novel.

## Tests so far

1. **AM** (done): with alignment shaping unchanged, the state critic turned the social learning gain from +0.5 to +6.7 and removed most of the learned rise in attacks.
2. **AN** (done): in a linear-softmax forager, shaping lowered the Hebbian forward food weights by −28.5 [−43.0, −16.9]. A state baseline restored +16.5. Score-function credit was unaffected (+0.3 [−0.9, +1.2]), and shaping helped it 3.6×.

## Next tests

- Several tasks and learning rates.
- A standard R-STDP implementation from the literature.
- A thorough literature search.

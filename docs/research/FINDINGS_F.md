# Findings: Experiment F — does spatial structure protect evolving populations from extinction?

**Status:** completed 2026-10-12. 24 runs: 2 conditions × 12 seeds × 18000
ticks. Pre-registered at commit `591d801`, spec unchanged, no deviations.
Report: [`results/F_viscosity_extinction/`](../../results/F_viscosity_extinction/REPORT.md).

| Hypothesis | Result | Verdict |
|---|---|---|
| H14: well-mixed populations go extinct more often | **9/12 vs 1/12** (difference +0.67 [0.25, 1.0]; Fisher p = 0.003) | supported |
| H14b: well-mixed populations die out sooner | −4616 ticks [−6844, −2349] | supported |
| H15: the aggression gene evolves higher in well-mixed survivors | +0.06 [−0.09, 0.21] (only 3 well-mixed populations survived) | not supported |

## A design flaw we have to report

The spec ran seeds 0–11. **Seeds 0–5 used exactly the same configuration as
the C2 runs that suggested this hypothesis**, and they reproduced those runs
number for number. Half of the "confirmation" is therefore the original
observation, not an independent test.

On the **fresh seeds only (6–11)**:

| Condition | Extinct |
|---|---|
| well-mixed | 4/6 |
| viscous | 0/6 |

The direction is the same, but Fisher p = 0.061 two-sided (0.030 one-sided).
That is suggestive, not conclusive on its own.

**Fix:** specs now take `seed_start`. The confirmatory replication F2 uses
seeds 100–115, which have never been run.

## Interpretation (so far)

- Offspring placement alone separates populations that persist from
  populations that crash. That is the only difference between the two
  conditions.
- The heritable aggression gene does not explain it (H15), at least in the
  few well-mixed populations that survived.
- **F2** tests the confirmation on fresh seeds and a candidate mechanism:
  boom-bust dynamics, measured as larger population fluctuations in
  well-mixed worlds.
- Related theory: local dispersal favours restraint and avoids a tragedy of
  the commons (Kerr et al. 2006).

## F2: independent replication on fresh seeds

**Status:** completed 2026-10-15. 32 runs: 2 conditions × 16 seeds (100–115,
never run before) × 18000 ticks. Pre-registered at commit `435ab42`, spec
unchanged, no deviations. Report:
[`results/F2_viscosity_extinction_replication/`](../../results/F2_viscosity_extinction_replication/REPORT.md).

| Hypothesis | Result | Verdict |
|---|---|---|
| H14r: well-mixed populations go extinct more often | **13/16 vs 7/16**, difference +0.375 [0.0, 0.69] (Fisher p = 0.033 one-sided, 0.066 two-sided) | **not supported** by the registered rule (the CI lower bound is exactly 0) |
| H14br: well-mixed populations die out sooner | −3140 ticks [−5183, −1084] (12890 vs 16031) | supported |
| H17: well-mixed population sizes are more volatile (CV) | +0.058 [0.012, 0.108] | supported by the registered rule, **but confounded** (see below) |

**H17 is confounded by extinction itself.** The CV is computed over the whole
run, including the final collapse to zero, so populations that die get a
higher CV for that reason alone. Over the first 6000 ticks, before any
population died (the earliest extinction was at tick 7332), the CVs are equal:
0.073 vs 0.073, difference +0.0007 [−0.0005, 0.0025]. This check was not
pre-registered. As far as we can tell, there is **no evidence of boom-bust
dynamics before the collapse**.

**What replicated and what did not.**

- The direction replicated: well-mixed populations died more often and
  sooner.
- The size of the effect did not. In F2, viscous populations also went
  extinct often (7/16, compared with 1/12 in F), and the extinction-count
  test missed the registered threshold.
- Pooling every fresh seed (F seeds 6–11 plus F2) gives 17/22 vs 7/22,
  two-sided Fisher p = 0.006. This pooling was decided after seeing the data,
  so treat it as descriptive.
- Survival time is the more sensitive measure, and it replicated.

**Updated interpretation.** Spatial structure delays extinction in this world,
and probably makes it less likely, but it does not prevent it. The mechanism
is still unknown. Volatility before the collapse is not it. A next step would
be to measure *what* collapses first: food depletion, attack-driven deaths, or
failed reproduction.

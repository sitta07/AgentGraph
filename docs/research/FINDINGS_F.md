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

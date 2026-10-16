# Findings: Experiment Q3 — energy recycling from killing offspring does not explain why viscosity helps

**Status:** completed 2026-10-16. 36 runs: 3 conditions × 12 seeds
(1800–1811, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `fd86928`, spec unchanged, no deviations. No pilot. Report:
[`results/Q3_filial_energy_recycling/`](../../results/Q3_filial_energy_recycling/REPORT.md).

**Intervention.** With `no_filial_gain`, an attack on one's own offspring
still drains the offspring, but the parent gets no energy and no reward from
it. All other attacks are unchanged.

| Hypothesis | Test (viscous_nogain − viscous) | Result |
|---|---|---|
| H33a: without the energy gain, populations die out sooner | +1162 [−18, 2734] ticks | not supported (if anything, the reverse) |
| H33b: … go extinct more often | −0.25 [−0.58, 0.08] | not supported (1/12 vs 4/12) |
| H33c: … the early birth rate falls | −0.00065 [−0.0010, −0.0003] | **supported** |
| H33d: manipulation check, parents still kill offspring in ≥ 10% of kills | 0.24 | **supported** |

| condition | extinct | kills of own offspring | birth rate (0–6000) | starvation share of deaths |
|---|---|---|---|---|
| viscous | 4/12 | 42% | 0.0035 | 32% |
| viscous_nogain | **1/12** | 24% | 0.0028 | 38% |
| stranger | 11/12 | 4% | 0.0028 | 39% |

## Interpretation

- **The recycling explanation from Q2 is falsified.** Taking away the energy
  that parents gain from killing their offspring did lower the birth rate, as
  expected. But populations did not die out sooner. Survival was nominally
  longer: 1/12 extinct vs 4/12, p = 0.32, so this is not a reliable
  difference.
- Without the energy gain, parents killed their offspring less often (24% vs
  42% of kills). One likely reason is that the attack no longer produces
  reward, so learning stops reinforcing it. That is untested.
- **The main effect replicated a third time.** Placing newborns beside a
  stranger gave 11/12 extinctions against 4/12 for placement beside the
  parent (p = 0.009). Pooled over Q, Q2 and Q3, it is **34/36 vs 13/36**
  (Fisher p ≈ 2 × 10⁻⁷).
- So viscosity's protection is robust, and it does not come from:
  - local density alone (Q);
  - strangers killing newborns (Q2);
  - parents recycling energy (Q3).
  The mechanism is still open.

## Candidates for the next study (untested)

- **Spatial spread.** With viscous placement, a lineage stays in one area.
  Strangers or random placement scatter newborns across the world, which
  could spread attackers into every area.
- **Local competition between relatives.** Kin crowding may limit
  reproduction to a level the food supply can sustain. Viscous births were
  not lower, though.
- A useful first step is a time series of the spatial clustering of
  lineages and of where killings happen, before collapse.

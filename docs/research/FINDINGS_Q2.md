# Findings: Experiment Q2 — strangers do not kill newborns more; parents do, and viscous populations still last longest

**Status:** completed 2026-10-16. 36 runs: 3 conditions × 12 seeds
(1600–1611, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `fdf4cc3`, spec unchanged, no deviations. A one-seed pilot (seed 9997)
was disclosed in the spec. Report:
[`results/Q2_who_kills_newborns/`](../../results/Q2_who_kills_newborns/REPORT.md).

**Measures (ticks 0–6000).** Every killing is logged with three facts: is the
killer a relative, is it the victim's parent, and is the victim young (age
under 150 ticks)? `early_young_kill_excess` is the share of kills with a
young victim minus the share of agent-ticks spent young.

| Hypothesis | Test | Result |
|---|---|---|
| H31a: young are over-killed (viscous) | +0.38 [0.36, 0.40] | **supported** |
| H31a2: young are over-killed (stranger) | +0.22 [0.21, 0.23] | **supported** |
| H31b: newborns beside a stranger are over-killed more than beside the parent | stranger − viscous = −0.16 [−0.18, −0.14] | **not supported (clearly the reverse)** |
| H31c: replication of Q, stranger placement dies sooner than viscous | −4410 [−6605, −1900] ticks | **supported** |
| H31d: parents commit ≥ 10% of killings on their own offspring (viscous) | 0.42, i.e. +0.32 [0.29, 0.34] above 0.10 | **supported** |

| condition | extinct | kills of kin | kills of own offspring | kills of young | time spent young | birth rate |
|---|---|---|---|---|---|---|
| mixed | 10/12 | 35% | 3% | 44% | 28% | 0.0026 |
| stranger | **12/12** | 29% | 4% | 53% | 31% | 0.0030 |
| viscous | **6/12** | 61% | **42%** | **68%** | 30% | **0.0039** |

## Interpretation

- **Q's post-hoc finding replicates as a pre-registered test.** When newborns
  are placed beside a stranger, populations die out sooner than when they are
  placed beside their parent: 12/12 vs 6/12 extinct (Fisher p = 0.014).
  Pooled over Q and Q2, it is 23/24 vs 9/24.
- **The proposed mechanism is wrong.** Strangers are not the danger to
  newborns. Young agents are over-killed most when they are born beside their
  **parent**. In viscous populations, 42% of all killings are a parent
  killing its own offspring.
- **And yet viscous populations last longest and breed fastest.** In this
  model an attack transfers energy from victim to attacker. A parent that
  kills its offspring takes back part of the energy it spent on
  reproduction. This resembles filial cannibalism, which is common in some
  fish and can recover parental investment when resources are short (Manica
  2002, *Biological Reviews* 77:261–277). We have **not** tested whether
  this energy recycling is why viscous populations persist. It is now the
  leading candidate.
- So "viscosity helps through kinship" is still the best summary of Q and
  Q2. But it is not the kind of kin benefit we expected (relatives not
  attacking). It is a parent that is nearby, and the cost of that falls on
  the offspring.

## Limits

- "Young" means age under 150 ticks (10% of max lifespan). The threshold was
  fixed before the run.
- The log covers ticks 0–6000 only. Kills are counted when both killer and
  victim were alive in the previous or current tick.
- The attack rule hits the nearest agent in reach and does not target by
  identity. So "parent kills offspring" is mostly a consequence of who is
  nearest, not a choice to kill kin.

## Next step

Test energy recycling directly. Keep viscous placement but stop attacks from
transferring energy when the victim is the attacker's own offspring. If the
recycling explains persistence, viscous survival should fall to the
`stranger` level.

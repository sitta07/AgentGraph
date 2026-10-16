# Findings: Experiment N — Lamarckian vs Darwinian inheritance, static vs shifting world

**Status:** completed 2026-10-16. 32 runs: 4 conditions × 8 seeds (600–607,
never run before) × 12000 ticks. Pre-registered at commit `3af2228`, spec
unchanged, no deviations. Report:
[`results/N_lamarck_vs_darwin_shift/`](../../results/N_lamarck_vs_darwin_shift/REPORT.md).

**Citation correction.** The spec cites "Sasaki & Tokoro (1997, 2000)". The
work we meant is Sasaki & Tokoro, *Artificial Life* (1999) and LNCS (1999),
plus their 2000 *Knowledge and Information Systems* paper. They report that
populations with less inheritance of acquired weights cope better with a
changing environment.

| Hypothesis | Test | Result |
|---|---|---|
| H22a: static — Lamarckian innate foraging is higher | +0.4 [−2.8, 4.3] | not supported |
| H22b: static — Lamarckian realised foraging is higher | −0.006 [−0.012, 0.0003] | not supported |
| H22c: after shift — Darwinian innate foraging is higher | +2.8 [0.25, 7.1] | supported (weak; few paired survivors) |
| H22d: after shift — Darwinian realised foraging is higher | +0.005 [−0.002, 0.011] | not supported |
| H22e: manipulation check — the shift lowers Darwinian foraging | +0.002 [−0.002, 0.006] | **not supported** |

## The environment shift did not work as a test

- H22e failed: Darwinian populations foraged no worse after the mirror shift
  than without it.
- Realised foraging was measured in the final quarter (ticks 9000–12000),
  3000+ ticks after the shift. That left enough time for learning and
  selection to recover.
- So this study **cannot answer the static vs dynamic question**. H22c should
  not be read as support for Sasaki & Tokoro. A proper test needs the
  measurement right after the shift, or repeated shifts.

## What it did show: Lamarckian inheritance compounds the learning side effect

This was not pre-registered as a hypothesis, but the effect is large.

| condition | extinct | attack rate | share-gene ratio | max generation |
|---|---|---|---|---|
| darwin_static | 1/8 | 0.18 | 0.84 | 15 |
| lamarck_static | 5/8 | **0.43** | 0.95 | 29 |
| darwin_shift | 1/8 | 0.15 | 0.87 | 16 |
| lamarck_shift | 4/8 | **0.35** | 0.91 | 40 |

- Lamarckian populations went extinct in **9/16 runs, against 2/16**
  Darwinian runs. Pooling over static and shift gives Fisher p = 0.023
  two-sided. This pooling was not pre-registered.
- Their attack rates were 2–3× higher.
- The share-gene ratio (social / locomotion inborn weight) rose toward 1 in
  Lamarckian populations. In this design, inheriting learned weights means
  inheriting the weakened locomotion found in I–K. Generation after
  generation, the bias builds up in the inherited wiring, so social actions,
  above all attack, take over and populations die out.
- This fits I–K and the R-STDP bias term (Frémaux et al. 2010). It is a
  post-hoc explanation. A pre-registered replication would predict a rising
  inborn social/locomotion ratio across generations under Lamarckian
  inheritance, and no rise under Darwinian inheritance.

## Limits

- Innate and realised foraging are measured on survivors only. With 9/16
  Lamarckian extinctions, the paired tests rest on few seeds.
- Attack rate is measured in the final window, so populations that died
  earlier are missing.
- The mirror shift was weaker than intended (see above).

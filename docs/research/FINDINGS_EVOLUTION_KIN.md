# Findings: selfish lifetime learning vs kin-selected helping (Experiment C)

**Status:** completed 2026-10-12. 24 runs: 2×2 conditions × 6 seeds × 6000
ticks, about 6–9 generations. Raw data, charts and the auto-generated report
are in [`results/evolution_kin/`](../../results/evolution_kin/REPORT.md).
Reproduce with:
`python -m neuralmind.research.evolution --seeds 6 --ticks 6000`

## Design (pre-registered in `neuralmind/research/evolution.py`)

Evolving populations of 12→36 spiking agents can share energy. Sharing costs
the giver *a* and gives the receiver *2a*. The learning reward is selfish
(r_prosocial = 0). We crossed two factors:

- **Viscous:** offspring are born next to their parent. **Well-mixed:**
  offspring are born anywhere.
- **Plasticity on:** reward-modulated learning during life. **Plasticity off:**
  innate wiring only.

## Results vs predictions

| Hypothesis | Prediction | Result | Verdict |
|---|---|---|---|
| H5 | Viscosity raises the *innate* share drive | +0.007 [0.000, 0.014] | nominally supported, **but tiny and fragile** |
| H6 | Selfish learning lowers realised sharing (viscous) | learning *doubles* sharing: 1.61% vs 0.78%, difference −0.83 pp [−0.97, −0.70] | **falsified (opposite direction)** |
| H7 | No kin-directed sharing without kin recognition (null) | shares reach kin 4.0 pp above chance [2.1, 6.6]; well-mixed shows no bias (10.2% vs 10.5%) | **null rejected** |

## Interpretation

1. **Innate social genes barely evolved.**
   - The share drive stayed near its founding value of 0.85 in every
     condition.
   - Six to nine generations of weak selection are not enough to move it
     much.
   - The H5 effect is at the detection limit, so we do not treat it as
     established.
2. **Learning increased sharing.** This is the opposite of our prediction.
   - Learners also met relatives far more often: 17% vs 5% of encounters in
     viscous populations, and they reached more generations (7.0 vs 5.8).
   - A plausible explanation is **crowding**: better foragers cluster at the
     same food. More neighbours means more drive from the "other agents"
     sensors into the share population, so sharing goes up as a by-product
     and not because sharing was rewarded.
   - This is a *post-hoc* explanation and has not been tested yet.
3. **Kin received more help than chance, but only in viscous populations,
   with no kin-recognition sensor.**
   - Offspring are born closer (≈0.04) than the reach for helping (0.08).
   - If agents help their nearest neighbour, and the nearest neighbour is
     disproportionately kin, then location alone produces a kin bias.
   - This is the classic "kin discrimination by spatial cue" idea. It is also
     post-hoc.

## Pre-registered follow-up (Experiment C2)

Two new hypotheses come from the results above. Each has a direct test:

- **H9 (crowding):** conditioned on having a neighbour in reach, the learning
  effect on sharing disappears. Falsified if the share-given-encounter rate is
  still higher with learning on (CI excludes 0).
- **H10 (spatial kin cue):** in viscous populations, partners in share events
  are closer than the average nearest neighbour in reach, and closer
  partners are more often kin. Falsified if share-partner distance is not
  smaller than encounter distance.

C2 also runs ~3× longer, so selection has more generations to act on innate
genes.

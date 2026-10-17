# Findings: Experiment AN — outside NeuralMind, shaping breaks Hebbian credit but not policy-gradient credit

**Status:** completed 2026-10-17. 72 runs: 6 conditions × 12 seeds (100–111,
never run before). Pre-registered at commit `943f375`
([PREREG_AN.md](PREREG_AN.md)), unchanged, no deviations. Run time 36 s.
The system shares no code with NeuralMind: a linear-softmax forager,
[`tools/theory/forager.py`](../../tools/theory/forager.py).
Raw data: [`results/AN_forager/`](../../results/AN_forager/).

**Question.** [The theory note](THEORY_shaping_covariance.md) predicts:

- Potential-based shaping depresses inputs that track the potential when
  credit is Hebbian and the baseline is a single scalar.
- A state-dependent baseline removes this.
- Score-function (policy-gradient) credit is immune.

| id | test | result (95% CI) | verdict |
|---|---|---|---|
| N1 | shaping lowers forward food weights (Hebbian, scalar) | −28.5 [−43.0, −16.9] | **supported** |
| N2 | state baseline keeps them higher (Hebbian) | +16.5 [+5.7, +32.1] | **supported** |
| N3 | same depression under score-function credit (predicted not) | +0.3 [−0.9, +1.2] | not supported, **as predicted** |
| N4 | shaping helps score-function foraging | +39.4 [+34.6, +44.0] food/1000 | **supported** |
| N5 | state baseline helps Hebbian foraging | +7.1 [+5.5, +8.7] food/1000 | **supported** |

**By the pre-registered rule (N1 and N2 supported, N3 not), the theory's
prediction holds outside NeuralMind.**

| condition | food per 1000 steps | stay share | forward food weight |
|---|---|---|---|
| Hebbian, no shaping | 4.6 | 20% | +5.6 |
| Hebbian, shaping, scalar baseline | **0.9** | **41%** | **−22.9** |
| Hebbian, shaping, state baseline | 8.0 | 27% | −6.4 |
| score function, no shaping | 15.4 | 4% | +3.0 |
| score function, shaping, scalar baseline | 54.8 | 0.2% | +3.3 |
| score function, shaping, state baseline | 60.4 | 0.2% | +2.9 |

## Interpretation

- **The same shaping reward has opposite effects depending on the credit
  rule.** It made the policy-gradient forager eat 3.6 times more, and it
  made the Hebbian forager collapse: 0.9 food per 1000 steps, standing still
  41% of the time. This matches what AE and AF found in NeuralMind, where
  the non-moving actions won by default.
- **A state-dependent baseline rescued the Hebbian forager** (8.0, above
  its no-shaping level), as the theory predicts.
- **A practical rule, for systems like these.** Potential-based shaping is
  safe for score-function learners. For Hebbian three-factor learners, which
  are common in spiking and neuromorphic reinforcement learning, it needs a
  per-state reward baseline.

## Limits

- One task, one learning rate, linear policies. The Hebbian forager learns
  poorly even without shaping (4.6 vs 15.4), so it is a weak learner in
  absolute terms.
- The state baseline keys on 8 binarised states, so it removes only part of
  the bias (the food weights are still negative).
- Novelty is not established; see the literature section of the theory note.

## Next step

Test across learning rates, tasks and a standard R-STDP implementation, and
do a deeper literature search before writing this up as a preprint.

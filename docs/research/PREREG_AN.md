# Pre-registration: Experiment AN — the shaping bias outside NeuralMind

**Registered 2026-10-17, before any run on the registered seeds.**

**Question.** [The theory note](THEORY_shaping_covariance.md) predicts two things. Potential-based shaping depresses inputs whose activity tracks the potential when credit is Hebbian, meaning eligibility is a non-negative post activity times pre activity, and the baseline is a single scalar. It predicts no such systematic depression under score-function (policy-gradient) credit, whose post term has zero mean, and that a state-dependent baseline removes it. AN tests these predictions in a system that shares no code with NeuralMind: a linear-softmax forager, [`tools/theory/forager.py`](../../tools/theory/forager.py).

**Design.**
- Six conditions:
  - credit: Hebbian or score-function
  - baseline: scalar or state
  - shaping: on or off; the no-shaping conditions use a scalar baseline only
- Seeds 100–111 (12 per condition), never run.
- 30000 learning steps, then 5000 test steps with learning off, sampling from the policy.
- Fixed in advance: lr 0.05, shaping weight 4, 8 food items, 4 actions (left, forward, right, stay).
- `w_food_forward` is the summed weight from the three food bins to the forward action at the end of learning.

**Analysis.** [`tools/theory/analyse_forager.py`](../../tools/theory/analyse_forager.py) runs paired bootstrap 95% CIs across seeds. A directional test is supported if its CI excludes zero in the predicted direction.

| id | test | metric | a vs b | direction |
|---|---|---|---|---|
| N1 | shaping depresses food weights under Hebbian credit, scalar baseline | w_food_forward | hebb_scalar vs hebb_noshape | less |
| N2 | a state baseline reduces that depression | w_food_forward | hebb_state vs hebb_scalar | greater |
| N3 | the same depression under score-function credit (predicted: **not** supported) | w_food_forward | score_scalar vs score_noshape | less |
| N4 | shaping helps score-function foraging | food_per_1000 | score_scalar vs score_noshape | greater |
| N5 | a state baseline helps Hebbian foraging | food_per_1000 | hebb_state vs hebb_scalar | greater |

**Interpretation rule, fixed in advance.** The theory's prediction holds outside NeuralMind if N1 and N2 are supported and N3 is not.

**Disclosed engineering check.** Before registering, I made two engineering runs on seed 999, which is excluded from the registered seeds. The first used one food item. Foraging was too rare to learn from (about 1.5 food per 1000 steps), so I changed to 8 items. The second used 15000 learning steps and 3000 test steps, and gave these results:

| condition | food per 1000 steps | w_food_forward |
|---|---|---|
| score, no shaping | 13.7 | +2.4 |
| score, scalar | 58.3 | +2.4 |
| hebb, scalar | 7.3 | −13.2 |
| hebb, state | 9.3 | −2.5 |

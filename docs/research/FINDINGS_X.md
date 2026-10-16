# Findings: Experiment X — with the fixed decision dynamics, learning still does not pay in evolving social populations

**Status:** completed 2026-10-17. 40 runs: 4 conditions × 10 seeds
(2300–2309, never run before) × 6000 ticks. Pre-registered at commit
`36019d1`, spec unchanged, no deviations. A 2-seed pilot on other seeds
(9200–9201) preceded registration. Run time 108 min.
Report: [`results/X_learning_in_evolving_populations/`](../../results/X_learning_in_evolving_populations/REPORT.md).

**Setup.** The three fixes from [W](FINDINGS_W.md) (32 ms decisions, state
cleared before each decision, normalised input weights) on the standard
evolution base. Each action neuron's input weights are normalised to its own
innate sum (`normalize_to="innate"`), not to one shared budget. The shared
budget erased the weaker innate social drive and led to extinction within
1000 ticks in the W pilot.

| Hypothesis | Test (a − b) | Result |
|---|---|---|
| H40a: fixed learners eat more than fixed non-learners | +0.0020 [−0.0028, 0.0062] food per agent-tick | not supported |
| H40b: fixed learners eat more with real than with scrambled senses | +0.0005 [−0.0046, 0.0052] | not supported |
| H40c: fixed learners eat more than default non-learners | −0.0125 [−0.0161, −0.0084] | not supported (they eat 27% less) |
| H40d: learning raises the attack rate under the fixed dynamics | +0.049 [−0.026, 0.130] | not supported |
| H40e: survival does not differ (learn vs no learn) | 0 [0, 0] | no difference detected (no run went extinct) |

**By the pre-registered rule (H40a not supported), learning does not pay in
evolving populations even with the fixed dynamics.** The pilot's small
learning advantage (0.033–0.037 vs 0.030–0.032) did not replicate.

| condition | food per agent-tick | attack rate | early deaths by killing | by starvation | by old age | births in 6000 ticks | innate foraging |
|---|---|---|---|---|---|---|---|
| fixed, learning | 0.0334 | 0.23 | 73% | 27% | 1% | 1336 | 6.4 |
| fixed, no learning | 0.0314 | 0.18 | 65% | 32% | 3% | 794 | 6.8 |
| fixed, learning, scrambled senses | 0.0329 | 0.25 | 72% | 27% | 1% | 1282 | 6.4 |
| **default, no learning** | **0.0458** | **0.012** | 6% | 44% | 50% | 214 | 8.8 |

## Interpretation

- **The fixed dynamics hurt evolving social populations, with or without
  learning.** They cut foraging by about 30% and raised the attack rate
  about 15× (0.18 vs 0.012). Killing became the main cause of death (65–73%
  against 6%), and births rose 4–6×, so the populations turned over quickly.
  None went extinct, which the innate-sum normalisation achieved.
- **The attack rate comes from the decision rule itself.** It is already
  0.18 without any learning. With cleared state and a 32 ms window, the
  choice among six actions is closer to uniform, and attack wins often. With
  the default dynamics, lock-in into movement keeps attacks rare. V and W
  suggested this; X measures it in populations.
- **Learning did not use the senses here** (H40b). Scrambling the senses left
  food intake unchanged, in contrast to single agents in W.
- **A candidate explanation, not tested: lives are too short to learn.**
  W's agents trained for 40 episodes × 500 ticks. Here, a rough estimate
  (about 35 agents × 6000 ticks ÷ 1336 births) gives a mean life of about
  150 ticks, against about 1000 with the default dynamics, and most lives
  end in a kill. Learning that needs thousands of ticks of
  practice cannot pay off in that time.

## Limits

- 6000 ticks, shorter than the 18000 ticks of the Q studies, chosen for the
  4× compute of 32 substeps. Longer runs could let evolution adapt the
  innate weights to the new dynamics.
- Only one normalisation rule (innate sum) was tested in populations.

## Next step

Test the short-life account directly: raise the cost of attacks or lower
the innate attack drive under the fixed dynamics, so that lives lengthen,
and check whether learning then pays. A single-agent W-style test with
episode length cut to the lifetimes seen here would also show whether
learning needs more time than these agents have.

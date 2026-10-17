# Findings: Experiment AE — the learned rise in attacks is carried by the movement neurons' input weights

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 training seeds
(3200–3211), agent 0 tested on 8 held-out worlds (9920–9927). Seeds and
worlds had never been run. Same design as [AC](FINDINGS_AC.md)'s `social12`:
12 social agents, 24 food, no hazards, fixed dynamics, frustration drive on,
1500 training ticks. Pre-registered at commit `8f02a7b`, spec unchanged, no
deviations. Run time 37 min.
Report: [`results/AE_which_weights/`](../../results/AE_which_weights/REPORT.md).

**Question.** Among social peers, learning raises the attack rate (AB, AC).
An exploratory probe after AC froze the input weights of one group of actions
during learning and pointed at the movement neurons. AE tests that on new
seeds. `frozen_inputs` lists actions whose input weights never learn.

| Hypothesis | Test | Result |
|---|---|---|
| H51a: when only the movement inputs learn, learning raises the attack rate | +0.196 [0.166, 0.231] | **supported** |
| H51b: freezing the movement inputs shrinks the learned rise in attacks | −0.117 [−0.152, −0.088] | **supported** |
| H51c: with the movement inputs frozen, learning pays | +2.62 [1.66, 3.50] food per episode | **supported** |
| H51d: freezing the movement inputs raises the learning gain | −0.91 [−3.67, 1.58] | not supported |

**By the pre-registered rule (H51a and H51b supported), learning in the
movement neurons carries the rise in attacks.** Freezing those inputs
removes the rise and leaves a positive learning gain, but not a larger one
than learning everything.

| what learns | trained | untrained | learning gain | trained attack rate | untrained attack rate | seeds with gain > 0 |
|---|---|---|---|---|---|---|
| all actions | 18.0 | 14.5 | +3.5 | 0.141 | 0.059 | 10/12 |
| movement only | 10.2 | 14.5 | −4.3 | 0.255 | 0.059 | 3/12 |
| social only | 17.1 | 14.5 | +2.6 | 0.024 | 0.059 | 11/12 |

## Interpretation

- **The attack neurons need not learn anything for attacks to rise.** With
  their inputs frozen, the attack rate more than quadrupled (0.059 → 0.255)
  and food fell by 4.3 per episode. What changed was the movement neurons'
  input weights.
- **A mechanism consistent with the probes, partly tested here.** Under
  the default alignment-shaping reward, the reward-prediction error is
  negatively correlated with eligibility
  ([`rpe_eligibility_probe.py`](../../tools/probes/rpe_eligibility_probe.py),
  r ≈ −0.11, solo agents, 3 seeds per condition). Active synapses are
  therefore depressed on average, and per-neuron normalisation moves their
  weight onto silent sensors. The movement neurons respond less to what they
  see, and the untouched attack neurons win the competition more often. AE
  shows the second half of this chain: the movement weights carry the rise
  in attacks. The first half is tested in AF.
- **When only the social inputs learn, attacks fall below the untrained
  level** (0.024 vs 0.059). Attacks cost energy and pay little, so learning
  in the attack neurons turns attacks down.
- **The learning gain with all actions learning varies between studies:**
  +3.5 [10/12 seeds positive] here, +0.4 in AC, +0.3 in AB. All three used
  12 seeds and different seed ranges. Gains among social peers are small and
  noisy, so single studies should not be over-read.

## Limits

- 1500 training ticks, no hazards, agent 0 only, 8 test worlds.
- Freezing whole groups of inputs is a blunt tool. It shows where the
  attack rise lives, not which sensors drive it.

## Next step

[AF](../../studies/AF_reward_shape.json), already pre-registered, replaces
alignment shaping with approach shaping. If the drift comes from the
alignment reward, the learned rise in attacks should shrink.

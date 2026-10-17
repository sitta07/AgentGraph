# Findings: Experiment AF — with approach shaping instead of alignment shaping, social agents learn in groups

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 training seeds
(3300–3311), agent 0 tested on 8 held-out worlds (9930–9937). Seeds and
worlds had never been run. Same design as [AE](FINDINGS_AE.md): fixed
dynamics, no hazards, 1500 training ticks. Pre-registered at commit
`0e8b4d1`, spec unchanged, no deviations. Run time 23 min.
Report: [`results/AF_reward_shape/`](../../results/AF_reward_shape/REPORT.md).

**Question.** [AE](FINDINGS_AE.md) found that the learned rise in attacks
among social peers lives in the movement neurons' input weights. A probe
([`rpe_eligibility_probe.py`](../../tools/probes/rpe_eligibility_probe.py))
found why they might drift. Under the default alignment-shaping reward,
`r_align × (change in alignment with the nearest food)`, the reward-prediction
error is negatively correlated with eligibility (r ≈ −0.11). Under approach
shaping, `r_approach × (decrease in distance to it)`, the correlation was
positive. AF swaps one for the other.

| Hypothesis | Test | Result |
|---|---|---|
| H52a: with approach shaping, learning raises attacks less | −0.078 [−0.123, −0.041] | **supported** |
| H52b: approach shaping gives social peers a larger learning gain | +5.95 [3.60, 8.46] food per episode | **supported** |
| H52c: with approach shaping, learning pays among social peers | +4.85 [3.55, 6.07] | **supported** |
| H52d: with approach shaping, learning pays for a solo agent | +1.95 [1.43, 2.52] | **supported** |

**By the pre-registered rule (H52a supported), alignment shaping causes the
learned rise in attacks; approach shaping rescues social learning (H52b, H52c
supported).**

| condition | trained | untrained | learning gain | seeds with gain > 0 | trained attack rate | untrained attack rate | trained forward share |
|---|---|---|---|---|---|---|---|
| social12, alignment | 11.4 | 12.5 | −1.1 | 3/12 | 0.125 | 0.058 | 0.32 |
| social12, approach | 17.4 | 12.5 | +4.9 | 12/12 | 0.047 | 0.058 | 0.39 |
| solo, approach | 5.8 | 3.9 | +1.9 | 12/12 | — | — | 0.35 |

## Interpretation

- **The social learning failure seen in Z, AB, AC and here is a property of
  the reward, not of social life.** With approach shaping, every one of 12
  seeds gained, the learned rise in attacks vanished (0.058 → 0.047), and
  trained agents moved forward more often.
- **Approach shaping is no free lunch.** A solo agent learns under it, but
  only a little: +1.9, ending at 5.8 food per episode. Under alignment
  shaping, solo agents in [Y](FINDINGS_Y.md) gained +26% after 150 ticks and
  2.6× after 500, and the AF pilot gave +11.4 (spent seeds, not compared
  here). Which shaping signal works best depends on the agent's situation.
- **Why the two shapings differ, as a working account.** Alignment is
  bounded. When food is straight ahead, the sensors are strongly active and
  alignment can only get worse, so strong input tends to come with negative
  reward-prediction error. Under a covariance learning rule (Frémaux,
  Sprekeler & Gerstner 2010), this depresses the active synapses. Distance
  to food has no such ceiling while the agent approaches it. Both shapings
  are potential-based (a difference of a potential), which leaves the
  optimal policy unchanged (Ng, Harada & Russell 1999). Under a three-factor
  rule with per-decision credit, the learning dynamics are not left
  unchanged. This account is consistent with the probes and AE but is not
  proven here.
- **Pilots have now misled three times** (Y, AC, and here the solo approach
  pilot, which suggested no learning at all).

## Limits

- 1500 training ticks, no hazards, agent 0 only, 8 test worlds.
- AF did not include solo with alignment shaping, so the solo trade-off
  rests on earlier studies with other seeds.

## Next step

Neither shaping wins everywhere, so let evolution choose. Make the shaping
weights heritable genes and ask whether evolving populations move toward
approach shaping, and whether learning then starts to pay in evolving
populations, where it did not in [X](FINDINGS_X.md).

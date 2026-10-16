# Findings: Experiment Z — other foragers do not block learning, social agents do, and theft is not the reason

**Status:** completed 2026-10-17. 48 runs: 4 conditions × 12 training seeds
(830–841), agent 0 tested on 8 held-out worlds (9300–9307). Seeds and worlds
had never been run. No evolution: a fixed group trains together for 1500
ticks (3 episodes of 500), then agent 0 is tested frozen among its frozen
peers. All conditions use the fixed dynamics (32 ms decisions, state cleared,
weights normalised to each neuron's innate sum). Pre-registered at commit
`a98ba24`, spec unchanged, no deviations. A 4-seed pilot (solo and social12
only) preceded registration. Run time 105 min.
Report: [`results/Z_social_learning/`](../../results/Z_social_learning/REPORT.md).

| Hypothesis | Test | Result |
|---|---|---|
| H43a: in a social group, learning lowers foraging | −2.8 [−5.9, +0.5] food per episode | not supported (9/12 seeds negative) |
| H43b: among non-social foragers, learning still pays | +6.9 [3.6, 10.5] | **supported** |
| H43c: removing theft restores the learning gain | +0.4 [−2.9, 3.9] | not supported |
| H43d: in a social group, learning raises the attack rate | +0.048 [0.020, 0.076] | **supported** |
| H43e: replication, solo learning pays | +8.3 [6.2, 10.2] | **supported** |

**By the pre-registered rule (H43b supported, H43a not), the result is
mixed.** Crowding does not stop learning. In social groups, learning did not
pay, but the loss fell just short of significance. Theft is not the cause
(H43c).

| condition | trained | trained, scrambled senses | untrained | learning gain | trained attack rate | untrained attack rate |
|---|---|---|---|---|---|---|
| solo (1 agent, 8 food) | 15.3 | 3.4 | 7.0 | +8.3 | — | — |
| crowd12 (12 non-social, 24 food) | 23.4 | 14.8 | 16.5 | +6.9 | — | — |
| social12 (12 social, 24 food) | 10.7 | 9.1 | 13.5 | −2.8 | 0.112 | 0.063 |
| social12, no theft | 10.6 | 9.2 | 13.0 | −2.4 | 0.113 | 0.096 |

## Interpretation

- **Other foragers are not the problem.** Agents learning among 11
  non-social peers that compete for the same food still gained +6.9, and
  scrambling their senses cost them 8.6 food. They learned sensory foraging.
- **Social agents do not learn to forage.** In social groups, trained agents
  ate less than untrained ones in 9 of 12 seeds, and scrambling their senses
  cost only 1.6 food. They attacked about twice as often after training.
- **Theft is not what drives this.** With `steal=0` an attack gains nothing
  and harms no one, yet trained agents attacked just as often (0.113) and ate
  just as little. Attacks were then pure cost, so reward did not select them.
- **A candidate, untested: the social agent's body, not its company.** A
  social agent has 6 actions instead of 3, and 3 of them do not move it. It
  also has 11 sensors instead of 7. Learning may spread over the non-moving
  actions, or the extra "other agent" and hearing inputs may drive the
  action neurons in ways unrelated to food. This would also explain X, and
  it could be tested with a social agent alone in the world.
- The untrained baseline is one network per test world, so it is the same
  across training seeds. Solo untrained agents ate 7.0 here and 3.6 in Y.
  The test worlds differ, and untrained agents vary a lot between worlds.

## Limits

- Fixed group, 1500 training ticks, no evolution.
- 8 test worlds per agent; only agent 0 is tested.

## Next step

Train a social agent alone (social actions and sensors, no other agents) and
compare it with a non-social agent alone. If it fails to learn, the problem
is the extra actions or sensors; then remove the non-moving actions and the
social sensors one at a time.

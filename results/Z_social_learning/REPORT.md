# What stops lifetime learning from paying among other agents?

**Question.** W and Y showed that a single agent with the fixed decision dynamics learns sensory foraging fast (2.6x after 500 ticks, 4.4x after 1500). X found that learning did not pay in evolving social populations, and Y ruled out short lives as the whole explanation. Here there is no evolution: a fixed group of agents learns together for 1500 ticks, and agent 0 is then tested frozen among its frozen peers. The conditions separate the presence of other foragers from the social actions, and theft from the other social actions.

All conditions use substeps=32, reset_each_decision, normalize with normalize_to='innate'. solo: one agent, 8 food, non-social. crowd12: 12 non-social agents, 24 food (competition for food only). social12: 12 social agents (attack, share, signal), 24 food. social12_nosteal: as social12 with steal=0, so an attack takes no energy: the attacker gains nothing and the target loses nothing, but the attacker still pays the attack cost. Each run trains all agents for 1500 ticks (3 episodes of 500), freezes them, and tests agent 0 on 8 held-out worlds with its trained peers; the untrained baseline is a fresh untrained group on the same worlds. learning_gain = trained_food - untrained_food for agent 0. Exploratory pilot (seeds 720-723, worlds 9600-9605): learning_gain +15.5 solo and -4.0 social12 (all four seeds negative); crowd12 and social12_nosteal were not piloted. Interpretation rule, fixed in advance: social actions (not crowding) block learning if H43a and H43b are supported; theft is the cause if H43c is also supported. Seeds 830-841 and worlds 9300-9307 have never been run.

NeuralMind 0.2.0 · 2026-10-17 05:16 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/Z_social_learning.json` at commit `a98ba24577e3033599b2d037de4d198176205ab1` (2026-10-17T03:31:20+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H43a | In a social group, learning lowers foraging (trained eat less than untrained) | -2.823 [-5.886, 0.5107] | **not supported** |
| H43b | Among non-social foragers, learning still pays | 6.896 [3.625, 10.48] | **supported** |
| H43c | Removing theft restores part of the learning gain (nosteal beats social12) | 0.4062 [-2.907, 3.885] | **not supported** |
| H43d | In a social group, learning raises agent 0's attack rate (trained minus untrained) | 0.04824 [0.02047, 0.0763] | **supported** |
| H43e | Replication of W/Y: solo learning pays | 8.26 [6.188, 10.19] | **supported** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| solo | 15.26 [13.19, 17.19] | 3.385 [2.885, 3.812] | 7 [7, 7] | 8.26 [6.188, 10.19] | 11.88 [9.698, 13.88] | 0 [0, 0] | 0.3293 [0.296, 0.362] |
| crowd12 | 23.4 [20.12, 26.98] | 14.78 [13.48, 16.15] | 16.5 [16.5, 16.5] | 6.896 [3.625, 10.48] | 8.615 [5.802, 11.73] | 0 [0, 0] | 0.3986 [0.3232, 0.4773] |
| social12 | 10.68 [7.614, 14.01] | 9.125 [8.26, 10] | 13.5 [13.5, 13.5] | -2.823 [-5.886, 0.5107] | 1.552 [-1.604, 5.135] | 0 [0, 0] | 0.3159 [0.2308, 0.4066] |
| social12_nosteal | 10.58 [8.082, 13] | 9.229 [8.062, 10.32] | 13 [13, 13] | -2.417 [-4.918, 0] | 1.354 [-1.5, 4.084] | 0 [0, 0] | 0.2912 [0.251, 0.3329] |



Full per-metric summaries and raw per-run data: `results.json`.
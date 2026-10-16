# How much practice does lifetime learning need before it pays?

**Question.** W showed that single agents with the fixed decision dynamics learn sensory foraging after 40 episodes x 500 ticks (20000 ticks) and eat about 5.7x more. X found that in evolving social populations with the same dynamics learning did not pay, and a rough estimate put the mean lifetime there at about 150 ticks (about 35 agents x 6000 ticks / 1336 births). If learning needs much more practice than that, short lives alone can explain X's null result. This study measures how food intake after training depends on the training budget.

Each run trains one fresh single agent with the W 'full' dynamics (substeps=32, reset_each_decision, normalize) for a total of train_ticks ticks, in episodes of at most 500 ticks, then freezes it and tests it on 16 held-out 500-tick worlds with real and scrambled senses; an untrained agent is tested on the same worlds. learning_gain = trained_food - untrained_food. Exploratory pilot (training seeds 700-705, test worlds 9500-9507): trained food 3.4 at 150 ticks, 6.9 at 500, 15.9 at 1500, 16.7 at 5000, 19.5 at 20000, against 4.75 untrained. Interpretation rule, fixed in advance: short lives can explain X's null result if H42a and H42b are supported and H42c is not. This tests single agents only; it does not show that longer lives would make learning pay in populations. Training seeds 800-811 and test worlds 9200-9215 have never been run.

NeuralMind 0.2.0 · 2026-10-17 03:12 · mean [95% bootstrap CI] over seeds; paired differences use the same seeds.

**Pre-registration:** spec `studies/Y_learning_budget.json` at commit `89f6310d520b951e63aabc44aeb6e70a48895340` (2026-10-17T02:48:35+07:00) · unchanged since commit: **True** · preregistered: **True**

## Hypotheses

| id | statement | test (a − b) | result |
|---|---|---|---|
| H42a | After 1500 ticks of training, learning pays (trained eat more than untrained) | 12.15 [9.547, 14.54] | **supported** |
| H42b | Agents trained for 1500 ticks eat more than agents trained for 150 ticks | 11.21 [8.411, 13.79] | **supported** |
| H42c | After only 150 ticks of training (about the mean lifetime in X), learning pays | 0.9375 [0.4479, 1.417] | **supported** |
| H42d | After 500 ticks of training, learning pays | 5.88 [4.562, 7.203] | **supported** |
| H42e | Agents trained for 20000 ticks eat more than agents trained for 1500 ticks | 3.438 [1.417, 5.776] | **supported** |

## Conditions

| condition | trained_food | trained_food_scrambled | untrained_food | learning_gain | sense_gain | collapsed01 | trained_forward_frac |
|---|---|---|---|---|---|---|---|
| t150 | 4.562 [4.073, 5.042] | 3.516 [3.109, 3.927] | 3.625 [3.625, 3.625] | 0.9375 [0.4479, 1.417] | 1.047 [0.3905, 1.724] | 0 [0, 0] | 0.3376 [0.33, 0.3454] |
| t500 | 9.505 [8.188, 10.83] | 3.51 [3.188, 3.844] | 3.625 [3.625, 3.625] | 5.88 [4.562, 7.203] | 5.995 [4.578, 7.391] | 0 [0, 0] | 0.3562 [0.3442, 0.3674] |
| t1500 | 15.77 [13.17, 18.17] | 3.245 [2.839, 3.641] | 3.625 [3.625, 3.625] | 12.15 [9.547, 14.54] | 12.53 [9.901, 15.03] | 0 [0, 0] | 0.3278 [0.2919, 0.3656] |
| t5000 | 17.57 [16.11, 18.95] | 2.943 [2.62, 3.261] | 3.625 [3.625, 3.625] | 13.94 [12.49, 15.33] | 14.62 [13.25, 15.99] | 0 [0, 0] | 0.1427 [0.1239, 0.1631] |
| t20000 | 19.21 [18.03, 20.18] | 3.135 [2.75, 3.505] | 3.625 [3.625, 3.625] | 15.58 [14.4, 16.55] | 16.07 [14.84, 17.16] | 0 [0, 0] | 0.0725 [0.05617, 0.08889] |



Full per-metric summaries and raw per-run data: `results.json`.
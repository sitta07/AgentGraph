# Findings: Experiment V — evolving agents do not measurably use their senses to find food

**Status:** completed 2026-10-16. 48 runs: 4 conditions × 12 seeds
(2000–2011, never run before) × 8000 ticks. Viscous, no extinctions.
Pre-registered at commit `5e396d5`, spec unchanged, no deviations. A
positive-control pilot was run before registration (below). Run time 47 min.
Report: [`results/V_do_agents_use_senses/`](../../results/V_do_agents_use_senses/REPORT.md).

**Intervention.** `scramble_senses=True` shuffles the 6 food and hazard
sensor values every tick. The total input current is unchanged, but which
value belongs to which direction and object is lost. `sense_gain` is the
innate-foraging assay from E (a surviving genome alone in a fresh world for
300 ticks, learning off) with real senses minus the same genome with
scrambled senses.

| Hypothesis | Test | Result |
|---|---|---|
| H36a: evolved innate wiring uses the senses (sense_gain > 0, no learning) | +0.27 [−1.66, 2.06] food | not supported |
| H36b: no-learning populations eat more with real senses | +0.0015 [−0.0007, 0.0038] per agent-tick | not supported |
| H36c: learning populations eat more with real senses | +0.0014 [−0.0016, 0.0041] per agent-tick | not supported |
| H36d: evolving with real senses yields more sense use than evolving scrambled | −0.25 [−2.16, 1.62] food | not supported |

| condition | food per agent-tick | innate foraging, real senses | innate foraging, scrambled | attack rate | max generation |
|---|---|---|---|---|---|
| no learning | 0.0507 | 9.58 | 9.31 | 0.015 | 6.8 |
| no learning, scrambled all life | 0.0492 | 11.06 | 10.54 | 0.018 | 6.5 |
| learning | 0.0366 | 7.15 | 7.72 | 0.107 | 8.8 |
| learning, scrambled all life | 0.0352 | 7.77 | 6.79 | 0.111 | 9.3 |

**By the pre-registered rule (H36a and H36b both not supported), foraging in
these evolving populations does not measurably depend on sensory
information.** The upper end of the H36b interval puts any benefit of real
senses at most about 7% of the food rate.

## Positive-control pilot (before registration)

Single agents trained for 40 episodes ate 4.03 food per test episode with
real senses and 2.60 with scrambled senses (6 training seeds × 16 test
worlds; lower in 5 of 6). So scrambling does remove information that a
trained agent can use. Untrained random wiring ate 1.0 with real senses and
2.5 with scrambled senses.

## Interpretation

- **Populations that evolved with scrambled senses reached the same innate
  foraging score** (10.5–11.1) as those with real senses (9.3–9.6). Whatever
  evolution improves in these worlds does not need sensory information. The
  +5.5 innate-foraging gain in E is therefore not evidence of evolved
  sensory guidance. It is more likely better movement, for example fewer
  wasted turns or social actions. That reading is untested.
- **This explains the three failed environment-shift tests.** Swapping left
  and right (N, N3) or swapping the food and hazard channels (pilot) cannot
  hurt wiring that does not use those channels.
- **The foraging cost of learning appears again**, at the same size as in
  P and T: 0.0366 vs 0.0507, −28%.
- **What it does not show.** A single trained agent does use its senses (the
  pilot). The result is about evolved innate wiring and about the population
  food rate in this world.

## Exploratory follow-up: why the senses do not matter (not pre-registered)

These probes ran on single agents in the default world after V was
registered. They are exploratory, with few seeds, and they motivate a
separate study. The scripts for items 1 and the pilot are in `tools/probes/`;
the others need the `reset_each_decision` option and are added with that study.

1. **Evolved weights have no sensory structure.** In two evolved
   populations (8000 ticks, about 6 generations, no learning), the mean
   innate weights from food and hazard sensors into every movement
   population stayed near the founder value (1.1–1.4), with no left/right
   pattern.
2. **Action selection locks in.** Membrane and synaptic state carry over
   from one decision to the next, and the populations inhibit each other.
   So the current winner tends to keep winning. An untrained single agent
   repeated the same action for a median longest run of 217 of 500 ticks,
   and chose forward only 13% of the time. Given a fixed input, a random
   brain chose left 91–97% of the time whether food was on the left, on the
   right, or absent.
3. **Clearing state before each decision breaks the lock-in, but then the
   senses are too slow.** With state cleared each tick, an untrained agent
   chose each move about a third of the time and ate 2.6× more (2.62 vs
   1.00 per episode). But a decision lasts 8 ms of simulated time and the
   membrane time constant is 20 ms. Starting from rest, sensory input barely
   reaches the action populations, and trained agents no longer differed
   between real and scrambled senses (3.34 vs 3.36).
4. **A longer decision window lets learning find real sensory foraging,
   sometimes.** With state cleared and a 32 ms window, 5 of 12 trained agents
   foraged far better with real than with scrambled senses (7.8–17.6 vs
   2.3–4.2 food per episode; untrained 3.5). The other runs collapsed to
   about 0.3: one movement pathway's weights ran up to the ceiling and the
   others fell, so the agent turned in circles. With the per-state critic
   from R, 7 of 12 succeeded (9.3–19.6) and 5 collapsed. Skorheim, Lonjers &
   Bazhenov (2014) report the same instability for rewarded STDP in a
   spiking forager, and fix it with input balancing.

Together these suggest that the absence of sensory foraging, and part of
the foraging cost of learning, come from the decision dynamics: lock-in, a
decision window shorter than the membrane time constant, and runaway
potentiation. That is a hypothesis for the next pre-registered study, not
a finding.

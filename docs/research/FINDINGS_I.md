# Findings: Experiment I — does learning strengthen every social action, rewarded or not?

**Status:** completed 2026-10-15. 24 runs: 3 conditions × 8 seeds (200–207,
never run before) × 8000 ticks. No population went extinct. Pre-registered at
commit `6201432`, spec unchanged, no deviations. Report:
[`results/I_nonspecific_social_potentiation/`](../../results/I_nonspecific_social_potentiation/REPORT.md).

**Question.** In E and G, learning raised attacks ~11× and sharing ~2×. The
gift-reward loop explained only ~22% of the sharing rise (G). Is the rest a
side effect of the learning rule? The rule applies one global reward
prediction error (RPE) to the input weights of *every* action population that
was active, not only the one that was executed.

**Conditions.**

- `learn_all`: the current rule.
- `learn_chosen`: the RPE changes only the executed action's input weights
  (`credit_chosen_only=True`).
- `nolearn`: no plasticity.

| Hypothesis | Test | Result |
|---|---|---|
| H18a: learning raises signalling, which only costs energy | learn_all − nolearn = +0.019 [0.012, 0.028] (0.027 vs 0.008, ≈3.5×) | **supported** |
| H18b: social input weights drift up relative to locomotion | +0.025 [0.019, 0.030] | **supported**, but see below: all weights *fell* |
| H18c: chosen-only credit lowers attacks | +0.004 [−0.022, 0.031] | not supported |
| H18d: chosen-only credit lowers sharing (neighbour in reach) | +0.0025 [0.0003, 0.0052] | supported |
| H18e: chosen-only credit lowers signalling | +0.010 [0.004, 0.016] | supported |
| H18f: replication — learning raises attacks | +0.081 [0.068, 0.096] (0.100 vs 0.019) | supported (fourth time) |

## What the weights actually did

H18b passed, but its wording ("grow more") is misleading. Lifetime drift per
action, as mean learned weight / mean innate weight − 1, in living agents at
the end of the run:

| condition | locomotion | attack | share | signal |
|---|---|---|---|---|
| learn_all | −0.032 [−0.038, −0.025] | −0.011 [−0.017, −0.006] | −0.004 [−0.008, −0.001] | −0.005 [−0.010, −0.001] |
| learn_chosen | −0.025 [−0.032, −0.019] | −0.007 [−0.016, 0.002] | −0.001 [−0.001, 0.000] | −0.001 [−0.002, 0.000] |

All input weights went **down** over a lifetime. Locomotion weights went down
the most. Social actions gained only *relative to* locomotion. The mechanism
written in the spec was "potentiation pulls every pathway up", and it is
wrong in that form.

## Interpretation

- **Learning raises costly, unrewarded signalling** (≈3.5×). That cannot come
  from reward for signalling, because there is none, so part of the learning
  effect is non-specific.
- **Shared credit explains part of it.** Restricting credit to the executed
  action removed about **half of the signalling rise** (0.010 of 0.019) and
  about **40% of the sharing rise** (0.0025 of 0.0067). It removed **none of
  the attack rise**.
- **Candidate explanation, not yet tested.** Locomotion weights weaken over a
  lifetime, in both learning conditions. Action selection is a spike-count
  competition between populations, so weaker locomotion lets every social
  population win more often. The weakening happens even under chosen-only
  credit, where social weights barely change. That would explain why most of
  the attack rise and half of the signalling rise survive the intervention.
- Attacks with a target *are* rewarded (stolen energy counts as food). Some of
  the attack rise may therefore be ordinary reinforcement as well.

## Side observation (not pre-registered)

Innate foraging was lower in learning populations: 7.9 vs 12.4,
−4.5 [−7.6, −1.5]. This is the hiding effect from E, now on fresh seeds.

## Limits and disclosure

- One ecology, viscous populations only, 8 seeds.
- Drift is measured only in agents alive at the end, so it is biased toward
  survivors.
- After committing this spec, but before the results came in, we noticed that
  E and G's raw data already showed about 3× more signalling under learning.
  H18a was therefore not a blind prediction about direction. The seeds used
  here are new.

## Next step

Test the locomotion-weakening explanation directly. Freeze plasticity on the
locomotion inputs only. If the explanation is right, the learning-induced rise
in attack and signal rates should shrink.

# Findings: Experiment AM — the state critic predicted by theory rescues learning without changing the reward

**Status:** completed 2026-10-17. 60 runs: 5 conditions × 12 training seeds
(3800–3811), agent 0 tested on 8 held-out worlds (9940–9947). Seeds and
worlds had never been run. Same design as [AF](FINDINGS_AF.md). Pre-registered
at commit `f99f830`, spec unchanged, no deviations. No pilot. Run time 40 min.
Report: [`results/AM_state_critic/`](../../results/AM_state_critic/REPORT.md).

**Question.** [The theory note](THEORY_shaping_covariance.md) gives a reason
for the failure behind AE and AF. Potential-based shaping makes the reward
negatively correlated with any input that tracks the potential, by
`−(1−ρ)Var(Φ)`, so a three-factor rule with a scalar baseline depresses
those inputs. The same derivation predicts a fix that keeps the reward
unchanged: a state-dependent baseline. AM keeps the default alignment
shaping and switches NeuralMind's critic from one reward expectation
(`scalar`) to one per binarised sensor state (`state`).

| Hypothesis | Test | Result |
|---|---|---|
| H60a: state critic shrinks the learned rise in attacks | −0.080 [−0.154, −0.012] | **supported** |
| H60b: state critic raises the learning gain among social peers | +6.21 [2.06, 9.88] | **supported** |
| H60c: with the state critic, learning pays among social peers | +6.72 [3.59, 9.55] | **supported** |
| H60d: a solo agent still learns with the state critic | +13.04 [12.01, 14.12] | **supported** |
| H60e: state critic vs approach shaping among social peers | +2.51 [−0.07, 4.97] | no difference detected |

**By the pre-registered rule (H60a, H60b and H60c supported), the theory's
fix works in NeuralMind and fully rescues social learning.**

| condition | trained | untrained | learning gain | seeds > 0 | trained / untrained attack rate |
|---|---|---|---|---|---|
| social12, scalar critic | 14.6 | 14.1 | +0.5 | 7/12 | 0.154 / 0.063 |
| social12, state critic | 20.8 | 14.1 | +6.7 | 11/12 | 0.074 / 0.063 |
| social12, approach shaping | 18.3 | 14.1 | +4.2 | 12/12 | 0.047 / 0.063 |
| solo, scalar critic | 14.9 | 5.6 | +9.3 | 12/12 | — |
| solo, state critic | 18.7 | 5.6 | +13.0 | 12/12 | — |

## Interpretation

- **The fix was predicted before the run, from a derivation, and it worked.**
  With the reward unchanged, the state critic turned the learning gain
  among social peers from +0.5 to +6.7 and removed most of the learned rise
  in attacks.
- **It removes the trade-off AF left.** Approach shaping helped in groups but
  was weak alone. The state critic did well in both. Its solo gain (+13.0)
  was higher than the scalar critic's (+9.3). That comparison is descriptive,
  not a pre-registered test.
- **Replicated outside NeuralMind.** [AN](FINDINGS_AN.md) found the same
  pattern in a linear-softmax forager that shares no code with NeuralMind.
  Shaping broke Hebbian credit under a scalar baseline, a state baseline
  rescued it, and policy-gradient credit was unaffected.
- **Learning gains in NeuralMind's social groups vary between studies.**
  The scalar-critic gain was +0.5 here, +0.4 in AC, +3.5 in AE and −1.1 in
  AF. The state-critic effect is large compared with that spread.

## Limits

- 1500 training ticks, no hazards, agent 0 only, 8 test worlds.
- The state critic keys on binarised sensors (up to 2048 states). How much
  of the bias it removes was not measured directly.
- Novelty of the theory is not established.

## Next step

- Rerun X, learning in evolving populations, with the state critic.
- Measure the RPE–eligibility correlation under each critic.

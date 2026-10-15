# Findings: Experiment M — signals do not evolve meaning in this world

**Status:** completed 2026-10-16. 24 runs: 2 conditions × 12 seeds (700–711,
never run before) × 18000 ticks. Learning off. Two populations went extinct
in each condition. Pre-registered at commit `6fe6eb6`, spec unchanged, no
deviations. Report:
[`results/M_signal_meaning/`](../../results/M_signal_meaning/REPORT.md).

**Design.** In the `hearing` condition, receivers can hear signals. In the
`deaf` control, the heard-signal sensor always reads 0, so a signal cannot
affect anyone and selection has no reason to shape it. If signals evolve
meaning, they should carry more information about the signaller's state when
they can be heard.

| Hypothesis | Test (hearing − deaf) | Result |
|---|---|---|
| H23a: more information about food | −0.00005 [−0.00015, 0.00004] bits | not supported |
| H23b: more information about threat | −0.00016 [−0.00034, −0.00001] bits | not supported (slightly the reverse) |
| H23c: more information about hunger | +0.00015 [−0.0006, 0.0011] bits | not supported |
| H23d: at least 0.01 bits about food | 0.00022 bits on average | not supported |
| H23e: same signalling rate | +0.0001 [−0.0018, 0.0022] | no difference detected |

## Interpretation

- **Signals carry almost no information**: about 0.0002–0.001 bits, in both
  conditions. The values are the same whether anyone can hear or not, so
  nothing indicates that selection is shaping meaning.
- **"Significant" is not "meaningful".**
  - The G-test of independence rejected the null in 11/12 hearing runs and
    **12/12 deaf runs**.
  - With thousands of samples, any tiny dependence is detected. Here it comes
    from the signal neuron receiving the same sensory inputs as every other
    action population.
  - Earlier summaries that cited significant p-values for signals (C2 and the
    exploratory notes) should be read this way.
- **No incentive for signalling exists in this world.** Nothing is
  cooperative to coordinate, and hearing a call gives no exploitable benefit.
  That fits the literature: referential signalling in evolved spiking swarms
  appeared under cooperative tasks (arXiv 2212.08484).

## Limits and next step

- Learning was off, and the runs lasted 18000 ticks (about 13–19
  generations). That may be too short for a signalling system to form.
- MI uses 2×2 tables of binarised sensors. Richer codes would be missed.
- **Next step:** add a reason to communicate before testing again. For
  example, food that needs two agents to harvest, or a hazard that one agent
  can see and others cannot. Then the deaf control becomes a meaningful
  comparison.

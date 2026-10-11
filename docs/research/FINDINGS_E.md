# Findings: Experiment E — Baldwin effect or hiding effect?

**Status:** completed 2026-10-12. 18 runs: 3 conditions × 6 seeds × 8000
ticks. No population went extinct. Pre-registered at commit `589e709`, spec
unchanged, no deviations. Report:
[`results/E_baldwin_vs_hiding/`](../../results/E_baldwin_vs_hiding/REPORT.md).

**Question.** Does reward-modulated lifetime learning speed up the evolution
of innate foraging ability (the Baldwin effect), or does it shield genotypes
from selection (the hiding effect)? Theory allows both (Hinton & Nowlan 1987;
Mayley 1997; Paenke, Sendhoff & Kawecki 2007).

**Measure.** Each evolved genome is tested alone in a fresh world with
learning switched **off**, so only the inherited wiring counts. The score is
food eaten in 300 ticks.

| Hypothesis | Test | Result |
|---|---|---|
| H12: mutation + selection improves innate foraging (sanity check) | evolving, no learning (9.73) − no mutation (4.25) = **+5.5 [3.3, 7.6]** | **supported** |
| H11a: Baldwin — learning populations evolve *higher* innate foraging | learning (5.35) − no learning (9.73) = −4.4 [−7.0, −1.5] | not supported |
| H11b: hiding — learning populations evolve *lower* innate foraging | same difference | **supported** |

## Interpretation

- Evolution works in this world. Without learning, innate foraging more
  than doubled over the founders.
- **With learning, innate foraging barely moved from the founders' level
  (5.35 vs 4.25).** Learning compensated for poor inherited wiring, so
  selection had little reason to improve it. This is the hiding effect.
- Generation count does not explain it. Learning populations went through
  *more* generations (11 vs 6.8), which gave selection more chances, yet
  their innate ability stayed lower.

## Exploratory side observation (not pre-registered)

Learning populations attacked about **11× more often** (14.6% vs 1.3% of
agent-ticks). The cause is not yet tested.

## Limits

- One ecology and 6 seeds per condition.
- The innate assay uses a solo world, while populations evolved in a social
  one.
- Inheritance is Darwinian only. The Lamarckian condition is available
  (`lamarckian=True`) but was not part of this study.

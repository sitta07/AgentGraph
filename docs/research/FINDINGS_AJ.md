# Findings: Experiment AJ — a successful donor's genome restores survival partly, not fully

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 seeds
(3500–3511, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `9aad7aa`, spec unchanged, no deviations. No pilot. Run time 43 min.
Report: [`results/AJ_successful_donor/`](../../results/AJ_successful_donor/REPORT.md).

**Question.** [AI](FINDINGS_AI.md) found that newborns beside their parent
lose the protection when they carry a random unrelated agent's genome. Two
accounts fitted. In (1), genomes clustering with their family in space
protect. In (2), selection is switched off, because a random donor need not
have reproduced. AJ keeps selection by using the genome of the unrelated
agent that reproduced most recently (`foster_from_reproducer=True`).

| Hypothesis | Test | Result |
|---|---|---|
| H57a: successful donor gives fewer extinctions than random donor | −0.17 [−0.50, 0.25] | not supported |
| H57b: successful donor gives longer survival than random donor | +4354 [943, 7424] ticks | **supported** |
| H57c: successful donor still gives more extinctions than own genome | +0.25 [−0.08, 0.58] | not supported |
| H57d: replication of AI, random donor vs own genome | +0.42 [0.08, 0.75] | **supported** |

**By the pre-registered rule, neither clean outcome occurred.** H57a and H57c
were both unsupported, so AJ does not decide between the accounts. AI
replicated (H57d).

| condition | extinct | mean survival | max generation | food per agent-tick | attack rate | fallback births |
|---|---|---|---|---|---|---|
| beside parent, own genome | 4/12 | 16799 | 21.5 | 0.032 | 0.27 | 0% |
| beside parent, random donor | 9/12 | 10380 | 5.6 | 0.045 | 0.12 | 12% |
| beside parent, successful donor | 7/12 | 14734 | 13.6 | 0.032 | 0.22 | 21% |

## Interpretation

- **The foster-genome effect replicated.** Pooled over AI and AJ, a random
  donor gave 19/24 extinctions, against 8/24 with the parent's own genome.
- **Selection contributes.** A successful donor's genome lengthened survival
  by 4354 ticks over a random donor's. It also put the extinction count
  (7/12) between the two references.
- **Clustering is not settled.** With a successful donor, extinctions were
  7/12 against 4/12 for the parent's own genome. That gap is in the
  direction of the clustering account but not detectable with 12 seeds.
- **Random-donor populations ate the most and attacked least.** Food per
  agent-tick was 0.045 against 0.032, and the attack rate 0.12 against 0.27.
  Yet they went extinct most often. In these runs, how well individuals
  forage does not predict whether the population survives.

## Limits

- 21% of successful-donor births fell back to a random unrelated donor (no
  unrelated agent had reproduced yet), which dilutes the manipulation.
- The donor is always the single most recent breeder, so many newborns can
  share one genome. This lowers genetic diversity in a way the parent
  condition does not.

## Next step

Sharpen the contrast with more seeds and a donor rule without fallback or a
single dominant donor. One option: the genome of a random unrelated agent
that has reproduced at least once, falling back to the parent.

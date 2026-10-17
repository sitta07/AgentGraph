# Findings: Experiment AG — starting beside a successful stranger does not protect newborns

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 seeds
(2800–2811, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `7e9b933`, spec unchanged, no deviations. No pilot. Run time 21 min.
Report: [`results/AG_birth_site/`](../../results/AG_birth_site/REPORT.md).

**Question.** Beside the parent, populations survive; beside a random
stranger, they mostly die out. A parent has just reached the reproduction
threshold, so it may stand where food has recently been easy to find. If the
protection comes from that birth site, placing newborns beside the stranger
with the most energy should give the same protection.

| Hypothesis | Test | Result |
|---|---|---|
| H53a: beside the richest stranger, fewer extinctions than beside a random stranger | 0.00 [−0.25, 0.25] | not supported |
| H53b: beside the richest stranger, longer survival | −41 [−2885, 2913] ticks | not supported |
| H53c: birth sites beside the parent have fewer neighbours | +0.49 [0.08, 0.90] (more, not fewer) | not supported |
| H53d: birth sites beside the parent have more food in range | +0.02 [−0.27, 0.31] | not supported |

**By the pre-registered rule (H53a and H53b not supported), the birth-site
account is not supported.**

| condition | extinct | mean survival | neighbours at birth | food at birth | kills of kin | aggression gene |
|---|---|---|---|---|---|---|
| beside parent | 7/12 | 15144 | 22.8 | 15.6 | 65% | 1.28 |
| beside a random stranger | 11/12 | 11499 | 22.3 | 15.6 | 32% | 2.00 |
| beside the richest stranger | 11/12 | 11458 | 23.2 | 15.9 | 28% | 1.40 |

## Interpretation

- **Starting beside a successful adult does not protect.** The richest
  stranger gave exactly the stranger outcome (11/12).
- **Birth sites differed little.** Beside the parent there was about the same
  food in range and slightly more neighbours, not fewer.
- **Pooled over ten studies,** stranger placement went extinct in 110/120
  runs and parent placement in 43/120.
- **Ruled out so far:**
  - local density (Q, Q2)
  - any relative (Q5)
  - parental culling (Q6)
  - the aggression sink (Q7, Q9)
  - parent–offspring sharing (Q8)
  - sensing the parent (AD)
  - birth-site quality (AG)

## Limits

- The birth-site metrics count agents and food within sensor range (`sensor_range`), which covers a large part of the arena, so they are coarse. A finer radius might show differences these do not.

## Next step

So far every candidate has been ecological. An evolutionary candidate is
left: beside the parent, a family's genome stays clustered in space, so
selection can act on families as units (multilevel selection in a viscous
population). A direct test keeps the birth position beside the parent but
gives the newborn the genome of a random unrelated agent. If the protection
disappears, it works through inherited genomes clustering in space, not
through where newborns start.

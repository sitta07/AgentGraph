# Findings: Experiment AI — with a stranger's genome, newborns beside the parent lose the protection

**Status:** completed 2026-10-17. 36 runs: 3 conditions × 12 seeds
(2900–2911, never run before) × 18000 ticks. Learning on. Pre-registered at
commit `572a94d`, spec unchanged, no deviations. No pilot. Run time 39 min.
Report: [`results/AI_foster_genome/`](../../results/AI_foster_genome/REPORT.md).

**Question.** Ten studies found that newborns placed beside their parent
protect a population, and that placing them beside a stranger does not. Every
ecological account tested failed:

- local density
- being beside any relative
- parental culling
- the aggression sink
- parent–offspring sharing
- sensing the parent
- birth-site quality

AI tests an evolutionary account. Newborns stay beside their parent but
inherit the genome (input weights and aggression gene) of a random living
agent unrelated to the parent (`foster_genome=True`).

| Hypothesis | Test | Result |
|---|---|---|
| H55a: with foster genomes, more extinctions beside the parent | +0.50 [0.08, 0.83] | **supported** |
| H55b: with foster genomes, populations die out sooner | −8069 [−10910, −4790] ticks | **supported** |
| H55c: foster-genome and stranger populations differ in extinction | +0.08 [−0.25, 0.42] | no difference detected |

**By the pre-registered rule (H55a and H55b supported), the protection
works through who carries which genome beside the parent.** This is the first
intervention in eleven studies that removed it.

| condition | extinct | mean survival | final population | max generation | aggression gene |
|---|---|---|---|---|---|
| beside parent, own genome | 4/12 | 16939 | 24.0 | 20.5 | 1.38 |
| beside parent, stranger's genome | 10/12 | 8870 | 4.6 | 4.8 | 1.13 |
| beside a stranger, own genome | 9/12 | 14284 | 8.8 | 7.2 | 0.77 |

Fisher exact (two-sided, not pre-registered): foster vs parent p = 0.036;
stranger vs parent p = 0.10 (the stranger effect is smaller than usual in
this sample; pooled over eleven studies it is 119/132 vs 47/132); foster vs
stranger p = 1.0.

## Interpretation

- **Protection needs the newborn to carry its parent's genome and to start
  beside the parent.** Breaking either link gives about the stranger outcome:
  - own genome, placed beside a stranger: 9/12 extinct
  - stranger's genome, placed beside the parent: 10/12
- **Foster-genome populations died fastest** (mean survival 8870 ticks) and
  reached only about 5 generations.
- **Two accounts fit, and AI cannot tell them apart.**
  1. *Genomes clustered in space.* Each family's genome stays together in
     one place, so families compete as units. This is multilevel or
     kin-structured selection in a viscous population.
  2. *Selection switched off.* A foster genome comes from a random agent,
     which need not have reproduced. Offspring then no longer carry the
     genome of the agent whose success produced them, so selection on
     genomes is largely removed.

  The stranger condition keeps selection intact and still fails. That
  argues against account 2 alone, but does not rule out that both matter.

## Limits

- 12 seeds per condition. The parent and stranger extinction counts in this
  sample (4/12 vs 9/12) are closer than in most earlier studies.
- `birth_fallback_frac` was 4% in the foster condition (no unrelated agent
  alive, so the parent's genome was used).

## Next step

Separate the two accounts. Keep selection but break the family–place link.
The newborn stays beside its parent but inherits the genome of a different
agent that has itself just reproduced (a successful donor). If the
protection returns, account 2 (selection) was the cause. If it stays lost,
genomes must cluster with their family in space.

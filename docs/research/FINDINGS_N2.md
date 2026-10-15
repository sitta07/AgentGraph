# Findings: Experiment N2 — Lamarckian inheritance kills populations; a per-state critic does not save them

**Status:** completed 2026-10-16. 36 runs: 3 conditions × 12 seeds
(1300–1311, never run before) × 12000 ticks. Viscous, static world, learning
on. Pre-registered at commit `f5bde9b`, spec unchanged, no deviations.
Report:
[`results/N2_lamarck_bias_compounding/`](../../results/N2_lamarck_bias_compounding/REPORT.md).

**Design.**
- `darwin`: offspring inherit the parent's inborn weights.
- `lamarck`: offspring inherit the parent's learned weights (scalar critic).
- `lamarck_state`: Lamarckian, with the per-state critic from R.

| Hypothesis | Test (a − b) | Result |
|---|---|---|
| H28a: Lamarckian populations die out sooner | −5685 [−8043, −3039] ticks | **supported** |
| H28b: … go extinct more often | +0.67 [0.25, 1.0] | **supported** (9/12 vs 1/12, Fisher p = 0.003) |
| H28c: inherited wiring shifts toward sharing | +0.14 [0.07, 0.21] | **supported**, but on only 3 surviving pairs |
| H28d: state critic lets Lamarckian populations survive longer | +911 [−1970, 3888] ticks | not supported (also 9/12 extinct) |
| H28e: state critic reduces the inherited shift | no data | no seed had both Lamarckian conditions surviving |

## Interpretation

- **The post-hoc result from N replicates on fresh seeds and as a
  pre-registered test.** N had 9/16 vs 2/16 extinctions, and N2 has 9/12 vs
  1/12. Median survival was 4940 ticks for Lamarckian populations, while 11/12
  Darwinian populations lasted the full 12000.
- **Lamarckian populations boom first.** The early birth rate was about 3×
  the Darwinian rate (0.0102 vs 0.0035 mean, ticks 0–6000). The surviving
  Lamarckian populations reached 47–82 generations against 12–40. Surviving
  populations attacked on about 41% of ticks, against 15% for Darwinian ones.
- **The per-state critic did not prevent the collapse** (9/12 extinct, as
  with the scalar critic). So the bias that R removes within a lifetime is
  not, on its own, what kills Lamarckian populations. Something else about
  inheriting learned weights does. One candidate: offspring start from
  weights tuned to the parent's last situation, and the population converges
  quickly. That is untested.
- **Two of the three surviving `lamarck_state` populations were very
  different.**
  - Killings made up 11% of early deaths, against 58–80% everywhere else.
  - Attacks were about 2% of ticks.
  - Food per agent-tick was 0.060–0.061, the highest of any condition so far
    (no-learning in R: 0.050).
  - This was not predicted and comes from 2 runs. It suggests Lamarckian
    inheritance plus a better critic can sometimes lock in a peaceful,
    efficient foraging strategy, and otherwise collapses. Worth a dedicated
    test.

## Limits

- H28c compares only the 3 seeds where both `darwin` and `lamarck`
  survived. Surviving Lamarckian populations are a selected subset, so the
  share-gene difference may reflect survivor bias.
- H28e has no data: the survivors of the two Lamarckian conditions were on
  different seeds. The registered paired design did not anticipate that
  much extinction.
- In this simulator, Lamarckian inheritance copies all plastic weights,
  including drifts that would not normally be heritable. The comparison is
  between inheritance rules in this model, not a claim about biology.

## Next step

Test whether the peaceful high-food outcome in `lamarck_state` recurs. Use
more seeds and record the attack rate and food rate over time, to see when a
run commits to one outcome or the other.

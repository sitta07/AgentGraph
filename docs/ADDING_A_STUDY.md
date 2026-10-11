# Adding your own study

Anyone can add a pre-registered study without touching the simulator.

## 1. Write a spec

Create `studies/<ID>.json`. Use the structure of this repository's own specs
as a template, for example
[`studies/E_baldwin_vs_hiding.json`](../studies/E_baldwin_vs_hiding.json).

| Field | Meaning |
|---|---|
| `id` | folder name for results (`results/<id>/`) |
| `title`, `question`, `background` | shown in the Discovery Lab and the report |
| `simulator` | `"evolution"`: evolving populations of spiking agents |
| `seeds`, `ticks` | replicate runs per condition and the length of each run |
| `base` | any `WorldConfig` fields shared by all conditions (see `neuralmind/world.py`) |
| `conditions` | `{name: {"config": {...}, "learning": true/false}}` |
| `hypotheses` | list of `{id, statement, metric, a, b, direction}` |

`direction` is the decision rule on the paired difference *a − b*. Every
condition uses the same seeds, so differences are paired.

- `greater`: supported if the 95% bootstrap CI lies above 0.
- `less`: supported if the CI lies below 0.
- `none`: "no difference detected" if the CI contains 0. This is weak
  evidence and is reported as such.

**Metrics available** are any numeric output of
`neuralmind.research.evolution.run_evolution`. They are measured over the
final 25% of each run:

| Group | Metrics |
|---|---|
| Population | `final_pop`, `max_generation`, `births` |
| Heritable traits | `aggr_gene` (aggression gain), `share_gene` (innate share drive) |
| Innate ability | `innate_foraging`: food eaten by evolved genomes alone, with learning off |
| Behaviour rates | `share_rate`, `attack_rate` |
| Encounter-conditioned rates | `share_given_encounter`, `attack_given_encounter`, `encounter_rate` |
| Kin structure | `share_to_kin`, `encounter_kin` |
| Distances | `share_dist`, `enc_dist`, `enc_dist_kin`, `enc_dist_nonkin` |
| Signal meaning | `mi_signal_food`, `mi_signal_threat`, `mi_signal_hunger`, `mi_heard_action` (bits), and their `p_*` G-test values |

## 2. Register it (commit before running)

```bash
python -c "from neuralmind.research.spec import load; load('studies/<ID>.json')"   # validate
git add studies/<ID>.json && git commit -m "register study <ID>"
```

The runner records this commit. If the spec changes after the commit, the
study is shown as **not** pre-registered.

## 3. Run it

```bash
python -m neuralmind.research.spec studies/<ID>.json
```

You can also open **Discovery Lab → Registered studies → Run as registered**.
Results go to `results/<ID>/`: `REPORT.md`, `results.json` with raw per-run
data, and SVG charts. Using `--seeds` or `--ticks` to change the design is
allowed, but it is recorded as a deviation.

## 4. Report honestly

- Commit the results whatever they show.
- Write the interpretation in `docs/research/`. Separate pre-registered tests
  from post-hoc explanations.
- If something surprising appears, register a follow-up instead of moving the
  goalposts.

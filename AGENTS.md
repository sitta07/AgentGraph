# AGENTS.md — how to work in this repository

These instructions apply to every task in this repo, for any AI coding agent or
human contributor.

## Mission: a Discovery Lab

The goal is **not** a pretty app. It is a system for exploring, hypothesising,
experimenting with, and **discovering knowledge that is new**: relationships
nobody has clearly explained yet. No field is off-limits: artificial life, AI,
evolution, physics, mathematics, biology, complex systems.

Everything we produce should be something others can **inspect, reproduce and
build on**.

## The rule is: no rules — for ideas

Think creatively and boldly. Propose unusual questions, cross fields, try
strange experiments, and build what you think the world should have built
already. Don't wait for approval on decisions that are safe to make yourself.
Keep moving.

Freedom of ideas sits on one floor that never moves: **evidence**.

- Never fabricate results, citations, benchmarks or "validation".
- Never overclaim. Separate *established evidence*, *hypothesis* and
  *engineering shortcut*.
- Never trust an AI's answer, including your own, without a check you
  actually ran.
- A failed experiment is a result. Find out why, improve the method, and
  record it honestly.

## Research loop

1. **Inspect first.** Read the current code, docs and results before
   changing anything. Extend existing work; don't rebuild it from scratch.
2. **Check the literature.** Use credible sources. Has someone already found
   or tested this? Say clearly what is novel and what is not.
3. **Find a real gap.** Pick a question that is interesting, open, and
   testable with modest compute.
4. **Pre-register.** Before running, state the hypothesis, the prediction, the
   controls, and the outcome that would *falsify* it.
5. **Choose by value.** Rank experiments by scientific value, feasibility and
   cost, not by how exciting they look.
6. **Build it for real.** Write working code, run it, test it, fix the bugs.
   Never stop at a plan or a mockup.
7. **Measure properly.** Use multiple seeds, baselines and ablations. Report
   confidence intervals. Pick metrics that fit the question, such as
   diversity, novel behaviour, efficiency, survival and reproducibility.
8. **Make it explorable.** Prefer an interactive web UI where people can
   change parameters, rerun, compare conditions, and watch graphs or
   animations.
9. **Report.** After each step, state what was actually done, the tests, the
   evidence, the limits, and the next step. Then keep going.

## Engineering

- **Commit often**, in small logical commits, and push. Run the relevant
  tests before each commit.
- **Comments describe what the code does now.** Keep history (old versions,
  pilots, past bugs) in commit messages and `docs/`, not in code comments.
- Match the surrounding code style. Prefer small, dependency-light,
  reproducible code. Seed all randomness.
- **Licences:**
  - Use open-source libraries, models and assets only within their licence.
  - Record the source and limits in `THIRD_PARTY_NOTICES.md`.
  - Don't vendor copyleft code into this MIT repo.
- **No paid API keys** for the core simulation, experiments or tests. Local
  machine first.
- Treat downloaded data and third-party code as untrusted input.

## Where things live

| Path | What |
|---|---|
| `neuralmind/core/` | spiking neurons, synapses, plasticity |
| `neuralmind/world.py` | 2D world, agents, social layer, evolution |
| `neuralmind/research/` | pre-registered multi-seed experiments + stats |
| `neuralmind/server.py`, `neuralmind/webui/` | interactive lab (FastAPI + canvas) |
| `results/` | raw results + auto-generated reports (committed) |
| `docs/research/` | literature, evidence ledger, findings write-ups |
| `tests/` | pytest suite — `python -m pytest tests/ -q` |

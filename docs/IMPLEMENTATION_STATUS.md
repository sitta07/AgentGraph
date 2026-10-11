# NeuralMind — Implementation Status

**Updated:** 2026-10-11
**Branch:** `feat/neuralmind-core`
**Current state:** Phases 0–6 substantially complete. All 15 acceptance criteria
in the brief are met for the baseline platform. Remaining work is depth
(more engines, larger networks, richer UI) rather than missing capability.

## 1. What works now (executed and tested this session)
- **Neural core** (`neuralmind/core/`): vectorised LIF populations, current-based
  synapses with one-step delay, pair-based STDP with optional eligibility traces,
  `SpikingNetwork` orchestrator. NumPy-only, deterministic from a seed.
- **Affect layer** (`neuralmind/affect/`): TD(0) `RewardPredictor` (RPE) and a
  bounded `AffectState` (valence/arousal/threat/frustration/motivation).
- **Experiments** (`neuralmind/experiments/`): `reward_learning` (baseline
  ~0.5 → learned ~0.8–0.95), `threat_avoidance` (paired ≫ unpaired),
  `pain_response` (monotonic dose-response + recovery), `forgetting`
  (retroactive/catastrophic interference via synaptic scaling).
- **Persistence** (`neuralmind/persistence/`): SQLite save/reload/list of runs.
- **Knowledge** (`neuralmind/knowledge/`): stdlib TF-IDF document index with
  traceable source citations (Subsystem B).
- **Recorder + viewer** (`neuralmind/recorder.py`, `viz.py`): records real
  simulation state and renders a dependency-free interactive HTML viewer
  (spike raster, rates, affect, play/step/timeline). Verified in a browser.
- **Benchmark** (`neuralmind/bench.py`): real runtime + peak-memory numbers.
- **CLI** (`neuralmind/cli.py`): `list`, `run`, `runs`, `show`, `search`,
  `visualize`. Fully offline.

## 2. Commands actually executed
```
git clone https://github.com/sitta07/AgentGraph.git
git checkout -b feat/neuralmind-core
python3 -m venv .venv && pip install numpy pytest     # numpy 2.5.4, pytest 9.1.1
python -m pytest tests/ -q                             # 55 passed
python -m neuralmind.cli run reward_learning --seed 0 --save
python -m neuralmind.cli search "spike timing dependent plasticity"
python -m neuralmind.cli visualize --steps 450 --seed 0 --out examples/neuralmind_viewer.html
python -m neuralmind.bench --sizes 50 100 200 400 --steps 500
```
The viewer was opened and scrubbed in a real browser (Playwright) to confirm
rendered values match the recorded simulation state.

## 3. Tests — 55 passing (~3 s)
`test_neurons` (9), `test_plasticity` (4), `test_network` (7), `test_affect` (9),
`test_experiments` (5), `test_experiments_extra` (5), `test_persistence` (4),
`test_knowledge` (6), `test_bench` (2), `test_recorder_viz` (4).

## 4. Benchmarks / measurements (dev machine, Apple Silicon, Python 3.14)
- Static recurrent net: ~18k–30k steps/s for n=50–400 (10% connectivity).
- Plastic (STDP) net: ~6k–15k steps/s for n=50–200; peak memory < 1 MB.
- Full test suite ~3 s.

## 5. Research sources inspected
`docs/research/RESEARCH_REPORT.md` (with an honesty note on inspection depth —
web docs/metadata, not full clones), `REUSE_MATRIX.md`, `SCIENTIFIC_EVIDENCE.md`,
`THIRD_PARTY_NOTICES.md`. Verified: TVB=GPLv3, Brian2=CeCILL-2.1, NEST=GPLv2+.

## 6. Known limitations
- Simplified LIF/point-neuron model; no morphology, no GPU, no large-scale
  connectome yet. Big engines (TVB/Brian2/NEST) are reference-only.
- Engine adapters (ADR-0004) are a defined seam, not yet implemented.
- Affect variables are hand-tuned illustrative constructs, not calibrated.
- `forgetting` shows near-catastrophic interference (documented, not a bug).
- Viewer is a playback tool, not yet a live parameter-editing UI.

## 7. Acceptance criteria — 15/15 met for the baseline
- [x] 1 Clean install runs the basic simulation locally
- [x] 2 Core requires no paid API key
- [x] 3 State changes come from documented dynamics
- [x] 4 Reproducible runs with fixed seeds
- [x] 5 Learning measured against a baseline
- [x] 6 Memory retrieval returns traceable source references (knowledge index)
- [x] 7 Saved experiments reload and inspect
- [x] 8 UI values reflect actual simulation state (recorder + viewer)
- [x] 9 Numerical stability / invalid-parameter handling tested
- [x] 10 Tests cover core equations and state transitions
- [x] 11 Performance benchmarks report runtime and memory
- [x] 12 Distinguishes evidence / hypothesis / abstraction
- [x] 13 License and attribution satisfied
- [x] 14 New user can run a documented experiment from the README alone
- [x] 15 No fabricated results/validation claims

## 8. Next concrete tasks (depth, priority order)
1. **Engine adapter** implementing the `SpikingNetwork` interface over Brian2
   (optional dependency) to validate the core against a mature simulator.
2. **Social-attachment experiment** (brief's Experiment 4) and a
   **memory-under-stress** experiment (Experiment 5), both exploratory.
3. **Ablation harness**: toggle mechanisms (WTA, eligibility, scaling) and
   report their effect on each experiment's metric.
4. **Live UI**: parameter editing + re-run from the browser (Subsystem C can
   wire the existing LLM app to the simulation API).
5. **Insect-connectome demo** using a public dataset (verify license first).

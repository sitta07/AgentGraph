# NeuralMind — Implementation Status

**Updated:** 2026-10-11
**Branch:** `feat/neuralmind-core`
**Current phase:** Phases 0–3 complete; Phase 4 partially (affect layer + two
affect-related experiments done); Phases 5–7 pending.

## 1. What works now (executed and tested this session)
- **Neural core** (`neuralmind/core/`): vectorised LIF populations, current-based
  synapses with one-step delay, pair-based STDP with optional eligibility traces,
  and a `SpikingNetwork` orchestrator. NumPy-only, deterministic from a seed.
- **Affect layer** (`neuralmind/affect/`): TD(0) `RewardPredictor` producing a
  reward prediction error; bounded `AffectState`
  (valence/arousal/threat/frustration/motivation) with documented update rules.
- **Experiments** (`neuralmind/experiments/`):
  - `reward_learning` — reward-modulated STDP + soft winner-take-all. Baseline
    (no learning) ≈ 0.43–0.57 selection; with learning ≈ 0.77–0.97 toward the
    rewarded action across seeds 0–2 and both rewarded actions.
  - `threat_avoidance` — Pavlovian CS→US pairing. Paired associative gain ≫
    unpaired control; weights grow only in the paired case.
- **Persistence** (`neuralmind/persistence/`): SQLite store; save/reload/list
  experiment runs with full config+metrics+series+notes.
- **CLI** (`neuralmind/cli.py`): `list`, `run`, `runs`, `show`. Runs offline.

## 2. Commands actually executed
```
git clone https://github.com/sitta07/AgentGraph.git
git checkout -b feat/neuralmind-core
python3 -m venv .venv && pip install numpy pytest   # numpy 2.5.4, pytest 9.1.1
python -m pytest tests/ -q                           # 38 passed
python -m neuralmind.cli list
python -m neuralmind.cli run reward_learning --seed 0 --save --db /tmp/nm_test.sqlite
python -m neuralmind.cli runs --db /tmp/nm_test.sqlite
```

## 3. Tests — 38 passing
- `test_neurons.py` (9): rest, sub/supra-threshold, refractory limit, monotone
  f–I curve, determinism, stability guard, parameter/shape validation.
- `test_plasticity.py` (4): pre→post potentiation, post→pre depression, weight
  bounds, reward-modulator sign flip.
- `test_network.py` (7): dt/shape/unknown-population validation, transmission,
  silence, determinism, reset.
- `test_affect.py` (9): RPE sign/convergence, affect valence/threat/pain/
  frustration behaviour, bounds, param validation.
- `test_experiments.py` (5): learning beats baseline (both actions),
  determinism, paired > unpaired threat, affect read-out.
- `test_persistence.py` (4): round-trip, ordering, missing row, reopen.

## 4. Benchmarks / measurements
- Full test suite runs in ~2 s on the dev machine (Apple Silicon, Python 3.14).
- Not yet: a dedicated benchmark harness reporting runtime/memory per network
  size (planned, Phase 6, acceptance criterion 11).

## 5. Research sources inspected
See `docs/research/RESEARCH_REPORT.md` (honesty note on inspection depth),
`REUSE_MATRIX.md`, `SCIENTIFIC_EVIDENCE.md`. License decisions in
`THIRD_PARTY_NOTICES.md`. Verified: TVB=GPLv3, Brian2=CeCILL-2.1, NEST=GPLv2+.

## 6. Known limitations
- Core is a deliberately simplified LIF/point-neuron model (see SCIENTIFIC_EVIDENCE).
- No GPU, no large-scale/connectome networks yet; big engines are reference-only.
- Affect variables are hand-tuned illustrative constructs, not calibrated.
- No visualization UI yet; no document/knowledge subsystem (Subsystem B) yet.
- No engine adapters implemented (seam defined in ADR-0004).

## 7. Definition of done (acceptance criteria tracking)
- [x] 1 Clean install runs the basic simulation locally
- [x] 2 Core requires no paid API key
- [x] 3 State changes come from documented dynamics
- [x] 4 Reproducible runs with fixed seeds
- [x] 5 Learning measured against a baseline
- [ ] 6 Memory retrieval returns traceable source references (Subsystem B pending)
- [x] 7 Saved experiments reload and inspect
- [ ] 8 UI values reflect actual simulation state (no UI yet)
- [x] 9 Numerical stability / invalid-parameter handling tested
- [x] 10 Tests cover core equations and state transitions
- [ ] 11 Performance benchmarks report runtime and memory
- [x] 12 Distinguishes evidence / hypothesis / abstraction (SCIENTIFIC_EVIDENCE)
- [x] 13 License and attribution satisfied (THIRD_PARTY_NOTICES)
- [ ] 14 New user can run a documented experiment from the README alone (README pending)
- [x] 15 No fabricated results/validation claims

## 8. Next concrete tasks (priority order)
1. **Benchmark harness** (`neuralmind/bench.py`) → criterion 11.
2. **README / NeuralMind quickstart** so a new user can run an experiment →
   criterion 14.
3. **More experiments**: pain-related input, forgetting/interference (exploratory).
4. **Subsystem B** (document/knowledge index with traceable sources) → criterion 6.
5. **Visualization** (spike raster, weight/affect time series) → Phase 5, criterion 8.

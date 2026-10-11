# Architecture Decision Records (ADRs)

Lightweight ADRs for NeuralMind. Status: Accepted unless noted.

## ADR-0001 — Preserve AgentGraph; build NeuralMind alongside it
**Context.** The repo is an MIT-licensed LLM orchestration app (LangGraph +
Streamlit + Novita/Llama). It has no neural-simulation core but is working code.
**Decision.** Do not delete or rewrite it. Add a new `neuralmind/` Python package
and `tests/` beside the existing files. The old app can later become optional
**Subsystem C** (language interface) over the simulation API.
**Consequences.** Clean git history; no loss of user work; two subsystems
coexist. Work proceeds on branch `feat/neuralmind-core`.

## ADR-0002 — NumPy-only LIF/STDP simulation core for the baseline
**Context.** Acceptance criteria demand a local, no-API-key, reproducible core
on an ordinary machine. Mature engines (Brian2 CeCILL-2.1, NEST GPLv2+, TVB
GPLv3) are copyleft and/or need a C++ build toolchain (see REUSE_MATRIX).
**Decision.** Implement a transparent, audited LIF + synapse + STDP engine using
only **NumPy** (BSD-3). Keep it small and fully unit-tested.
**Consequences.** Zero-build install, MIT-compatible, easy to inspect for a
*learning* platform. We forgo the maturity/scale of the big engines for the
default path — mitigated by ADR-0004.

## ADR-0003 — Deterministic, seeded, time-stepped simulation
**Context.** Reproducibility is a hard requirement (criterion 4).
**Decision.** All stochasticity flows through `numpy.random.default_rng(seed)`.
Fixed `dt`, forward-Euler, one-step synaptic transmission delay so update order
cannot affect results. `reset()` restores state while preserving weights.
**Consequences.** Byte-identical reruns given a seed (tested). Forward-Euler
accuracy is bounded by a `dt <= tau_m` guard.

## ADR-0004 — Engine-adapter seam for future back-ends
**Context.** We want Brian2/NEST/TVB to be addable later "without rewriting the
application", and licenses require them to stay optional, separately-installed.
**Decision.** Experiments depend on the `SpikingNetwork` interface
(`add_population`, `connect`, `step`, `apply_reward`, `reset`), not on internals.
A future `neuralmind/engines/` package can provide adapters that satisfy the
same interface by delegating to Brian2/NEST/TVB when the user has them installed.
**Consequences.** The copyleft engines remain optional dependencies (no
vendoring). Status: **Accepted (seam defined; adapters not yet implemented).**

## ADR-0005 — Three-factor learning via eligibility traces
**Context.** Reward arrives at the *end* of a trial, after the spikes that earned
it; immediate STDP cannot assign that delayed credit.
**Decision.** STDP optionally accumulates changes into a decaying **eligibility
trace**; `network.apply_reward(modulator)` converts eligibility into a weight
change. The modulator is a TD(0) reward prediction error.
**Consequences.** Biologically-motivated credit assignment; matches the
Frémaux & Gerstner (2016) framing. Immediate-mode STDP is retained for Hebbian
experiments (e.g. threat conditioning).

## ADR-0006 — Competition (soft winner-take-all) for action selection
**Context.** With independent, equally-weighted action pathways, a global reward
signal strengthens all pathways equally and never breaks symmetry.
**Decision.** Action populations inhibit each other (lateral inhibition). The
winner fires and suppresses the loser, so the eligibility trace is concentrated
on the *chosen* pathway, which reward can then specifically reinforce.
**Consequences.** Reward learning rises from a ~0.5 chance baseline to ~0.8–0.95
selection of the rewarded action (tested across seeds and both actions).

## ADR-0007 — Separate the kinds of "memory" explicitly
**Context.** The brief warns against conflating vector similarity with biological
memory.
**Decision.** Keep four distinct stores: (1) **learned synaptic weights** (in the
network), (2) **simulation state** (membrane/traces, transient), (3)
**experiment history** (SQLite via `persistence.ExperimentStore`), and (4) a
future **document/knowledge index** (Subsystem B, not yet built). Each is named
and documented separately.
**Consequences.** No category confusion; the SQLite store holds *records about*
runs, never claims to be biological memory.

## ADR-0008 — Standard-library persistence (SQLite + JSON)
**Context.** Experiments must be saveable/reloadable with no external service.
**Decision.** Use stdlib `sqlite3` + `json`. One `runs` table; config/metrics/
series/notes stored as JSON.
**Consequences.** Zero extra dependencies; portable single-file DB. A richer
store (vector/graph DB for Subsystem B) can be added later without changing the
experiment API.

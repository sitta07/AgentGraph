# NeuralMind — Research Report

**Date:** 2026-10-11
**Phase:** 1 (source research) — informing the architecture decision in
[`../architecture/ARCHITECTURE_DECISIONS.md`](../architecture/ARCHITECTURE_DECISIONS.md).

## Honesty note on inspection method

This report was produced under a constraint that must be stated plainly: the
large scientific simulators below were inspected via **web search of their
official documentation, package registries, and license metadata**, combined
with prior engineering knowledge of these tools. **Full source clones and local
example runs of TVB, Brian2, NEST, and FlyBrainLab were NOT performed** in this
session (repository size, build toolchains such as C++/Cython, and network/time
constraints). Where a claim could not be verified from an inspected source, it
is labelled as such rather than asserted. This directly follows the project
rule: *"If a candidate cannot be inspected because network access is
unavailable, record that limitation instead of pretending it was reviewed."*

What **was** executed locally in this session is the NeuralMind code in this
repository: see [`../IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md) for
the exact commands and test results.

## Starting point (verified against source)

The original `AgentGraph` repository (branch `main`) is a **multi-agent LLM
application** — not a neural simulator. Verified by reading the source:

- `app.py` (442 LOC) — Streamlit UI.
- `main.py`, `src/graph/{nodes,state}.py` — a LangGraph state machine wiring
  four LLM "agents" (Architect, Security, Evaluator, Mermaid validator).
- `src/prompts/*` — prompt registry; `src/utils/*` — convergence/cost helpers.
- `requirements.txt` — `langgraph`, `langchain-*`, `streamlit`, `pydantic`.
- It calls **Meta Llama 3.3 70B via the Novita API** and therefore **requires a
  paid API key** to do anything. It stores no explicit numerical state.

Conclusion: AgentGraph is a useful *language-interface / orchestration* codebase
(maps onto optional Subsystem C) but contains **no** reusable neural-simulation
core. It is preserved untouched; NeuralMind is added alongside it.

## Candidate engines (see REUSE_MATRIX.md for the decision table)

### A. Whole-brain / neural-mass simulation
- **The Virtual Brain (TVB)** — `github.com/the-virtual-brain/tvb-root`.
  Large-scale brain-network simulator using **neural mass models** over a
  connectome (regions = nodes, tractography = weighted/delayed edges); outputs
  firing rate, LFP, and forward models for EEG/MEG/BOLD. **License: GPLv3**
  (some bundled third-party packages differ). Mature, actively maintained.
  Heavy dependency footprint.
- **FlyBrainLab** — `github.com/FlyBrainLab/FlyBrainLab`. An **interactive 3-D
  exploration/visualization + executable-circuit** platform for the *Drosophila*
  connectome, not a general numerical SNN engine. Open source; exact license
  **not confirmed** from inspected sources (check its `LICENSE`).

### B. Spiking neural network engines
- **Brian2** — `github.com/brian-team/brian2`. Clock-driven SNN simulator;
  models (incl. LIF) and plasticity (incl. STDP) are specified as **equations in
  strings** and code-generated/compiled. **License: CeCILL 2.1** (a
  French GPL-compatible copyleft license). Mature, well-documented, pip-installable.
- **NEST** — `github.com/nest/nest-simulator`. Large-scale **point-neuron** SNN
  kernel in C++ with a Python interface (PyNEST). Focuses on network dynamics,
  size and structure. **License: GPLv2-or-later** (some bundled MIT/LGPL parts).
  Requires a C++ build toolchain.

### C. Learning / memory / affect — literature (not a single library)
Mechanisms were researched from the primary literature and are cited in
[`SCIENTIFIC_EVIDENCE.md`](SCIENTIFIC_EVIDENCE.md): pair-based STDP (Bi & Poo
1998; Song, Miller & Abbott 2000), three-factor / reward-modulated plasticity
(Izhikevich 2007; Frémaux & Gerstner 2016), TD learning and the dopamine-RPE
hypothesis (Sutton & Barto 2018; Schultz, Dayan & Montague 1997), the
circumplex model of core affect (Russell 1980), and threat conditioning
(LeDoux 2000).

## Key finding driving the architecture

Both practical SNN engines that could host NeuralMind's mechanisms (**Brian2,
NEST**) and the whole-brain option (**TVB**) are **copyleft** (CeCILL 2.1 /
GPLv2+/GPLv3). The existing repository is **MIT**. Shipping a *local-first,
MIT-licensed, zero-build, no-API-key* baseline that merely imports these engines
would either (a) force a heavier install + build toolchain (NEST), or (b) raise
redistribution/compatibility questions if their code were vendored.

**Decision (detailed in ARCHITECTURE_DECISIONS.md):** build a small, transparent
**NumPy-only LIF/STDP core** (ADR-0002) that any machine can run, and design an
**engine-adapter boundary** (ADR-0004) so Brian2/NEST/TVB can be added later as
optional, separately-licensed back-ends for users who install them. This
respects the licenses (we depend on / interoperate rather than vendor) and keeps
the default experience lightweight and reproducible.

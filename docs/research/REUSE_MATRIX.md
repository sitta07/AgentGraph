# NeuralMind — Reuse Matrix

For each candidate: what it is, license, inspection depth **in this session**,
whether it runs locally without special toolchains, and the final decision.

Inspection legend: **doc** = official docs/registry/license metadata read via
web search; **src** = source files read; **run** = examples executed locally.

| Candidate | Role | License | Inspected | Local run w/o build toolchain | Decision |
|---|---|---|---|---|---|
| AgentGraph (this repo) | LLM orchestration UI | MIT | src | Yes (needs Novita API key) | **Keep as-is**; maps to optional Subsystem C (language interface). No neural core to reuse. |
| The Virtual Brain (TVB) | Whole-brain neural-mass sim | GPLv3 (+3rd-party) | doc | Partial (heavy deps) | **Reference only** now; candidate future **optional back-end** via adapter. Copyleft → do not vendor into MIT core. |
| Brian2 | Clock-driven SNN (equations) | CeCILL 2.1 | doc | Yes (pip) | **Reference now**; strong candidate **optional dependency** behind the engine adapter (ADR-0004). Copyleft → optional, not bundled. |
| NEST | Large-scale point-neuron SNN | GPLv2-or-later | doc | No (needs C++ build) | **Reference only**; possible future adapter for large networks. Build toolchain conflicts with zero-install goal. |
| FlyBrainLab | 3-D connectome explorer | Unconfirmed | doc | Unknown | **Reference only**; relevant to a *future* insect-connectome demo + visualization. Confirm license before any use. |
| NumPy | Numerical core | BSD-3-Clause | src+run | Yes | **Integrate (dependency)**. Permissive; already the basis of the implemented core. |
| SciPy | Numerics (optional) | BSD-3-Clause | doc | Yes | **Adopt only if needed** (not required by the current core). |
| pytest | Testing | MIT | run | Yes | **Integrate (dev dependency)**. |
| Matplotlib / Plotly | Plotting | PSF-like / MIT | doc | Yes | **Defer** to the visualization phase (Phase 5). |

## Rationale for building a small core rather than adopting an engine wholesale

1. **License fit.** TVB (GPLv3), NEST (GPLv2+), Brian2 (CeCILL 2.1) are all
   copyleft; the repo is MIT. Depending on them *optionally* is fine; vendoring
   their code into an MIT package is not. A clean-room NumPy core avoids the
   question entirely for the default install.
2. **Local-first / zero-build.** NEST needs a C++ toolchain; TVB pulls a heavy
   dependency tree. A NumPy-only core runs on "an ordinary developer machine"
   with `pip install numpy`, satisfying acceptance criterion 1.
3. **Interpretability for a *learning* platform.** The scientific value here is
   transparent, inspectable dynamics and plasticity, which a ~200-line audited
   core gives directly.
4. **Not reinventing numerics.** We reuse **NumPy** (BSD) for all vectorised
   math rather than writing our own linear-algebra/RNG layer.
5. **Future-proofing.** ADR-0004 defines an engine-adapter seam so Brian2/NEST/
   TVB can be plugged in later for users who install them, without rewriting the
   experiments or persistence layers.

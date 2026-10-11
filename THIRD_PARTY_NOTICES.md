# Third-Party Notices

NeuralMind is distributed under the MIT License (see `LICENSE`). It currently
**bundles no third-party source code**. This file records the external projects
it depends on at runtime/dev time, and projects studied for reference whose
licenses would govern any future integration.

## Runtime / development dependencies (installed via pip, not vendored)

| Project | Version pin | License | Use |
|---|---|---|---|
| NumPy | see `requirements-neuralmind.txt` | BSD-3-Clause | All numerical arrays/RNG in the simulation core |
| pytest | dev only | MIT | Test runner |

These are permissively licensed and are **not** redistributed as part of this
repository; users install them themselves.

## Reference-only projects (studied, NOT integrated or copied)

The following were researched (documentation/metadata) to inform the design but
**no code from them is included** in this repository. If any is integrated in
the future (e.g. as an optional engine adapter, see ADR-0004), its license below
governs that use and this notice must be updated accordingly.

| Project | License | Repository |
|---|---|---|
| The Virtual Brain (tvb-root) | GPL-3.0-or-later (some bundled parts differ) | https://github.com/the-virtual-brain/tvb-root |
| Brian2 | CeCILL 2.1 | https://github.com/brian-team/brian2 |
| NEST simulator | GPL-2.0-or-later (some bundled MIT/LGPL parts) | https://github.com/nest/nest-simulator |
| FlyBrainLab | License not confirmed at time of writing — verify before any use | https://github.com/FlyBrainLab/FlyBrainLab |

> Note on copyleft: TVB, Brian2, and NEST are copyleft. They may be used as
> **optional, separately-installed dependencies**. Their source must **not** be
> copied into this MIT-licensed repository. See
> `docs/architecture/ARCHITECTURE_DECISIONS.md` (ADR-0002, ADR-0004).

## Original project

The pre-existing AgentGraph application (LangGraph/LangChain/Streamlit based) is
retained under this repository's MIT License. Its own Python dependencies are
declared in `requirements.txt` and carry their respective upstream licenses.

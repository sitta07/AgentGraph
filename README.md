<h1 align="center">🧠 NeuralMind — an open Artificial-Life Lab</h1>

<p align="center">
  <b>Pixel-art creatures whose brains are real spiking neural networks.</b><br>
  They forage, learn, fight, share, signal, reproduce and evolve.<br>
  You can watch every neuron, run pre-registered experiments, and plug in your own RL agents.
</p>

<p align="center">
  <a href="https://github.com/sitta07/NeuralMind/actions/workflows/tests.yml"><img src="https://github.com/sitta07/NeuralMind/actions/workflows/tests.yml/badge.svg" alt="tests"></a>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.13-blue" alt="python">
  <img src="https://img.shields.io/badge/PettingZoo-ParallelEnv-8a5cf6" alt="PettingZoo">
  <img src="https://img.shields.io/badge/GPU-not%20needed-lightgrey" alt="no GPU">
  <img src="https://img.shields.io/badge/API%20key-not%20needed-lightgrey" alt="no API key">
</p>

<p align="center">
  <img src="docs/media/evolution_world.gif" width="440" alt="An evolving population of spiking-neural agents: births, attacks, sharing and signals">
  &nbsp;
  <img src="docs/media/brain_scanner.gif" width="300" alt="Brain scanner: one agent's spiking network and its action competition, live">
</p>
<p align="center"><sub>
  ① An evolving population, recorded from the app. Families share a sprite; 😠 marks a
  frustration-driven aggression drive and 😫 marks hunger. ② One individual's brain, live.
  The action population that fires most is the move it makes — the network chooses, not a rule.
</sub></p>

---

## 🔓 Open for you to build on

NeuralMind is **MIT-licensed**. It is designed to be forked, extended and cited:

| You want to… | Use |
|---|---|
| **Test a MARL algorithm** in a rich social world | the **PettingZoo `ParallelEnv`** (passes the official API test). RL agents can live *alongside* spiking-brain agents. |
| **Ask a new scientific question** without writing simulator code | a **declarative study spec** (`studies/*.json`): commit it, then run it. The commit hash is your pre-registration. → [`docs/ADDING_A_STUDY.md`](docs/ADDING_A_STUDY.md) |
| **Check or extend our results** | the committed raw data in [`results/`](results/) and auto-generated reports with bootstrap CIs |
| **Teach** neurons, plasticity, reinforcement learning or evolution | the interactive Playground: click any creature to see its brain |
| **Build on the engine** | small, dependency-light NumPy code with 118+ tests and CI |

If you use it in research, please cite it ([`CITATION.cff`](CITATION.cff)). PRs
and new studies are welcome; see [`CONTRIBUTING.md`](CONTRIBUTING.md).

> **What this is:** a computational model with explicitly defined mechanisms:
> leaky integrate-and-fire neurons, reward-modulated plasticity, reward
> prediction error, and bounded affect variables.
>
> **What this is not:** a human brain, a conscious system, or evidence of real
> feelings. See
> [`docs/research/SCIENTIFIC_EVIDENCE.md`](docs/research/SCIENTIFIC_EVIDENCE.md),
> which separates evidence, hypotheses and engineering shortcuts.

---

## 🚀 Quickstart

```bash
git clone https://github.com/sitta07/NeuralMind.git && cd AgentGraph
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-neuralmind.txt -r requirements-server.txt -r requirements-research.txt

python -m neuralmind.server     # Playground → http://127.0.0.1:8000   ·   Lab → http://127.0.0.1:8000/lab
python -m pytest tests/ -q      # full test suite
```

## 🎮 The Playground

![Playground](docs/media/playground.png)

| Try this | How |
|---|---|
| **Watch a brain drive behaviour** | Press **Play**. The Brain Scanner shows the selected creature's spikes, and the winning action population is the move it makes. |
| **Scan anyone's brain** | Click any creature. The scanner loads *that individual's* current learned weights and live spikes. |
| **Social life** | Tick **Social**. Creatures see each other and can **attack** (steal energy 💢), **share** (the recipient gets 2× 💚) or **signal** (📢). Each is a neural population competing in the same winner-take-all. |
| **Evolution** | Tick **Evolution**. Well-fed creatures reproduce, and children inherit a mutated *innate* brain plus an aggression gene (✨ birth, 💀 death). |
| **Starvation experiment** | **🚫 Deprive**, then **⏩ +1 / +3 days**. A day-by-day table shows energy, hunger, affect and neural firing. |
| **Feed someone** | Click the grass, or press **🍎 Food ahead**. |
| **Does learning help?** | **Train 40 episodes**, then **Compare vs untrained**. |

## 🔬 The Discovery Lab (`/lab`)

![Discovery Lab](docs/media/discovery_lab.png)

- Every study is **pre-registered**: its JSON spec is committed before the run.
- Every hypothesis has a stated falsifier. Results are shown with 95%
  bootstrap CIs, and negative results stay on the board.
- You can re-run any registered study from the browser.

### What we have found so far

| Study | Result | Status |
|---|---|---|
| **Can spiking agents learn aggression or cooperation within one lifetime?** ([write-up](docs/research/FINDINGS_SOCIAL.md)) | **No.** None of the 4 pre-registered hypotheses were supported. Attacks are untargeted, which points to an exploration bottleneck. An ablation also showed that an apparent 12.7% "aggression" came from a modelling artifact. | completed |
| **Does selfish lifetime learning undermine kin-selected helping?** (evolution, [write-up](docs/research/FINDINGS_EVOLUTION_KIN.md)) | Selfish learning *doubled* sharing, the opposite of our prediction. Help reached relatives above chance **without any kin-recognition sensor**, but only when offspring stayed near their parents. | completed; follow-up C2 running |
| **Does an aggression gene evolve under scarcity?** (D) | pre-registered in [`studies/`](studies/) | queued |
| **Baldwin effect vs hiding effect** (E): does learning speed up or shield the evolution of innate ability? | pre-registered as competing predictions | queued |
| Foraging: trained vs untrained agent, 60 held-out worlds | 4.85 vs 3.45 food per episode (≈ +40%) | real but noisy |

The full ranked agenda of open questions is in
[`docs/research/RESEARCH_AGENDA.md`](docs/research/RESEARCH_AGENDA.md).

## 🧩 How a decision is made

```
world ──► egocentric sensors ──► input currents ──► LIF spiking network
 ▲     food/threat ×3, hunger,      (nA)            sensory → action populations
 │     others ×3, heard signal                       (move / attack / share / signal)
 │                                                    with lateral inhibition
 │                                         most active population = action
 │                                                          ▼
 └── weights change ◄── reward-modulated ◄── reward prediction ◄── eat / hurt / steal / give
     (and genomes        Hebbian learning     error (TD)
      mutate across
      generations)
```

- The physics only moves bodies and does the energy bookkeeping. **It never
  picks an action.**
- Reward shaping is an explicit engineering choice.
- Affect is computed from the primary reward only.

## 🤖 For RL researchers

```python
from neuralmind.envs import parallel_env
env = parallel_env(n_rl=4, n_snn=4, config={"social": True}, max_cycles=500)
obs, infos = env.reset(seed=0)
while env.agents:
    obs, rewards, terms, truncs, infos = env.step(
        {a: env.action_space(a).sample() for a in env.agents})
```

- **Observations:** the sensor vector the SNN agents use.
- **Actions:** `Discrete` over move, plus attack / share / signal when social.
- **Rewards:** the same reward the SNN agents learn from.

## 🛠 Command-line tools

```bash
python -m neuralmind.research.spec studies/E_baldwin_vs_hiding.json   # run a registered study
python -m neuralmind.research.social all --seeds 10                    # lifetime social study
python -m neuralmind.research.evolution --experiment kin               # kin-selection study
python -m neuralmind.cli run reward_learning --seed 0                  # classic experiments
python -m neuralmind.bench --sizes 50 100 200 400                      # runtime + memory
python tools/make_media.py                                             # re-record these GIFs
```

## 📁 Project layout

```
neuralmind/
  core/          LIF neurons, synapses, STDP / eligibility traces
  affect/        reward prediction error, affect state
  world.py       2D world · Agent · social layer · evolution · genealogy
  envs/          PettingZoo ParallelEnv
  research/      pre-registered studies, stats (bootstrap CI, MI, G-test), spec runner
  lab.py         Discovery Lab API
  server.py      FastAPI backend (the browser only renders backend state)
  webui/         Playground + Discovery Lab (vanilla JS + canvas, Kenney CC0 pixel art)
studies/         registered study specs        results/   raw results + reports
docs/research/   findings, evidence ledger, agenda, literature
tests/           pytest suite (CI on 3.12 / 3.13)
```

## ⚠️ Known limitations

- Small brains: 31–59 neurons per agent, point-neuron LIF. This is not a model of any real nervous system.
- Within-lifetime learning alone does not produce targeted social behaviour (see findings).
- Evolution studies run for tens of generations, not thousands.
- A "day" is a simulation unit (`ticks_per_day`).

## Licence & credits

- **Code:** MIT (see `LICENSE`).
- **Pixel art:** [Tiny Town](https://kenney.nl/assets/tiny-town) and [Tiny Dungeon](https://kenney.nl/assets/tiny-dungeon) by **[Kenney](https://kenney.nl)**, released under CC0. Thank you! CC0 doesn't require credit, but we give it gladly.
- **Optional dependencies:** FastAPI, PettingZoo, Gymnasium (MIT); Uvicorn (BSD); Playwright (Apache-2.0, media recording only).
- Details in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

<details>
<summary><b>Legacy project: AgentGraph (original LLM multi-agent app — needs a Novita API key)</b></summary>

This repository started as **AgentGraph**, a LangGraph/Streamlit multi-agent
architecture consultant. Its code (`app.py`, `main.py`, `src/`, `evals/`) is kept
unchanged and is independent of NeuralMind.

## AgentGraph: AI Architecture Consultant

<div align="center">

[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen.svg)](https://github.com/sitta07/NeuralMind)
[![Built with LangGraph](https://img.shields.io/badge/Built%20with-LangGraph-blue.svg)](https://langchain-ai.github.io/langgraph/)
[![Built with LangSmith](https://img.shields.io/badge/Built%20with-LangSmith-green.svg)](https://smith.langchain.com/)
[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red.svg)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

A multi-agent system for real-time system design, security evaluation, and architecture optimization using **Meta Llama 3.3 70B** and **LangGraph**. Generates Mermaid diagrams, identifies vulnerabilities, and iteratively improves designs for cost-effectiveness and security.

> [!NOTE]
> **Learning Project**: This repository is an active learning playground for mastering advanced Agentic AI patterns. It serves as a hands-on exploration of:
> - **LangGraph** — Multi-agent orchestration and state management
> - **LangSmith** — LLM observability, tracing, and prompt management
>
> The project is continuously evolving as I deepen my understanding of production-grade agent architectures. Contributions and feedback are welcome!

---

## Features

### Multi-Agent System
- **4 Specialized Agents** working in a coordinated loop:
  - **Architect** — Generates system architecture with cost estimates
  - **Security** — Identifies vulnerabilities and mitigation strategies
  - **Evaluator** — Scores designs on security (40%), feasibility (30%), cost-effectiveness (30%)
  - **Mermaid Validator** — Ensures diagram syntax correctness

### Professional UI/UX
- **Minimal Aesthetic Streamlit UI** — Clean, modern interface with real-time agent outputs
- **Vertical Mermaid Diagrams** — `graph TD` layout for better readability (prevents horizontal compression)
- **Executive Session Summary** — AI-generated chronological narrative of the entire design session

### Engineering Best Practices
- **Prompt Registry Pattern** — Clean separation of prompt logic from agent implementation (`src/prompts/`)
- **Dynamic LangSmith Tracing** — Runtime-configurable with dynamic UUIDs for each session
- **Loop Prevention** — Convergence detection via similarity tracking, feedback deduplication, and score stagnation detection
- **Robust Error Handling** — Specific exception handling for JSON parsing and validation errors
- **Full English Localization** — Professional English throughout (no mixed languages)

### Cost-Conscious Design
- Budget-aware architecture recommendations in **Thai Baht (฿)**
- Pragmatic MVP-first approach (80% users, 20% features)
- Small team feasibility assessment (3-5 engineers)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- `pip` package manager
- Novita API key (for Meta Llama 3.3 70B access)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/sitta07/NeuralMind.git
cd AgentGraph
```

2. Create a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file in project root
echo "NOVITA_API_KEY=your_api_key_here" > .env
```

---

## Quick Start

### Web Interface (Streamlit)

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`.

Define your system requirements in the sidebar and set a monthly operating budget. The system will automatically:
1. Generate an initial architecture design
2. Run security validation
3. Evaluate against multiple criteria
4. Refine iteratively until passing (score ≥ 9.5/10)
5. Display Mermaid diagrams for each iteration
6. Generate an Executive Session Summary

### CLI Execution

```bash
python main.py
```

The CLI outputs detailed logs from each agent and saves diagrams to the `/diagrams` directory.

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NOVITA_API_KEY` | ✅ | Your API key for Llama 3.3 70B access via Novita |
| `LLM_BASE_URL` | ❌ | API base URL (default: `https://api.novita.ai/v3/openai`) |
| `MODEL_NAME` | ❌ | Model identifier (default: `meta-llama/llama-3.3-70b-instruct`) |
| `MODEL_TEMPERATURE` | ❌ | LLM temperature (default: `0.2`) |
| `DEFAULT_BUDGET_THB` | ❌ | Default monthly budget in THB (default: `5000.0`) |
| `LANGSMITH_PROMPT_NAME` | ❌ | LangSmith prompt name (default: `agentgraph-architect`) |

### Agent Tuning

Key parameters in `src/graph/nodes.py`:

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Model** | `meta-llama/llama-3.3-70b-instruct` | Via Novita API |
| **Temperature** | `0.2` | Low randomness for consistency |
| **Passing Threshold** | `≥ 9.5/10.0` | Near-perfect score required |
| **Max Revisions** | `3` | Iterations before stopping |
| **Output Similarity** | `≥ 90%` | Loop prevention threshold |
| **Feedback Repetition** | `≥ 85%` | Loop prevention threshold |

---

## Project Structure

```
AgentGraph/
├── app.py                          # Streamlit web UI with final summary generation
├── main.py                         # Graph builder & CLI execution
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (not in repo)
├── src/
│   ├── graph/
│   │   ├── state.py               # GraphState TypedDict & EvaluationRubric
│   │   ├── nodes.py               # 4 agent nodes + routing logic
│   │   └── __init__.py
│   ├── prompts/                   # 🆕 Prompt Registry
│   │   ├── __init__.py
│   │   ├── architect_prompts.py   # Architect agent prompts
│   │   ├── security_prompts.py   # Security agent prompts
│   │   └── evaluator_prompts.py  # Evaluator agent prompts + session summary
│   └── utils/
│       ├── convergence_utils.py    # Loop prevention functions
│       ├── cost_utils.py           # Cost calculation utilities
│       ├── diagram_generator.py    # Mermaid extraction & rendering
│       └── __init__.py
├── diagrams/                       # Generated architecture diagrams (PNG)
├── evals/                          # Evaluation rubrics & reports
└── README.md
```

---

## How It Works

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│  Architect  │────▶│ Mermaid Validator│────▶│   Security  │
└─────────────┘     └─────────────────┘     └─────────────┘
      ▲                                             │
      │                                             ▼
      │                                        ┌─────────────┐
      │                                        │  Evaluator  │
      │                                        └─────────────┘
      │                                               │
      │◀────────────────── feedback (if failed) ◀────┘
```

1. **Architect** → Generates initial `graph TD` Mermaid diagram with cost breakdown
2. **Mermaid Validator** → Checks syntax; returns to Architect if invalid
3. **Security** → Identifies vulnerabilities and pragmatic mitigations
4. **Evaluator** → Scores 0-10.0 based on security, feasibility, cost; requires ≥ 9.5 to pass
5. **Loop Prevention** → Stops iteration if converged, repeated feedback, or stagnant scores

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `langgraph` | Multi-agent orchestration framework |
| `langchain-core` | Message types and output parsing |
| `langchain-openai` | OpenAI-compatible LLM interface |
| `langsmith` | LLM observability and tracing |
| `streamlit` | Web UI framework |
| `python-dotenv` | Environment variable management |
| `requests` | HTTP requests for Mermaid API |
| `pydantic` | Data validation |

See `requirements.txt` for pinned versions.

---

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make focused changes with clear commit messages
4. Ensure Python compiles without errors (`python3 -m py_compile src/**/*.py`)
5. Submit a pull request with a description of your changes

### Areas for Contribution

- Additional agent types (e.g., Cost Optimizer, Performance Analyst)
- Enhanced Mermaid syntax support
- Alternative LLM providers (OpenAI, Anthropic, local models)
- Additional evaluation criteria
- Improved loop prevention heuristics
- Multi-language localization

---

## License

MIT License (2026) — See [LICENSE](LICENSE) file for details

---

**Built with**: LangGraph + Llama 3.3 70B + LangSmith + Streamlit

**Questions?** Review agent prompts in `src/prompts/` or check the conversation history in the UI.

</details>

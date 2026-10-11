# NeuralMind — a local-first computational brain-simulation laboratory

> **This repository is being transformed from the original *AgentGraph* LLM app
> into *NeuralMind*, a scientifically-grounded platform for experimenting with
> computational models of neurons, learning, memory, and affect-related
> dynamics.** The original AgentGraph application is preserved below and still
> works; the new NeuralMind engine lives in the `neuralmind/` package.

**What NeuralMind is:** a transparent, reproducible neural simulator you can run
on an ordinary laptop with **no GPU and no API key**. It implements leaky
integrate-and-fire neurons, spike-timing-dependent plasticity, reward-modulated
(three-factor) learning, and a low-dimensional affect/motivation layer, plus a
set of runnable, tested experiments.

**What NeuralMind is *not*:** a biologically complete brain, a conscious or
sentient system, or evidence of subjective feeling. It uses deliberately
simplified, documented approximations — see
[`docs/research/SCIENTIFIC_EVIDENCE.md`](docs/research/SCIENTIFIC_EVIDENCE.md),
which separates established findings from hypotheses and engineering choices.

## Quickstart (NeuralMind)

```bash
# 1. From the repository root, create an isolated environment.
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install the only runtime/test dependencies (NumPy + pytest).
pip install -r requirements-neuralmind.txt

# 3. Run the test suite (should report "passed").
python -m pytest tests/ -q

# 4. List and run experiments.
python -m neuralmind.cli list
python -m neuralmind.cli run reward_learning --seed 0 --save
python -m neuralmind.cli run reward_learning --seed 0 --no-learning   # baseline control
python -m neuralmind.cli runs            # list saved runs
python -m neuralmind.cli show 1          # inspect a saved run as JSON

# 5. Benchmark the engine (real runtime + memory numbers).
python -m neuralmind.bench --sizes 50 100 200 400 --steps 500
```

### Worked example: does reward change behaviour?

`reward_learning` builds a context population projecting to two competing action
populations (lateral inhibition = soft winner-take-all). A TD(0) reward
prediction error modulates STDP via eligibility traces (three-factor learning).

```bash
python -m neuralmind.cli run reward_learning --seed 0                # with learning
python -m neuralmind.cli run reward_learning --seed 0 --no-learning  # baseline
```

You should see `final_selection_rate` near chance (~0.4–0.6) **without** learning
and clearly higher (~0.8–0.95) **with** learning — i.e. the agent learns to pick
the rewarded action. Results are deterministic for a given `--seed`.

### Available experiments

| Name | Question | Status |
|---|---|---|
| `reward_learning` | Does reward-modulated STDP shift action selection? | validated (qualitative) |
| `threat_avoidance` | Does a CS paired with an aversive US acquire a defensive response? | validated (qualitative) |
| `pain_response` | Does a nociceptive-like input scale with intensity and recover? | exploratory |
| `forgetting` | Does a new memory retroactively interfere with an old one? | exploratory |

### Package layout

```
neuralmind/
  core/        LIF neurons, synapses, STDP, SpikingNetwork
  affect/      reward prediction error (TD), affect state variables
  experiments/ reward_learning, threat_avoidance, pain_response, forgetting
  persistence/ SQLite experiment store (save / reload / list)
  knowledge/   local, source-cited document index (Subsystem B)
  bench.py     runtime + memory benchmark harness
  cli.py       command-line runner
docs/          research report, reuse matrix, scientific evidence, ADRs, status
tests/         pytest suite
```

See [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) for the
current state, acceptance-criteria tracking, and next tasks.

---

# AgentGraph: AI Architecture Consultant

<div align="center">

[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen.svg)](https://github.com/sitta07/AgentGraph)
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
git clone https://github.com/sitta07/AgentGraph.git
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

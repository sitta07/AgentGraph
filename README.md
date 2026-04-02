# AgentGraph: AI Architecture Consultant

A multi-agent system for real-time system design, security evaluation, and architecture optimization using Meta Llama 3.3 70B and LangGraph. Generates Mermaid diagrams, identifies vulnerabilities, and iteratively improves designs for cost-effectiveness and security.

## Features

- **Multi-Agent Collaboration**: 4 specialized agents (Architect, Security, Evaluator, Mermaid Validator) working in a coordinated loop
- **Real-time Architecture Design**: Generates system architecture diagrams in Mermaid.js syntax with monthly cost estimates
- **Security-First Evaluation**: Identifies vulnerabilities and scoring designs on security (40%), feasibility (30%), and cost-effectiveness (30%)
- **Cost-Aware Design**: Designs pragmatic solutions respecting user-specified monthly operating budgets
- **Loop Prevention**: Convergence detection prevents infinite iterations through similarity tracking, feedback deduplication, and score stagnation detection
- **Mermaid Validation**: Syntax validation ensures diagrams render correctly before final output
- **Interactive Web UI**: Streamlit-based interface for chat-like interaction with real-time agent outputs
- **CLI Support**: Run directly from command line with comprehensive logging

## Installation

### Prerequisites

- Python 3.8 or higher
- `pip` package manager
- Novita API key (for Meta Llama 3.3 70B access)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
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
4. Refine iteratively until passing
5. Display Mermaid diagrams for each iteration

### CLI Execution

```bash
python main.py
```

The CLI outputs detailed logs from each agent and saves diagrams to the `/diagrams` directory.

## Configuration

### Environment Variables

- **NOVITA_API_KEY** (required): Your API key for Llama 3.3 70B access via Novita
  ```bash
  export NOVITA_API_KEY=your_key_here
  ```

### UI Parameters (Streamlit)

- **System Requirements**: Text description of the system to design
- **Monthly Operating Budget**: Budget constraint (฿ Thailand Baht) that the Architect considers when designing cost-effective solutions

### Agent Tuning

Key parameters in `src/graph/nodes.py`:

- **Model**: `meta-llama/llama-3.3-70b-instruct` (via Novita API)
- **Temperature**: `0.2` (low randomness for consistency)
- **Passing Threshold**: Score = 10.0 (perfect only)
- **Max Revisions**: 3 iterations before stopping
- **Loop Prevention Thresholds**:
  - Output similarity: ≥90% converged
  - Feedback repetition: ≥85% repeated
  - Score stagnation: No improvement for 2+ rounds

## Project Structure

```
AgentGraph/
├── app.py                          # Streamlit web UI
├── main.py                         # Graph builder & CLI execution
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (not in repo)
├── src/
│   ├── graph/
│   │   ├── state.py               # GraphState TypedDict & EvaluationRubric
│   │   ├── nodes.py               # 4 agent nodes + routing logic
│   │   └── __init__.py
│   └── utils/
│       ├── convergence_utils.py    # Loop prevention functions
│       ├── cost_utils.py           # Cost calculation utilities
│       ├── diagram_generator.py    # Mermaid extraction & rendering
│       └── __init__.py
├── diagrams/                       # Generated architecture diagrams (PNG)
├── evals/                          # Evaluation rubrics & reports
└── README.md
```

## How It Works

1. **Architect** → Generates initial Mermaid diagram with cost breakdown based on requirements and budget
2. **Mermaid Validator** → Checks diagram syntax; returns to Architect if invalid
3. **Security** → Identifies vulnerabilities and security concerns in the design
4. **Evaluator** → Scores 0-10 based on security, feasibility, and cost-effectiveness; requires perfect score (10.0) to pass
5. **Loop Prevention** → Checks for convergence before next iteration; stops if converged, repeated feedback, or stagnant scores

Architecture is considered **passed** only when the Evaluator assigns a perfect score (10.0).

## Dependencies

- **langgraph** (0.x): Multi-agent orchestration framework
- **langchain-core**: Message types and output parsing
- **langchain-openai**: OpenAI-compatible LLM interface for Novita API
- **streamlit**: Web UI framework
- **python-dotenv**: Environment variable management
- **requests**: HTTP requests for Mermaid API
- **pydantic**: Data validation

See `requirements.txt` for pinned versions.

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make focused changes with clear commit messages
4. Ensure Python compiles without errors (`python3 -m py_compile src/ *.py`)
5. Submit a pull request with a description of your changes

Areas for contribution:
- Additional agent types (e.g., Cost Optimizer, Performance Analyst)
- Enhanced Mermaid syntax support
- Alternative LLM providers
- Additional evaluation criteria
- Improved loop prevention heuristics

## License

MIT License (2026) — See [LICENSE](LICENSE) file for details

---

**Built with**: LangGraph + Llama 3.3 70B + Streamlit

**Questions?** Check the conversation summary in the repository or review specific agent prompts in `src/graph/nodes.py`.

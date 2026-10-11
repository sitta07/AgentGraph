# Contributing to NeuralMind

Thanks for helping build an open artificial-life lab.

- **Read [`AGENTS.md`](AGENTS.md).** It describes the mission and the working
  principles: unconventional ideas are welcome, fabricated results never are.
- **Add a study** without coding: see
  [`docs/ADDING_A_STUDY.md`](docs/ADDING_A_STUDY.md).
- **Plug in an RL algorithm** through the PettingZoo env
  (`neuralmind.envs.parallel_env`).
- **Code changes:**
  - Keep defaults backward-compatible.
  - Add tests (`python -m pytest tests/ -q`).
  - Make comments describe current behaviour.
  - Make small commits.
- **Licences:** only use code and assets whose licence allows it, and record
  them in `THIRD_PARTY_NOTICES.md`.

CI runs the full test suite on Python 3.12 and 3.13 for every push and pull
request.

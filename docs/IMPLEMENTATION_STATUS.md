# NeuralMind — Implementation Status

**Updated:** 2026-10-12 · **Branch:** `feat/social-agents` (main has the Playground via PR #1)

## 1. What works now (all executed and tested)

| Area | Module | Notes |
|---|---|---|
| Spiking core | `neuralmind/core/` | LIF populations, current-based synapses (1-step delay), pair STDP, eligibility traces, `clear_eligibility()`; NumPy-only, seeded |
| Affect | `neuralmind/affect/` | TD(0) reward prediction error; bounded valence/arousal/threat/frustration/motivation |
| Embodied world | `neuralmind/world.py` | 2D arena, 1–8 `Agent`s with their own brains sharing food & hazards; egocentric sensors → SNN → WTA action → physics → shaped reward → reward-modulated Hebbian learning; energy, hunger, starvation mode, place-food, day counter |
| Backend | `neuralmind/server.py` | FastAPI: session, step, reset, config (clamped), train, compare, advance (N days + daily snapshots), place_food, deprive, save, runs |
| Frontend | `neuralmind/webui/` | Pixel-art arena (Kenney CC0), multiple people with name tags/energy bars, click-to-select, Brain Scanner (3D, live spike glow), Agent Inspector, affect bars, day-by-day timeline, experiment controls, learning curve, trained-vs-untrained comparison |
| Experiments (CLI) | `neuralmind/experiments/` | reward_learning, threat_avoidance, pain_response, forgetting |
| Persistence / search | `persistence/`, `knowledge/` | SQLite runs; TF-IDF doc search with citations |
| Tooling | `cli.py`, `bench.py`, `recorder.py`, `viz.py` | CLI, benchmark, 3D brain viewer export |
| Social layer | `world.py` (`social=True`) | sensors for other agents + heard signals; attack / share / signal as neural actions; frustration→attack drive (ablatable); Hamilton-style reward accounting |
| Evolution | `world.py` (`evolve=True`) | reproduction, mutating innate genome + aggression gene, ageing, genealogy & relatedness, viscous vs well-mixed birth, Darwinian/Lamarckian |
| MARL interface | `neuralmind/envs/` | PettingZoo ParallelEnv (passes official API test); RL agents can share the world with SNN agents |
| Research harness | `neuralmind/research/` | pre-registered multi-seed studies, bootstrap CIs, auto reports + SVG charts; results committed in `results/` |
| CI | `.github/workflows/tests.yml` | full suite on Python 3.12 / 3.13 |

## 2. Tests — 108 passing (`python -m pytest tests/ -q`)

Neurons, plasticity, network, affect, experiments, persistence, knowledge,
benchmark, recorder/viewer, world (sensing direction, action→movement, walls,
energy, eating, network-chosen action, determinism, learning-beats-baseline,
multi-agent draw-order invariance, shared food), server (session, causality,
bounds, reproducibility, save, place_food, deprive, day/affect, multi-agent,
advance/starvation snapshots). The browser UI was checked end-to-end manually
with Playwright (play, step, train, compare, deprive, fast-forward, 5 agents).

## 3. Scientific results (measured, not asserted)

- **Foraging learning:** agents trained 80 episodes on 3 training seeds, then
  tested on 60 held-out worlds. Trained: 4.85 food/episode; untrained: 3.45.
  The trained agent won in 36 of 60 worlds. Real but noisy.
- **Learning curves** rise for every training seed (e.g. 0.6 → 6.3 food/episode).
- **Starvation:** with food removed, energy falls monotonically per day and
  hunger rises; sensory-population firing increases as the hunger sensor drives it.
- **Reproducibility:** identical seed → identical episode (tested).

## 4. Bugs found and fixed (selected)

| Bug | Fix |
|---|---|
| Pair STDP (a_minus > a_plus) net-depressed co-active pathways under sustained firing, **inverting** the learned food→turn map (trained < untrained) | Potentiation-only eligibility (reward-modulated Hebbian) + exploration noise |
| Reward credited "forward" generically → agent ignored food direction | Alignment-based shaping |
| `plastic` flag ignored at runtime (weights changed during "frozen" recall) | `learn()` respects `plastic` |
| Canvas `fit()` multiplied height every frame → browser crash | idempotent sizing from CSS box |
| Chart `line()` left `hi` undefined → blank learning curve | compute `lo`/`hi` independently |
| SQLite connection used across server threads | `check_same_thread=False` |

## 5. Known limitations

- Lifetime learning alone does not produce targeted social behaviour (see
  `docs/research/FINDINGS_SOCIAL.md`); evolution studies are in progress.
- Reward shaping is an engineering choice; learning gains vary per world.
- Affect variables are hand-tuned model quantities, not calibrated or subjective.
- Big simulators (TVB, Brian2, NEST) are reference-only (copyleft); no engine adapter yet.

## 6. Next tasks

1. Finish Experiment C (kin selection vs selfish learning), then the ranked
   agenda in `docs/research/RESEARCH_AGENDA.md`.
2. Ablation harness (disable sensors/populations/learning; multi-seed).
3. Engine adapter to validate the core against Brian2.

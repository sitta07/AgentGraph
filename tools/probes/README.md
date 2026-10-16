# Exploratory probes

Small scripts behind the exploratory (not pre-registered) numbers quoted in
`docs/research/FINDINGS_*.md`. Each takes the repository root as its first
argument, so it runs against that checkout:

    python -I tools/probes/scramble_pilot.py .

| Script | Used in |
|---|---|
| `weights_probe.py` | V, follow-up item 1: innate weights after 8000 ticks of evolution |
| `scramble_pilot.py` | V, positive-control pilot: trained single agents with real vs scrambled senses |
| `sparse_pilot.py` | pilot: does sparse food make sensing matter (4 seeds) |
| `braitenberg_pilot.py` | V follow-up: hand-wired sensory foraging vs random wiring |
| `control_index.py` | V follow-up item 2: action choice under fixed inputs (lock-in) |
| `reset_detail3.py` | V follow-up items 3–4 and the W pilot: `python -I tools/probes/reset_detail3.py . <substeps> <reset 0/1> <critic> <normalize 0/1>` |

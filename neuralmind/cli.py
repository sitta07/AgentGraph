"""Command-line interface for running and inspecting NeuralMind experiments.

Examples
--------
    python -m neuralmind.cli list
    python -m neuralmind.cli run reward_learning --seed 0 --save
    python -m neuralmind.cli run threat_avoidance --no-learning
    python -m neuralmind.cli runs
    python -m neuralmind.cli show 1

The core simulation runs offline with no API key.
"""

from __future__ import annotations

import argparse
import json
import sys

from neuralmind import __version__
from neuralmind.experiments.reward_learning import (
    RewardLearningConfig,
    RewardLearningExperiment,
)
from neuralmind.experiments.threat_avoidance import (
    ThreatAvoidanceConfig,
    ThreatAvoidanceExperiment,
)
from neuralmind.experiments.pain_response import (
    PainResponseConfig,
    PainResponseExperiment,
)
from neuralmind.experiments.forgetting import (
    ForgettingConfig,
    ForgettingExperiment,
)
from neuralmind.knowledge.index import KnowledgeIndex
from neuralmind.persistence.store import ExperimentStore

REGISTRY = {
    "reward_learning": (RewardLearningExperiment, RewardLearningConfig),
    "threat_avoidance": (ThreatAvoidanceExperiment, ThreatAvoidanceConfig),
    "pain_response": (PainResponseExperiment, PainResponseConfig),
    "forgetting": (ForgettingExperiment, ForgettingConfig),
}


def _build_config(config_cls, overrides: dict):
    fields = {f for f in config_cls.__dataclass_fields__}
    kwargs = {k: v for k, v in overrides.items() if k in fields and v is not None}
    return config_cls(**kwargs)


def _run(args: argparse.Namespace) -> int:
    if args.experiment not in REGISTRY:
        print(f"unknown experiment '{args.experiment}'. Try: {', '.join(REGISTRY)}")
        return 2
    exp_cls, cfg_cls = REGISTRY[args.experiment]
    cfg = _build_config(cfg_cls, {"seed": args.seed})
    exp = exp_cls(cfg)

    if args.experiment == "reward_learning":
        result = exp.run(learning=not args.no_learning)
    elif args.experiment == "threat_avoidance":
        result = exp.run(paired=not args.unpaired)
    else:  # pain_response, forgetting: no learning/paired switch
        result = exp.run()

    print(f"experiment : {result.name}  [{result.status}]")
    print("metrics    :")
    for k, v in result.metrics.items():
        print(f"    {k:28s} = {v:.4f}")
    print("notes      :")
    for n in result.notes:
        print(f"    - {n}")

    if args.save:
        with ExperimentStore(args.db) as store:
            run_id = store.save(result)
        print(f"saved run id={run_id} to {args.db}")
    return 0


def _runs(args: argparse.Namespace) -> int:
    with ExperimentStore(args.db) as store:
        rows = store.list()
    if not rows:
        print("(no saved runs)")
        return 0
    for r in rows:
        key = next(iter(r["metrics"]), None)
        head = f" {key}={r['metrics'][key]:.3f}" if key else ""
        print(f"[{r['id']}] {r['name']:18s} {r['status']:11s} {r['created']}{head}")
    return 0


def _show(args: argparse.Namespace) -> int:
    with ExperimentStore(args.db) as store:
        result = store.get(args.id)
    if result is None:
        print(f"run {args.id} not found")
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def _search(args: argparse.Namespace) -> int:
    from pathlib import Path

    idx = KnowledgeIndex()
    root = Path(args.path)
    files = ([root] if root.is_file()
             else sorted(p for ext in ("*.md", "*.txt") for p in root.rglob(ext)))
    for f in files:
        try:
            idx.ingest_file(f)
        except OSError:
            continue
    print(f"indexed {len(idx)} passages from {len(files)} file(s)")
    results = idx.search(args.query, top_k=args.top_k)
    if not results:
        print("(no matches)")
        return 0
    for r in results:
        print(f"\n[{r.score:.3f}] {r.citation}")
        snippet = " ".join(r.text.split())[:200]
        print(f"    {snippet}")
    return 0


def _visualize(args: argparse.Namespace) -> int:
    import numpy as np

    from neuralmind.affect.affect_state import AffectState
    from neuralmind.core.network import Connection, SpikingNetwork
    from neuralmind.core.neurons import LIFPopulation
    from neuralmind.recorder import record
    from neuralmind.viz import render_html

    rng = np.random.default_rng(args.seed)
    dt = 1.0
    net = SpikingNetwork(dt=dt)
    net.add_population("input", LIFPopulation(10, dt=dt, seed=args.seed))
    net.add_population("exc", LIFPopulation(40, dt=dt, seed=args.seed + 1,
                                            randomize_initial_v=True))
    net.add_population("inh", LIFPopulation(10, dt=dt, seed=args.seed + 2))
    net.connect(Connection("input", "exc",
                           weights=rng.uniform(0, 2.6, (40, 10)), tau_syn=5.0))
    net.connect(Connection("exc", "inh",
                           weights=rng.uniform(0, 1.0, (10, 40)), tau_syn=5.0))
    net.connect(Connection("inh", "exc",
                           weights=-rng.uniform(0, 0.8, (40, 10)), tau_syn=10.0))
    net.build()

    affect = AffectState()
    state = {"threat": 0.0, "arousal": 0.0, "valence": 0.0}

    def external(i: int) -> dict:
        # A stimulus pulse arrives for the middle third of the run.
        on = args.steps // 3 <= i < 2 * args.steps // 3
        drive = (8.0 if on else 2.0) + rng.normal(0, 1.5, 10)
        return {"input": drive}

    def extra(i: int) -> dict:
        exc_rate = net.populations["exc"].spikes.mean() * 1000.0 / dt
        affect.update(threat_cue=min(1.0, exc_rate / 120.0),
                      reward_expectation=0.3)
        return {"valence": affect.valence, "arousal": affect.arousal,
                "threat": affect.threat}

    rec = record(net, args.steps, external=external, extra_series=extra,
                 meta={"demo": "input->E/I network with affect read-out"})
    out = render_html(rec, args.out,
                      title="NeuralMind — E/I network activity",
                      subtitle=("Input→excitatory/inhibitory network. Stimulus "
                                "pulses during the middle third. Affect variables "
                                "are read out from live population activity."))
    print(f"wrote {out}  ({rec.n_steps} steps, {len(rec.populations)} populations)")
    print("open it in a browser to play back the recorded simulation.")
    return 0


def _list(_args: argparse.Namespace) -> int:
    print("available experiments:")
    for name in REGISTRY:
        print(f"    {name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="neuralmind", description=__doc__)
    p.add_argument("--version", action="version", version=f"neuralmind {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("list", help="list available experiments")
    sp.set_defaults(func=_list)

    sp = sub.add_parser("run", help="run an experiment")
    sp.add_argument("experiment")
    sp.add_argument("--seed", type=int, default=0)
    sp.add_argument("--save", action="store_true")
    sp.add_argument("--db", default="neuralmind_experiments.sqlite")
    sp.add_argument("--no-learning", action="store_true",
                    help="reward_learning: disable learning (baseline control)")
    sp.add_argument("--unpaired", action="store_true",
                    help="threat_avoidance: unpaired control")
    sp.set_defaults(func=_run)

    sp = sub.add_parser("runs", help="list saved runs")
    sp.add_argument("--db", default="neuralmind_experiments.sqlite")
    sp.set_defaults(func=_runs)

    sp = sub.add_parser("show", help="print a saved run as JSON")
    sp.add_argument("id", type=int)
    sp.add_argument("--db", default="neuralmind_experiments.sqlite")
    sp.set_defaults(func=_show)

    sp = sub.add_parser("search", help="keyword-search local docs with source citations")
    sp.add_argument("query")
    sp.add_argument("--path", default="docs", help="file or directory to index")
    sp.add_argument("--top-k", type=int, default=5)
    sp.set_defaults(func=_search)

    sp = sub.add_parser("visualize", help="record a demo simulation to a self-contained HTML viewer")
    sp.add_argument("--steps", type=int, default=450)
    sp.add_argument("--seed", type=int, default=0)
    sp.add_argument("--out", default="neuralmind_viewer.html")
    sp.set_defaults(func=_visualize)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

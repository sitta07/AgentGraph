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
from neuralmind.persistence.store import ExperimentStore

REGISTRY = {
    "reward_learning": (RewardLearningExperiment, RewardLearningConfig),
    "threat_avoidance": (ThreatAvoidanceExperiment, ThreatAvoidanceConfig),
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
    else:
        result = exp.run(paired=not args.unpaired)

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
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

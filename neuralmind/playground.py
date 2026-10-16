"""The Playground API as plain Python: one in-process simulation session.

Every operation takes a JSON-like ``dict`` and returns one, so the same code
serves two front doors: :mod:`neuralmind.server` (FastAPI, local install) and
the browser build, where Pyodide runs this module inside a Web Worker and
calls :func:`dispatch`. No web framework is imported here.
"""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import fields
from urllib.parse import parse_qs, urlsplit

from neuralmind.experiments.base import ExperimentResult
from neuralmind.world import ACTIONS, SOCIAL_ACTIONS, World2D, WorldConfig

# Safe bounds for user-editable parameters (min, max).
BOUNDS = {
    "n_agents": (1, 8), "n_food": (0, 30), "n_hazard": (0, 10), "max_ticks": (10, 5000),
    "ticks_per_day": (10, 1000),
    "attack_radius": (0.01, 0.3), "steal": (0.0, 1.0), "attack_cost": (0.0, 0.5),
    "share_amount": (0.0, 1.0), "share_benefit": (0.0, 5.0), "signal_range": (0.05, 2.0),
    "signal_cost": (0.0, 0.1), "r_prosocial": (0.0, 1.0), "r_hurt": (0.0, 10.0),
    "aggression_gain": (0.0, 10.0), "w_social_scale": (0.1, 1.5),
    "repro_threshold": (0.5, 1.5), "repro_cost": (0.05, 1.0), "max_pop": (2, 60),
    "max_age": (50, 20000), "mut_sigma": (0.0, 1.0), "trait_sigma": (0.0, 2.0),
    "birth_radius": (0.0, 0.5), "mirror_at": (-1, 100000), "coop_radius": (0.0, 0.5), "mirror_every": (0, 100000),
    "sensor_range": (0.05, 2.0), "speed": (0.002, 0.1), "turn": (0.05, 1.5),
    "e0": (0.1, 5.0), "food_energy": (0.0, 2.0), "move_cost": (0.0, 0.1),
    "hazard_cost": (0.0, 0.5), "n_action": (2, 32), "substeps": (1, 20),
    "idle_drive": (0.0, 10.0), "sensor_gain": (0.0, 20.0),
    "action_noise": (0.0, 10.0), "lr": (0.0, 5.0), "w_init": (0.05, 5.0),
    "w_max": (0.5, 10.0), "w_inhib": (0.0, 5.0), "r_eat": (0.0, 10.0),
    "r_approach": (0.0, 20.0), "r_align": (0.0, 20.0), "r_hazard": (0.0, 10.0),
    "seed": (0, 10_000_000),
}

_INTEGER = ("n_agents", "n_food", "n_hazard", "max_ticks", "n_action", "substeps", "seed",
            "ticks_per_day", "max_pop", "max_age", "mirror_at", "mirror_every")


class PlaygroundError(Exception):
    """A request the session cannot serve; ``status`` is the matching HTTP code."""

    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


def validate(overrides: dict) -> WorldConfig:
    """Build a WorldConfig from user input: unknown keys dropped, numbers clamped."""
    valid = {f.name for f in fields(WorldConfig)}
    kwargs = {}
    for k, v in (overrides or {}).items():
        if k not in valid:
            continue
        if k == "reward_mode":
            kwargs[k] = v if v in ("align", "approach") else "align"
            continue
        if k == "critic":
            kwargs[k] = v if v in ("scalar", "state") else "scalar"
            continue
        if isinstance(getattr(WorldConfig, k, None), bool):
            kwargs[k] = bool(v)
            continue
        if isinstance(getattr(WorldConfig, k, None), tuple):
            names = v if isinstance(v, (list, tuple)) else []
            kwargs[k] = tuple(str(x) for x in names if x in ACTIONS + SOCIAL_ACTIONS)
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            raise PlaygroundError(400, f"parameter '{k}' must be numeric")
        if not math.isfinite(v):
            raise PlaygroundError(400, f"parameter '{k}' must be finite")
        if k in BOUNDS:
            lo, hi = BOUNDS[k]
            v = min(max(v, lo), hi)
        if k in _INTEGER:
            v = int(round(v))
        kwargs[k] = v
    return WorldConfig(**kwargs)


def _cfg_with_seed(cfg: WorldConfig, seed: int) -> WorldConfig:
    d = cfg.as_dict()
    d["seed"] = seed
    return WorldConfig(**d)


class Session:
    """Single in-process simulation session (one world at a time)."""

    def __init__(self) -> None:
        self.world: World2D | None = None
        self.config = WorldConfig()
        self.episode_rewards: list[float] = []

    def _world(self, detail: str = "no session") -> World2D:
        if self.world is None:
            raise PlaygroundError(409, detail)
        return self.world

    def create(self, overrides: dict) -> dict:
        cfg = validate(overrides)
        self.config = cfg
        self.world = World2D(cfg)
        self.episode_rewards = []
        return self.session_info()

    def session_info(self) -> dict:
        w = self._world()
        lay = w.brain_layout()
        return {
            "config": self.config.as_dict(),
            "bounds": BOUNDS,
            "actions": list(w.agents[0].actions),
            "size": self.config.size,
            "hazards": w.hazard_list(),
            "node_order": w._node_order,
            "sizes": {p: w.net.populations[p].n for p in w._node_order},
            "layout": {"nodes": lay["nodes"], "edges": lay["edges"],
                       "matrix": lay["matrix"]},
            "state": w._frame(),
        }

    def step(self, body: dict) -> dict:
        w = self._world("no session; POST /api/session first")
        n = min(max(int(body.get("n", 1)), 1), 60)
        learning = bool(body.get("learning", True))
        frames = []
        for _ in range(n):
            if not w.alive:
                break
            frames.append(w.step(learning=learning))
        return {
            "frames": frames,
            "alive": w.alive,
            "metrics": {
                "t": w.t, "food_eaten": w.food_eaten, "energy": round(float(w.energy), 4),
                "hazard_hits": w.hazard_hits, "total_reward": round(w.total_reward, 3),
                "distance": round(w.distance, 3),
            },
        }

    def brain(self, agent_id: int) -> dict:
        """One agent's own brain right now: 3-D layout, its current (learned)
        weights as edges and connectivity matrix, plus its live spike glow."""
        w = self._world()
        ag = next((a for a in w.agents if a.id == agent_id), None)
        if ag is None:
            raise PlaygroundError(404, f"agent {agent_id} not found")
        lay = ag.brain_layout()
        return {"id": ag.id, "node_order": ag._node_order,
                "sizes": {p: ag.net.populations[p].n for p in ag._node_order},
                "layout": {"nodes": lay["nodes"], "edges": lay["edges"], "matrix": lay["matrix"]},
                "glow": ag.neural_glow(), "actions": list(ag.actions)}

    def lineage(self, limit: int = 3000) -> dict:
        """Genealogy of every agent that ever lived in this world (most recent
        ``limit`` records): id, parent, lineage, generation, born, died, gene."""
        w = self._world()
        recs = sorted(getattr(w, "registry", {}).values(), key=lambda r: r["id"])[-max(1, limit):]
        return {"t": w.t, "records": recs, "alive": [a.id for a in w.agents if a.alive],
                "evolve": w.cfg.evolve}

    def advance(self, body: dict) -> dict:
        """Fast-forward N simulated 'days', recording a snapshot of one agent's
        body, affect and per-population firing at the end of every day. All values
        come from the running engine; nothing is interpolated."""
        w = self._world()
        days = min(max(float(body.get("days", 1)), 0.1), 30.0)
        want = int(body.get("agent", w.agents[0].id))
        target = next((a for a in w.agents if a.id == want), w.agents[0])
        learning = bool(body.get("learning", True))
        tpd = max(1, w.cfg.ticks_per_day)
        total = min(int(round(days * tpd)), 5000)
        snapshots, frame, fired = [], None, None
        for i in range(total):
            if not any(ag.alive for ag in w.agents):
                break
            frame = w.step(learning=learning)
            ag = next((a for a in frame["agents"] if a["id"] == target.id), None)
            if ag is None:          # pruned after death: stop recording this agent
                break
            acc = [1.0 if v >= 0.999 else 0.0 for v in ag["glow"]]   # spiked this tick
            fired = acc if fired is None else [a + b for a, b in zip(fired, acc)]
            if (w.t % tpd == 0) or i == total - 1:
                rates, off = {}, 0
                ticks = tpd if w.t % tpd == 0 else (w.t % tpd)
                for p in target._node_order:
                    n = target.net.populations[p].n
                    rates[p] = round(sum(fired[off:off + n]) / (n * max(1, ticks)), 3)
                    off += n
                snapshots.append({"day": round(w.t / tpd, 2), "t": w.t,
                                  "energy": ag["energy"], "hunger": ag["hunger"],
                                  "alive": ag["alive"], "food_eaten": ag["food_eaten"],
                                  "affect": ag["affect"], "firing": rates})
                fired = None
        return {"frame": frame or w._frame(), "snapshots": snapshots,
                "alive": any(ag.alive for ag in w.agents)}

    def place_food(self, body: dict) -> dict:
        w = self._world()
        if body.get("ahead"):
            w.place_food_ahead()
        else:
            w.place_food(float(body.get("x", 0.5)), float(body.get("y", 0.5)))
        return {"food": w._frame()["food"]}

    def deprive(self, body: dict) -> dict:
        w = self._world()
        w.set_deprive(bool(body.get("on", True)))
        return {"deprive": w.deprive}

    def reset(self, body: dict) -> dict:
        w = self._world()
        self.episode_rewards.append(round(w.total_reward, 3))
        seed = body.get("seed")
        w.reset(seed=int(seed) if seed is not None else None,
                keep_weights=bool(body.get("keep_weights", False)))
        return self.session_info()

    def set_config(self, body: dict) -> dict:
        """Change parameters; recreates the world (requires reset)."""
        merged = self.config.as_dict()
        merged.update(body)
        return self.create(merged)

    def train(self, body: dict) -> dict:
        """Train the current agent across N episodes; return the learning curve."""
        w = self._world()
        episodes = min(max(int(body.get("episodes", 40)), 1), 400)
        curve = []
        for ep in range(episodes):
            w.reset(keep_weights=(ep > 0))
            m = w.run(learning=True)
            curve.append({"episode": ep + 1, "food": m["food_eaten"],
                          "reward": m["total_reward"], "survival": m["survival_ticks"]})
        return {"curve": curve, "episodes": episodes}

    def compare(self, body: dict) -> dict:
        """Trained (current weights) vs untrained control over held-out seeds."""
        w = self._world()
        n = min(max(int(body.get("seeds", 10)), 1), 50)
        start = int(body.get("start_seed", 9000))
        trained, untrained = [], []
        for s in range(start, start + n):
            w.reset(seed=s, keep_weights=True)
            trained.append(w.run(learning=False)["food_eaten"])
            untrained.append(
                World2D(_cfg_with_seed(self.config, s)).run(learning=False)["food_eaten"])
        return {
            "seeds": list(range(start, start + n)),
            "trained": trained, "untrained": untrained,
            "trained_mean": round(statistics.mean(trained), 3),
            "untrained_mean": round(statistics.mean(untrained), 3),
        }

    def episode_result(self, note: str = "") -> ExperimentResult:
        """The current episode as an experiment record, ready to store or download."""
        w = self._world()
        return ExperimentResult(
            name="playground_episode", status="exploratory",
            config=self.config.as_dict(),
            metrics={"food_eaten": float(w.food_eaten), "survival": float(w.t),
                     "total_reward": float(w.total_reward),
                     "hazard_hits": float(w.hazard_hits)},
            series={"episode_rewards": self.episode_rewards},
            notes=[note],
        )


_POST = {
    "session": Session.create, "step": Session.step, "advance": Session.advance,
    "place_food": Session.place_food, "deprive": Session.deprive, "reset": Session.reset,
    "config": Session.set_config, "train": Session.train, "compare": Session.compare,
}


def route(session: Session, path: str, body: dict | None) -> dict:
    """Serve one ``/api/...`` request the way :mod:`neuralmind.server` does.

    ``body`` is None for a GET. ``/api/save`` returns the episode record under
    ``download`` instead of storing it, since the browser has no run database.
    """
    url = urlsplit(path)
    name, _, arg = url.path.removeprefix("/api/").partition("/")
    if body is not None and name in _POST and not arg:
        return _POST[name](session, body)
    if body is not None and name == "save":
        return {"id": None, "download": session.episode_result(body.get("note", "")).to_dict()}
    if body is None and name == "brain" and arg:
        try:
            agent_id = int(arg)
        except ValueError:
            raise PlaygroundError(422, "agent id must be an integer")
        return session.brain(agent_id)
    if body is None and name == "lineage":
        limit = parse_qs(url.query).get("limit", ["3000"])[0]
        return session.lineage(int(limit))
    if body is None and name == "health":
        return {"ok": True, "has_session": session.world is not None}
    raise PlaygroundError(404, f"no route {path}")


def dispatch(session: Session, path: str, body_json: str | None = None) -> tuple[int, str]:
    """JSON in, ``(status, JSON)`` out: the entry point the browser worker calls."""
    try:
        body = None if body_json is None else (json.loads(body_json) or {})
        return 200, json.dumps(route(session, path, body))
    except PlaygroundError as e:
        return e.status, json.dumps({"detail": e.detail})
    except (TypeError, ValueError) as e:
        return 400, json.dumps({"detail": str(e)})

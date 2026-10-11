"""FastAPI backend for the NeuralMind Artificial Life Playground.

The browser talks to THIS server, which runs the real NumPy neural-agent engine
(:mod:`neuralmind.world`). No learning logic lives in the frontend — the backend
owns the simulation and returns actual recorded state each step. Runs fully
offline with no API key.

Launch:
    python -m neuralmind.server            # then open http://127.0.0.1:8000
"""

from __future__ import annotations

import math
from dataclasses import fields
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from neuralmind.persistence.store import ExperimentStore
from neuralmind.world import ACTIONS, World2D, WorldConfig

app = FastAPI(title="NeuralMind Artificial Life Playground")

_WEBUI = Path(__file__).parent / "webui"

# Safe bounds for user-editable parameters (min, max).
_BOUNDS = {
    "n_agents": (1, 8), "n_food": (0, 30), "n_hazard": (0, 10), "max_ticks": (10, 5000),
    "ticks_per_day": (10, 1000),
    "attack_radius": (0.01, 0.3), "steal": (0.0, 1.0), "attack_cost": (0.0, 0.5),
    "share_amount": (0.0, 1.0), "share_benefit": (0.0, 5.0), "signal_range": (0.05, 2.0),
    "signal_cost": (0.0, 0.1), "r_prosocial": (0.0, 1.0), "r_hurt": (0.0, 10.0),
    "aggression_gain": (0.0, 10.0), "w_social_scale": (0.1, 1.5),
    "sensor_range": (0.05, 2.0), "speed": (0.002, 0.1), "turn": (0.05, 1.5),
    "e0": (0.1, 5.0), "food_energy": (0.0, 2.0), "move_cost": (0.0, 0.1),
    "hazard_cost": (0.0, 0.5), "n_action": (2, 32), "substeps": (1, 20),
    "idle_drive": (0.0, 10.0), "sensor_gain": (0.0, 20.0),
    "action_noise": (0.0, 10.0), "lr": (0.0, 5.0), "w_init": (0.05, 5.0),
    "w_max": (0.5, 10.0), "w_inhib": (0.0, 5.0), "r_eat": (0.0, 10.0),
    "r_approach": (0.0, 20.0), "r_align": (0.0, 20.0), "r_hazard": (0.0, 10.0),
    "seed": (0, 10_000_000),
}


class Session:
    """Single in-process simulation session (one world at a time)."""

    def __init__(self) -> None:
        self.world: World2D | None = None
        self.config = WorldConfig()
        self.episode_rewards: list[float] = []
        self.store = ExperimentStore("neuralmind_playground.sqlite")

    def create(self, overrides: dict) -> dict:
        cfg = self._validate(overrides)
        self.config = cfg
        self.world = World2D(cfg)
        self.episode_rewards = []
        return self.session_info()

    def _validate(self, overrides: dict) -> WorldConfig:
        valid = {f.name for f in fields(WorldConfig)}
        kwargs = {}
        for k, v in (overrides or {}).items():
            if k not in valid:
                continue
            if k == "reward_mode":
                kwargs[k] = v if v in ("align", "approach") else "align"
                continue
            if k in ("normalize", "social"):
                kwargs[k] = bool(v)
                continue
            try:
                v = float(v)
            except (TypeError, ValueError):
                raise HTTPException(400, f"parameter '{k}' must be numeric")
            if not math.isfinite(v):
                raise HTTPException(400, f"parameter '{k}' must be finite")
            if k in _BOUNDS:
                lo, hi = _BOUNDS[k]
                v = min(max(v, lo), hi)
            if k in ("n_agents", "n_food", "n_hazard", "max_ticks", "n_action",
                     "substeps", "seed", "ticks_per_day"):
                v = int(round(v))
            kwargs[k] = v
        return WorldConfig(**kwargs)

    def session_info(self) -> dict:
        w = self.world
        lay = w.brain_layout()
        return {
            "config": self.config.as_dict(),
            "bounds": _BOUNDS,
            "actions": list(w.agents[0].actions),
            "size": self.config.size,
            "hazards": w.hazard_list(),
            "node_order": w._node_order,
            "sizes": {p: w.net.populations[p].n for p in w._node_order},
            "layout": {"nodes": lay["nodes"], "edges": lay["edges"],
                       "matrix": lay["matrix"]},
            "state": w._frame(),
        }


SESSION = Session()


@app.post("/api/session")
def create_session(body: dict | None = None):
    return SESSION.create(body or {})


@app.post("/api/step")
def step(body: dict | None = None):
    if SESSION.world is None:
        raise HTTPException(409, "no session; POST /api/session first")
    body = body or {}
    n = min(max(int(body.get("n", 1)), 1), 60)
    learning = bool(body.get("learning", True))
    frames = []
    for _ in range(n):
        if not SESSION.world.alive:
            break
        frames.append(SESSION.world.step(learning=learning))
    w = SESSION.world
    return {
        "frames": frames,
        "alive": w.alive,
        "metrics": {
            "t": w.t, "food_eaten": w.food_eaten, "energy": round(float(w.energy), 4),
            "hazard_hits": w.hazard_hits, "total_reward": round(w.total_reward, 3),
            "distance": round(w.distance, 3),
        },
    }


@app.post("/api/advance")
def advance(body: dict | None = None):
    """Fast-forward N simulated 'days', recording a snapshot of one agent's
    body, affect and per-population firing at the end of every day. All values
    come from the running engine; nothing is interpolated."""
    if SESSION.world is None:
        raise HTTPException(409, "no session")
    body = body or {}
    w = SESSION.world
    days = min(max(float(body.get("days", 1)), 0.1), 30.0)
    aid = min(max(int(body.get("agent", 0)), 0), len(w.agents) - 1)
    learning = bool(body.get("learning", True))
    tpd = max(1, w.cfg.ticks_per_day)
    total = min(int(round(days * tpd)), 5000)
    snapshots, frame, fired = [], None, None
    for i in range(total):
        if not any(ag.alive for ag in w.agents):
            break
        frame = w.step(learning=learning)
        ag = frame["agents"][aid]
        g = ag["glow"]
        acc = [1.0 if v >= 0.999 else 0.0 for v in g]   # spiked this tick
        fired = acc if fired is None else [a + b for a, b in zip(fired, acc)]
        if (w.t % tpd == 0) or i == total - 1:
            agent = w.agents[aid]
            rates, off = {}, 0
            ticks = tpd if w.t % tpd == 0 else (w.t % tpd)
            for p in agent._node_order:
                n = agent.net.populations[p].n
                rates[p] = round(sum(fired[off:off + n]) / (n * max(1, ticks)), 3)
                off += n
            snapshots.append({"day": round(w.t / tpd, 2), "t": w.t,
                              "energy": ag["energy"], "hunger": ag["hunger"],
                              "alive": ag["alive"], "food_eaten": ag["food_eaten"],
                              "affect": ag["affect"], "firing": rates})
            fired = None
    return {"frame": frame or w._frame(), "snapshots": snapshots,
            "alive": any(ag.alive for ag in w.agents)}


@app.post("/api/place_food")
def place_food(body: dict | None = None):
    if SESSION.world is None:
        raise HTTPException(409, "no session")
    body = body or {}
    if body.get("ahead"):
        SESSION.world.place_food_ahead()
    else:
        SESSION.world.place_food(float(body.get("x", 0.5)), float(body.get("y", 0.5)))
    return {"food": SESSION.world._frame()["food"]}


@app.post("/api/deprive")
def deprive(body: dict | None = None):
    if SESSION.world is None:
        raise HTTPException(409, "no session")
    SESSION.world.set_deprive(bool((body or {}).get("on", True)))
    return {"deprive": SESSION.world.deprive}


@app.post("/api/reset")
def reset(body: dict | None = None):
    if SESSION.world is None:
        raise HTTPException(409, "no session")
    body = body or {}
    SESSION.episode_rewards.append(round(SESSION.world.total_reward, 3))
    seed = body.get("seed")
    keep = bool(body.get("keep_weights", False))
    SESSION.world.reset(seed=int(seed) if seed is not None else None,
                        keep_weights=keep)
    return SESSION.session_info()


@app.post("/api/config")
def set_config(body: dict | None = None):
    """Change parameters; recreates the world (requires reset)."""
    merged = SESSION.config.as_dict()
    merged.update(body or {})
    return SESSION.create(merged)


@app.post("/api/train")
def train(body: dict | None = None):
    """Train the current agent across N episodes; return the learning curve."""
    if SESSION.world is None:
        raise HTTPException(409, "no session")
    episodes = min(max(int((body or {}).get("episodes", 40)), 1), 400)
    curve = []
    w = SESSION.world
    for ep in range(episodes):
        w.reset(keep_weights=(ep > 0))
        m = w.run(learning=True)
        curve.append({"episode": ep + 1, "food": m["food_eaten"],
                      "reward": m["total_reward"], "survival": m["survival_ticks"]})
    return {"curve": curve, "episodes": episodes}


@app.post("/api/compare")
def compare(body: dict | None = None):
    """Trained (current weights) vs untrained control over held-out seeds."""
    if SESSION.world is None:
        raise HTTPException(409, "no session")
    body = body or {}
    n = min(max(int(body.get("seeds", 10)), 1), 50)
    start = int(body.get("start_seed", 9000))
    trained, untrained = [], []
    for s in range(start, start + n):
        SESSION.world.reset(seed=s, keep_weights=True)
        trained.append(SESSION.world.run(learning=False)["food_eaten"])
        untrained.append(
            World2D(_cfg_with_seed(SESSION.config, s)).run(learning=False)["food_eaten"])
    import statistics as st
    return {
        "seeds": list(range(start, start + n)),
        "trained": trained, "untrained": untrained,
        "trained_mean": round(st.mean(trained), 3),
        "untrained_mean": round(st.mean(untrained), 3),
    }


def _cfg_with_seed(cfg: WorldConfig, seed: int) -> WorldConfig:
    d = cfg.as_dict(); d["seed"] = seed
    return WorldConfig(**d)


@app.post("/api/save")
def save(body: dict | None = None):
    if SESSION.world is None:
        raise HTTPException(409, "no session")
    from neuralmind.experiments.base import ExperimentResult
    w = SESSION.world
    result = ExperimentResult(
        name="playground_episode", status="exploratory",
        config=SESSION.config.as_dict(),
        metrics={"food_eaten": float(w.food_eaten), "survival": float(w.t),
                 "total_reward": float(w.total_reward),
                 "hazard_hits": float(w.hazard_hits)},
        series={"episode_rewards": SESSION.episode_rewards},
        notes=[(body or {}).get("note", "")],
    )
    rid = SESSION.store.save(result)
    return {"id": rid}


@app.get("/api/runs")
def runs():
    return {"runs": SESSION.store.list()}


@app.get("/api/health")
def health():
    return {"ok": True, "has_session": SESSION.world is not None}


@app.get("/")
def index():
    return FileResponse(_WEBUI / "index.html")


if _WEBUI.exists():
    app.mount("/static", StaticFiles(directory=str(_WEBUI)), name="static")


def main() -> None:
    import uvicorn
    print("NeuralMind Playground -> http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


if __name__ == "__main__":
    main()

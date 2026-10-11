"""Integration tests for the FastAPI backend (real engine, no mocks)."""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from neuralmind.server import app, SESSION  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    # Point persistence at a temp DB so tests don't touch the real file.
    from neuralmind.persistence.store import ExperimentStore
    SESSION.store = ExperimentStore(tmp_path / "t.sqlite")
    return TestClient(app)


def test_session_returns_layout_and_state(client):
    r = client.post("/api/session", json={"seed": 0, "n_food": 6})
    assert r.status_code == 200
    d = r.json()
    assert len(d["layout"]["matrix"]) == len(d["layout"]["matrix"][0])
    assert d["node_order"][0] == "sensory"
    assert set(("agent", "food", "action", "scores", "glow")).issubset(d["state"])


def test_step_advances_and_moves_agent(client):
    client.post("/api/session", json={"seed": 1})
    r = client.post("/api/step", json={"n": 20, "learning": True})
    d = r.json()
    assert len(d["frames"]) == 20
    # Agent position changes across the episode (actions affect the world).
    first = d["frames"][0]["agent"]
    last = d["frames"][-1]["agent"]
    assert first != last


def test_step_without_session_is_conflict(client):
    SESSION.world = None
    assert client.post("/api/step", json={"n": 1}).status_code == 409


def test_config_bounds_are_clamped(client):
    r = client.post("/api/session", json={"n_food": 99999, "lr": -5})
    cfg = r.json()["config"]
    assert cfg["n_food"] <= 30      # clamped to upper bound
    assert cfg["lr"] >= 0.0         # clamped to lower bound


def test_reset_same_seed_is_reproducible(client):
    client.post("/api/session", json={"seed": 42})
    a = client.post("/api/step", json={"n": 10, "learning": False}).json()
    client.post("/api/reset", json={"seed": 42})
    b = client.post("/api/step", json={"n": 10, "learning": False}).json()
    assert a["frames"][-1]["agent"] == b["frames"][-1]["agent"]


def test_save_and_list_runs(client):
    client.post("/api/session", json={"seed": 0})
    client.post("/api/step", json={"n": 5})
    rid = client.post("/api/save", json={"note": "hi"}).json()["id"]
    runs = client.get("/api/runs").json()["runs"]
    assert any(run["id"] == rid for run in runs)


def test_place_food_adds_item(client):
    d0 = client.post("/api/session", json={"seed": 0, "n_food": 3}).json()
    n0 = len(d0["state"]["food"])
    d = client.post("/api/place_food", json={"x": 0.5, "y": 0.5}).json()
    assert len(d["food"]) == n0 + 1


def test_deprive_clears_food_and_starves(client):
    client.post("/api/session", json={"seed": 0, "n_food": 8, "e0": 0.2})
    client.post("/api/deprive", json={"on": True})
    # With no food and energy draining, the agent should die within the episode.
    out = client.post("/api/step", json={"n": 60, "learning": False}).json()
    assert out["frames"][-1]["deprive"] is True
    # no food remains to eat
    assert out["frames"][-1]["food"] == []
    assert "hunger" in out["frames"][-1] and "affect" in out["frames"][-1]


def test_frame_has_day_and_affect(client):
    client.post("/api/session", json={"seed": 0})
    f = client.post("/api/step", json={"n": 1}).json()["frames"][0]
    assert "day" in f and "hunger" in f
    assert set(("valence", "arousal", "threat")).issubset(f["affect"])


def test_glow_matches_node_count(client):
    d = client.post("/api/session", json={"seed": 0}).json()
    total = sum(d["sizes"].values())
    frame = client.post("/api/step", json={"n": 1}).json()["frames"][0]
    assert len(frame["glow"]) == total


def test_multi_agent_session(client):
    d = client.post("/api/session", json={"seed": 0, "n_agents": 4}).json()
    assert d["config"]["n_agents"] == 4
    assert len(d["state"]["agents"]) == 4
    f = client.post("/api/step", json={"n": 5}).json()["frames"][-1]
    assert len(f["agents"]) == 4
    # each agent has its own brain activity vector
    assert all(len(a["glow"]) == len(f["agents"][0]["glow"]) for a in f["agents"])


def test_advance_days_starvation_snapshots(client):
    client.post("/api/session", json={"seed": 0, "ticks_per_day": 20})
    client.post("/api/deprive", json={"on": True})
    d = client.post("/api/advance", json={"days": 3}).json()
    snaps = d["snapshots"]
    assert [s["day"] for s in snaps] == [1.0, 2.0, 3.0]
    # without food, energy strictly falls and hunger rises day over day
    assert snaps[0]["energy"] > snaps[1]["energy"] > snaps[2]["energy"]
    assert snaps[0]["hunger"] < snaps[2]["hunger"]
    assert set(snaps[0]["firing"]) == {"sensory", "left", "forward", "right"}


def test_brain_endpoint_returns_that_agents_own_weights(client):
    client.post("/api/session", json={"seed": 0, "n_agents": 3, "social": True})
    client.post("/api/step", json={"n": 30})
    a = client.get("/api/brain/0").json()
    b = client.get("/api/brain/1").json()
    assert a["node_order"] == b["node_order"]
    assert "attack" in a["node_order"]
    assert a["layout"]["matrix"] != b["layout"]["matrix"]   # different individuals
    assert client.get("/api/brain/99").status_code == 404


def test_evolve_session_reports_population(client):
    d = client.post("/api/session", json={"seed": 0, "n_agents": 4, "social": True,
                                          "evolve": True}).json()
    assert d["config"]["evolve"] is True
    f = client.post("/api/step", json={"n": 5}).json()["frames"][-1]
    assert f["evolve"] is True and f["population"] >= 1
    assert "generation" in f["agents"][0]

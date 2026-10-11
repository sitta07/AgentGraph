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


def test_glow_matches_node_count(client):
    d = client.post("/api/session", json={"seed": 0}).json()
    total = sum(d["sizes"].values())
    frame = client.post("/api/step", json={"n": 1}).json()["frames"][0]
    assert len(frame["glow"]) == total

"""The framework-free Playground API that the browser build calls through Pyodide."""

import json

from neuralmind.playground import Session, dispatch


def call(session, path, body=None):
    status, text = dispatch(session, path, None if body is None else json.dumps(body))
    return status, json.loads(text)


def test_dispatch_runs_a_session_end_to_end():
    s = Session()
    status, info = call(s, "/api/session", {"seed": 0, "n_agents": 3, "social": True, "evolve": True})
    assert status == 200 and len(info["state"]["agents"]) == 3
    status, out = call(s, "/api/step", {"n": 5})
    assert status == 200 and len(out["frames"]) == 5
    status, b = call(s, "/api/brain/0")
    assert status == 200 and b["id"] == 0
    status, lin = call(s, "/api/lineage?limit=2")
    assert status == 200 and len(lin["records"]) == 2
    status, saved = call(s, "/api/save", {"note": "x"})
    assert status == 200 and saved["id"] is None
    assert saved["download"]["name"] == "playground_episode"
    assert saved["download"]["notes"] == ["x"]


def test_dispatch_matches_the_same_seeded_world():
    a, b = Session(), Session()
    call(a, "/api/session", {"seed": 7})
    call(b, "/api/session", {"seed": 7})
    fa = call(a, "/api/step", {"n": 10, "learning": False})[1]["frames"][-1]
    fb = call(b, "/api/step", {"n": 10, "learning": False})[1]["frames"][-1]
    assert fa["agent"] == fb["agent"]


def test_dispatch_errors_carry_http_status_and_detail():
    s = Session()
    assert call(s, "/api/step", {"n": 1}) == (409, {"detail": "no session; POST /api/session first"})
    call(s, "/api/session", {})
    assert call(s, "/api/brain/99")[0] == 404
    assert call(s, "/api/brain/x")[0] == 422
    assert call(s, "/api/session", {"lr": "abc"})[0] == 400
    assert call(s, "/api/nope", {})[0] == 404
    assert call(s, "/api/step")[0] == 404          # GET on a POST route

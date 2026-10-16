"""Tests for declarative pre-registered study specs."""

import json

import pytest

from neuralmind.research.spec import decide, load, preregistration, run, write


def _spec(tmp_path, **over):
    spec = {"id": "T", "title": "t", "question": "q", "simulator": "evolution",
            "seeds": 2, "ticks": 60, "base": {"n_agents": 4, "max_pop": 8},
            "conditions": {"a": {"config": {"n_food": 30}, "learning": True},
                           "b": {"config": {"n_food": 10}, "learning": True}},
            "hypotheses": [{"id": "H", "statement": "s", "metric": "final_pop",
                            "a": "a", "b": "b", "direction": "greater"}]}
    spec.update(over)
    p = tmp_path / "s.json"
    p.write_text(json.dumps(spec))
    return p


def test_committed_specs_are_valid():
    from pathlib import Path
    for f in sorted(Path("studies").glob("*.json")):
        load(f)


def test_load_rejects_unknown_condition(tmp_path):
    p = _spec(tmp_path, hypotheses=[{"id": "H", "statement": "s", "metric": "m",
                                     "a": "zzz", "b": "b", "direction": "greater"}])
    with pytest.raises(ValueError):
        load(p)


def test_decide_rules():
    ci = lambda lo, m, hi: {"lo": lo, "mean": m, "hi": hi}
    assert decide(ci(0.1, 0.2, 0.3), "greater") == "supported"
    assert decide(ci(-0.1, 0.2, 0.3), "greater") == "not supported"
    assert decide(ci(-0.3, -0.2, -0.1), "less") == "supported"
    assert decide(ci(-0.1, 0.0, 0.1), "none") == "no difference detected"


def test_uncommitted_spec_is_not_marked_preregistered(tmp_path):
    assert preregistration(_spec(tmp_path))["preregistered"] is False


def test_run_and_write_end_to_end(tmp_path):
    p = _spec(tmp_path)
    res = run(load(p), p, seeds=2, ticks=60)
    assert set(res["verdict"]) == {"H"}
    assert res["deviations"] == {}
    rep = write(res, tmp_path / "out")
    assert "Pre-registration" in rep.read_text()


def test_numeric_b_is_a_one_sample_test(tmp_path):
    p = _spec(tmp_path, hypotheses=[{"id": "H", "statement": "s", "metric": "final_pop",
                                     "a": "a", "b": 0, "direction": "greater"}])
    res = run(load(p), p, seeds=2, ticks=60)
    assert res["verdict"]["H"] in ("supported", "not supported")


def test_seed_start_uses_fresh_seeds(tmp_path):
    p = _spec(tmp_path, seed_start=50)
    res = run(load(p), p, seeds=2, ticks=40)
    assert res["design"]["seed_start"] == 50
    assert "pop_cv" in res["summary"]["a"]


def test_single_agent_simulator_end_to_end(tmp_path):
    p = _spec(tmp_path, simulator="single", base={}, ticks=40, train_episodes=2, test_worlds=2,
              conditions={"a": {"config": {}}, "b": {"config": {"reset_each_decision": True}}},
              hypotheses=[{"id": "H", "statement": "s", "metric": "trained_food",
                           "a": "a", "b": "b", "direction": "none"}])
    res = run(load(p), p)
    r = res["raw"]["a"][0]
    assert r["learning_gain"] == r["trained_food"] - r["untrained_food"]
    assert res["design"]["train_episodes"] == 2
    assert "trained_food" in write(res, tmp_path / "out").read_text()

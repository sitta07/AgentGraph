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

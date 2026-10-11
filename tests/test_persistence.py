"""Tests for the SQLite experiment store and round-tripping."""

from neuralmind.experiments.base import ExperimentResult
from neuralmind.persistence.store import ExperimentStore


def _sample():
    return ExperimentResult(
        name="demo",
        status="exploratory",
        config={"seed": 0, "n": 3},
        metrics={"score": 0.75},
        series={"x": [1, 2, 3]},
        notes=["a note"],
    )


def test_save_and_reload_roundtrip(tmp_path):
    db = tmp_path / "exp.sqlite"
    with ExperimentStore(db) as store:
        rid = store.save(_sample())
        loaded = store.get(rid)
    assert loaded is not None
    assert loaded.name == "demo"
    assert loaded.config == {"seed": 0, "n": 3}
    assert loaded.metrics["score"] == 0.75
    assert loaded.series["x"] == [1, 2, 3]
    assert loaded.notes == ["a note"]


def test_list_returns_newest_first(tmp_path):
    db = tmp_path / "exp.sqlite"
    with ExperimentStore(db) as store:
        first = store.save(_sample())
        second = store.save(_sample())
        rows = store.list()
    assert [r["id"] for r in rows] == [second, first]


def test_get_missing_returns_none(tmp_path):
    with ExperimentStore(tmp_path / "exp.sqlite") as store:
        assert store.get(999) is None


def test_persistence_survives_reopen(tmp_path):
    db = tmp_path / "exp.sqlite"
    with ExperimentStore(db) as store:
        rid = store.save(_sample())
    # Reopen a fresh connection to the same file.
    with ExperimentStore(db) as store2:
        assert store2.get(rid) is not None

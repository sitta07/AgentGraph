"""SQLite-backed store for experiment runs.

Stores each :class:`~neuralmind.experiments.base.ExperimentResult` with its full
configuration, metrics, series and notes as JSON so a run can be reloaded and
inspected later. Uses only the Python standard library (``sqlite3`` + ``json``),
so no external service or API key is required.

This is the *experiment history*. It is deliberately kept separate from
learned synaptic weights, simulation state, and any document/knowledge index:
those are different kinds of memory and must not be conflated.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from neuralmind.experiments.base import ExperimentResult

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    status    TEXT NOT NULL,
    created   TEXT NOT NULL,
    config    TEXT NOT NULL,
    metrics   TEXT NOT NULL,
    series    TEXT NOT NULL,
    notes     TEXT NOT NULL
);
"""


class ExperimentStore:
    """A tiny persistence layer for experiment results."""

    def __init__(self, path: str | Path = "neuralmind_experiments.sqlite") -> None:
        self.path = str(path)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def save(self, result: ExperimentResult) -> int:
        """Persist a result and return its new row id."""
        cur = self._conn.execute(
            "INSERT INTO runs (name, status, created, config, metrics, series, notes)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                result.name,
                result.status,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(result.config),
                json.dumps(result.metrics),
                json.dumps(result.series),
                json.dumps(result.notes),
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def get(self, run_id: int) -> ExperimentResult | None:
        """Reload a stored run as an :class:`ExperimentResult`."""
        row = self._conn.execute(
            "SELECT * FROM runs WHERE id = ?", (run_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_result(row)

    def list(self, name: str | None = None) -> list[dict]:
        """List run summaries (id, name, status, created, metrics), newest first."""
        if name is None:
            rows = self._conn.execute(
                "SELECT id, name, status, created, metrics FROM runs ORDER BY id DESC"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id, name, status, created, metrics FROM runs"
                " WHERE name = ? ORDER BY id DESC",
                (name,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "status": r["status"],
                "created": r["created"],
                "metrics": json.loads(r["metrics"]),
            }
            for r in rows
        ]

    @staticmethod
    def _row_to_result(row: sqlite3.Row) -> ExperimentResult:
        return ExperimentResult(
            name=row["name"],
            status=row["status"],
            config=json.loads(row["config"]),
            metrics=json.loads(row["metrics"]),
            series=json.loads(row["series"]),
            notes=json.loads(row["notes"]),
        )

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "ExperimentStore":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

"""Tests for the recorder and the HTML viewer writer."""

import json

import numpy as np

from neuralmind.core.network import Connection, SpikingNetwork
from neuralmind.core.neurons import LIFPopulation
from neuralmind.recorder import build_layout, record
from neuralmind.viz import render_html


def _net(dt=1.0):
    net = SpikingNetwork(dt=dt)
    net.add_population("a", LIFPopulation(5, dt=dt))
    net.add_population("b", LIFPopulation(5, dt=dt))
    net.connect(Connection("a", "b", weights=np.full((5, 5), 20.0)))
    net.build()
    return net


def test_record_shapes_and_rates():
    net = _net()
    rec = record(net, steps=30, external={"a": 6.0},
                 extra_series=lambda i: {"drive": 6.0})
    assert rec.n_steps == 30
    assert set(rec.populations) == {"a", "b"}
    assert len(rec.spikes["a"]) == 30
    assert len(rec.rate["a"]) == 30
    assert all(r >= 0 for r in rec.rate["a"])
    assert len(rec.series["drive"]) == 30
    # Driven population 'a' should fire at least once.
    assert any(len(s) > 0 for s in rec.spikes["a"])


def test_recording_json_roundtrips():
    net = _net()
    rec = record(net, steps=10, external={"a": 6.0})
    blob = json.dumps(rec.to_json_dict())
    data = json.loads(blob)
    assert data["n_steps"] == 10
    assert data["sizes"]["a"] == 5


def test_render_html_is_self_contained(tmp_path):
    net = _net()
    rec = record(net, steps=20, external={"a": 6.0})
    out = render_html(rec, tmp_path / "view.html", title="T")
    html = out.read_text(encoding="utf-8")
    assert "<!doctype html>" in html.lower()
    assert "NeuralMind" in html or "T" in html
    # Embedded data, no external script/stylesheet dependencies.
    assert "application/json" in html
    assert "http://" not in html and "https://" not in html
    assert "<canvas" in html


def test_build_layout_nodes_edges_matrix():
    net = _net()
    lay = build_layout(net, seed=0)
    assert lay["total"] == 10          # 5 + 5 neurons
    assert len(lay["nodes"]) == 10
    assert len(lay["matrix"]) == 10 and len(lay["matrix"][0]) == 10
    # Every node has a population and 3-D coords in range.
    for n in lay["nodes"]:
        assert n["p"] in {"a", "b"}
        assert all(-2.0 <= n[k] <= 2.0 for k in ("x", "y", "z"))
    # Edges reference valid global indices and carry the weight.
    assert lay["edges"]
    for e in lay["edges"]:
        assert 0 <= e["s"] < 10 and 0 <= e["t"] < 10


def test_record_with_layout_captures_activity():
    net = _net()
    rec = record(net, steps=15, external={"a": 6.0}, layout=True)
    assert len(rec.nodes) == 10
    assert len(rec.activity) == 15
    assert all(len(frame) == 10 for frame in rec.activity)
    # Activity is a bounded glow in [0, 1].
    assert all(0.0 <= v <= 1.0 for frame in rec.activity for v in frame)
    # The driven population should light up at some point.
    assert max(max(f) for f in rec.activity) > 0.0


def test_render_html_brain_view_is_self_contained(tmp_path):
    net = _net()
    rec = record(net, steps=12, external={"a": 6.0}, layout=True)
    html = render_html(rec, tmp_path / "b.html").read_text(encoding="utf-8")
    assert "net3d" in html and "matrix" in html
    assert "http://" not in html and "https://" not in html


def test_extra_series_recorded_rounded():
    net = _net()
    rec = record(net, steps=5, external={"a": 6.0},
                 extra_series=lambda i: {"x": i * 0.123456})
    assert rec.series["x"][2] == round(2 * 0.123456, 4)

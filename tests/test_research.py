"""Tests for research statistics and the social simulation harness."""

import math

import numpy as np
import pytest

from neuralmind.research.social import heatmap_svg, simulate
from neuralmind.research.stats import gini, mean_ci, paired_diff


def test_mean_ci_contains_mean_and_ignores_nan():
    ci = mean_ci([1.0, 2.0, 3.0, float("nan")])
    assert ci["n"] == 3
    assert ci["lo"] <= ci["mean"] == 2.0 <= ci["hi"]


def test_mean_ci_empty_and_single():
    assert math.isnan(mean_ci([])["mean"])
    assert mean_ci([5.0])["lo"] == 5.0


def test_paired_diff_detects_shift():
    a = np.arange(20) + 1.0
    ci = paired_diff(a, a - 1.0)
    assert ci["lo"] == ci["hi"] == 1.0


def test_gini_bounds():
    assert gini([1, 1, 1, 1]) == 0.0
    assert gini([0, 0, 0, 4]) > 0.7


def test_simulate_returns_rates_that_sum_to_one():
    r = simulate({"seed": 0, "n_agents": 3}, ticks=40)
    total = sum(r["rates_pre"].values())
    assert abs(total - 1.0) < 1e-9
    assert 0.0 <= r["encounter_share_pre"] <= 1.0


def test_simulate_deprivation_phase_split():
    r = simulate({"seed": 1, "n_agents": 3}, ticks=40, deprive_at=20)
    assert r["alive_ticks_pre"] > 0 and r["alive_ticks_post"] >= 0


def test_heatmap_svg_is_valid_markup():
    grid = {f"{f}|{r}": {"attack_rate": {"mean": 0.1 * f}} for f in (1, 2) for r in (0, 1)}
    svg = heatmap_svg(grid, [1, 2], [0, 1], "attack_rate", "t")
    assert svg.startswith("<svg") and svg.endswith("</svg>")


def test_evolution_run_produces_births_and_series():
    from neuralmind.research.evolution import run_evolution
    r = run_evolution({"seed": 0, "n_agents": 6, "max_pop": 12}, ticks=120, learning=True,
                      sample_every=40)
    assert r["births"] >= 0
    assert len(r["series"]["t"]) == 3
    assert not r["extinct"] or r["final_pop"] == 0


def test_relatedness_genealogy():
    from neuralmind.world import World2D, WorldConfig
    w = World2D(WorldConfig(seed=0, n_agents=2, social=True, evolve=True))
    p = w.agents[0]
    p.energy = 2.0
    c1 = w._birth(p)
    p.energy = 2.0
    c2 = w._birth(p)
    assert w.relatedness(p, c1) == 0.5
    assert w.relatedness(c1, c2) == 0.25
    assert w.relatedness(c1, w.agents[1]) == 0.0
    assert c1.generation == 1 and c1.lineage == p.lineage


def test_mutual_information_and_g_test():
    from neuralmind.research.stats import g_test_p, mutual_information
    assert mutual_information([[50, 0], [0, 50]]) == pytest.approx(1.0)
    assert mutual_information([[25, 25], [25, 25]]) == pytest.approx(0.0)
    assert g_test_p([[50, 0], [0, 50]]) < 1e-10
    assert g_test_p([[25, 25], [25, 25]]) > 0.99
    assert 0.0 <= g_test_p([[10, 20, 30], [30, 20, 10]]) < 0.01

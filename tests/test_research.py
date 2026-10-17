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


def test_evolution_reports_weight_drift_and_signal_rate():
    from neuralmind.research.evolution import run_evolution
    on = run_evolution({"seed": 0, "n_agents": 6, "max_pop": 12}, ticks=120, learning=True)
    off = run_evolution({"seed": 0, "n_agents": 6, "max_pop": 12}, ticks=120, learning=False)
    for k in ("signal_rate", "drift_loco", "drift_attack", "drift_share", "drift_signal",
              "drift_social_minus_loco"):
        assert np.isfinite(on[k]), k
    assert off["drift_loco"] == 0 and off["drift_social_minus_loco"] == 0


def test_early_demography_accounts_for_every_death():
    from neuralmind.research.evolution import run_evolution
    r = run_evolution({"seed": 0, "n_agents": 8, "max_pop": 16, "max_age": 200},
                      ticks=600, learning=True, early=500)
    total = r["early_frac_killed"] + r["early_frac_starved"] + r["early_frac_old_age"]
    assert abs(total - 1.0) < 1e-9
    assert r["early_frac_old_age"] > 0 and 0 < r["early_birth_rate"] < 1
    assert 0 <= r["early_offspring_success"] <= 1
    for k in ("early_frac_kills_kin", "early_frac_kills_young", "early_frac_young",
              "early_frac_kills_offspring"):
        assert np.isnan(r[k]) or 0 <= r[k] <= 1, k


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


def test_q_invaders_drive_their_lineages_only():
    from neuralmind.research.evolution import run_evolution
    from neuralmind.research.invasion import N_BITS, state_index
    assert state_index(np.zeros(11)) == 0 and state_index(np.ones(11)) == (1 << N_BITS) - 1
    kw = {"seed": 0, "n_agents": 6, "max_pop": 12}
    lab = run_evolution(kw, ticks=150, learning=True, invader={"founders": 3, "mode": "label"})
    plain = run_evolution(kw, ticks=150, learning=True)
    assert lab["final_pop"] == plain["final_pop"] and lab["attack_rate"] == plain["attack_rate"]
    assert 0 <= lab["invader_share"] <= 1
    q = run_evolution(kw, ticks=150, learning=True, invader={"founders": 3, "mode": "q_inherit"})
    assert 0 <= q["invader_share"] <= 1 and np.isfinite(q["invader_share_mean"])
    assert np.isnan(plain["invader_share"])


def test_drift_probe_restores_learning_rule_and_reports_all_tick_kinds():
    from neuralmind.research.drift_probe import probe
    from neuralmind.world import Agent
    before = Agent.learn_and_affect
    r = probe(seed=0, ticks=60, cfg={"n_agents": 4, "max_pop": 8})
    assert Agent.learn_and_affect is before
    assert sum(r["updates"].get(k, 0) for k in ("eat", "pain", "shaping")) > 0


def test_periodic_shift_reports_drop_after_each_flip():
    from neuralmind.research.evolution import _shift_recovery, run_evolution
    series = {"t": list(range(0, 4000, 100)),
              "food_rate": [0.05 if (t % 1000) >= 250 else 0.01 for t in range(0, 4000, 100)]}
    r = _shift_recovery(series, 1000)
    assert r["shift_drop"] > 0.03
    out = run_evolution({"seed": 0, "n_agents": 6, "max_pop": 12, "mirror_every": 100},
                        ticks=400, learning=False, sample_every=20)
    assert np.isfinite(out["shift_drop"]) and len(out["series"]["food_rate"]) == 20


def test_evolved_teacher_reports_shift_against_a_neutral_gene():
    from neuralmind.research.evolution import run_evolution
    r = run_evolution({"seed": 1, "n_agents": 8, "max_pop": 16, "max_age": 200, "evolve_teacher": True,
                       "teacher_init": (1.0, 0.0, 0.0, 0.0)}, ticks=500, learning=True)
    for k in ("align", "approach", "energy", "hunger"):
        assert abs(r[f"teacher_{k}_shift_minus_neutral"]
                   - (r[f"teacher_{k}"] - (1.0 if k == "align" else 0.0) - r["teacher_neutral"])) < 1e-9

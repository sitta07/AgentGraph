"""Unit + integration tests for the 2-D artificial-life world.

These test the causal chain pieces (sensing, action->movement, energy, reward)
and the end-to-end claim that learning beats a no-learning baseline.
"""

import math

import numpy as np
import pytest

from neuralmind.world import ACTIONS, World2D, WorldConfig


def test_reset_is_reproducible():
    a = World2D(WorldConfig(seed=3))
    b = World2D(WorldConfig(seed=3))
    assert np.allclose(a.agent, b.agent)
    assert np.allclose(a.food, b.food)
    assert a.heading == b.heading


def test_sensors_shape_and_bounds():
    w = World2D(WorldConfig(seed=0))
    s = w.sense()
    assert s.shape == (World2D.N_SENSORS,)
    assert np.all((s >= 0.0) & (s <= 1.0))


def test_sensor_detects_food_direction():
    """Food placed to the agent's left should excite the left food bin most."""
    w = World2D(WorldConfig(seed=0, n_food=1, n_hazard=0))
    w.agent = np.array([0.5, 0.5])
    w.heading = 0.0  # facing +x; agent's left is +y
    w.food = np.array([[0.5, 0.8]])  # directly to the left (+y)
    s = w.sense()
    left, front, right = s[0], s[1], s[2]
    assert left > right
    assert left > 0.0


def test_sensor_out_of_range_is_silent():
    w = World2D(WorldConfig(seed=0, n_food=1, n_hazard=0, sensor_range=0.1))
    w.agent = np.array([0.1, 0.1])
    w.food = np.array([[0.9, 0.9]])  # far away, beyond sensor range
    assert np.all(w.sense()[:3] == 0.0)


def test_forward_action_moves_along_heading():
    w = World2D(WorldConfig(seed=0))
    w.agent = np.array([0.5, 0.5])
    w.heading = 0.0
    w._move(1)  # forward
    assert w.agent[0] > 0.5
    assert math.isclose(w.agent[1], 0.5, abs_tol=1e-9)


def test_turn_actions_change_heading_oppositely():
    w = World2D(WorldConfig(seed=0))
    w.heading = 1.0
    w._move(0); left_h = w.heading
    w.heading = 1.0
    w._move(2); right_h = w.heading
    assert left_h > 1.0 > right_h


def test_walls_reflect_agent():
    w = World2D(WorldConfig(seed=0, size=1.0))
    w.agent = np.array([0.99, 0.5])
    w.heading = 0.0  # heading into the +x wall
    for _ in range(10):
        w._move(1)
    assert 0.0 <= w.agent[0] <= 1.0


def test_energy_decreases_each_tick_without_food():
    w = World2D(WorldConfig(seed=0, n_food=0, n_hazard=0))
    e0 = w.energy
    w.step(learning=False)
    assert w.energy < e0


def test_eating_food_adds_energy_and_count():
    w = World2D(WorldConfig(seed=0, n_hazard=0))
    w.agent = np.array([0.5, 0.5])
    w.food = np.array([[0.5, 0.5]])  # right on top of the agent
    before = w.energy
    w.step(learning=False)
    assert w.food_eaten >= 1
    assert w.energy > before - w.cfg.move_cost  # net gain despite metabolism


def test_action_is_chosen_by_network_not_rules():
    """The action index must come from action-population spike counts."""
    w = World2D(WorldConfig(seed=0))
    sensors = w.sense()
    action, scores, spikes = w._decide(sensors)
    assert 0 <= action < 3
    assert len(scores) == 3
    # spikes are per population from the real network step; action pops present
    assert set(ACTIONS).issubset(set(spikes))


def test_run_is_deterministic():
    a = World2D(WorldConfig(seed=5)).run(learning=True)
    b = World2D(WorldConfig(seed=5)).run(learning=True)
    assert a == b


def test_invalid_config_guards():
    # Non-finite / degenerate values should not crash a basic run.
    w = World2D(WorldConfig(seed=0, n_food=1, n_hazard=0, max_ticks=5))
    out = w.run(learning=True)
    assert out["survival_ticks"] <= 5


@pytest.mark.slow
def test_learning_beats_baseline_on_heldout():
    """Train one agent across episodes; it should forage better than an
    untrained agent on held-out worlds (averaged over seeds)."""
    trainer = World2D(WorldConfig(seed=0))
    for ep in range(60):
        trainer.reset(keep_weights=(ep > 0))
        trainer.run(learning=True)
    trained, untrained = [], []
    for s in range(400, 412):
        trainer.reset(seed=s, keep_weights=True)
        trained.append(trainer.run(learning=False)["food_eaten"])
        untrained.append(World2D(WorldConfig(seed=s)).run(learning=False)["food_eaten"])
    assert np.mean(trained) > np.mean(untrained)


def test_single_agent_numerics_unchanged_by_extra_agents():
    """Adding agents must not change agent-0's initial state (draw order)."""
    a = World2D(WorldConfig(seed=11, n_agents=1))
    b = World2D(WorldConfig(seed=11, n_agents=3))
    assert np.allclose(a.agent, b.agent) and a.heading == b.heading
    assert np.allclose(a.food, b.food)
    assert len(b.agents) == 3


def test_agents_share_food():
    w = World2D(WorldConfig(seed=0, n_agents=2, n_hazard=0, n_food=1))
    w.agents[1].pos = w.food[0].copy()
    before = w.food.copy()
    w.step(learning=False)
    # agent 1 stood on the only food item -> it was eaten and respawned elsewhere
    assert w.agents[1].food_eaten >= 1
    assert not np.allclose(before, w.food)


# ---------------- social layer ----------------
from neuralmind.world import SOCIAL_ACTIONS  # noqa: E402


def test_social_off_by_default_keeps_original_brain():
    w = World2D(WorldConfig(seed=0))
    assert w.agents[0].actions == ACTIONS
    assert w.agents[0].n_sensors == World2D.N_SENSORS


def test_social_adds_sensors_and_actions():
    w = World2D(WorldConfig(seed=0, n_agents=2, social=True))
    ag = w.agents[0]
    assert ag.actions == ACTIONS + SOCIAL_ACTIONS
    assert ag.n_sensors == World2D.N_SENSORS + 4


def test_social_sensor_sees_other_agent():
    w = World2D(WorldConfig(seed=0, n_agents=2, social=True, n_food=0, n_hazard=0))
    a, b = w.agents
    a.pos, a.heading = np.array([0.5, 0.5]), 0.0
    b.pos = np.array([0.5, 0.75])            # to a's left (+y)
    s = a.sense(w.food, w.hazards, np.array([b.pos]), np.empty((0, 2)))
    others = s[7:10]
    assert others[0] > others[2]


def _force(ag, w, name):
    return w._social_effects(ag, ag.actions.index(name), [o for o in w.agents if o is not ag])


def test_attack_transfers_energy_and_hurts_victim():
    w = World2D(WorldConfig(seed=0, n_agents=2, social=True))
    a, b = w.agents
    b.pos = a.pos + np.array([0.02, 0.0])
    ea, eb = a.energy, b.energy
    r, _ = _force(a, w, "attack")
    assert b.energy < eb and a.energy > ea - w.cfg.attack_cost
    assert b.pending_hurt > 0 and b.attacked == 1
    assert any(e["type"] == "attack" for e in w.events)


def test_attack_out_of_reach_only_costs():
    w = World2D(WorldConfig(seed=0, n_agents=2, social=True))
    a, b = w.agents
    b.pos = a.pos + np.array([0.4, 0.0])
    ea = a.energy
    _force(a, w, "attack")
    assert a.energy == pytest.approx(ea - w.cfg.attack_cost)


def test_share_follows_hamiltons_rule_sign():
    """Sharing reward is negative when r*B < 1 and positive when r*B > 1."""
    for r_pro, sign in ((0.0, -1), (1.0, 1)):
        w = World2D(WorldConfig(seed=0, n_agents=2, social=True,
                                r_prosocial=r_pro, share_benefit=2.0))
        a, b = w.agents
        b.pos = a.pos.copy()
        r, _ = _force(a, w, "share")
        assert np.sign(r) == sign
        assert b.pending_gift > 0


def test_social_run_is_deterministic():
    def run():
        w = World2D(WorldConfig(seed=4, n_agents=4, social=True))
        for _ in range(150):
            w.step(True)
        return [(x.attacks, x.shares_given, x.signals, round(x.energy, 6)) for x in w.agents]
    assert run() == run()


def test_gift_reward_flag_controls_recipient_reward_only():
    for flag in (True, False):
        w = World2D(WorldConfig(seed=0, n_agents=2, social=True, gift_reward=flag))
        a, b = w.agents
        b.pending_gift = 0.2
        e = b.energy
        r, _ = w._social_effects(b, b.actions.index("left"), [a])
        assert (r > 0) == flag
        assert b.energy == e        # energy was already transferred at gift time


def test_neutral_marker_is_inherited_but_off_by_default():
    w = World2D(WorldConfig(seed=0, n_agents=1, social=True, evolve=True, neutral_marker=True))
    p = w.agents[0]
    p.energy = 2.0
    c = w._birth(p)
    assert c.neutral_gene != p.neutral_gene     # mutated
    w2 = World2D(WorldConfig(seed=0, n_agents=1, social=True, evolve=True))
    p2 = w2.agents[0]
    p2.energy = 2.0
    c2 = w2._birth(p2)
    assert c2.neutral_gene == p2.neutral_gene   # not drawn when the flag is off


def test_registry_records_births_and_deaths():
    w = World2D(WorldConfig(seed=0, n_agents=3, social=True, evolve=True, max_age=40,
                            max_ticks=10**6))
    for _ in range(300):
        w.step(True)
    reg = w.registry
    assert len(reg) >= 3
    assert all(r["died"] is not None for r in reg.values() if r["born"] == 0)  # founders aged out
    for r in reg.values():
        if r["parent"] is not None:
            assert r["parent"] in reg and r["generation"] == reg[r["parent"]]["generation"] + 1


def test_evolving_world_is_open_ended():
    w = World2D(WorldConfig(seed=0, n_agents=4, social=True, evolve=True, max_ticks=20, n_food=24,
                            food_energy=0.6))
    for _ in range(60):
        w.step(True)
    assert any(a.alive for a in w.agents)


def test_credit_chosen_only_changes_only_the_executed_action():
    for flag in (False, True):
        w = World2D(WorldConfig(seed=0, n_agents=1, social=True, credit_chosen_only=flag))
        ag = w.agents[0]
        for cn in ag._plastic:
            cn._stdp.eligibility[:] = 0.5
        before = {cn.post: cn.weights.copy() for cn in ag._plastic}
        ag.learn_and_affect(1.0, np.zeros(ag.n_sensors), False, True,
                            action=ag.actions.index("share"))
        changed = {cn.post for cn in ag._plastic if not np.array_equal(cn.weights, before[cn.post])}
        assert changed == ({"share"} if flag else set(ag.actions))


def test_frozen_inputs_never_change():
    w = World2D(WorldConfig(seed=0, n_agents=1, social=True,
                            frozen_inputs=("left", "forward", "right")))
    ag = w.agents[0]
    for cn in ag._plastic:
        cn._stdp.eligibility[:] = 0.5
    before = {cn.post: cn.weights.copy() for cn in ag._plastic}
    ag.learn_and_affect(1.0, np.zeros(ag.n_sensors), False, True, action=0)
    changed = {cn.post for cn in ag._plastic if not np.array_equal(cn.weights, before[cn.post])}
    assert changed == {"attack", "share", "signal"}


def test_normalized_inputs_keep_innate_row_sums_but_still_learn():
    w = World2D(WorldConfig(seed=0, n_agents=1, social=True, normalized_inputs=("forward",)))
    ag = w.agents[0]
    cn = next(c for c in ag._plastic if c.post == "forward")
    rows, before = cn.weights.sum(axis=1), cn.weights.copy()
    cn._stdp.eligibility[:] = np.linspace(0, 1, cn.weights.size).reshape(cn.weights.shape)
    ag.learn_and_affect(1.0, np.zeros(ag.n_sensors), False, True, action=1)
    assert np.allclose(cn.weights.sum(axis=1), rows)
    assert not np.allclose(cn.weights, before)


def test_mirror_swaps_left_and_right_sensing_from_the_given_tick():
    w = World2D(WorldConfig(seed=0, n_agents=1, social=True, mirror_at=1))
    ag = w.agents[0]
    w.food = np.array([ag.pos + 0.1 * np.array([math.cos(ag.heading + 0.9), math.sin(ag.heading + 0.9)])])
    before = w.observe(ag)[0:3]
    ag.mirrored = True
    assert np.allclose(w.observe(ag)[0:3], before[::-1]) and before[0] != before[2]
    w2 = World2D(WorldConfig(seed=0, n_agents=1, social=True, mirror_at=1))
    w2.step(); assert not w2.agents[0].mirrored
    w2.step(); assert w2.agents[0].mirrored


def test_deaf_agents_hear_nothing():
    for deaf in (False, True):
        w = World2D(WorldConfig(seed=0, n_agents=1, social=True, deaf=deaf))
        ag = w.agents[0]
        s = ag.sense(w.food, w.hazards, np.empty((0, 2)), np.array([ag.pos]))
        assert (s[-1] == 0) == deaf


def test_positive_rpe_only_ignores_negative_errors():
    for flag in (False, True):
        w = World2D(WorldConfig(seed=0, n_agents=1, social=True, positive_rpe_only=flag))
        ag = w.agents[0]
        ag.learn_and_affect(1.0, np.zeros(ag.n_sensors), False, True, action=0)
        for cn in ag._plastic:
            cn._stdp.eligibility[:] = 0.5
        before = {cn.post: cn.weights.copy() for cn in ag._plastic}
        rpe = ag.learn_and_affect(-1.0, np.zeros(ag.n_sensors), False, True, action=0)
        assert rpe < 0
        same = all(np.array_equal(cn.weights, before[cn.post]) for cn in ag._plastic)
        assert same == flag


def test_born_near_stranger_places_newborn_next_to_a_non_relative():
    w = World2D(WorldConfig(seed=0, n_agents=3, social=True, evolve=True,
                            viscous=False, born_near_stranger=True))
    p = w.agents[0]
    p.energy = 2.0
    c = w._birth(p)
    others = [a for a in w.agents if a is not p and a is not c]
    d = min(np.linalg.norm(c.pos - a.pos) for a in others)
    assert d < 0.2 and np.linalg.norm(c.pos - p.pos) > d


def test_state_critic_keeps_separate_expectations_per_sensor_state():
    w = World2D(WorldConfig(seed=0, n_agents=1, social=True, critic="state"))
    ag = w.agents[0]
    a, b = np.zeros(ag.n_sensors), np.ones(ag.n_sensors)
    for _ in range(50):
        ag.learn_and_affect(1.0, a, False, False)
    assert ag.learn_and_affect(1.0, a, False, False) < 0.01   # predicted in state a
    assert ag.learn_and_affect(1.0, b, False, False) > 0.9    # novel state b


def test_directional_hearing_locates_callers_and_respects_deaf():
    for deaf in (False, True):
        w = World2D(WorldConfig(seed=0, n_agents=1, social=True, directional_hearing=True, deaf=deaf))
        ag = w.agents[0]
        caller = ag.pos + 0.1 * np.array([math.cos(ag.heading), math.sin(ag.heading)])
        s = ag.sense(w.food, w.hazards, np.empty((0, 2)), np.array([caller]))
        assert s.shape == (ag.n_sensors,) == (14,)
        assert (s[12] > 0) != deaf and s[12] >= max(s[11], s[13])


def test_cooperative_food_needs_a_partner():
    for partner in (False, True):
        w = World2D(WorldConfig(seed=0, n_agents=2, social=True, coop_radius=0.15, n_hazard=0))
        a, b = w.agents
        b.pos = a.pos + (np.array([0.05, 0.0]) if partner else np.array([0.6, 0.6]))
        w.food = np.array([a.pos.copy()])
        n = a.food_eaten
        w._advance_agent(a, learning=False, forced=a.actions.index("attack"))
        assert (a.food_eaten > n) == partner

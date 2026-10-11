"""PettingZoo ParallelEnv wrapper — official API test + determinism."""

import numpy as np
import pytest

pytest.importorskip("pettingzoo")
from pettingzoo.test import parallel_api_test  # noqa: E402

from neuralmind.envs import parallel_env  # noqa: E402


@pytest.mark.parametrize("kw", [dict(n_rl=3), dict(n_rl=2, n_snn=2, config={"social": True})])
def test_official_parallel_api(kw):
    parallel_api_test(parallel_env(max_cycles=40, **kw), num_cycles=120)


def test_seeded_rollout_is_deterministic():
    def roll():
        env = parallel_env(n_rl=2, n_snn=2, config={"social": True}, max_cycles=30)
        obs, _ = env.reset(seed=5)
        trace = []
        while env.agents:
            acts = {a: (i + env.world.t) % 6 for i, a in enumerate(env.agents)}
            obs, rew, *_ = env.step(acts)
            trace.append(sorted((k, round(v, 9)) for k, v in rew.items()))
        return trace
    assert roll() == roll()


def test_external_actions_control_the_body():
    env = parallel_env(n_rl=1, config={"n_hazard": 0}, max_cycles=5)
    env.reset(seed=0)
    ag = env.world.agents[0]
    h0 = ag.heading
    env.step({"agent_0": 0})            # 'left' turns counter-clockwise
    assert np.isclose((ag.heading - h0) % (2 * np.pi), env.world.cfg.turn)


def test_evolve_rejected():
    with pytest.raises(ValueError):
        parallel_env(n_rl=2, config={"evolve": True})

"""Standard multi-agent RL interfaces to the NeuralMind world."""

from neuralmind.envs.pettingzoo_env import NeuralMindParallelEnv, parallel_env

__all__ = ["NeuralMindParallelEnv", "parallel_env"]

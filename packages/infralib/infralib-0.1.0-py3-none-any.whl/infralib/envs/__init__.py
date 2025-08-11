r"""Infrastructure management environments for reinforcement learning.

This package provides gymnasium-compatible environments for training reinforcement
learning agents on infrastructure maintenance problems. All environments are fully
compatible with stable-baselines3 and other modern RL libraries.

The package includes:

- **Base Environment**: Abstract base class with model abstractions
- **Simple Environments**: POMDP and MDP variants with configuration support
- **Configuration System**: YAML and CSV-based environment setup
- **Rich Displays**: Terminal visualizations for interactive simulation

Example
-------
Basic usage with configuration files::

    from infralib.envs import SimpleInfraEnv, SimpleInfraMDPEnv

    # POMDP environment with partial observability
    pomdp_env = SimpleInfraEnv.from_config(
        config_path='config.yaml',
        components_path='components.csv',
        reward_scheme='cost_penalty'
    )

    # MDP environment with component margins
    mdp_env = SimpleInfraMDPEnv.from_config(
        config_path='config.yaml',
        components_path='components.csv',
        reward_scheme='margin'
    )

    # Training with stable-baselines3
    from stable_baselines3 import PPO
    model = PPO('MlpPolicy', mdp_env, verbose=1)
    model.learn(total_timesteps=10000)

Classes
-------
BaseInfraEnv : Abstract base class for infrastructure environments
SimpleInfraEnv : POMDP-style infrastructure environment
SimpleInfraMDPEnv : MDP-style infrastructure environment with component margins

Functions
---------
load_config_data : Load configuration parameters from YAML and CSV files
"""

from .base import BaseInfraEnv
from .simple import SimpleInfraEnv, SimpleInfraMDPEnv, load_config_data

__all__ = ["BaseInfraEnv", "SimpleInfraEnv", "SimpleInfraMDPEnv", "load_config_data"]

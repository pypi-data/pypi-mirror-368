"""InfraLib: Infrastructure Management Library for RL and Optimization.

InfraLib is a comprehensive Python library for modeling, simulating, and analyzing
large-scale infrastructure management problems. It provides a realistic and granular
representation of infrastructure systems by integrating hierarchical models that
capture intricate relationships between components and facilities.

Key Features:
    - Stochastic deterioration modeling with partial observability
    - Gymnasium-compatible RL environments
    - Scalable simulation supporting millions of components
    - Rich visualization and analysis tools
    - Flexible model architecture with dependency injection
    - Web-based human interface for expert data collection

Example:
    Basic usage with default models::

        from infralib.models.dynamics import WeibullDynamics
        from infralib.models.cost import SimpleCost
        from infralib.models.budget import FixedBudget
        from infralib.simulator import Simulator
        import numpy as np

        # Setup models
        dynamics = WeibullDynamics(n_states=10)
        cost = SimpleCost()
        budget = FixedBudget(initial_budget=10000)

        # Create and run simulator
        sim = Simulator(dynamics, cost, budget)
        sim.reset(n_components=5)
        actions = np.array([0, 1, 2, 0, 1])  # do_nothing, inspect, repair, do_nothing, inspect
        states, info = sim.step(actions)

        print(f"Total cost: {info['total_cost']:.2f}")
        print(f"Failures: {info['failures']}")

    Creating a custom RL environment::

        from infralib.envs.simple import SimpleInfraEnv
        import stable_baselines3 as sb3

        # Create environment
        env = SimpleInfraEnv(n_components=5, max_budget=10000)

        # Train RL agent
        model = sb3.PPO('MlpPolicy', env, verbose=1)
        model.learn(total_timesteps=100000)

        # Evaluate policy
        obs, info = env.reset()
        for _ in range(100):
            action, _states = model.predict(obs)
            obs, reward, done, truncated, info = env.step(action)
            if done or truncated:
                obs, info = env.reset()

Modules:
    models: Core models for dynamics, cost, budget, hierarchy, and metadata
    envs: Gymnasium-compatible RL environments
    simulator: High-performance infrastructure simulation engine
    visualize: Visualization and analysis tools
    infraio: Data input/output utilities

Note:
    InfraLib requires Python 3.12+ and depends on NumPy, SciPy, Gymnasium,
    and other scientific computing libraries. See the documentation for
    complete installation instructions.
"""

__version__ = "0.1.0"
__author__ = "InfraLib Team"
__email__ = "contact@prny.me"
__license__ = "MIT"
__url__ = "https://infralib.github.io/"
__repository__ = "https://github.com/pthangeda/InfraLib"

from . import envs, models, simulator

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
    "__repository__",
    "models",
    "envs",
    "simulator",
]

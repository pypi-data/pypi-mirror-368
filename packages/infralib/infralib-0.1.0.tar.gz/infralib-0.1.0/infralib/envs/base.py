r"""Base infrastructure management environment for gymnasium and stable-baselines3.

This module provides a base class for infrastructure maintenance environments that:

- Is fully compatible with gymnasium and stable-baselines3
- Uses the updated Simulator with model dependency system
- Provides abstract methods for model creation (no models defined in base)
- Supports all observability modes and reward schemes
- Includes comprehensive action and observation space handling

The base class assumes all inheriting environments will define appropriate
models (dynamics, cost, budget, hierarchy, metadata) as needed.

Example
-------
Creating a custom environment by inheriting from BaseInfraEnv::

    class MyCustomEnv(BaseInfraEnv):
        def _create_models(self):
            dynamics = MyDynamicsModel()
            cost = MyCostModel()
            budget = MyBudgetModel()
            return dynamics, cost, budget, None, None

        def _compute_reward(self, sim_info):
            return -sim_info['total_cost']

Classes
-------
BaseInfraEnv : Abstract base class for infrastructure environments
"""

from abc import ABC, abstractmethod
from typing import Any

import gymnasium as gym
import numpy as np

from ..models.budget import BudgetModel
from ..models.cost import CostModel
from ..models.dynamics import DynamicsModel
from ..models.hierarchy import HierarchyModel
from ..models.metadata import MetadataModel
from ..simulator import Simulator


class BaseInfraEnv(gym.Env, ABC):
    """Abstract base class for infrastructure maintenance environments.

    This base class provides the core functionality for infrastructure maintenance
    RL environments while requiring subclasses to define their own models and
    reward functions. It is fully compatible with gymnasium and stable-baselines3.

    The environment handles:
    - Action and observation space definition
    - Simulator integration with model dependencies
    - Episode management (reset, step, termination)
    - Multiple observability modes (full, partial, noisy)
    - Rendering capabilities

    Subclasses must implement:
    - _create_models(): Define dynamics, cost, budget, and optional hierarchy/metadata
    - _compute_reward(): Define reward function based on simulation info

    Parameters
    ----------
    n_components : int
        Number of infrastructure components to simulate
    max_steps : int, default 365
        Maximum number of steps per episode
    observability : {'full', 'partial', 'noisy'}, default 'full'
        Type of state observability
    action_type : {'multi_discrete', 'discrete', 'box'}, default 'multi_discrete'
        Format of action space
    render_mode : str, optional
        Rendering mode ('human', 'rgb_array', None)
    rich_display : bool, default False
        Enable rich terminal displays during simulation
    seed : int, optional
        Random seed for reproducibility

    Attributes
    ----------
    n_components : int
        Number of components in the system
    simulator : Simulator
        Infrastructure simulator instance
    current_step : int
        Current episode step counter
    action_space : gym.Space
        Gymnasium action space
    observation_space : gym.Space
        Gymnasium observation space

    Notes
    -----
    This class is designed to work seamlessly with stable-baselines3 and other
    modern RL libraries. All environments created by inheriting from this class
    will pass gymnasium's env_checker.

    The action space supports multiple formats:
    - 'multi_discrete': Separate action per component [4, 4, ..., 4]
    - 'discrete': Single action encoding all components (4^n_components)
    - 'box': Continuous actions (for advanced use cases)

    Examples
    --------
    >>> class SimpleEnv(BaseInfraEnv):
    ...     def _create_models(self):
    ...         dynamics = MarkovDynamics(n_states=10)
    ...         cost = SimpleCost()
    ...         budget = FixedBudget(initial_budget=5000)
    ...         return dynamics, cost, budget, None, None
    ...
    ...     def _compute_reward(self, sim_info):
    ...         return -sim_info['total_cost'] - sim_info['failures'] * 100
    ...
    >>> env = SimpleEnv(n_components=5)
    >>> obs, info = env.reset()
    >>> action = env.action_space.sample()
    >>> obs, reward, terminated, truncated, info = env.step(action)
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(
        self,
        n_components: int,
        max_steps: int = 365,
        observability: str = "full",
        action_type: str = "multi_discrete",
        render_mode: str | None = None,
        rich_display: bool = False,
        seed: int | None = None,
    ):
        super().__init__()

        # Environment configuration
        self.n_components = n_components
        self.max_steps = max_steps
        self.observability = observability
        self.action_type = action_type
        self.render_mode = render_mode
        self.rich_display = rich_display
        self.seed = seed

        # Environment state
        self.current_step = 0
        self.terminated = False
        self.truncated = False

        # Create models (must be implemented by subclasses)
        dynamics, cost, budget, hierarchy, metadata = self._create_models()

        # Create simulator with models
        self.simulator = Simulator(
            dynamics=dynamics,
            cost=cost,
            budget=budget,
            hierarchy=hierarchy,
            metadata=metadata,
            rich_display=rich_display,
            seed=seed,
        )

        # Set failure_conditions in simulator if available (for visualization compatibility)
        if hasattr(self, "failure_thresholds"):
            self.simulator.failure_conditions = self.failure_thresholds

        # Define action and observation spaces
        self._define_spaces()

        # Rendering
        self.render_history = []

    @abstractmethod
    def _create_models(
        self,
    ) -> tuple[
        DynamicsModel,
        CostModel,
        BudgetModel,
        HierarchyModel | None,
        MetadataModel | None,
    ]:
        """Create and return models for the environment.

        This method must be implemented by subclasses to define the specific
        models used by the environment. The base class makes no assumptions
        about which models to use.

        Returns
        -------
        tuple
            (dynamics, cost, budget, hierarchy, metadata) where hierarchy and
            metadata can be None if not needed

        Examples
        --------
        >>> def _create_models(self):
        ...     dynamics = MarkovDynamics(n_states=10)
        ...     cost = SimpleCost(base_repair_cost=100)
        ...     budget = FixedBudget(initial_budget=5000)
        ...     return dynamics, cost, budget, None, None
        """
        pass

    @abstractmethod
    def _compute_reward(self, sim_info: dict[str, Any]) -> float:
        """Compute reward based on simulation step information.

        This method must be implemented by subclasses to define the reward
        function. It receives the info dictionary from the simulator step.

        Parameters
        ----------
        sim_info : dict
            Information dictionary from simulator.step() containing:
            - 'total_cost': Cost of actions taken
            - 'failures': Number of failed components
            - 'budget_remaining': Remaining budget
            - 'mean_condition': Average component condition
            - And other simulation metrics

        Returns
        -------
        float
            Scalar reward value

        Examples
        --------
        >>> def _compute_reward(self, sim_info):
        ...     cost_penalty = sim_info['total_cost'] / 1000.0
        ...     failure_penalty = sim_info['failures'] * 10.0
        ...     condition_reward = sim_info['mean_condition'] / 10.0
        ...     return condition_reward - cost_penalty - failure_penalty
        """
        pass

    def _define_spaces(self):
        """Define gymnasium action and observation spaces."""
        # Action space
        if self.action_type == "multi_discrete":
            # Separate discrete action for each component: [0,1,2,3] per component
            self.action_space = gym.spaces.MultiDiscrete([4] * self.n_components)
        elif self.action_type == "discrete":
            # Single discrete action encoding all components: 4^n_components possibilities
            self.action_space = gym.spaces.Discrete(4**self.n_components)
        elif self.action_type == "box":
            # Continuous actions (can be useful for some algorithms)
            self.action_space = gym.spaces.Box(
                low=0, high=3, shape=(self.n_components,), dtype=np.float32
            )
        else:
            raise ValueError(f"Unknown action_type: {self.action_type}")

        # Observation space - get dimension from simulator
        # Create temporary observation to determine dimensions
        temp_states = np.ones(self.n_components) * 5  # Mid-range states
        self.simulator.reset(self.n_components, temp_states)
        sample_obs = self.simulator.get_observation(self.observability)
        obs_dim = len(sample_obs)

        # Define observation bounds
        if self.observability in ["full", "partial", "noisy"]:
            # States normalized to [0,1], time normalized, budget normalized
            low = np.full(obs_dim, -1.0, dtype=np.float32)
            high = np.full(obs_dim, 1.0, dtype=np.float32)
        else:
            low = np.full(obs_dim, -np.inf, dtype=np.float32)
            high = np.full(obs_dim, np.inf, dtype=np.float32)

        self.observation_space = gym.spaces.Box(
            low=low, high=high, shape=(obs_dim,), dtype=np.float32
        )

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Reset the environment to start a new episode.

        Parameters
        ----------
        seed : int, optional
            Random seed for the episode
        options : dict, optional
            Additional options including 'initial_states'

        Returns
        -------
        tuple
            (observation, info) where observation is the initial state observation
            and info contains environment metadata
        """
        super().reset(seed=seed)

        if seed is not None:
            np.random.seed(seed)

        # Reset simulator
        initial_states = None
        if options and "initial_states" in options:
            initial_states = options["initial_states"]

        self.simulator.reset(self.n_components, initial_states)

        # Reset environment state
        self.current_step = 0
        self.terminated = False
        self.truncated = False
        self.render_history = []

        # Get initial observation and info
        observation = self._get_observation()
        info = self._get_info()

        return observation.astype(np.float32), info

    def step(
        self, action: int | np.ndarray
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """Take a step in the environment.

        Parameters
        ----------
        action : int or np.ndarray
            Action to take, format depends on action_type

        Returns
        -------
        tuple
            (observation, reward, terminated, truncated, info)

        Raises
        ------
        RuntimeError
            If called on terminated/truncated environment
        ValueError
            If action format is invalid
        """
        if self.terminated or self.truncated:
            raise RuntimeError("Cannot call step() on terminated/truncated environment")

        # Convert action to numpy array format expected by simulator
        action_array = self._process_action(action)

        # Take step in simulator
        states, sim_info = self.simulator.step(action_array)

        # Compute reward
        reward = self._compute_reward(sim_info)

        # Check termination conditions
        self.terminated, self.truncated = self._check_termination(sim_info)

        # Increment step counter
        self.current_step += 1

        # Get observation and info
        observation = self._get_observation()
        info = self._get_info()
        info.update(sim_info)  # Add simulator info

        # Store for rendering
        if self.render_mode is not None:
            self.render_history.append(
                {
                    "step": self.current_step,
                    "states": states.copy(),
                    "actions": action_array.copy(),
                    "reward": reward,
                    "info": sim_info.copy(),
                }
            )

        return (
            observation.astype(np.float32),
            float(reward),
            self.terminated,
            self.truncated,
            info,
        )

    def _process_action(self, action: int | np.ndarray) -> np.ndarray:
        """Convert action from various formats to numpy array."""
        if self.action_type == "multi_discrete":
            # Action is already array-like
            action_array = np.asarray(action, dtype=np.int32)
            if len(action_array) != self.n_components:
                raise ValueError(
                    f"Multi-discrete action length {len(action_array)} != n_components {self.n_components}"
                )

        elif self.action_type == "discrete":
            # Decode single action index to per-component actions
            action_idx = int(action)
            action_array = []
            for _ in range(self.n_components):
                action_array.append(action_idx % 4)
                action_idx //= 4
            action_array = np.array(action_array[::-1], dtype=np.int32)  # Reverse order

        elif self.action_type == "box":
            # Round continuous actions to discrete
            action_array = np.round(np.clip(action, 0, 3)).astype(np.int32)

        else:
            raise ValueError(f"Unknown action_type: {self.action_type}")

        return action_array

    def _get_observation(self) -> np.ndarray:
        """Get current observation from simulator."""
        return self.simulator.get_observation(self.observability)

    def _get_info(self) -> dict[str, Any]:
        """Get environment info dictionary."""
        return {
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "n_components": self.n_components,
            "observability": self.observability,
            "action_type": self.action_type,
        }

    def _check_termination(self, sim_info: dict[str, Any]) -> tuple[bool, bool]:
        """Check episode termination conditions.

        Default implementation terminates on budget exhaustion or too many failures,
        and truncates on max steps. Can be overridden by subclasses.

        Parameters
        ----------
        sim_info : dict
            Simulation step information

        Returns
        -------
        tuple
            (terminated, truncated)
        """
        terminated = False
        truncated = False

        # Terminated if budget exhausted
        if sim_info.get("budget_remaining", 0) <= 0:
            terminated = True

        # Terminated if too many components failed (>50%)
        failure_threshold = self.n_components * 0.5
        if sim_info.get("failures", 0) > failure_threshold:
            terminated = True

        # Truncated if max steps reached (check after current step would be incremented)
        if self.current_step + 1 >= self.max_steps:
            truncated = True

        return terminated, truncated

    def render(self) -> np.ndarray | str | None:
        """Render the environment state.

        Returns
        -------
        np.ndarray or str or None
            Rendered output depending on render_mode
        """
        if self.render_mode == "human":
            if self.rich_display and self.simulator.console:
                # Use rich display if available
                last_info = (
                    self.render_history[-1]["info"] if self.render_history else {}
                )
                self.simulator.display_status(last_info)
            else:
                # Simple text output
                print(f"Step {self.current_step}:")
                print(f"  States: {self.simulator.states}")
                budget_available = (
                    self.simulator.budget.available()
                    if hasattr(self.simulator.budget, "available")
                    else self.simulator.budget._available_internal()
                )
                print(f"  Budget: {budget_available:.0f}")
                print(f"  Failures: {np.sum(self.simulator.states == 0)}")
            return None

        elif self.render_mode == "rgb_array":
            return self._render_rgb_array()

        else:
            return None

    def _render_rgb_array(self) -> np.ndarray:
        """Create RGB array visualization of component states."""
        height, width = 64, 64

        # Create grid layout for components
        grid_size = int(np.ceil(np.sqrt(self.n_components)))
        component_size = min(height // grid_size, width // grid_size)

        rgb_array = np.zeros((height, width, 3), dtype=np.uint8)

        for i, state in enumerate(self.simulator.states):
            row = i // grid_size
            col = i % grid_size

            y_start = row * component_size
            y_end = min((row + 1) * component_size, height)
            x_start = col * component_size
            x_end = min((col + 1) * component_size, width)

            # Color based on state: red=failed, yellow=poor, green=good
            if state == 0:
                color = [255, 0, 0]  # Red - failed
            elif state < 3:
                color = [255, 0, 0]  # Red - critical
            elif state < 5:
                color = [255, 165, 0]  # Orange - poor
            elif state < 7:
                color = [255, 255, 0]  # Yellow - fair
            else:
                color = [0, 255, 0]  # Green - good

            rgb_array[y_start:y_end, x_start:x_end] = color

        return rgb_array

    def close(self):
        """Clean up environment resources."""
        if hasattr(self.simulator, "close"):
            self.simulator.close()
        self.render_history = []


def make_env_from_config(env_class, config_path: str, **kwargs) -> BaseInfraEnv:
    """Create environment from configuration file.

    Parameters
    ----------
    env_class : class
        Environment class that inherits from BaseInfraEnv
    config_path : str
        Path to YAML configuration file
    **kwargs
        Additional keyword arguments to override config

    Returns
    -------
    BaseInfraEnv
        Configured environment instance
    """
    import yaml

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Extract environment configuration
    env_config = config.get("environment", {})
    env_config.update(kwargs)  # Override with kwargs

    return env_class(**env_config)

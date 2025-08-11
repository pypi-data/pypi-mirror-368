r"""Simple infrastructure management environments using config files.

This module provides simple implementations of infrastructure maintenance environments
that can be configured via YAML config files and CSV component data files. These
environments use standard models and are designed for ease of use and educational
purposes.

The environments support:

- Configuration-based setup from YAML and CSV files
- Both POMDP (partial observability) and MDP (full observability) variants
- Stable-baselines3 compatibility
- Multiple reward schemes and termination conditions
- Rich terminal displays and rendering

Example
-------
Using configuration files to create environments::

    # Create POMDP environment
    env = SimpleInfraEnv.from_config(
        config_path='config.yaml',
        components_path='components.csv'
    )

    # Create MDP environment
    env = SimpleInfraMDPEnv.from_config(
        config_path='config.yaml',
        components_path='components.csv'
    )

Classes
-------
SimpleInfraEnv : POMDP-style infrastructure environment
SimpleInfraMDPEnv : MDP-style infrastructure environment with component margins

Functions
---------
load_config_data : Load parameters from config and component files
"""

import csv
from typing import Any

import numpy as np
import yaml

from ..models.budget import FixedBudget
from ..models.cost import SimpleCost
from ..models.dynamics import MarkovDynamics, WeibullDynamics
from .base import BaseInfraEnv


def load_config_data(config_path: str, components_path: str) -> dict[str, Any]:
    """Load configuration from YAML and CSV files.

    Parameters
    ----------
    config_path : str
        Path to YAML configuration file
    components_path : str
        Path to CSV components data file

    Returns
    -------
    dict
        Dictionary containing all loaded parameters

    Examples
    --------
    >>> params = load_config_data('config.yaml', 'components.csv')
    >>> print(f"Budget: {params['initial_budget']}")
    >>> print(f"Components: {len(params['component_types'])}")
    """
    # Read config.yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Initialize lists to store component parameters
    component_types = []
    num_instances = []
    failure_conditions = []
    inspect_costs = []
    replace_costs = []
    repair_cost_params = []
    importance_scores = []
    dynamics_scale_means = []
    dynamics_scale_sds = []
    dynamics_shape_means = []
    dynamics_shape_sds = []

    # Read components.csv
    with open(components_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            component_types.append(row["component_type"])
            num_instances.append(int(row["num_instances"]))
            failure_conditions.append(float(row["failure_condition"]))
            inspect_costs.append(float(row["inspect_cost"]))
            replace_costs.append(float(row["replace_cost"]))
            repair_cost_params.append(float(row["repair_cost_param"]))
            importance_scores.append(float(row["importance_score"]))
            dynamics_scale_means.append(float(row["dynamics_scale_mean"]))
            dynamics_scale_sds.append(float(row["dynamics_scale_sd"]))
            dynamics_shape_means.append(float(row["dynamics_shape_mean"]))
            dynamics_shape_sds.append(float(row["dynamics_shape_sd"]))

    # Build component_ids
    component_ids = []
    for t, num in zip(component_types, num_instances, strict=False):
        for i in range(num):
            component_ids.append(f"{t}{i}")

    # Compile all parameters into a dictionary
    params = {
        "simulation_seed": config["simulation_seed"],
        "initial_budget": config["initial_budget"],
        "component_types": component_types,
        "num_components_per_type": num_instances,
        "component_ids": component_ids,
        "failure_conditions": failure_conditions,
        "inspect_costs": inspect_costs,
        "replace_costs": replace_costs,
        "repair_cost_params": repair_cost_params,
        "importance_scores": importance_scores,
        "dynamics_scale_means": dynamics_scale_means,
        "dynamics_scale_sds": dynamics_scale_sds,
        "dynamics_shape_means": dynamics_shape_means,
        "dynamics_shape_sds": dynamics_shape_sds,
        "dynamics_model_params": config["dynamics_model"],
        "cost_model_params": config["cost_model"],
        "budget_model_params": config["budget_model"],
    }

    return params


class SimpleInfraEnv(BaseInfraEnv):
    """Simple POMDP infrastructure environment with configuration support.

    This environment simulates infrastructure maintenance under partial observability
    where components can only be observed through inspections. The environment uses
    configuration files to define component properties and model parameters.

    Features:
    - POMDP formulation with inspection-based observations
    - Configuration-based setup from YAML/CSV files
    - Multiple reward schemes and termination conditions
    - Support for component types with different characteristics
    - Rich terminal displays and basic rendering

    Parameters
    ----------
    config_path : str, optional
        Path to YAML configuration file
    components_path : str, optional
        Path to CSV components data file
    reward_scheme : {'cost_penalty', 'survival', 'condition'}, default 'cost_penalty'
        Reward function to use
    max_steps : int, default 100
        Maximum episode length
    observability : {'full', 'partial', 'noisy'}, default 'partial'
        Observation mode (partial recommended for POMDP)
    action_type : {'multi_discrete', 'discrete'}, default 'discrete'
        Action space format
    render_mode : str, optional
        Rendering mode
    rich_display : bool, default False
        Enable rich terminal status displays

    Attributes
    ----------
    params : dict
        Loaded configuration parameters
    failure_thresholds : np.ndarray
        Failure thresholds per component
    component_types : list
        Component type names

    Notes
    -----
    This environment is designed for training RL agents on infrastructure
    maintenance problems with realistic component degradation and cost models.
    The POMDP formulation requires agents to balance exploration (inspections)
    with exploitation (maintenance actions).

    Actions are:
    - 0: Do nothing
    - 1: Inspect component
    - 2: Repair component
    - 3: Replace component

    Observations include last inspection results, time since inspections,
    and remaining budget information.

    Examples
    --------
    >>> env = SimpleInfraEnv.from_config('config.yaml', 'components.csv')
    >>> obs, info = env.reset()
    >>> action = env.action_space.sample()
    >>> obs, reward, terminated, truncated, info = env.step(action)

    >>> # Check environment with stable-baselines3
    >>> from stable_baselines3.common.env_checker import check_env
    >>> check_env(env, warn=True)
    """

    def __init__(
        self,
        config_path: str | None = None,
        components_path: str | None = None,
        reward_scheme: str = "cost_penalty",
        max_steps: int = 100,
        observability: str = "partial",
        action_type: str = "discrete",
        render_mode: str | None = None,
        rich_display: bool = False,
        seed: int | None = None,
    ):
        # Load configuration if provided
        if config_path and components_path:
            self.params = load_config_data(config_path, components_path)
            n_components = sum(self.params["num_components_per_type"])
            if seed is None:
                seed = self.params.get("simulation_seed", None)
        else:
            # Use defaults for testing/minimal setup
            self.params = self._create_default_params()
            n_components = 5

        self.reward_scheme = reward_scheme
        self.failure_thresholds = np.array(self.params["failure_conditions"])
        self.component_types = self.params["component_types"]

        # Initialize base environment
        super().__init__(
            n_components=n_components,
            max_steps=max_steps,
            observability=observability,
            action_type=action_type,
            render_mode=render_mode,
            rich_display=rich_display,
            seed=seed,
        )

    def _create_default_params(self) -> dict[str, Any]:
        """Create default parameters for testing."""
        return {
            "simulation_seed": 42,
            "initial_budget": 2000,
            "component_types": ["A", "B", "C", "D", "E"],
            "num_components_per_type": [1, 1, 1, 1, 1],
            "component_ids": ["A0", "B0", "C0", "D0", "E0"],
            "failure_conditions": [40, 40, 40, 40, 40],
            "inspect_costs": [10, 20, 30, 40, 50],
            "replace_costs": [200, 200, 100, 100, 100],
            "repair_cost_params": [2, 2.5, 3, 3.5, 4],
            "importance_scores": [1, 1.5, 1.2, 1.8, 2],
            "dynamics_scale_means": [37.22, 46.37, 27.45, 35.67, 42.89],
            "dynamics_scale_sds": [2.1, 0.4, 0.85, 0.97, 1.5],
            "dynamics_shape_means": [2.0, 1.89, 2.1, 1.95, 2.05],
            "dynamics_shape_sds": [0.07, 0.05, 0.08, 0.06, 0.09],
            "dynamics_model_params": {
                "name": "WeibullDynamics",
                "num_states": 101,
                "num_actions": 4,
                "num_obs": 102,
                "seed": 42,
            },
            "cost_model_params": {"name": "StandardCost", "seed": 42},
            "budget_model_params": {
                "name": "FixedBudget",
                "initial_budget": 2000,
                "seed": 42,
            },
        }

    def _create_models(self) -> tuple[Any, Any, Any, Any | None, Any | None]:
        """Create models from configuration parameters."""
        # Create dynamics model based on config
        dynamics_params = self.params["dynamics_model_params"]
        if dynamics_params["name"] == "WeibullDynamics":
            # FIXED: Use per-type Weibull parameters from CSV (no more averaging!)
            # Create type_indices array mapping each component to its type
            type_indices = []
            for type_idx, num_instances in enumerate(
                self.params["num_components_per_type"]
            ):
                type_indices.extend([type_idx] * num_instances)
            type_indices = np.array(type_indices)

            dynamics = WeibullDynamics(
                n_states=dynamics_params["num_states"],
                shapes=self.params["dynamics_shape_means"],  # Per-type shape parameters
                scales=self.params["dynamics_scale_means"],  # Per-type scale parameters
                type_indices=type_indices,  # Component-to-type mapping
                repair_effectiveness=0.7,
                seed=dynamics_params["seed"],
            )
        else:
            # Fallback to MarkovDynamics
            dynamics = MarkovDynamics(
                n_states=dynamics_params["num_states"],
                base_deterioration_rate=0.1,
                repair_effectiveness=0.7,
                seed=dynamics_params["seed"],
            )

        # Create cost model
        cost = SimpleCost(
            inspect_cost=np.mean(self.params["inspect_costs"]),
            repair_cost=np.mean([p * 100 for p in self.params["repair_cost_params"]]),
            replace_cost=np.mean(self.params["replace_costs"]),
        )

        # Create budget model
        budget = FixedBudget(initial_budget=self.params["initial_budget"])

        # No hierarchy or metadata for simple environment
        return dynamics, cost, budget, None, None

    def _compute_reward(self, sim_info: dict[str, Any]) -> float:
        """Compute reward based on selected reward scheme."""
        if self.reward_scheme == "cost_penalty":
            # Penalize costs and failures heavily
            cost_penalty = sim_info["total_cost"] / 100.0
            failure_penalty = sim_info["failures"] * 50.0
            # Small positive reward for surviving
            survival_reward = 1.0 if sim_info["failures"] == 0 else 0.0
            reward = survival_reward - cost_penalty - failure_penalty

        elif self.reward_scheme == "survival":
            # Focus on keeping components above failure threshold
            states = self.simulator.states
            # Create per-component thresholds
            if len(self.failure_thresholds) == len(self.component_types):
                # Expand thresholds to match component instances
                expanded_thresholds = []
                for i, (_comp_type, n_instances) in enumerate(
                    zip(
                        self.component_types,
                        self.params["num_components_per_type"],
                        strict=False,
                    )
                ):
                    expanded_thresholds.extend(
                        [self.failure_thresholds[i]] * n_instances
                    )
                thresholds = np.array(expanded_thresholds)
            else:
                thresholds = np.full(len(states), 40)  # Default threshold

            surviving = np.sum(states > thresholds)
            survival_rate = surviving / len(states)
            cost_penalty = sim_info["total_cost"] / 1000.0
            reward = survival_rate - cost_penalty

        elif self.reward_scheme == "condition":
            # Reward based on maintaining good condition
            mean_condition = sim_info.get("mean_condition", 5.0)
            condition_reward = mean_condition / 10.0  # Normalize to [0,1]
            cost_penalty = sim_info["total_cost"] / 500.0
            failure_penalty = sim_info["failures"] * 2.0
            reward = condition_reward - cost_penalty - failure_penalty

        else:
            # Default to cost penalty
            reward = -sim_info["total_cost"] / 100.0 - sim_info["failures"] * 10.0

        return float(reward)

    def _check_termination(self, sim_info: dict[str, Any]) -> tuple[bool, bool]:
        """Check termination with component-specific failure thresholds."""
        terminated = False
        truncated = False

        # Budget exhausted
        if sim_info.get("budget_remaining", 0) <= 0:
            terminated = True

        # Check component-specific failures
        states = self.simulator.states
        if len(self.failure_thresholds) == len(self.component_types):
            # Expand thresholds to match component instances
            expanded_thresholds = []
            for i, (_comp_type, n_instances) in enumerate(
                zip(
                    self.component_types,
                    self.params["num_components_per_type"],
                    strict=False,
                )
            ):
                expanded_thresholds.extend([self.failure_thresholds[i]] * n_instances)
            thresholds = np.array(expanded_thresholds)

            # Terminate if any component fails
            if np.any(states <= thresholds):
                terminated = True
        else:
            # Fallback to generic failure check
            if sim_info.get("failures", 0) > 0:
                terminated = True

        # Max steps reached
        if self.current_step >= self.max_steps:
            truncated = True

        return terminated, truncated

    @classmethod
    def from_config(
        cls, config_path: str, components_path: str, **kwargs
    ) -> "SimpleInfraEnv":
        """Create environment from configuration files.

        Parameters
        ----------
        config_path : str
            Path to YAML configuration file
        components_path : str
            Path to CSV components data file
        **kwargs
            Additional keyword arguments to override defaults

        Returns
        -------
        SimpleInfraEnv
            Configured environment instance

        Examples
        --------
        >>> env = SimpleInfraEnv.from_config(
        ...     'config.yaml', 'components.csv',
        ...     reward_scheme='survival', max_steps=200
        ... )
        """
        return cls(config_path=config_path, components_path=components_path, **kwargs)


class SimpleInfraMDPEnv(BaseInfraEnv):
    """Simple MDP infrastructure environment with component margins.

    This environment provides full observability of component states and focuses
    on the margin between current state and failure threshold. This formulation
    is easier to learn for many RL algorithms as it provides direct state information.

    Features:
    - MDP formulation with full state observability
    - Component margins as primary observation
    - Configuration-based setup from YAML/CSV files
    - Margin-based reward functions
    - Support for component types with different failure thresholds

    Parameters
    ----------
    config_path : str, optional
        Path to YAML configuration file
    components_path : str, optional
        Path to CSV components data file
    reward_scheme : {'margin', 'weighted_margin', 'binary'}, default 'margin'
        Reward function to use
    max_steps : int, default 100
        Maximum episode length
    action_type : {'multi_discrete', 'discrete'}, default 'multi_discrete'
        Action space format (multi_discrete recommended for MDP)
    render_mode : str, optional
        Rendering mode
    rich_display : bool, default False
        Enable rich terminal status displays

    Attributes
    ----------
    params : dict
        Loaded configuration parameters
    failure_thresholds : np.ndarray
        Failure thresholds per component type
    max_states : int
        Maximum component state value

    Notes
    -----
    The MDP formulation uses component margins as the primary state representation:
    margin = (current_state - failure_threshold) / (max_state - failure_threshold)

    This normalization makes the state space more uniform across component types
    and focuses learning on the critical region near failure thresholds.

    Observations include:
    - Component margins (normalized to [-1, 1] range)
    - Normalized remaining budget

    Examples
    --------
    >>> env = SimpleInfraMDPEnv.from_config('config.yaml', 'components.csv')
    >>> obs, info = env.reset()
    >>> print(f"Component margins: {obs[:-1]}")  # All but last element
    >>> print(f"Budget remaining: {obs[-1]}")    # Last element
    """

    def __init__(
        self,
        config_path: str | None = None,
        components_path: str | None = None,
        reward_scheme: str = "margin",
        max_steps: int = 100,
        action_type: str = "multi_discrete",
        render_mode: str | None = None,
        rich_display: bool = False,
        seed: int | None = None,
    ):
        # Load configuration if provided
        if config_path and components_path:
            self.params = load_config_data(config_path, components_path)
            n_components = sum(self.params["num_components_per_type"])
            if seed is None:
                seed = self.params.get("simulation_seed", None)
        else:
            # Use defaults
            self.params = self._create_default_params()
            n_components = 5

        self.reward_scheme = reward_scheme
        self.failure_thresholds = np.array(self.params["failure_conditions"])
        self.max_states = (
            self.params["dynamics_model_params"]["num_states"] - 1
        )  # 0-indexed

        # Initialize base environment with full observability
        super().__init__(
            n_components=n_components,
            max_steps=max_steps,
            observability="full",  # MDP uses full observability
            action_type=action_type,
            render_mode=render_mode,
            rich_display=rich_display,
            seed=seed,
        )

    def _create_default_params(self) -> dict[str, Any]:
        """Create default parameters for testing."""
        return {
            "simulation_seed": 42,
            "initial_budget": 2000,
            "component_types": ["A", "B", "C", "D", "E"],
            "num_components_per_type": [1, 1, 1, 1, 1],
            "component_ids": ["A0", "B0", "C0", "D0", "E0"],
            "failure_conditions": [40, 40, 40, 40, 40],
            "inspect_costs": [10, 20, 30, 40, 50],
            "replace_costs": [200, 200, 100, 100, 100],
            "repair_cost_params": [2, 2.5, 3, 3.5, 4],
            "importance_scores": [1, 1.5, 1.2, 1.8, 2],
            "dynamics_scale_means": [37.22, 46.37, 27.45, 35.67, 42.89],
            "dynamics_scale_sds": [2.1, 0.4, 0.85, 0.97, 1.5],
            "dynamics_shape_means": [2.0, 1.89, 2.1, 1.95, 2.05],
            "dynamics_shape_sds": [0.07, 0.05, 0.08, 0.06, 0.09],
            "dynamics_model_params": {
                "name": "WeibullDynamics",
                "num_states": 101,
                "num_actions": 4,
                "num_obs": 102,
                "seed": 42,
            },
            "cost_model_params": {"name": "StandardCost", "seed": 42},
            "budget_model_params": {
                "name": "FixedBudget",
                "initial_budget": 2000,
                "seed": 42,
            },
        }

    def _create_models(self) -> tuple[Any, Any, Any, Any | None, Any | None]:
        """Create models from configuration parameters."""
        # Create dynamics model based on config
        dynamics_params = self.params["dynamics_model_params"]
        if dynamics_params["name"] == "WeibullDynamics":
            # FIXED: Use per-type Weibull parameters from CSV (no more averaging!)
            # Create type_indices array mapping each component to its type
            type_indices = []
            for type_idx, num_instances in enumerate(
                self.params["num_components_per_type"]
            ):
                type_indices.extend([type_idx] * num_instances)
            type_indices = np.array(type_indices)

            dynamics = WeibullDynamics(
                n_states=dynamics_params["num_states"],
                shapes=self.params["dynamics_shape_means"],  # Per-type shape parameters
                scales=self.params["dynamics_scale_means"],  # Per-type scale parameters
                type_indices=type_indices,  # Component-to-type mapping
                repair_effectiveness=0.7,
                seed=dynamics_params["seed"],
            )
        else:
            # Fallback to MarkovDynamics
            dynamics = MarkovDynamics(
                n_states=dynamics_params["num_states"],
                base_deterioration_rate=0.1,
                repair_effectiveness=0.7,
                seed=dynamics_params["seed"],
            )

        # Create cost model
        cost = SimpleCost(
            inspect_cost=np.mean(self.params["inspect_costs"]),
            repair_cost=np.mean([p * 100 for p in self.params["repair_cost_params"]]),
            replace_cost=np.mean(self.params["replace_costs"]),
        )

        # Create budget model
        budget = FixedBudget(initial_budget=self.params["initial_budget"])

        return dynamics, cost, budget, None, None

    def _get_observation(self) -> np.ndarray:
        """Get MDP observation with component margins and budget."""
        states = self.simulator.states

        # Calculate component margins
        if len(self.failure_thresholds) == len(self.params["component_types"]):
            # Expand thresholds to match component instances
            expanded_thresholds = []
            for i, (_comp_type, n_instances) in enumerate(
                zip(
                    self.params["component_types"],
                    self.params["num_components_per_type"],
                    strict=False,
                )
            ):
                expanded_thresholds.extend([self.failure_thresholds[i]] * n_instances)
            thresholds = np.array(expanded_thresholds)
        else:
            thresholds = np.full(len(states), 40)  # Default threshold

        # Compute margins: (state - threshold) / (max_state - threshold)
        margins = (states - thresholds) / (self.max_states - thresholds)

        # Get normalized budget
        budget_available = (
            self.simulator.budget.available()
            if hasattr(self.simulator.budget, "available")
            else self.simulator.budget._available_internal()
        )
        normalized_budget = budget_available / self.params["initial_budget"]

        # Combine margins and budget
        observation = np.concatenate([margins, [normalized_budget]])

        return observation.astype(np.float32)

    def _compute_reward(self, sim_info: dict[str, Any]) -> float:
        """Compute reward based on selected reward scheme."""
        states = self.simulator.states

        if self.reward_scheme == "margin":
            # Reward based on average margin
            obs = self._get_observation()
            margins = obs[:-1]  # All but budget
            avg_margin = np.mean(margins)

            # Penalize negative margins (failures) heavily
            failure_penalty = np.sum(margins < 0) * 10.0
            cost_penalty = sim_info["total_cost"] / 1000.0

            reward = avg_margin - failure_penalty - cost_penalty

        elif self.reward_scheme == "weighted_margin":
            # Use importance scores to weight component margins
            obs = self._get_observation()
            margins = obs[:-1]

            # Get importance weights
            if len(self.params["importance_scores"]) == len(
                self.params["component_types"]
            ):
                expanded_importance = []
                for i, (_comp_type, n_instances) in enumerate(
                    zip(
                        self.params["component_types"],
                        self.params["num_components_per_type"],
                        strict=False,
                    )
                ):
                    expanded_importance.extend(
                        [self.params["importance_scores"][i]] * n_instances
                    )
                importance = np.array(expanded_importance)
            else:
                importance = np.ones(len(states))

            # Weighted average margin
            weighted_margin = np.average(margins, weights=importance)
            failure_penalty = np.sum(margins < 0) * 15.0
            cost_penalty = sim_info["total_cost"] / 1000.0

            reward = weighted_margin - failure_penalty - cost_penalty

        elif self.reward_scheme == "binary":
            # Binary reward for no failures
            obs = self._get_observation()
            margins = obs[:-1]

            if np.all(margins >= 0):
                reward = 1.0  # All components above threshold
            else:
                reward = -10.0  # At least one failure

            # Small cost penalty
            reward -= sim_info["total_cost"] / 2000.0

        else:
            # Default margin reward
            obs = self._get_observation()
            margins = obs[:-1]
            reward = np.mean(margins) - sim_info["total_cost"] / 1000.0

        return float(reward)

    def _check_termination(self, sim_info: dict[str, Any]) -> tuple[bool, bool]:
        """Check termination based on margins."""
        terminated = False
        truncated = False

        # Budget exhausted
        if sim_info.get("budget_remaining", 0) <= 0:
            terminated = True

        # Check if any component margin is negative (failed)
        obs = self._get_observation()
        margins = obs[:-1]  # All but budget
        if np.any(margins < 0):
            terminated = True

        # Max steps reached
        if self.current_step >= self.max_steps:
            truncated = True

        return terminated, truncated

    @classmethod
    def from_config(
        cls, config_path: str, components_path: str, **kwargs
    ) -> "SimpleInfraMDPEnv":
        """Create MDP environment from configuration files.

        Parameters
        ----------
        config_path : str
            Path to YAML configuration file
        components_path : str
            Path to CSV components data file
        **kwargs
            Additional keyword arguments to override defaults

        Returns
        -------
        SimpleInfraMDPEnv
            Configured MDP environment instance

        Examples
        --------
        >>> env = SimpleInfraMDPEnv.from_config(
        ...     'config.yaml', 'components.csv',
        ...     reward_scheme='weighted_margin'
        ... )
        """
        return cls(config_path=config_path, components_path=components_path, **kwargs)

r"""Fast vectorized infrastructure simulator with model dependencies and rich displays.

This module provides a high-performance simulator for infrastructure maintenance systems
with support for:

- Model dependency injection via ModelContext
- Rich terminal status displays
- Vectorized operations with Numba acceleration
- Comprehensive performance tracking and metrics
- Flexible observability modes (full, partial, noisy)
- Batch policy evaluation capabilities

Example
-------
Basic usage with model dependencies::

    from infralib.models.dynamics import MarkovDynamics
    from infralib.models.cost import SimpleCost
    from infralib.models.budget import FixedBudget
    from infralib.simulator import Simulator
    import numpy as np

    # Setup models
    dynamics = MarkovDynamics(n_states=10)
    cost = SimpleCost()
    budget = FixedBudget(initial_budget=10000)

    # Create simulator with rich displays
    sim = Simulator(dynamics, cost, budget, rich_display=True)
    sim.reset(n_components=5)

    # Run simulation step
    actions = np.array([0, 1, 2, 0, 1])
    states, info = sim.step(actions)

    print(f"Total cost: {info['total_cost']:.2f}")
    print(f"Failures: {info['failures']}")

Classes
-------
Simulator : Main infrastructure simulation class with model dependencies

Functions
---------
_fast_budget_check : Numba-accelerated budget constraint enforcement
"""

import os
from typing import Any

import numba
import numpy as np
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

from .models.base import ModelContext
from .models.budget import BudgetModel
from .models.cost import CostModel
from .models.dynamics import DynamicsModel
from .models.hierarchy import HierarchyModel
from .models.metadata import MetadataModel


@numba.jit(nopython=True)
def _fast_budget_check(
    costs: np.ndarray, available_budget: float
) -> tuple[np.ndarray, float]:
    """Fast budget constraint enforcement using numba.

    Implements greedy budget allocation by sorting actions by cost and approving
    actions in order until budget is exhausted. Uses Numba JIT compilation for
    high performance.

    Parameters
    ----------
    costs : np.ndarray
        Array of costs for each proposed action
    available_budget : float
        Total budget available for this time step

    Returns
    -------
    tuple[np.ndarray, float]
        - allowed_actions: Boolean array indicating which actions are approved
        - remaining_budget: Budget remaining after approved actions

    Notes
    -----
    This function uses a greedy allocation strategy that may not be globally
    optimal but provides good performance and predictable behavior. Actions
    are sorted by cost in ascending order and approved until budget runs out.
    """
    n_components = len(costs)
    allowed_actions = np.zeros(n_components, dtype=numba.boolean)
    remaining_budget = available_budget

    # Sort by cost (greedy allocation)
    sorted_indices = np.argsort(costs)

    for i in range(n_components):
        idx = sorted_indices[i]
        if costs[idx] <= remaining_budget:
            allowed_actions[idx] = True
            remaining_budget -= costs[idx]

    return allowed_actions, remaining_budget


class Simulator:
    """Fast vectorized infrastructure simulator with hierarchy and metadata support."""

    def __init__(
        self,
        dynamics: DynamicsModel,
        cost: CostModel,
        budget: BudgetModel,
        hierarchy: HierarchyModel | None = None,
        metadata: MetadataModel | None = None,
        rich_display: bool = False,
        seed: int | None = None,
    ):
        self.dynamics = dynamics
        self.cost = cost
        self.budget = budget
        self.hierarchy = hierarchy
        self.metadata = metadata
        self.rich_display = rich_display

        # Extract type_indices from dynamics model if available
        self.type_indices = getattr(dynamics, "type_indices", None)

        # Initialize failure_conditions (will be set by environment)
        self.failure_conditions = None

        # Initialize console if rich display is enabled
        if self.rich_display:
            self.console = Console()
        else:
            self.console = None

        if seed is not None:
            np.random.seed(seed)

        # Simulation state
        self.n_components = None
        self.states = None
        self.time_since_inspection = None
        self.time_step = 0

        # Performance tracking
        self.history = {
            "states": [],
            "actions": [],
            "costs": [],
            "rewards": [],
            "budget_remaining": [],
            "failures": [],
        }

    def reset(
        self, n_components: int, initial_states: np.ndarray | None = None
    ) -> np.ndarray:
        """Reset simulator state."""
        self.n_components = n_components

        # Initialize states
        if initial_states is not None:
            if len(initial_states) != n_components:
                raise ValueError(
                    f"Initial states length {len(initial_states)} != n_components {n_components}"
                )
            self.states = initial_states.copy()
        else:
            # Start in good condition (state 9 out of 10)
            self.states = np.full(n_components, 9, dtype=np.int32)

        # Reset other simulation variables
        self.time_since_inspection = np.zeros(n_components, dtype=np.int32)
        self.time_step = 0
        self.budget.reset()

        # Clear history
        self.history = {
            "states": [self.states.copy()],
            "actions": [],
            "costs": [],
            "rewards": [],
            "budget_remaining": [self.budget.available()],
            "failures": [np.sum(self.states == 0)],
        }

        return self.states.copy()

    def step(
        self, actions: np.ndarray, display_status: bool = False
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Execute one simulation step with budget constraints."""
        if len(actions) != self.n_components:
            raise ValueError(
                f"Actions length {len(actions)} != n_components {self.n_components}"
            )

        # Store previous states
        prev_states = self.states.copy()

        # Create context for model computations
        context = self._create_context(actions)

        # Compute costs for proposed actions
        costs = self.cost.compute(context)

        # Apply budget constraints
        allowed_actions, remaining_budget_after = _fast_budget_check(
            costs, self.budget.available()
        )

        # Modify actions based on budget constraints
        final_actions = np.where(
            allowed_actions, actions, 0
        )  # Fall back to "do nothing"

        # Create context for final actions
        final_context = self._create_context(final_actions)

        # Apply dynamics with budget-constrained actions
        self.states = self.dynamics.compute(final_context)

        # Recompute costs for actual actions taken
        actual_context = self._create_context(final_actions)
        actual_context.states = prev_states  # Use previous states for cost calculation
        actual_costs = self.cost.compute(actual_context)

        # Update budget
        total_cost = np.sum(actual_costs)
        budget_success = self.budget.update(total_cost)

        # Update time tracking
        self.time_since_inspection += 1
        self.time_since_inspection[final_actions == 1] = 0  # Reset for inspections
        self.time_step += 1

        # Update cyclic budget if needed
        if hasattr(self.budget, "step_time"):
            self.budget.step_time()

        # Count failures
        current_failures = np.sum(self.states == 0)
        new_failures = np.sum((self.states == 0) & (prev_states > 0))

        # Prepare info dict
        info = {
            "costs": actual_costs,
            "total_cost": total_cost,
            "budget_remaining": self.budget.available(),
            "budget_success": budget_success,
            "failures": current_failures,
            "new_failures": new_failures,
            "actions_taken": final_actions,
            "actions_blocked": np.sum(~allowed_actions),
            "time_step": self.time_step,
            "mean_condition": np.mean(self.states),
            "min_condition": np.min(self.states),
        }

        # Add hierarchy-based aggregations if available
        if self.hierarchy is not None:
            info.update(self._compute_hierarchy_metrics())

        # Add metadata-based metrics if available
        if self.metadata is not None:
            info.update(self._compute_metadata_metrics())

        # Update history
        self.history["states"].append(self.states.copy())
        self.history["actions"].append(final_actions.copy())
        self.history["costs"].append(actual_costs.copy())
        self.history["budget_remaining"].append(self.budget.available())
        self.history["failures"].append(current_failures)

        # Display status if requested
        if display_status:
            self.display_status(info)

        return self.states.copy(), info

    def _compute_hierarchy_metrics(self) -> dict[str, Any]:
        """Compute hierarchy-based aggregation metrics."""
        metrics = {}

        if self.hierarchy is None:
            return metrics

        # Use the hierarchy model's compute method
        context = self._create_context()
        hierarchy_metrics = self.hierarchy.compute(context)

        return hierarchy_metrics

    def _compute_metadata_metrics(self) -> dict[str, Any]:
        """Compute metadata-based metrics."""
        metrics = {}

        if self.metadata is None:
            return metrics

        # Use the metadata model's compute method
        context = self._create_context()
        metadata_metrics = self.metadata.compute(context)

        return metadata_metrics

    def get_observation(self, observability: str = "full") -> np.ndarray:
        """Get observation based on observability setting."""
        if observability == "full":
            # Full state observability
            obs = np.concatenate(
                [
                    self.states / 10.0,  # Normalized states
                    self.time_since_inspection / 100.0,  # Normalized time
                    [
                        self.budget.available()
                        / (
                            self.budget.initial_budget
                            if hasattr(self.budget, "initial_budget")
                            else 100000.0
                        )
                    ],
                ]
            )
        elif observability == "partial":
            # Only recently inspected components are observable
            observable_mask = self.time_since_inspection <= 1
            observed_states = np.where(
                observable_mask, self.states, -1
            )  # -1 for unobserved
            obs = np.concatenate(
                [
                    observed_states / 10.0,
                    self.time_since_inspection / 100.0,
                    [
                        self.budget.available()
                        / (
                            self.budget.initial_budget
                            if hasattr(self.budget, "initial_budget")
                            else 100000.0
                        )
                    ],
                ]
            )
        elif observability == "noisy":
            # Noisy observations
            noise = np.random.normal(0, 0.1, size=self.states.shape)
            noisy_states = np.clip(self.states + noise, 0, 10)
            obs = np.concatenate(
                [
                    noisy_states / 10.0,
                    self.time_since_inspection / 100.0,
                    [
                        self.budget.available()
                        / (
                            self.budget.initial_budget
                            if hasattr(self.budget, "initial_budget")
                            else 100000.0
                        )
                    ],
                ]
            )
        else:
            raise ValueError(f"Unknown observability type: {observability}")

        return obs

    def batch_rollout(
        self, policy_fn, horizon: int, n_rollouts: int = 1
    ) -> dict[str, np.ndarray]:
        """Run multiple rollouts in parallel for Monte Carlo evaluation."""
        all_returns = []
        all_costs = []
        all_failures = []

        original_state = self.states.copy() if self.states is not None else None
        original_time_step = self.time_step

        for _rollout in range(n_rollouts):
            # Reset for each rollout
            if original_state is not None:
                self.reset(len(original_state), original_state)

            total_return = 0
            total_cost = 0
            rollout_failures = []

            for _step in range(horizon):
                # Get observation
                obs = self.get_observation()

                # Get action from policy
                actions = policy_fn(obs)

                # Take step
                states, info = self.step(actions)

                # Simple reward (negative cost and failure penalty)
                reward = -info["total_cost"] - info["failures"] * 100
                total_return += reward
                total_cost += info["total_cost"]
                rollout_failures.append(info["failures"])

                # Early termination conditions
                if info["budget_remaining"] <= 0:
                    break
                if info["failures"] > self.n_components * 0.5:  # More than half failed
                    break

            all_returns.append(total_return)
            all_costs.append(total_cost)
            all_failures.append(rollout_failures)

        # Restore original state
        if original_state is not None:
            self.reset(len(original_state), original_state)
            self.time_step = original_time_step

        return {
            "returns": np.array(all_returns),
            "costs": np.array(all_costs),
            "failures": np.array(all_failures),
            "mean_return": np.mean(all_returns),
            "std_return": np.std(all_returns),
            "mean_cost": np.mean(all_costs),
        }

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics from simulation history."""
        if len(self.history["states"]) < 2:
            return {}

        states_array = np.array(self.history["states"])

        metrics = {
            # Basic metrics
            "total_steps": len(self.history["states"]) - 1,
            "total_cost": np.sum([np.sum(c) for c in self.history["costs"]]),
            "final_budget": self.history["budget_remaining"][-1],
            "total_failures": self.history["failures"][-1],
            # Condition metrics
            "mean_final_condition": np.mean(states_array[-1]),
            "min_final_condition": np.min(states_array[-1]),
            "condition_deterioration": np.mean(states_array[0])
            - np.mean(states_array[-1]),
            # Performance over time
            "mean_condition_over_time": np.mean(states_array, axis=1),
            "failure_progression": self.history["failures"],
            "cost_per_step": [np.sum(c) for c in self.history["costs"]],
        }

        return metrics

    def _create_context(self, actions: np.ndarray | None = None) -> ModelContext:
        """Create ModelContext for the current simulation state.

        Parameters
        ----------
        actions : np.ndarray, optional
            Current actions being taken

        Returns
        -------
        ModelContext
            Context object with current state and model references
        """
        return ModelContext(
            states=self.states.copy() if self.states is not None else None,
            actions=actions.copy() if actions is not None else None,
            time_step=self.time_step,
            dynamics=self.dynamics,
            cost=self.cost,
            budget=self.budget,
            hierarchy=self.hierarchy,
            metadata=self.metadata,
            history=dict(self.history) if self.history else None,
        )

    def create_status_display(
        self, info: dict[str, Any] | None = None
    ) -> tuple[Panel, Progress]:
        """Create rich status display components.

        Parameters
        ----------
        info : dict, optional
            Information from last simulation step

        Returns
        -------
        tuple[Panel, Progress]
            Rich panel with status table and progress bar for budget usage
        """
        if not self.rich_display:
            raise ValueError(
                "Rich display not enabled. Set rich_display=True in constructor."
            )

        if len(self.history["actions"]) == 0:
            # No actions taken yet
            table = Table(show_header=False, expand=True)
            table.add_row("Current Step:", "0")
            table.add_row("Status:", "Initialized, no actions taken")

            progress = Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                TextColumn("{task.percentage:>3.0f}%"),
                TextColumn(" | Budget: Not started"),
                transient=True,
            )
            progress.add_task("Budget Usage:", total=100, completed=0)

        else:
            action = self.history["actions"][-1]
            action_counts = np.bincount(action, minlength=4)
            action_percentages = (action_counts * 100) / len(action)

            failure_percentage = (np.sum(self.states == 0) / len(self.states)) * 100

            table = Table(show_header=False, expand=True)
            table.add_row("Current Step:", f"{self.time_step}")
            table.add_row(
                "Do Nothing:", f"{action_counts[0]} ({action_percentages[0]:.0f}%)"
            )
            table.add_row(
                "Inspect:", f"{action_counts[1]} ({action_percentages[1]:.0f}%)"
            )
            table.add_row(
                "Repair:", f"{action_counts[2]} ({action_percentages[2]:.0f}%)"
            )
            table.add_row(
                "Replace:", f"{action_counts[3]} ({action_percentages[3]:.0f}%)"
            )
            table.add_row("Min Condition:", f"{np.min(self.states):.1f}")
            table.add_row("Mean Condition:", f"{np.mean(self.states):.1f}")
            table.add_row("Max Condition:", f"{np.max(self.states):.1f}")
            table.add_row(
                "Total Failures:",
                f"{np.sum(self.states == 0)} ({failure_percentage:.1f}%)",
            )

            # Budget information
            current_budget = (
                self.budget.available()
                if hasattr(self.budget, "available")
                else self.budget._available_internal()
            )
            initial_budget = getattr(
                self.budget,
                "initial_budget",
                current_budget + sum(sum(c) for c in self.history["costs"]),
            )

            if info and "actions_blocked" in info:
                table.add_row("Actions Blocked:", f"{info['actions_blocked']}")

            if initial_budget > 0:
                percent_budget_used = (
                    (initial_budget - current_budget) / initial_budget
                ) * 100
            else:
                percent_budget_used = 0

            progress = Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                TextColumn("{task.percentage:>3.0f}%"),
                TextColumn(" | Remaining: {task.fields[remaining_budget]:,.0f}"),
                transient=True,
            )

            progress.add_task(
                "Budget Usage:",
                total=100,
                completed=percent_budget_used,
                remaining_budget=current_budget,
            )

        # Create panel
        panel = Panel.fit(
            table,
            title="Infrastructure Simulation Status",
            border_style="green"
            if np.mean(self.states) > 5
            else "yellow"
            if np.mean(self.states) > 2
            else "red",
            padding=(1, 2),
        )

        return panel, progress

    def clear_terminal(self):
        """Clear the terminal screen in a cross-platform way."""
        if os.name == "nt":
            _ = os.system("cls")
        else:
            _ = os.system("clear")

    def display_status(self, info: dict[str, Any] | None = None):
        """Display the current simulation status using rich formatting.

        Parameters
        ----------
        info : dict, optional
            Information from the last simulation step
        """
        if not self.rich_display or not self.console:
            return

        panel, progress = self.create_status_display(info)
        self.console.print(Group(panel, progress))

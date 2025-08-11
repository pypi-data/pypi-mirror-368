"""Cost models with unified interface."""

import numpy as np

from .base import BaseModel, ModelContext


class CostModel(BaseModel):
    """Base class for cost models with unified interface."""

    def compute(self, context: ModelContext) -> np.ndarray:
        """Compute costs using context.

        Args:
            context: Must contain states and actions

        Returns:
            costs: Array of costs per component
        """
        if context.actions is None:
            raise ValueError("Actions required in context for cost computation")

        self.validate_context(context)

        next_states = None
        if context.dynamics:
            next_states = context.dynamics.compute(context)

        return self._compute_costs(context, next_states)

    def _compute_costs(
        self, context: ModelContext, next_states: np.ndarray | None
    ) -> np.ndarray:
        """Internal cost computation to be implemented by subclasses."""
        raise NotImplementedError

    def compute_legacy(
        self, states: np.ndarray, actions: np.ndarray, next_states: np.ndarray
    ) -> np.ndarray:
        """Legacy interface for backward compatibility."""
        context = ModelContext(states=states, actions=actions)
        return self._compute_costs(context, next_states)


class SimpleCost(CostModel):
    """Fixed costs per action type with validation."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "inspect_cost": (float, (0.0, 1000.0), "Cost of inspection action"),
            "repair_cost": (float, (0.0, 10000.0), "Cost of repair action"),
            "replace_cost": (float, (0.0, 50000.0), "Cost of replacement action"),
            "failure_penalty": (
                float,
                (0.0, 100000.0),
                "Penalty for component failure",
            ),
        }

    def __init__(
        self,
        inspect_cost: float = 10.0,
        repair_cost: float = 100.0,
        replace_cost: float = 1000.0,
        failure_penalty: float = 5000.0,
    ):
        super().__init__(
            inspect_cost=inspect_cost,
            repair_cost=repair_cost,
            replace_cost=replace_cost,
            failure_penalty=failure_penalty,
        )

    def _setup(self):
        """Setup cost arrays after validation."""
        self.action_costs = np.array(
            [
                0.0,
                self.params["inspect_cost"],
                self.params["repair_cost"],
                self.params["replace_cost"],
            ]
        )
        self.failure_penalty = self.params["failure_penalty"]

    def _compute_costs(
        self, context: ModelContext, next_states: np.ndarray | None
    ) -> np.ndarray:
        """Compute costs based on actions and failures."""
        states = context.states
        actions = context.actions

        if next_states is None:
            next_states = states

        costs = self.action_costs[actions]

        failure_mask = (next_states == 0) & (states > 0)
        costs[failure_mask] += self.failure_penalty

        return costs

    def reset(self, context: ModelContext | None = None):
        """Reset cost model (nothing to reset for simple costs)."""
        pass


class LengthBasedCost(CostModel):
    """Costs scaled by component length (for road networks)."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "inspect_cost_per_km": (float, (0.0, 500.0), "Inspection cost per km"),
            "repair_cost_per_km": (float, (0.0, 5000.0), "Repair cost per km"),
            "replace_cost_per_km": (float, (0.0, 25000.0), "Replacement cost per km"),
            "failure_penalty_per_km": (float, (0.0, 50000.0), "Failure penalty per km"),
        }

    def __init__(
        self,
        inspect_cost_per_km: float = 50.0,
        repair_cost_per_km: float = 500.0,
        replace_cost_per_km: float = 5000.0,
        failure_penalty_per_km: float = 10000.0,
        component_lengths: np.ndarray = None,
    ):
        super().__init__(
            inspect_cost_per_km=inspect_cost_per_km,
            repair_cost_per_km=repair_cost_per_km,
            replace_cost_per_km=replace_cost_per_km,
            failure_penalty_per_km=failure_penalty_per_km,
        )
        self.component_lengths = component_lengths

    def _setup(self):
        """Setup cost arrays after validation."""
        self.cost_per_km = np.array(
            [
                0.0,
                self.params["inspect_cost_per_km"],
                self.params["repair_cost_per_km"],
                self.params["replace_cost_per_km"],
            ]
        )
        self.failure_penalty_per_km = self.params["failure_penalty_per_km"]

        if self.component_lengths is None:
            self.component_lengths = np.ones(1)

    def set_component_lengths(self, lengths: np.ndarray):
        """Set component lengths for cost calculation."""
        self.component_lengths = lengths

    def _compute_costs(
        self, context: ModelContext, next_states: np.ndarray | None
    ) -> np.ndarray:
        """Compute length-scaled costs."""
        states = context.states
        actions = context.actions

        if next_states is None:
            next_states = states

        if context.metadata and hasattr(context.metadata, "get_bulk_attribute"):
            try:
                lengths = context.metadata.get_bulk_attribute(
                    range(len(states)), "length_km"
                )
            except (KeyError, AttributeError):
                lengths = self._get_lengths(len(states))
        else:
            lengths = self._get_lengths(len(states))

        costs = self.cost_per_km[actions] * lengths

        failure_mask = (next_states == 0) & (states > 0)
        costs[failure_mask] += self.failure_penalty_per_km * lengths[failure_mask]

        return costs

    def _get_lengths(self, n_components: int) -> np.ndarray:
        """Get component lengths array."""
        if len(self.component_lengths) == 1:
            return np.full(n_components, self.component_lengths[0])
        return self.component_lengths

    def reset(self, context: ModelContext | None = None):
        """Reset cost model."""
        pass


class NonlinearCost(CostModel):
    """Nonlinear cost model reflecting deterioration-dependent repair costs."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "inspect_cost": (float, (0.0, 1000.0), "Base inspection cost"),
            "replacement_cost": (float, (0.0, 50000.0), "Full replacement cost"),
            "cost_sensitivity": (float, (1.0, 5.0), "Cost sensitivity parameter"),
            "min_repair_fraction": (float, (0.1, 0.5), "Minimum repair cost fraction"),
            "failure_threshold": (int, (0, 10), "State below which component fails"),
            "failure_penalty": (float, (0.0, 100000.0), "Failure penalty"),
        }

    def __init__(
        self,
        inspect_cost: float = 10.0,
        replacement_cost: float = 1000.0,
        cost_sensitivity: float = 2.0,
        min_repair_fraction: float = 0.2,
        failure_threshold: int = 1,
        failure_penalty: float = 5000.0,
        n_states: int = 10,
    ):
        super().__init__(
            inspect_cost=inspect_cost,
            replacement_cost=replacement_cost,
            cost_sensitivity=cost_sensitivity,
            min_repair_fraction=min_repair_fraction,
            failure_threshold=failure_threshold,
            failure_penalty=failure_penalty,
        )
        self.n_states = n_states

    def _setup(self):
        """Setup cost parameters after validation."""
        self.inspect_cost = self.params["inspect_cost"]
        self.replacement_cost = self.params["replacement_cost"]
        self.cost_sensitivity = self.params["cost_sensitivity"]
        self.min_repair_fraction = self.params["min_repair_fraction"]
        self.failure_threshold = self.params["failure_threshold"]
        self.failure_penalty = self.params["failure_penalty"]

    def _compute_costs(
        self, context: ModelContext, next_states: np.ndarray | None
    ) -> np.ndarray:
        """Compute nonlinear costs based on component condition."""
        states = context.states
        actions = context.actions

        if next_states is None:
            next_states = states

        costs = np.zeros_like(states, dtype=float)

        inspect_mask = actions == 1
        costs[inspect_mask] = self.inspect_cost

        repair_mask = actions == 2
        repair_costs = self._compute_repair_costs(states[repair_mask])
        costs[repair_mask] = repair_costs

        replace_mask = actions == 3
        costs[replace_mask] = self.replacement_cost

        failure_mask = (next_states <= self.failure_threshold) & (
            states > self.failure_threshold
        )
        costs[failure_mask] += self.failure_penalty

        return costs

    def reset(self, context: ModelContext | None = None):
        """Reset cost model."""
        pass

    def _compute_repair_costs(self, states: np.ndarray) -> np.ndarray:
        """Compute state-dependent repair costs."""
        if len(states) == 0:
            return np.array([])

        normalized_condition = states / (self.n_states - 1)
        cost_multiplier = (
            (1 - normalized_condition) ** self.cost_sensitivity
        ) + self.min_repair_fraction

        return cost_multiplier * self.replacement_cost

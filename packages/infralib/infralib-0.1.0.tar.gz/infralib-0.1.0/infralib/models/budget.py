"""Budget models with unified interface."""

from typing import Any

import numpy as np

from .base import BaseModel, ModelContext


class BudgetModel(BaseModel):
    """Base class for budget models with unified interface."""

    def compute(self, context: ModelContext) -> dict[str, Any]:
        """Compute budget state and constraints.

        Args:
            context: Contains costs and state information

        Returns:
            Dict with 'available', 'consumed', 'sufficient' keys
        """
        self.validate_context(context)
        return self._compute_budget(context)

    def _compute_budget(self, context: ModelContext) -> dict[str, Any]:
        """Internal budget computation to be implemented by subclasses."""
        raise NotImplementedError

    def apply_constraint(self, costs: np.ndarray) -> tuple[np.ndarray, float]:
        """Apply budget constraints to proposed costs.

        Args:
            costs: Proposed costs per component

        Returns:
            (allowed_mask, remaining_budget)
        """
        raise NotImplementedError

    def update(self, cost: float) -> bool:
        """Legacy interface for backward compatibility."""
        result = self._update_internal(cost)
        return result

    def available(self) -> float:
        """Legacy interface for backward compatibility."""
        return self._available_internal()

    def _update_internal(self, cost: float) -> bool:
        """Internal update method."""
        raise NotImplementedError

    def _available_internal(self) -> float:
        """Internal available method."""
        raise NotImplementedError


class FixedBudget(BudgetModel):
    """Fixed budget model with validation."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "initial_budget": (float, (0.0, 1e9), "Initial budget amount"),
        }

    def __init__(self, initial_budget: float = 100000.0):
        super().__init__(initial_budget=initial_budget)

    def _setup(self):
        """Setup budget parameters after validation."""
        self.initial_budget = self.params["initial_budget"]
        self.current_budget = self.initial_budget

    def reset(self, context: ModelContext | None = None):
        """Reset budget to initial amount."""
        self.current_budget = self.initial_budget

    def _compute_budget(self, context: ModelContext) -> dict[str, Any]:
        """Compute budget state."""
        total_cost = 0.0
        if context.cost and context.actions is not None:
            costs = context.cost.compute(context)
            total_cost = np.sum(costs)

        sufficient = total_cost <= self.current_budget

        return {
            "available": self.current_budget,
            "consumed": total_cost,
            "sufficient": sufficient,
            "remaining_after": self.current_budget - total_cost if sufficient else 0,
        }

    def apply_constraint(self, costs: np.ndarray) -> tuple[np.ndarray, float]:
        """Apply budget constraints to costs."""
        n_components = len(costs)
        allowed = np.zeros(n_components, dtype=bool)
        remaining = self.current_budget

        sorted_indices = np.argsort(costs)

        for idx in sorted_indices:
            if costs[idx] <= remaining:
                allowed[idx] = True
                remaining -= costs[idx]

        return allowed, remaining

    def _update_internal(self, cost: float) -> bool:
        """Update budget with cost."""
        if cost <= self.current_budget:
            self.current_budget -= cost
            return True
        return False

    def _available_internal(self) -> float:
        """Return available budget."""
        return self.current_budget


class CyclicBudget(BudgetModel):
    """Cyclic budget model with periodic allocations."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "cycle_budget": (float, (0.0, 1e9), "Budget per cycle"),
            "cycle_length": (int, (1, 1000), "Length of each budget cycle"),
        }

    def __init__(self, cycle_budget: float = 50000.0, cycle_length: int = 30):
        super().__init__(cycle_budget=cycle_budget, cycle_length=cycle_length)

    def _setup(self):
        """Setup budget parameters after validation."""
        self.cycle_budget = self.params["cycle_budget"]
        self.cycle_length = self.params["cycle_length"]
        self.current_budget = self.cycle_budget
        self.time_in_cycle = 0

    def reset(self, context: ModelContext | None = None):
        """Reset budget to initial state."""
        self.current_budget = self.cycle_budget
        self.time_in_cycle = 0

    def step_time(self):
        """Advance time and refresh budget if cycle complete."""
        self.time_in_cycle += 1
        if self.time_in_cycle >= self.cycle_length:
            self.current_budget = self.cycle_budget
            self.time_in_cycle = 0

    def _compute_budget(self, context: ModelContext) -> dict[str, Any]:
        """Compute budget state."""
        total_cost = 0.0
        if context.cost and context.actions is not None:
            costs = context.cost.compute(context)
            total_cost = np.sum(costs)

        sufficient = total_cost <= self.current_budget

        return {
            "available": self.current_budget,
            "consumed": total_cost,
            "sufficient": sufficient,
            "remaining_after": self.current_budget - total_cost if sufficient else 0,
            "time_in_cycle": self.time_in_cycle,
            "cycle_length": self.cycle_length,
        }

    def apply_constraint(self, costs: np.ndarray) -> tuple[np.ndarray, float]:
        """Apply budget constraints to costs."""
        n_components = len(costs)
        allowed = np.zeros(n_components, dtype=bool)
        remaining = self.current_budget

        sorted_indices = np.argsort(costs)

        for idx in sorted_indices:
            if costs[idx] <= remaining:
                allowed[idx] = True
                remaining -= costs[idx]

        return allowed, remaining

    def _update_internal(self, cost: float) -> bool:
        """Update budget with cost."""
        if cost <= self.current_budget:
            self.current_budget -= cost
            return True
        return False

    def _available_internal(self) -> float:
        """Return available budget."""
        return self.current_budget


class VariableCyclicBudget(BudgetModel):
    """Variable cyclic budget with different amounts per cycle."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "min_budget": (float, (0.0, 1e9), "Minimum cycle budget"),
            "max_budget": (float, (0.0, 1e9), "Maximum cycle budget"),
            "cycle_length": (int, (1, 1000), "Length of each budget cycle"),
        }

    def __init__(self, cycle_budgets: list[float], cycle_lengths: list[int] = None):
        if not cycle_budgets:
            raise ValueError("Must provide at least one cycle budget")

        for budget in cycle_budgets:
            if budget < 0:
                raise ValueError("Budget amounts must be non-negative")

        self.cycle_budgets = cycle_budgets
        self.cycle_lengths = (
            cycle_lengths if cycle_lengths else [30] * len(cycle_budgets)
        )

        if len(self.cycle_lengths) != len(cycle_budgets):
            raise ValueError("Must provide equal number of budgets and cycle lengths")

        super().__init__()

    def _setup(self):
        """Setup budget parameters."""
        self.current_cycle_index = 0
        self.current_budget = self.cycle_budgets[0]
        self.time_in_cycle = 0

    @classmethod
    def get_parameter_spec(cls):
        return {}

    def reset(self, context: ModelContext | None = None):
        """Reset budget to initial state."""
        self.current_cycle_index = 0
        self.current_budget = self.cycle_budgets[0]
        self.time_in_cycle = 0

    def step_time(self):
        """Advance time and refresh budget if cycle complete."""
        self.time_in_cycle += 1
        current_cycle_length = self.cycle_lengths[self.current_cycle_index]

        if self.time_in_cycle >= current_cycle_length:
            # Move to next cycle
            self.current_cycle_index = (self.current_cycle_index + 1) % len(
                self.cycle_budgets
            )
            self.current_budget = self.cycle_budgets[self.current_cycle_index]
            self.time_in_cycle = 0

    def _compute_budget(self, context: ModelContext) -> dict[str, Any]:
        """Compute budget state."""
        total_cost = 0.0
        if context.cost and context.actions is not None:
            costs = context.cost.compute(context)
            total_cost = np.sum(costs)

        sufficient = total_cost <= self.current_budget

        return {
            "available": self.current_budget,
            "consumed": total_cost,
            "sufficient": sufficient,
            "remaining_after": self.current_budget - total_cost if sufficient else 0,
            "cycle_index": self.current_cycle_index,
            "time_in_cycle": self.time_in_cycle,
        }

    def apply_constraint(self, costs: np.ndarray) -> tuple[np.ndarray, float]:
        """Apply budget constraints to costs."""
        n_components = len(costs)
        allowed = np.zeros(n_components, dtype=bool)
        remaining = self.current_budget

        sorted_indices = np.argsort(costs)

        for idx in sorted_indices:
            if costs[idx] <= remaining:
                allowed[idx] = True
                remaining -= costs[idx]

        return allowed, remaining

    def _update_internal(self, cost: float) -> bool:
        """Update budget with cost."""
        if cost <= self.current_budget:
            self.current_budget -= cost
            return True
        return False

    def _available_internal(self) -> float:
        """Return available budget."""
        return self.current_budget


class EmergencyReserveBudget(BudgetModel):
    """Budget with emergency reserve that can be accessed under certain conditions."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "normal_budget": (float, (0.0, 1e9), "Normal operating budget"),
            "emergency_reserve": (float, (0.0, 1e9), "Emergency reserve amount"),
            "emergency_threshold": (
                int,
                (1, 100),
                "Failure count triggering emergency",
            ),
        }

    def __init__(
        self,
        normal_budget: float = 100000.0,
        emergency_reserve: float = 50000.0,
        emergency_threshold: int = 5,
    ):
        super().__init__(
            normal_budget=normal_budget,
            emergency_reserve=emergency_reserve,
            emergency_threshold=emergency_threshold,
        )

    def _setup(self):
        """Setup budget parameters after validation."""
        self.initial_normal_budget = self.params["normal_budget"]
        self.emergency_reserve_amount = self.params["emergency_reserve"]
        self.emergency_threshold = self.params["emergency_threshold"]

        self.normal_budget = self.initial_normal_budget
        self.emergency_reserve = self.emergency_reserve_amount
        self.emergency_active = False

    def reset(self, context: ModelContext | None = None):
        """Reset budget to initial state."""
        self.normal_budget = self.initial_normal_budget
        self.emergency_reserve = self.emergency_reserve_amount
        self.emergency_active = False

    def activate_emergency(self, failure_count: int):
        """Activate emergency reserve if failure threshold exceeded."""
        if failure_count >= self.emergency_threshold:
            self.emergency_active = True

    def _compute_budget(self, context: ModelContext) -> dict[str, Any]:
        """Compute budget state with emergency reserve logic."""
        total_cost = 0.0
        if context.cost and context.actions is not None:
            costs = context.cost.compute(context)
            total_cost = np.sum(costs)

        failures = np.sum(context.states == 0) if context.states is not None else 0
        if failures >= self.emergency_threshold:
            self.emergency_active = True

        available_budget = self.normal_budget
        if self.emergency_active:
            available_budget += self.emergency_reserve

        sufficient = total_cost <= available_budget

        return {
            "available": available_budget,
            "consumed": total_cost,
            "sufficient": sufficient,
            "normal_budget": self.normal_budget,
            "emergency_reserve": self.emergency_reserve,
            "emergency_active": self.emergency_active,
            "failures": failures,
        }

    def apply_constraint(self, costs: np.ndarray) -> tuple[np.ndarray, float]:
        """Apply budget constraints with emergency reserve."""
        n_components = len(costs)
        allowed = np.zeros(n_components, dtype=bool)

        available = self.normal_budget
        if self.emergency_active:
            available += self.emergency_reserve

        remaining = available
        sorted_indices = np.argsort(costs)

        for idx in sorted_indices:
            if costs[idx] <= remaining:
                allowed[idx] = True
                remaining -= costs[idx]

        return allowed, remaining

    def _update_internal(self, cost: float) -> bool:
        """Update budget with cost, using emergency reserve if needed."""
        if cost <= self.normal_budget:
            self.normal_budget -= cost
            return True
        elif self.emergency_active and cost <= (
            self.normal_budget + self.emergency_reserve
        ):
            remaining_cost = cost - self.normal_budget
            self.normal_budget = 0
            self.emergency_reserve -= remaining_cost
            return True
        return False

    def _available_internal(self) -> float:
        """Return available budget."""
        if self.emergency_active:
            return self.normal_budget + self.emergency_reserve
        return self.normal_budget

"""Example of adaptive budget model that adjusts based on system health."""

import numpy as np

from infralib.models.base import ModelContext
from infralib.models.budget import BudgetModel


class AdaptiveBudget(BudgetModel):
    """Budget model that adapts allocation based on hierarchy and metadata."""

    @classmethod
    def get_required_models(cls) -> list[str]:
        """Requires hierarchy to assess system health."""
        return ["hierarchy"]

    @classmethod
    def get_parameter_spec(cls):
        return {
            "base_budget": (float, (0.0, 1e9), "Base budget allocation"),
            "emergency_multiplier": (
                float,
                (1.0, 5.0),
                "Budget multiplier for emergencies",
            ),
            "critical_threshold": (
                float,
                (0.0, 10.0),
                "Health threshold to trigger emergency",
            ),
            "health_bonus": (float, (0.0, 2.0), "Bonus multiplier for healthy systems"),
        }

    def __init__(
        self,
        base_budget: float = 100000.0,
        emergency_multiplier: float = 2.0,
        critical_threshold: float = 3.0,
        health_bonus: float = 1.2,
    ):
        super().__init__(
            base_budget=base_budget,
            emergency_multiplier=emergency_multiplier,
            critical_threshold=critical_threshold,
            health_bonus=health_bonus,
        )

    def _setup(self):
        """Setup adaptive budget parameters."""
        self.base_budget = self.params["base_budget"]
        self.emergency_multiplier = self.params["emergency_multiplier"]
        self.critical_threshold = self.params["critical_threshold"]
        self.health_bonus = self.params["health_bonus"]

        self.current_budget = self.base_budget
        self.last_period_budget = self.base_budget
        self.emergency_active = False

    def _compute_budget(self, context: ModelContext) -> dict[str, any]:
        """Compute adaptive budget based on system health."""
        if context.states is None:
            return {"available": self.current_budget, "consumed": 0, "sufficient": True}

        # Assess overall system health using hierarchy
        system_health_scores = {}
        emergency_systems = []
        healthy_systems = []

        if context.hierarchy:
            # Get system-level health metrics
            for level in context.hierarchy.get_hierarchy_levels():
                if level.name == "system":
                    systems = context.hierarchy.get_all_groups("system")
                    for system in systems:
                        components = context.hierarchy.get_group_components(
                            system, "system"
                        )
                        if components:
                            component_states = [
                                context.states[cid]
                                for cid in components
                                if cid < len(context.states)
                            ]
                            if component_states:
                                avg_health = np.mean(component_states)
                                system_health_scores[system] = avg_health

                                if avg_health <= self.critical_threshold:
                                    emergency_systems.append(system)
                                elif avg_health >= 8.0:  # Healthy threshold
                                    healthy_systems.append(system)

        # Adjust budget based on system health
        budget_multiplier = 1.0

        if emergency_systems:
            # Emergency: Increase budget significantly
            self.emergency_active = True
            emergency_severity = len(emergency_systems) / max(
                1, len(system_health_scores)
            )
            budget_multiplier = 1 + (self.emergency_multiplier - 1) * emergency_severity

        elif len(healthy_systems) > len(system_health_scores) * 0.7:
            # Most systems healthy: Apply health bonus
            self.emergency_active = False
            budget_multiplier = self.health_bonus

        else:
            # Normal operation
            self.emergency_active = False
            budget_multiplier = 1.0

        # Calculate adjusted budget
        adjusted_budget = self.base_budget * budget_multiplier

        # Smooth budget transitions (don't change too drastically)
        max_change = 0.3  # Maximum 30% change per period
        budget_change = adjusted_budget - self.last_period_budget
        if abs(budget_change) > self.last_period_budget * max_change:
            if budget_change > 0:
                adjusted_budget = self.last_period_budget * (1 + max_change)
            else:
                adjusted_budget = self.last_period_budget * (1 - max_change)

        self.current_budget = adjusted_budget
        self.last_period_budget = adjusted_budget

        # Calculate costs if available
        total_cost = 0.0
        if context.cost and context.actions is not None:
            costs = context.cost.compute(context)
            total_cost = np.sum(costs)

        sufficient = total_cost <= self.current_budget

        return {
            "available": self.current_budget,
            "consumed": total_cost,
            "sufficient": sufficient,
            "base_budget": self.base_budget,
            "budget_multiplier": budget_multiplier,
            "emergency_active": self.emergency_active,
            "emergency_systems": emergency_systems,
            "healthy_systems": healthy_systems,
            "system_health_scores": system_health_scores,
        }

    def apply_constraint(self, costs: np.ndarray) -> tuple[np.ndarray, float]:
        """Apply adaptive constraints - prioritize emergency systems."""
        n_components = len(costs)
        allowed = np.zeros(n_components, dtype=bool)
        remaining = self.current_budget

        # Simple greedy allocation for now
        sorted_indices = np.argsort(costs)

        for idx in sorted_indices:
            if costs[idx] <= remaining:
                allowed[idx] = True
                remaining -= costs[idx]

        return allowed, remaining

    def reset(self, context: ModelContext | None = None):
        """Reset adaptive budget."""
        self.current_budget = self.base_budget
        self.last_period_budget = self.base_budget
        self.emergency_active = False

    def _update_internal(self, cost: float) -> bool:
        """Update budget with cost."""
        if cost <= self.current_budget:
            self.current_budget -= cost
            return True
        return False

    def _available_internal(self) -> float:
        """Return available budget."""
        return self.current_budget


if __name__ == "__main__":
    from infralib.models.hierarchy import SimpleHierarchy

    # Setup scenario
    hierarchy = SimpleHierarchy()

    # Create systems with different health levels
    for i in range(12):
        system = f"sys_{i//4}"  # 3 systems with 4 components each
        hierarchy.assign_component(i, {"component": f"comp_{i}", "system": system})

    # Set system criticality
    hierarchy.set_group_property("sys_0", "system", "criticality", "critical")
    hierarchy.set_group_property("sys_1", "system", "criticality", "normal")
    hierarchy.set_group_property("sys_2", "system", "criticality", "normal")

    # Create budget model
    adaptive_budget = AdaptiveBudget(
        base_budget=50000.0,
        emergency_multiplier=2.5,
        critical_threshold=3.0,
        health_bonus=1.3,
    )

    # Test different scenarios
    print("=== Scenario 1: Normal Operation ===")
    normal_states = np.array([8, 7, 6, 9, 8, 7, 6, 8, 9, 7, 8, 6])  # Decent health
    context1 = ModelContext(states=normal_states, hierarchy=hierarchy)

    budget_info1 = adaptive_budget.compute(context1)
    print(f"Available budget: ${budget_info1['available']:,.0f}")
    print(f"Budget multiplier: {budget_info1['budget_multiplier']:.2f}")
    print(f"Emergency active: {budget_info1['emergency_active']}")
    print(f"System health scores: {budget_info1['system_health_scores']}")

    print("\n=== Scenario 2: Emergency - Critical System Failing ===")
    emergency_states = np.array(
        [1, 0, 2, 1, 8, 7, 6, 8, 9, 7, 8, 6]
    )  # sys_0 in bad shape
    context2 = ModelContext(states=emergency_states, hierarchy=hierarchy)

    budget_info2 = adaptive_budget.compute(context2)
    print(f"Available budget: ${budget_info2['available']:,.0f}")
    print(f"Budget multiplier: {budget_info2['budget_multiplier']:.2f}")
    print(f"Emergency active: {budget_info2['emergency_active']}")
    print(f"Emergency systems: {budget_info2['emergency_systems']}")
    print(f"System health scores: {budget_info2['system_health_scores']}")

    print("\n=== Scenario 3: All Systems Healthy ===")
    healthy_states = np.array(
        [9, 9, 8, 9, 9, 8, 9, 9, 9, 8, 9, 8]
    )  # All systems healthy
    context3 = ModelContext(states=healthy_states, hierarchy=hierarchy)

    budget_info3 = adaptive_budget.compute(context3)
    print(f"Available budget: ${budget_info3['available']:,.0f}")
    print(f"Budget multiplier: {budget_info3['budget_multiplier']:.2f}")
    print(f"Emergency active: {budget_info3['emergency_active']}")
    print(f"Healthy systems: {budget_info3['healthy_systems']}")
    print(f"System health scores: {budget_info3['system_health_scores']}")

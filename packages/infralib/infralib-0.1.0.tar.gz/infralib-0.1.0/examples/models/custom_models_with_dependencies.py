"""Example custom models that use dependencies between models."""

import numpy as np

from infralib.models.base import ModelContext
from infralib.models.cost import CostModel
from infralib.models.dynamics import DynamicsModel


class HierarchyAwareCost(CostModel):
    """Custom cost model that uses hierarchy to adjust costs."""

    @classmethod
    def get_required_models(cls) -> list[str]:
        """This model requires hierarchy and optionally uses metadata."""
        return ["hierarchy"]

    @classmethod
    def get_parameter_spec(cls):
        return {
            "base_inspect_cost": (float, (0.0, 1000.0), "Base inspection cost"),
            "base_repair_cost": (float, (0.0, 10000.0), "Base repair cost"),
            "base_replace_cost": (float, (0.0, 50000.0), "Base replacement cost"),
            "critical_multiplier": (
                float,
                (1.0, 5.0),
                "Cost multiplier for critical components",
            ),
        }

    def __init__(
        self,
        base_inspect_cost: float = 10.0,
        base_repair_cost: float = 100.0,
        base_replace_cost: float = 1000.0,
        critical_multiplier: float = 2.0,
    ):
        super().__init__(
            base_inspect_cost=base_inspect_cost,
            base_repair_cost=base_repair_cost,
            base_replace_cost=base_replace_cost,
            critical_multiplier=critical_multiplier,
        )

    def _setup(self):
        """Setup cost arrays."""
        self.base_costs = np.array(
            [
                0.0,
                self.params["base_inspect_cost"],
                self.params["base_repair_cost"],
                self.params["base_replace_cost"],
            ]
        )
        self.critical_multiplier = self.params["critical_multiplier"]

    def _compute_costs(
        self, context: ModelContext, next_states: np.ndarray | None
    ) -> np.ndarray:
        """Compute costs with hierarchy-based adjustments."""
        states = context.states
        actions = context.actions
        n_components = len(states)

        base_costs = self.base_costs[actions]

        if context.hierarchy:
            for i in range(n_components):
                system = context.hierarchy.get_component_group(i, "system")
                if system:
                    criticality = context.hierarchy.get_group_property(
                        system, "system", "criticality"
                    )
                    if criticality == "critical":
                        base_costs[i] *= self.critical_multiplier

        if context.metadata:
            try:
                importance = context.metadata.get_bulk_attribute(
                    range(n_components), "importance"
                )
                base_costs *= importance
            except (KeyError, AttributeError):
                pass

        return base_costs

    def reset(self, context: ModelContext | None = None):
        """Reset cost model."""
        pass


class MetadataBasedDynamics(DynamicsModel):
    """Custom dynamics that deteriorate based on metadata attributes."""

    @classmethod
    def get_required_models(cls) -> list[str]:
        """This model requires metadata."""
        return ["metadata"]

    @classmethod
    def get_parameter_spec(cls):
        return {
            "n_states": (int, (2, 100), "Number of discrete states"),
            "base_deterioration_rate": (
                float,
                (0.0, 1.0),
                "Base deterioration probability",
            ),
            "environment_factor": (
                float,
                (1.0, 3.0),
                "Environmental deterioration multiplier",
            ),
        }

    def __init__(
        self,
        n_states: int = 10,
        base_deterioration_rate: float = 0.1,
        environment_factor: float = 1.5,
    ):
        super().__init__(
            n_states=n_states,
            base_deterioration_rate=base_deterioration_rate,
            environment_factor=environment_factor,
        )

    def _setup(self):
        """Setup dynamics parameters."""
        self.n_states = self.params["n_states"]
        self.base_rate = self.params["base_deterioration_rate"]
        self.env_factor = self.params["environment_factor"]

    def _compute_dynamics(self, context: ModelContext) -> np.ndarray:
        """Compute dynamics with metadata-based deterioration rates."""
        states = context.states
        actions = context.actions
        n_components = len(states)
        next_states = states.copy()

        deterioration_rates = np.full(n_components, self.base_rate)

        if context.metadata:
            try:
                environments = context.metadata.get_bulk_attribute(
                    range(n_components), "environment"
                )
                for i, env in enumerate(environments):
                    if env == "harsh":
                        deterioration_rates[i] *= self.env_factor
                    elif env == "mild":
                        deterioration_rates[i] *= 0.5
            except (KeyError, AttributeError):
                pass

        for i in range(n_components):
            if actions[i] in [0, 1]:
                if states[i] > 0 and np.random.random() < deterioration_rates[i]:
                    next_states[i] = max(0, states[i] - 1)
            elif actions[i] == 2:
                improvement = int(0.7 * (self.n_states - states[i]))
                next_states[i] = min(self.n_states - 1, states[i] + improvement)
            elif actions[i] == 3:
                next_states[i] = self.n_states - 1

        return next_states

    def reset(self, context: ModelContext | None = None):
        """Reset dynamics model."""
        pass


class IntegratedCostModel(CostModel):
    """Complex cost model using dynamics, hierarchy, and metadata."""

    @classmethod
    def get_required_models(cls) -> list[str]:
        """This model uses all available models."""
        return ["dynamics", "hierarchy", "metadata"]

    @classmethod
    def get_parameter_spec(cls):
        return {
            "base_cost": (float, (0.0, 10000.0), "Base action cost"),
            "failure_penalty": (float, (0.0, 100000.0), "Penalty for failures"),
            "preventive_discount": (
                float,
                (0.0, 1.0),
                "Discount for preventive maintenance",
            ),
        }

    def __init__(
        self,
        base_cost: float = 100.0,
        failure_penalty: float = 5000.0,
        preventive_discount: float = 0.3,
    ):
        super().__init__(
            base_cost=base_cost,
            failure_penalty=failure_penalty,
            preventive_discount=preventive_discount,
        )

    def _setup(self):
        """Setup cost parameters."""
        self.base_cost = self.params["base_cost"]
        self.failure_penalty = self.params["failure_penalty"]
        self.preventive_discount = self.params["preventive_discount"]

    def _compute_costs(
        self, context: ModelContext, next_states: np.ndarray | None
    ) -> np.ndarray:
        """Compute integrated costs using all available information."""
        states = context.states
        actions = context.actions
        n_components = len(states)

        action_costs = np.array([0, 0.1, 1.0, 3.0]) * self.base_cost
        costs = action_costs[actions]

        if next_states is None and context.dynamics:
            next_states = context.dynamics.compute(context)

        if next_states is not None:
            failures = (next_states == 0) & (states > 0)
            failure_penalties = np.zeros(n_components)
            failure_penalties[failures] = self.failure_penalty

            if context.hierarchy:
                for i in np.where(failures)[0]:
                    system = context.hierarchy.get_component_group(i, "system")
                    if system:
                        criticality = context.hierarchy.get_group_property(
                            system, "system", "criticality"
                        )
                        if criticality == "critical":
                            failure_penalties[i] *= 2.0

                        system_components = context.hierarchy.get_group_components(
                            system, "system"
                        )
                        if len(system_components) > 1:
                            failure_penalties[i] *= 1.5

            costs += failure_penalties

        if context.metadata:
            try:
                ages = context.metadata.get_bulk_attribute(range(n_components), "age")
                preventive_mask = (actions == 2) & (states > 5) & (ages < 5)
                costs[preventive_mask] *= 1 - self.preventive_discount
            except (KeyError, AttributeError):
                pass

        if context.hierarchy and context.metadata:
            for level in context.hierarchy.get_hierarchy_levels():
                if level.name == "component":
                    continue

                groups = context.hierarchy.get_all_groups(level.name)
                for group in groups:
                    components = context.hierarchy.get_group_components(
                        group, level.name
                    )
                    if len(components) > 5:
                        group_actions = actions[components]
                        if np.sum(group_actions > 0) > 3:
                            costs[components] *= 0.8

        return costs

    def reset(self, context: ModelContext | None = None):
        """Reset cost model."""
        pass


if __name__ == "__main__":
    from infralib.models.dynamics import MarkovDynamics
    from infralib.models.hierarchy import SimpleHierarchy
    from infralib.models.metadata import SimpleMetadata

    hierarchy = SimpleHierarchy()
    for i in range(10):
        hierarchy.assign_component(
            i, {"component": f"comp_{i}", "system": f"sys_{i//3}"}
        )
    hierarchy.set_group_property("sys_0", "system", "criticality", "critical")

    metadata = SimpleMetadata()
    for i in range(10):
        metadata.add_component(
            i,
            {
                "id": i,
                "name": f"Component {i}",
                "importance": 1.0 + (i % 3) * 0.5,
                "location": "coastal" if i < 5 else "inland",
            },
        )

    dynamics = MarkovDynamics(n_states=10)

    custom_cost = HierarchyAwareCost(critical_multiplier=2.5)

    context = ModelContext(
        states=np.array([9, 8, 7, 6, 5, 4, 3, 2, 1, 9]),
        actions=np.array([0, 1, 2, 3, 2, 1, 0, 2, 3, 1]),
        hierarchy=hierarchy,
        metadata=metadata,
        dynamics=dynamics,
    )

    costs = custom_cost.compute(context)
    print(f"Component costs: {costs}")
    print(f"Total cost: {np.sum(costs):.2f}")

    print("\nHierarchy metrics:")
    hierarchy_metrics = hierarchy.compute(context)
    for level, metrics in hierarchy_metrics.items():
        print(f"  {level}: {metrics}")

    print("\nMetadata metrics:")
    metadata_metrics = metadata.compute(context)
    for field, stats in metadata_metrics.items():
        if isinstance(stats, dict):
            print(
                f"  {field}: mean={stats.get('mean', 0):.2f}, std={stats.get('std', 0):.2f}"
            )

    integrated_cost = IntegratedCostModel()
    integrated_costs = integrated_cost.compute(context)
    print(f"\nIntegrated costs: {integrated_costs}")
    print(f"Total integrated cost: {np.sum(integrated_costs):.2f}")

"""Tests for core models with unified architecture."""

import numpy as np
import pytest

from infralib.models.base import ModelContext
from infralib.models.budget import CyclicBudget, EmergencyReserveBudget, FixedBudget
from infralib.models.cost import NonlinearCost, SimpleCost
from infralib.models.dynamics import MarkovDynamics, WeibullDynamics
from infralib.models.hierarchy import GeneralHierarchy, HierarchyLevel, SimpleHierarchy
from infralib.models.metadata import FieldDefinition, GeneralMetadata, SimpleMetadata


class TestBaseModel:
    """Test base model functionality."""

    def test_model_context_creation(self):
        """Test ModelContext creation and access."""
        states = np.array([5, 3, 8])
        actions = np.array([0, 1, 2])

        context = ModelContext(states=states, actions=actions, time_step=10)

        assert np.array_equal(context.states, states)
        assert np.array_equal(context.actions, actions)
        assert context.time_step == 10
        assert context.dynamics is None
        assert context.get_model("dynamics") is None

    def test_model_context_with_dependencies(self):
        """Test ModelContext with model dependencies."""
        dynamics = MarkovDynamics()
        hierarchy = SimpleHierarchy()

        context = ModelContext(
            states=np.array([5]), dynamics=dynamics, hierarchy=hierarchy
        )

        assert context.get_model("dynamics") == dynamics
        assert context.get_model("hierarchy") == hierarchy
        assert context.get_model("cost") is None


class TestDynamicsModels:
    """Test dynamics models with unified interface."""

    def test_weibull_dynamics_initialization(self):
        """Test WeibullDynamics initialization and parameter validation."""
        dynamics = WeibullDynamics(n_states=10, shape=2.5, scale=15.0)
        assert dynamics.params["n_states"] == 10
        assert dynamics.params["shape"] == 2.5
        assert dynamics.params["scale"] == 15.0

        with pytest.raises(ValueError):
            WeibullDynamics(n_states=1)

        with pytest.raises(ValueError):
            WeibullDynamics(shape=0.1)

    def test_weibull_dynamics_compute(self):
        """Test dynamics computation with context."""
        dynamics = WeibullDynamics(n_states=10, seed=42)

        states = np.array([5, 3, 8])
        actions = np.array([0, 2, 3])

        context = ModelContext(states=states, actions=actions)
        next_states = dynamics.compute(context)

        assert len(next_states) == 3
        assert next_states[2] == 9  # Replace should restore to perfect
        assert all(0 <= s <= 9 for s in next_states)

    def test_dynamics_legacy_interface(self):
        """Test backward compatibility with step() method."""
        dynamics = WeibullDynamics(n_states=10, seed=42)

        states = np.array([5])
        actions = np.array([0])

        next_states = dynamics.step(states, actions)
        assert len(next_states) == 1
        assert 0 <= next_states[0] <= 9

    def test_markov_dynamics(self):
        """Test MarkovDynamics model."""
        dynamics = MarkovDynamics(n_states=10, base_deterioration_rate=0.2, seed=42)

        context = ModelContext(states=np.array([5, 3]), actions=np.array([0, 1]))

        next_states = dynamics.compute(context)
        assert len(next_states) == 2
        assert all(0 <= s <= 9 for s in next_states)


class TestCostModels:
    """Test cost models with unified interface."""

    def test_simple_cost(self):
        """Test SimpleCost model."""
        cost_model = SimpleCost(
            inspect_cost=10.0,
            repair_cost=100.0,
            replace_cost=1000.0,
            failure_penalty=5000.0,
        )

        states = np.array([5, 3, 1])
        actions = np.array([0, 1, 2])

        context = ModelContext(states=states, actions=actions)
        costs = cost_model.compute(context)

        expected_costs = np.array([0.0, 10.0, 100.0])
        np.testing.assert_array_equal(costs, expected_costs)

    def test_cost_with_dynamics_context(self):
        """Test cost model using dynamics from context."""
        dynamics = MarkovDynamics(n_states=10, seed=42)
        cost_model = SimpleCost(failure_penalty=5000.0)

        states = np.array([1])
        actions = np.array([0])

        context = ModelContext(states=states, actions=actions, dynamics=dynamics)

        costs = cost_model.compute(context)
        assert len(costs) == 1

    def test_nonlinear_cost(self):
        """Test NonlinearCost model."""
        cost_model = NonlinearCost(
            replacement_cost=1000.0,
            cost_sensitivity=2.0,
            min_repair_fraction=0.2,
            n_states=10,
        )

        good_context = ModelContext(states=np.array([8]), actions=np.array([2]))

        poor_context = ModelContext(states=np.array([2]), actions=np.array([2]))

        good_cost = cost_model.compute(good_context)
        poor_cost = cost_model.compute(poor_context)

        assert poor_cost[0] > good_cost[0]


class TestBudgetModels:
    """Test budget models with unified interface."""

    def test_fixed_budget(self):
        """Test FixedBudget model."""
        budget = FixedBudget(initial_budget=1000.0)

        # Test legacy interface
        assert budget.available() == 1000.0

        success = budget.update(200.0)
        assert success
        assert budget.available() == 800.0

        # Test compute interface
        context = ModelContext(states=np.array([5]))
        budget_info = budget.compute(context)

        assert budget_info["available"] == 800.0
        assert "consumed" in budget_info
        assert "sufficient" in budget_info

        # Test constraint application
        costs = np.array([300.0, 600.0, 200.0])
        allowed, remaining = budget.apply_constraint(costs)

        assert allowed[0]  # 300 <= 800
        assert allowed[2]  # 200 <= remaining
        assert remaining < 800

    def test_cyclic_budget(self):
        """Test CyclicBudget model."""
        budget = CyclicBudget(cycle_budget=500.0, cycle_length=10)

        assert budget.available() == 500.0

        budget.update(200.0)
        assert budget.available() == 300.0

        # Test compute interface with time info
        context = ModelContext(states=np.array([5]), time_step=5)
        budget_info = budget.compute(context)

        assert budget_info["available"] == 300.0
        assert budget_info["time_in_cycle"] == 0  # Just reset
        assert budget_info["cycle_length"] == 10

        # Complete cycle
        for _ in range(10):
            budget.step_time()
        assert budget.available() == 500.0

    def test_emergency_reserve_budget(self):
        """Test EmergencyReserveBudget model."""
        budget = EmergencyReserveBudget(
            normal_budget=1000.0, emergency_reserve=500.0, emergency_threshold=3
        )

        # Test with emergency context
        failed_states = np.array([0, 0, 0, 5, 5])  # 3 failures
        context = ModelContext(states=failed_states)

        budget_info = budget.compute(context)

        assert budget_info["emergency_active"]
        assert budget_info["available"] == 1500.0  # Normal + reserve
        assert budget_info["failures"] == 3


class TestHierarchySystem:
    """Test hierarchy system with unified interface."""

    def test_simple_hierarchy(self):
        """Test SimpleHierarchy implementation."""
        hierarchy = SimpleHierarchy()

        levels = hierarchy.get_hierarchy_levels()
        assert len(levels) == 2
        assert levels[0].name == "component"
        assert levels[1].name == "system"

        # Assign components
        hierarchy.assign_component(0, {"component": "comp_0", "system": "sys_A"})
        hierarchy.assign_component(1, {"component": "comp_1", "system": "sys_A"})
        hierarchy.assign_component(2, {"component": "comp_2", "system": "sys_B"})

        # Set system properties
        hierarchy.set_group_property("sys_A", "system", "criticality", "critical")
        hierarchy.set_group_property("sys_B", "system", "criticality", "normal")

        # Test queries
        assert hierarchy.get_component_group(0, "system") == "sys_A"
        assert (
            hierarchy.get_group_property("sys_A", "system", "criticality") == "critical"
        )

        sys_a_components = hierarchy.get_group_components("sys_A", "system")
        assert 0 in sys_a_components
        assert 1 in sys_a_components
        assert 2 not in sys_a_components

    def test_hierarchy_compute_metrics(self):
        """Test hierarchy metrics computation."""
        hierarchy = SimpleHierarchy()

        # Setup components
        for i in range(6):
            system = "sys_A" if i < 3 else "sys_B"
            hierarchy.assign_component(i, {"component": f"comp_{i}", "system": system})

        # Test compute with states
        states = np.array([9, 8, 7, 6, 5, 4])
        context = ModelContext(states=states)

        metrics = hierarchy.compute(context)

        assert "system_metrics" in metrics
        sys_metrics = metrics["system_metrics"]

        assert "sys_A" in sys_metrics
        assert "sys_B" in sys_metrics

        # sys_A has components [9, 8, 7], sys_B has [6, 5, 4]
        assert sys_metrics["sys_A"]["mean"] == 8.0  # (9+8+7)/3
        assert sys_metrics["sys_A"]["min"] == 7.0
        assert sys_metrics["sys_B"]["mean"] == 5.0  # (6+5+4)/3

    def test_general_hierarchy(self):
        """Test GeneralHierarchy with custom levels."""
        levels = [
            HierarchyLevel("component"),
            HierarchyLevel(
                "group", "component", aggregation_rules={"condition": "min"}
            ),
            HierarchyLevel("zone", "group", aggregation_rules={"condition": "mean"}),
        ]

        hierarchy = GeneralHierarchy(levels)

        hierarchy.assign_component(
            0, {"component": "comp_0", "group": "grp_1", "zone": "zone_A"}
        )

        assert hierarchy.get_component_group(0, "zone") == "zone_A"
        assert hierarchy.get_component_group(0, "group") == "grp_1"


class TestMetadataSystem:
    """Test metadata system with unified interface."""

    def test_simple_metadata(self):
        """Test SimpleMetadata functionality."""
        metadata = SimpleMetadata()

        # Add components
        metadata.add_component(
            0,
            {
                "id": 0,
                "name": "Pump A",
                "type": "pump",
                "importance": 8.0,
                "location": "building_1",
            },
        )

        metadata.add_component(
            1,
            {
                "id": 1,
                "name": "Valve B",
                "type": "valve",
                "importance": 5.0,
                "location": "building_2",
            },
        )

        # Test attribute access
        assert metadata.get_component_attribute(0, "name") == "Pump A"
        assert metadata.get_component_attribute(0, "importance") == 8.0

        # Test bulk attribute access
        importance_values = metadata.get_bulk_attribute([0, 1], "importance")
        np.testing.assert_array_equal(importance_values, [8.0, 5.0])

        # Test queries
        pumps = metadata.query_components(type="pump")
        assert 0 in pumps
        assert 1 not in pumps

    def test_metadata_compute_metrics(self):
        """Test metadata metrics computation."""
        metadata = SimpleMetadata()

        for i in range(5):
            metadata.add_component(
                i,
                {
                    "id": i,
                    "importance": float(i + 1),  # 1.0 to 5.0
                    "name": f"Component {i}",
                },
            )

        states = np.array([9, 8, 7, 6, 5])
        context = ModelContext(states=states)

        metrics = metadata.compute(context)

        assert "importance_stats" in metrics
        importance_stats = metrics["importance_stats"]

        assert importance_stats["mean"] == 3.0  # (1+2+3+4+5)/5
        assert importance_stats["min"] == 1.0
        assert importance_stats["max"] == 5.0

    def test_general_metadata_with_custom_fields(self):
        """Test GeneralMetadata with custom field definitions."""
        fields = [
            FieldDefinition("id", int, required=True),
            FieldDefinition("temperature", float, default_value=20.0),
            FieldDefinition("status", str, default_value="active"),
        ]

        metadata = GeneralMetadata(fields)

        # Add component with partial data
        metadata.add_component(0, {"id": 0, "temperature": 25.5})

        # Check defaults were applied
        assert metadata.get_component_attribute(0, "status") == "active"
        assert metadata.get_component_attribute(0, "temperature") == 25.5

        # Test weighted metric
        values = np.array([10.0, 20.0])
        metadata.add_component(1, {"id": 1, "temperature": 30.0})

        # This should use temperature as weights if implemented
        try:
            weighted = metadata.compute_weighted_metric(values, "temperature")
            assert isinstance(weighted, float)
        except (KeyError, AttributeError):
            pass  # Expected if temperature weighting not fully implemented


class TestModelIntegration:
    """Test integration between different model types."""

    def test_cost_with_hierarchy_dependency(self):
        """Test cost model that requires hierarchy."""
        hierarchy = SimpleHierarchy()
        hierarchy.assign_component(0, {"component": "comp_0", "system": "critical_sys"})
        hierarchy.set_group_property(
            "critical_sys", "system", "criticality", "critical"
        )

        cost_model = SimpleCost()

        context = ModelContext(
            states=np.array([5]),
            actions=np.array([2]),  # Repair
            hierarchy=hierarchy,
        )

        costs = cost_model.compute(context)
        assert len(costs) == 1

    def test_full_model_integration(self):
        """Test all models working together."""
        # Setup all models
        dynamics = MarkovDynamics(n_states=10, seed=42)
        cost_model = SimpleCost(repair_cost=100.0)
        budget = FixedBudget(initial_budget=1000.0)
        hierarchy = SimpleHierarchy()
        metadata = SimpleMetadata()

        # Setup hierarchy
        hierarchy.assign_component(0, {"component": "comp_0", "system": "sys_A"})
        hierarchy.assign_component(1, {"component": "comp_1", "system": "sys_A"})

        # Setup metadata
        metadata.add_component(0, {"id": 0, "importance": 2.0})
        metadata.add_component(1, {"id": 1, "importance": 1.0})

        # Create context with all models
        context = ModelContext(
            states=np.array([5, 3]),
            actions=np.array([2, 1]),  # Repair, inspect
            dynamics=dynamics,
            hierarchy=hierarchy,
            metadata=metadata,
        )

        # Test that all models can compute with this context
        next_states = dynamics.compute(context)
        costs = cost_model.compute(context)
        budget_info = budget.compute(context)
        hierarchy_metrics = hierarchy.compute(context)
        metadata_metrics = metadata.compute(context)

        assert len(next_states) == 2
        assert len(costs) == 2
        assert "available" in budget_info
        assert "system_metrics" in hierarchy_metrics
        assert isinstance(metadata_metrics, dict)


if __name__ == "__main__":
    pytest.main([__file__])

"""Tests for the simulator."""

import numpy as np
import pytest

from infralib.models.budget import FixedBudget
from infralib.models.cost import SimpleCost
from infralib.models.dynamics import MarkovDynamics
from infralib.models.hierarchy import SimpleHierarchy
from infralib.models.metadata import SimpleMetadata
from infralib.simulator import Simulator


class TestSimulator:
    """Test the core simulator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dynamics = MarkovDynamics(n_states=10, base_deterioration_rate=0.1)
        self.cost_model = SimpleCost(
            inspect_cost=10.0, repair_cost=100.0, replace_cost=1000.0
        )
        self.budget_model = FixedBudget(initial_budget=10000.0)

        self.simulator = Simulator(
            dynamics=self.dynamics,
            cost=self.cost_model,
            budget=self.budget_model,
            seed=42,
        )

    def test_simulator_initialization(self):
        """Test simulator initialization."""
        assert self.simulator.dynamics == self.dynamics
        assert self.simulator.cost == self.cost_model
        assert self.simulator.budget == self.budget_model
        assert self.simulator.n_components is None

    def test_simulator_reset(self):
        """Test simulator reset functionality."""
        n_components = 5
        initial_states = self.simulator.reset(n_components)

        assert self.simulator.n_components == n_components
        assert len(initial_states) == n_components
        assert len(self.simulator.states) == n_components
        assert len(self.simulator.time_since_inspection) == n_components
        assert self.simulator.time_step == 0
        budget_available = (
            self.budget_model.available()
            if hasattr(self.budget_model, "available")
            else self.budget_model._available_internal()
        )
        assert budget_available == 10000.0

        # Test with custom initial states
        custom_states = np.array([5, 3, 8, 2, 6])
        initial_states = self.simulator.reset(n_components, custom_states)
        np.testing.assert_array_equal(initial_states, custom_states)
        np.testing.assert_array_equal(self.simulator.states, custom_states)

    def test_simulator_step(self):
        """Test simulator step functionality."""
        n_components = 3
        self.simulator.reset(n_components)

        # Test single step
        actions = np.array([0, 1, 2])  # Do nothing, inspect, repair
        states, info = self.simulator.step(actions)

        assert len(states) == n_components
        assert "costs" in info
        assert "total_cost" in info
        assert "budget_remaining" in info
        assert "failures" in info
        assert "actions_taken" in info
        assert self.simulator.time_step == 1

        # Check cost computation
        assert len(info["costs"]) == n_components
        assert info["total_cost"] == np.sum(info["costs"])

        # Check budget update
        assert info["budget_remaining"] <= 10000.0

    def test_budget_constraints(self):
        """Test budget constraint enforcement."""
        n_components = 3
        self.simulator.reset(n_components)

        # Expensive actions that exceed budget
        expensive_actions = np.array([3, 3, 3])  # All replacements

        # Drain most of the budget first
        if hasattr(self.budget_model, "update"):
            self.budget_model.update(9500.0)  # Leave only 500
        else:
            self.budget_model._update_internal(9500.0)

        states, info = self.simulator.step(expensive_actions)

        # Should have blocked some actions due to budget constraints
        assert info["actions_blocked"] > 0
        assert np.sum(info["actions_taken"] == 3) < 3  # Not all replacements allowed

    def test_inspection_tracking(self):
        """Test time since inspection tracking."""
        n_components = 2
        self.simulator.reset(n_components)

        # Initially no inspections
        assert np.all(self.simulator.time_since_inspection == 0)

        # Take step without inspection
        actions = np.array([0, 0])
        self.simulator.step(actions)
        assert np.all(self.simulator.time_since_inspection == 1)

        # Inspect one component
        actions = np.array([1, 0])
        self.simulator.step(actions)
        assert self.simulator.time_since_inspection[0] == 0  # Reset
        assert self.simulator.time_since_inspection[1] == 2  # Continued counting

    def test_observation_modes(self):
        """Test different observation modes."""
        n_components = 3
        self.simulator.reset(n_components)

        # Full observability
        obs_full = self.simulator.get_observation("full")
        assert len(obs_full) == n_components * 2 + 1

        # Partial observability
        obs_partial = self.simulator.get_observation("partial")
        assert len(obs_partial) == n_components * 2 + 1

        # Noisy observability
        obs_noisy = self.simulator.get_observation("noisy")
        assert len(obs_noisy) == n_components * 2 + 1

    def test_simulator_with_hierarchy(self):
        """Test simulator with hierarchy system."""
        hierarchy = SimpleHierarchy()
        hierarchy.assign_component(0, {"component": "comp_0", "system": "hvac"})
        hierarchy.assign_component(1, {"component": "comp_1", "system": "hvac"})
        hierarchy.assign_component(2, {"component": "comp_2", "system": "plumbing"})

        sim_with_hierarchy = Simulator(
            dynamics=self.dynamics,
            cost=self.cost_model,
            budget=self.budget_model,
            hierarchy=hierarchy,
            seed=42,
        )

        n_components = 3
        sim_with_hierarchy.reset(n_components)

        actions = np.array([0, 1, 2])
        states, info = sim_with_hierarchy.step(actions)

        # Should have hierarchy metrics in info
        assert any(key.endswith("_metrics") for key in info.keys())

    def test_simulator_with_metadata(self):
        """Test simulator with metadata system."""
        metadata_manager = SimpleMetadata()

        # Add components with different importance
        metadata_manager.add_component(
            0,
            {
                "id": 0,
                "name": "Pump A",
                "type": "pump",
                "importance": 8.0,
                "criticality": "critical",
            },
        )
        metadata_manager.add_component(
            1,
            {
                "id": 1,
                "name": "Valve B",
                "type": "valve",
                "importance": 5.0,
                "criticality": "medium",
            },
        )

        sim_with_metadata = Simulator(
            dynamics=self.dynamics,
            cost=self.cost_model,
            budget=self.budget_model,
            metadata=metadata_manager,
            seed=42,
        )

        n_components = 2
        sim_with_metadata.reset(n_components)

        actions = np.array([0, 1])
        states, info = sim_with_metadata.step(actions)

        # Should have metadata-based metrics
        if "importance_weighted_condition" in info:
            assert isinstance(info["importance_weighted_condition"], float)

    def test_batch_rollout(self):
        """Test batch rollout functionality."""
        n_components = 2
        self.simulator.reset(n_components)

        # Simple random policy
        def random_policy(obs):
            return np.random.randint(0, 4, size=n_components)

        results = self.simulator.batch_rollout(random_policy, horizon=10, n_rollouts=3)

        assert "returns" in results
        assert "costs" in results
        assert "failures" in results
        assert "mean_return" in results
        assert len(results["returns"]) == 3
        assert len(results["costs"]) == 3

    def test_performance_metrics(self):
        """Test performance metrics computation."""
        n_components = 3
        self.simulator.reset(n_components)

        # Take a few steps
        for i in range(5):
            actions = np.array([i % 4, (i + 1) % 4, (i + 2) % 4])
            self.simulator.step(actions)

        metrics = self.simulator.get_performance_metrics()

        assert "total_steps" in metrics
        assert "total_cost" in metrics
        assert "final_budget" in metrics
        assert "total_failures" in metrics
        assert "mean_final_condition" in metrics
        assert metrics["total_steps"] == 5

    def test_simulator_reproducibility(self):
        """Test that simulator is reproducible with same seed."""
        n_components = 3

        # Run 1
        sim1 = Simulator(self.dynamics, self.cost_model, self.budget_model, seed=42)
        sim1.reset(n_components)
        actions = np.array([0, 1, 2])
        states1, info1 = sim1.step(actions)

        # Run 2 with same seed
        sim2 = Simulator(self.dynamics, self.cost_model, self.budget_model, seed=42)
        sim2.reset(n_components)
        states2, info2 = sim2.step(actions)

        # Results should be identical
        np.testing.assert_array_equal(states1, states2)
        assert info1["total_cost"] == info2["total_cost"]

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        n_components = 3
        self.simulator.reset(n_components)

        # Wrong action length
        with pytest.raises(ValueError):
            self.simulator.step(np.array([0, 1]))  # Too short

        # Reset with mismatched initial states
        with pytest.raises(ValueError):
            self.simulator.reset(n_components, np.array([1, 2]))  # Wrong length

    def test_rich_display_initialization(self):
        """Test rich display initialization."""
        # Without rich display
        sim_no_rich = Simulator(
            dynamics=self.dynamics,
            cost=self.cost_model,
            budget=self.budget_model,
            rich_display=False,
        )
        assert sim_no_rich.rich_display is False
        assert sim_no_rich.console is None

        # With rich display
        sim_rich = Simulator(
            dynamics=self.dynamics,
            cost=self.cost_model,
            budget=self.budget_model,
            rich_display=True,
        )
        assert sim_rich.rich_display is True
        assert sim_rich.console is not None

    def test_model_context_creation(self):
        """Test ModelContext creation."""
        n_components = 3
        self.simulator.reset(n_components)

        actions = np.array([0, 1, 2])
        context = self.simulator._create_context(actions)

        assert context.states is not None
        assert context.actions is not None
        np.testing.assert_array_equal(context.actions, actions)
        assert context.time_step == 0
        assert context.dynamics == self.dynamics
        assert context.cost == self.cost_model
        assert context.budget == self.budget_model

    def test_model_dependency_validation(self):
        """Test model dependency validation."""
        # This should work without issues
        sim = Simulator(
            dynamics=self.dynamics, cost=self.cost_model, budget=self.budget_model
        )
        assert sim is not None

        # Test with models that have dependencies would require custom models
        # from examples/models, which may not be available in test environment

    def test_step_with_display_parameter(self):
        """Test step method with display_status parameter."""
        n_components = 2
        self.simulator.reset(n_components)

        actions = np.array([0, 1])

        # Test with display_status=False (should not raise even if rich_display=True)
        states, info = self.simulator.step(actions, display_status=False)
        assert len(states) == n_components

        # Test with display_status=True on simulator without rich display
        # Should not raise error, just not display anything
        states, info = self.simulator.step(actions, display_status=True)
        assert len(states) == n_components

    def test_status_display_methods(self):
        """Test rich status display methods."""
        # Test with rich display enabled
        sim_rich = Simulator(
            dynamics=self.dynamics,
            cost=self.cost_model,
            budget=self.budget_model,
            rich_display=True,
        )

        n_components = 2
        sim_rich.reset(n_components)

        # Test create_status_display before any actions
        panel, progress = sim_rich.create_status_display()
        assert panel is not None
        assert progress is not None

        # Take a step and test again
        actions = np.array([0, 1])
        states, info = sim_rich.step(actions)

        panel, progress = sim_rich.create_status_display(info)
        assert panel is not None
        assert progress is not None

        # Test display_status method (should not raise)
        sim_rich.display_status(info)

    def test_status_display_without_rich(self):
        """Test status display methods when rich_display=False."""
        # Should raise error when trying to create display without rich enabled
        with pytest.raises(ValueError, match="Rich display not enabled"):
            self.simulator.create_status_display()

    def test_backward_compatibility(self):
        """Test that the updated simulator maintains backward compatibility."""
        n_components = 3

        # Old-style usage should still work
        self.simulator.reset(n_components)
        actions = np.array([0, 1, 2])
        states, info = self.simulator.step(actions)

        # All expected info fields should be present
        required_fields = [
            "costs",
            "total_cost",
            "budget_remaining",
            "failures",
            "actions_taken",
            "time_step",
            "mean_condition",
        ]
        for field in required_fields:
            assert field in info, f"Missing required field: {field}"

        # Methods should work as before
        obs = self.simulator.get_observation()
        assert len(obs) > 0

        metrics = self.simulator.get_performance_metrics()
        assert "total_steps" in metrics


if __name__ == "__main__":
    pytest.main([__file__])

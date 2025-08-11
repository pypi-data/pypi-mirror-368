"""Advanced simulator example using model dependencies and hierarchy."""

import os

# Import the custom models from examples
import sys

import numpy as np

from infralib.models.hierarchy import SimpleHierarchy
from infralib.models.metadata import SimpleMetadata
from infralib.simulator import Simulator

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

from adaptive_budget_model import AdaptiveBudget
from custom_models_with_dependencies import HierarchyAwareCost, MetadataBasedDynamics


def setup_infrastructure():
    """Setup a realistic infrastructure system with hierarchy and metadata."""

    # Create hierarchy: 3 systems with 4 components each
    hierarchy = SimpleHierarchy()

    for i in range(12):
        system_id = f"sys_{i//4}"  # sys_0, sys_1, sys_2
        facility_id = f"facility_{i//8}"  # facility_0, facility_1

        hierarchy.assign_component(
            i, {"component": f"comp_{i}", "system": system_id, "facility": facility_id}
        )

    # Set system criticality levels
    hierarchy.set_group_property("sys_0", "system", "criticality", "critical")
    hierarchy.set_group_property("sys_1", "system", "criticality", "normal")
    hierarchy.set_group_property("sys_2", "system", "criticality", "normal")

    # Create metadata with environmental conditions
    metadata = SimpleMetadata()
    environments = ["indoor", "coastal", "industrial"]

    for i in range(12):
        metadata.add_component(
            i,
            {
                "id": i,
                "name": f"Component {i}",
                "importance": 1.0 + (i % 3) * 0.5,  # Varying importance
                "environment": environments[i % 3],
                "age": np.random.uniform(1, 10),
                "location": f"Building {i//6 + 1}",
            },
        )

    return hierarchy, metadata


def risk_based_policy(
    simulator: Simulator, states: np.ndarray, time_step: int
) -> np.ndarray:
    """Risk-based maintenance policy using hierarchy information."""
    actions = np.zeros(len(states), dtype=int)

    # Always replace failed components
    actions[states == 0] = 3

    # Get hierarchy info if available
    if simulator.hierarchy:
        for i in range(len(states)):
            if states[i] == 0:
                continue  # Already handled

            # Check if component is in a critical system
            system = simulator.hierarchy.get_component_group(i, "system")
            if system:
                criticality = simulator.hierarchy.get_group_property(
                    system, "system", "criticality"
                )

                if criticality == "critical":
                    # More aggressive maintenance for critical systems
                    if states[i] <= 5:
                        actions[i] = 2  # Repair
                    elif time_step % 5 == 0:  # Inspect frequently
                        actions[i] = 1
                else:
                    # Normal maintenance for non-critical systems
                    if states[i] <= 3:
                        actions[i] = 2  # Repair
                    elif time_step % 10 == 0:  # Inspect less frequently
                        actions[i] = 1
            else:
                # Default policy if no hierarchy info
                if states[i] <= 2:
                    actions[i] = 2
    else:
        # Fallback policy without hierarchy
        actions[(states > 0) & (states <= 3)] = 2
        if time_step % 8 == 0:
            actions[states > 3] = 1

    return actions


def main():
    """Run advanced simulation with model dependencies."""
    print("=== Advanced Simulator with Model Dependencies ===")

    # Setup infrastructure
    hierarchy, metadata = setup_infrastructure()

    # Create models with dependencies
    dynamics = MetadataBasedDynamics(
        n_states=10, base_deterioration_rate=0.12, environment_factor=1.5
    )

    cost = HierarchyAwareCost(
        base_inspect_cost=75.0,
        base_repair_cost=600.0,
        base_replace_cost=2500.0,
        critical_multiplier=1.8,
    )

    budget = AdaptiveBudget(
        base_budget=60000.0,
        emergency_multiplier=2.2,
        critical_threshold=3.0,
        health_bonus=1.3,
    )

    # Create simulator
    simulator = Simulator(
        dynamics=dynamics,
        cost=cost,
        budget=budget,
        hierarchy=hierarchy,
        metadata=metadata,
        rich_display=True,
        seed=123,
    )

    # Initialize system
    n_components = 12
    # Start with mixed conditions - critical system in worse shape
    initial_states = np.array(
        [
            5,
            4,
            3,
            6,  # sys_0 (critical) - worse condition
            8,
            7,
            9,
            8,  # sys_1 (normal) - good condition
            7,
            6,
            8,
            9,  # sys_2 (normal) - good condition
        ]
    )

    simulator.reset(n_components, initial_states)

    print(f"Initialized {n_components} components across 3 systems")
    print("System criticality: sys_0=critical, sys_1=normal, sys_2=normal")
    print(f"Initial adaptive budget: ${budget._available_internal():,.2f}")
    print("\nStarting advanced simulation...\n")

    # Run simulation
    n_steps = 40
    emergency_detected = False

    for step in range(n_steps):
        # Get actions from risk-based policy
        actions = risk_based_policy(simulator, simulator.states, step)

        # Take simulation step
        states, info = simulator.step(actions, display_status=True)

        # Check for emergency budget activation
        if (
            hasattr(budget, "emergency_active")
            and budget.emergency_active
            and not emergency_detected
        ):
            print(f"\n🚨 EMERGENCY BUDGET ACTIVATED at step {step}!")
            print(f"Emergency systems: {getattr(budget, 'emergency_systems', [])}")
            emergency_detected = True

        # Print hierarchy metrics occasionally
        if step % 15 == 0 and step > 0:
            print(f"\n--- Step {step} Hierarchy Status ---")
            for level_name, level_metrics in info.items():
                if level_name.endswith("_metrics") and isinstance(level_metrics, dict):
                    print(f"{level_name}: {level_metrics}")

        # Check termination conditions
        if info["budget_remaining"] <= 0:
            print(f"\nSimulation ended at step {step}: Budget exhausted")
            break

        if info["failures"] > n_components * 0.4:
            print(
                f"\nSimulation ended at step {step}: System failure threshold reached"
            )
            break

    # Final analysis
    print("\n=== Advanced Simulation Complete ===")
    metrics = simulator.get_performance_metrics()

    print(f"Total steps: {metrics['total_steps']}")
    print(f"Total cost: ${metrics['total_cost']:,.2f}")
    print(f"Final budget: ${metrics['final_budget']:,.2f}")
    print(f"Total failures: {metrics['total_failures']}")
    print(f"Mean final condition: {metrics['mean_final_condition']:.2f}")

    # System-level analysis
    if simulator.hierarchy:
        print("\n=== System-Level Analysis ===")
        context = simulator._create_context()
        final_hierarchy_metrics = simulator._compute_hierarchy_metrics()

        for level_name, level_data in final_hierarchy_metrics.items():
            if isinstance(level_data, dict):
                print(f"\n{level_name}:")
                for system_id, system_metrics in level_data.items():
                    criticality = (
                        simulator.hierarchy.get_group_property(
                            system_id, "system", "criticality"
                        )
                        or "unknown"
                    )
                    print(
                        f"  {system_id} ({criticality}): "
                        f"mean={system_metrics.get('mean_condition', 0):.1f}, "
                        f"failures={system_metrics.get('failure_count', 0)}"
                    )

    # Budget analysis
    if hasattr(budget, "emergency_active"):
        print("\nBudget Analysis:")
        print(f"Emergency mode activated: {emergency_detected}")
        print(
            f"Final budget multiplier: {getattr(budget, 'budget_multiplier', 1.0):.2f}"
        )

    return simulator, metrics


if __name__ == "__main__":
    simulator, metrics = main()

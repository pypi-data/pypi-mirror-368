"""Basic simulator example with rich status displays."""

import numpy as np

from infralib.models.budget import FixedBudget
from infralib.models.cost import SimpleCost
from infralib.models.dynamics import MarkovDynamics
from infralib.simulator import Simulator


def basic_policy(states: np.ndarray, time_step: int) -> np.ndarray:
    """Simple maintenance policy.

    Args:
        states: Current component states
        time_step: Current time step

    Returns:
        Actions for each component
    """
    actions = np.zeros(len(states), dtype=int)

    # Replace failed components
    actions[states == 0] = 3

    # Repair components in poor condition
    actions[(states > 0) & (states <= 3)] = 2

    # Inspect every 10 steps
    if time_step % 10 == 0:
        actions[states > 3] = 1

    return actions


def main():
    """Run basic simulation example."""
    print("=== Basic Infrastructure Simulator Example ===")

    # Setup models
    dynamics = MarkovDynamics(
        n_states=10, base_deterioration_rate=0.15, repair_effectiveness=0.7
    )

    cost = SimpleCost(
        base_inspect_cost=50.0, base_repair_cost=500.0, base_replace_cost=2000.0
    )

    budget = FixedBudget(initial_budget=50000.0)

    # Create simulator with rich displays
    simulator = Simulator(
        dynamics=dynamics, cost=cost, budget=budget, rich_display=True, seed=42
    )

    # Initialize with 20 components
    n_components = 20
    initial_states = np.random.randint(
        6, 10, size=n_components
    )  # Start in good condition
    simulator.reset(n_components, initial_states)

    print(f"Initialized {n_components} components")
    print(f"Initial budget: ${budget._available_internal():,.2f}")
    print("\nStarting simulation...\n")

    # Run simulation
    n_steps = 50
    for step in range(n_steps):
        # Get actions from policy
        actions = basic_policy(simulator.states, step)

        # Take simulation step
        states, info = simulator.step(actions, display_status=True)

        # Check for early termination
        if info["budget_remaining"] <= 0:
            print(f"\nSimulation ended at step {step}: Budget exhausted")
            break

        if info["failures"] > n_components * 0.5:
            print(f"\nSimulation ended at step {step}: Too many failures")
            break

    # Final results
    print("\n=== Simulation Complete ===")
    metrics = simulator.get_performance_metrics()

    print(f"Total steps: {metrics['total_steps']}")
    print(f"Total cost: ${metrics['total_cost']:,.2f}")
    print(f"Final budget: ${metrics['final_budget']:,.2f}")
    print(f"Total failures: {metrics['total_failures']}")
    print(f"Mean final condition: {metrics['mean_final_condition']:.2f}")
    print(f"Condition deterioration: {metrics['condition_deterioration']:.2f}")

    return simulator, metrics


if __name__ == "__main__":
    simulator, metrics = main()

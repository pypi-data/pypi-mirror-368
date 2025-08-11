"""Example of batch policy evaluation and comparison using the simulator."""

from collections.abc import Callable

import numpy as np

from infralib.models.budget import FixedBudget
from infralib.models.cost import SimpleCost
from infralib.models.dynamics import MarkovDynamics
from infralib.simulator import Simulator


def reactive_policy(obs: np.ndarray) -> np.ndarray:
    """Reactive policy - only acts when components are in poor condition."""
    # Extract states from observation (first n_components elements)
    n_components = len(obs) // 2  # Assuming obs = [states, time_since_inspection]
    states = obs[:n_components] * 10  # Denormalize

    actions = np.zeros(n_components, dtype=int)
    actions[states == 0] = 3  # Replace failed
    actions[(states > 0) & (states <= 2)] = 2  # Repair very poor

    return actions


def preventive_policy(obs: np.ndarray) -> np.ndarray:
    """Preventive policy - proactive maintenance."""
    n_components = len(obs) // 2
    states = obs[:n_components] * 10
    time_since_inspection = obs[n_components:] * 100

    actions = np.zeros(n_components, dtype=int)
    actions[states == 0] = 3  # Replace failed
    actions[(states > 0) & (states <= 4)] = 2  # Repair poor/fair condition
    actions[(states > 4) & (time_since_inspection >= 8)] = (
        1  # Inspect if not checked recently
    )

    return actions


def balanced_policy(obs: np.ndarray) -> np.ndarray:
    """Balanced policy - mix of reactive and preventive."""
    n_components = len(obs) // 2
    states = obs[:n_components] * 10
    time_since_inspection = obs[n_components:] * 100

    actions = np.zeros(n_components, dtype=int)
    actions[states == 0] = 3  # Replace failed
    actions[(states > 0) & (states <= 3)] = 2  # Repair poor condition

    # Preventive inspections for components not recently checked
    inspect_mask = (states > 3) & (time_since_inspection >= 12)
    actions[inspect_mask] = 1

    return actions


def aggressive_policy(obs: np.ndarray) -> np.ndarray:
    """Aggressive policy - maintains components in excellent condition."""
    n_components = len(obs) // 2
    states = obs[:n_components] * 10

    actions = np.zeros(n_components, dtype=int)
    actions[states == 0] = 3  # Replace failed
    actions[(states > 0) & (states <= 6)] = 2  # Repair anything below good condition
    actions[states > 6] = 1  # Regular inspections for good components

    return actions


def evaluate_policy(
    policy: Callable, simulator: Simulator, n_rollouts: int = 5, horizon: int = 100
):
    """Evaluate a policy using batch rollouts."""
    print(f"Evaluating {policy.__name__}...")

    results = simulator.batch_rollout(policy, horizon, n_rollouts)

    return {
        "policy_name": policy.__name__.replace("_policy", "").title(),
        "mean_return": results["mean_return"],
        "std_return": results["std_return"],
        "mean_cost": results["mean_cost"],
        "returns": results["returns"],
        "costs": results["costs"],
    }


def main():
    """Run batch policy evaluation example."""
    print("=== Batch Policy Evaluation Example ===")

    # Setup models
    dynamics = MarkovDynamics(
        n_states=10, base_deterioration_rate=0.1, repair_effectiveness=0.6
    )

    cost = SimpleCost(
        base_inspect_cost=25.0, base_repair_cost=300.0, base_replace_cost=1500.0
    )

    budget = FixedBudget(initial_budget=100000.0)

    # Create simulator (without rich display for batch evaluation)
    simulator = Simulator(
        dynamics=dynamics, cost=cost, budget=budget, rich_display=False, seed=456
    )

    # Initialize system
    n_components = 15
    simulator.reset(n_components)

    print(f"Evaluating policies on {n_components} components")
    print(f"Budget per rollout: ${budget._available_internal():,.2f}")
    print("Evaluation horizon: 100 steps")
    print("Number of rollouts per policy: 10\n")

    # Define policies to evaluate
    policies = [reactive_policy, preventive_policy, balanced_policy, aggressive_policy]

    # Evaluate each policy
    results = []
    for policy in policies:
        result = evaluate_policy(policy, simulator, n_rollouts=10, horizon=100)
        results.append(result)

        print(f"{result['policy_name']} Policy:")
        print(
            f"  Mean Return: {result['mean_return']:,.0f} ± {result['std_return']:,.0f}"
        )
        print(f"  Mean Cost: {result['mean_cost']:,.0f}")
        print("")

    # Compare policies
    print("=== Policy Comparison ===")
    best_return = max(results, key=lambda x: x["mean_return"])
    lowest_cost = min(results, key=lambda x: x["mean_cost"])
    most_consistent = min(results, key=lambda x: x["std_return"])

    print(
        f"Best Average Return: {best_return['policy_name']} ({best_return['mean_return']:,.0f})"
    )
    print(
        f"Lowest Average Cost: {lowest_cost['policy_name']} ({lowest_cost['mean_cost']:,.0f})"
    )
    print(
        f"Most Consistent: {most_consistent['policy_name']} (std: {most_consistent['std_return']:,.0f})"
    )

    # Create visualization
    try:
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Returns comparison
        policy_names = [r["policy_name"] for r in results]
        mean_returns = [r["mean_return"] for r in results]
        std_returns = [r["std_return"] for r in results]

        ax1.bar(policy_names, mean_returns, yerr=std_returns, capsize=5, alpha=0.7)
        ax1.set_title("Policy Returns (Higher is Better)")
        ax1.set_ylabel("Average Return")
        ax1.tick_params(axis="x", rotation=45)

        # Cost comparison
        mean_costs = [r["mean_cost"] for r in results]

        ax2.bar(policy_names, mean_costs, alpha=0.7, color="orange")
        ax2.set_title("Policy Costs (Lower is Better)")
        ax2.set_ylabel("Average Cost")
        ax2.tick_params(axis="x", rotation=45)

        plt.tight_layout()
        plt.savefig(
            "/Users/pranay/Repos/InfraLib-dev/examples/simulator/policy_comparison.png",
            dpi=150,
            bbox_inches="tight",
        )
        print("\nPolicy comparison plot saved to: policy_comparison.png")

    except ImportError:
        print("Matplotlib not available - skipping visualization")

    # Detailed analysis of best policy
    print(f"\n=== Detailed Analysis of {best_return['policy_name']} Policy ===")

    # Run one detailed simulation with the best policy
    simulator.reset(n_components)
    simulator.rich_display = True
    simulator.console = simulator.console or Console()

    print(f"Running detailed simulation with {best_return['policy_name']} policy...")

    policy_func = next(
        p
        for p in policies
        if p.__name__.replace("_policy", "").title() == best_return["policy_name"]
    )

    for step in range(20):  # Shorter detailed run
        obs = simulator.get_observation()
        actions = policy_func(obs)
        states, info = simulator.step(actions, display_status=True)

        if step % 5 == 0:
            print(
                f"Step {step}: Mean condition = {info['mean_condition']:.2f}, "
                f"Failures = {info['failures']}, "
                f"Budget = ${info['budget_remaining']:,.0f}"
            )

    return results


if __name__ == "__main__":
    results = main()

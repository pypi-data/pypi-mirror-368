"""Simple example demonstrating visualization of simulation results.

This example shows how to use the visualization utilities to analyze
a single simulation run with different policies.
"""

import numpy as np

from infralib.envs.simple import SimpleInfraEnv
from infralib.visualize import (
    plot_action_distribution,
    plot_component_states_comparison,
    plot_state_budget_history,
)


def run_simulation(env, policy_func, max_steps=100, seed=42):
    """Run a simulation with a given policy function."""
    obs, info = env.reset(seed=seed)

    state_history = [env.simulator.states.copy()]
    action_history = []
    total_reward = 0

    for step in range(max_steps):
        action = policy_func(obs, step, env)
        obs, reward, terminated, truncated, info = env.step(action)

        state_history.append(env.simulator.states.copy())
        action_history.append(action.copy())
        total_reward += reward

        if terminated or truncated:
            break

    return np.array(state_history), np.array(action_history), total_reward


def random_policy(obs, step, env):
    """Random action policy."""
    return env.action_space.sample()


def no_action_policy(obs, step, env):
    """Do nothing policy."""
    return np.zeros(env.n_components, dtype=int)


def periodic_inspection_policy(obs, step, env):
    """Inspect every 10 steps, repair if needed."""
    action = np.zeros(env.n_components, dtype=int)

    if step % 10 == 0:
        # Inspect all components
        action[:] = 1
    elif step % 10 == 1:
        # After inspection, repair components in poor condition
        current_state = env.simulator.states

        for i in range(env.n_components):
            # Use failure_conditions if available, otherwise simple threshold
            if (
                hasattr(env.simulator, "failure_conditions")
                and env.simulator.failure_conditions is not None
            ):
                if (
                    hasattr(env.simulator, "type_indices")
                    and env.simulator.type_indices is not None
                ):
                    # Multi-type case
                    component_type = env.simulator.type_indices[i]
                    failure_threshold = (
                        env.simulator.failure_conditions[component_type] / 100.0 * 10
                    )  # Convert to 0-10 scale
                else:
                    # Single-type case
                    failure_threshold = (
                        env.simulator.failure_conditions[0] / 100.0 * 10
                    )  # Convert to 0-10 scale
            else:
                # Fallback: Use a simple threshold for failure (state <= 2)
                failure_threshold = 2

            if (
                current_state[i] <= failure_threshold * 1.5
            ):  # Repair if close to failure
                action[i] = 2  # Repair

    return action


def main():
    """Run example visualizations."""
    print("=== Infrastructure Simulation Visualization Example ===\n")

    # Create output directory
    from pathlib import Path

    output_dir = Path("output/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create environment
    env = SimpleInfraEnv.from_config(
        config_path="config.yaml",
        components_path="components.csv",
        reward_scheme="cost_penalty",
        max_steps=100,
        observability="partial",
        action_type="multi_discrete",
        rich_display=False,
    )

    print(f"Environment created with {env.n_components} components")

    # Run simulations with different policies
    policies = {
        "Random": random_policy,
        "No-Action": no_action_policy,
        "Periodic Inspection": periodic_inspection_policy,
    }

    results = {}

    print("\n=== Running Simulations ===")
    for name, policy in policies.items():
        state_hist, action_hist, total_reward = run_simulation(
            env, policy, max_steps=100, seed=42
        )
        results[name] = (state_hist, action_hist, total_reward)
        print(f"{name:20s}: Total Reward = {total_reward:8.2f}")

    # Visualize results
    print("\n=== Generating Visualizations ===")

    # 1. Plot state and budget history for best policy
    best_policy = max(results.keys(), key=lambda k: results[k][2])
    print(f"\nBest performing policy: {best_policy}")

    # Re-run best policy to get simulator history
    env.reset(seed=42)
    obs, _ = env.reset(seed=42)
    for step in range(100):
        action = policies[best_policy](obs, step, env)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break

    # Plot simulator history
    print("Generating state and budget history plot...")
    plot_state_budget_history(
        env.simulator,
        num_steps=100,
        save_path=str(output_dir / "simulation_history.png"),
        show=False,
    )

    # 2. Compare component states across policies
    print("\nGenerating component comparison plot...")
    state_histories = [r[0] for r in results.values()]
    action_histories = [r[1] for r in results.values()]
    labels = list(results.keys())

    plot_component_states_comparison(
        state_histories=state_histories,
        action_histories=action_histories,
        labels=labels,
        component_idx=0,  # First component
        max_steps=100,
        save_path=str(output_dir / "component_comparison.png"),
        show=False,
    )

    # 3. Plot action distribution for each policy
    print("\nGenerating action distribution plots...")
    for name, (_, action_hist, _) in results.items():
        plot_action_distribution(
            action_hist,
            save_path=str(output_dir / f"actions_{name.replace(' ', '_').lower()}.png"),
            show=False,
        )

    print("\n=== Visualization Complete ===")
    print(f"All figures saved to: {output_dir}")
    print("Generated plots:")
    print("  - simulation_history.png: State and budget evolution")
    print("  - component_comparison.png: Component state comparison")
    print("  - actions_*.png: Action distribution for each policy")


if __name__ == "__main__":
    main()

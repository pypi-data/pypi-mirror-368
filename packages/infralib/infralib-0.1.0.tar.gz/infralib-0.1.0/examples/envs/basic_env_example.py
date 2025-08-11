"""Basic environment example using SimpleInfraEnv.

This example demonstrates how to:
1. Create a SimpleInfraEnv with configuration files
2. Run the environment manually with random actions
3. Show basic usage patterns
"""

from infralib.envs.simple import SimpleInfraEnv


def main():
    """Run basic environment demonstration."""
    print("=== Basic SimpleInfraEnv Example ===")

    # Create environment from config files
    env = SimpleInfraEnv.from_config(
        config_path="config.yaml",
        components_path="components.csv",
        reward_scheme="cost_penalty",
        max_steps=50,
        observability="partial",  # POMDP-style
        action_type="multi_discrete",
        rich_display=True,  # Enable rich terminal displays
    )

    print(f"Environment created with {env.n_components} components")
    print(f"Action space: {env.action_space}")
    print(f"Observation space shape: {env.observation_space.shape}")
    print(f"Using reward scheme: {env.reward_scheme}")
    print()

    # Run a few episodes
    num_episodes = 3

    for episode in range(num_episodes):
        print(f"\n--- Episode {episode + 1} ---")
        obs, info = env.reset(seed=42 + episode)

        print(f"Initial observation shape: {obs.shape}")
        print(f"Initial info: {info}")

        episode_reward = 0
        step_count = 0

        while True:
            # Take random action
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)

            episode_reward += reward
            step_count += 1

            # Print step information
            if step_count <= 5 or step_count % 10 == 0:
                print(
                    f"Step {step_count}: reward={reward:.2f}, "
                    f"failures={info.get('failures', 0)}, "
                    f"budget_remaining={info.get('budget_remaining', 0):.0f}"
                )

            # Check termination
            if terminated or truncated:
                termination_reason = "terminated" if terminated else "truncated"
                print(f"Episode ended ({termination_reason}) after {step_count} steps")
                break

        print(f"Episode {episode + 1} total reward: {episode_reward:.2f}")
        print(f"Final failures: {info.get('failures', 0)}")
        print(f"Final budget: {info.get('budget_remaining', 0):.0f}")

    # Demonstrate different reward schemes
    print("\n=== Testing Different Reward Schemes ===")

    reward_schemes = ["cost_penalty", "survival", "condition"]

    for scheme in reward_schemes:
        print(f"\n--- {scheme} reward scheme ---")
        test_env = SimpleInfraEnv.from_config(
            config_path="config.yaml",
            components_path="components.csv",
            reward_scheme=scheme,
            max_steps=10,
            rich_display=False,  # Disable rich display for cleaner output
        )

        obs, info = test_env.reset(seed=123)

        total_reward = 0
        for _step in range(5):
            action = test_env.action_space.sample()
            obs, reward, terminated, truncated, info = test_env.step(action)
            total_reward += reward

            if terminated or truncated:
                break

        print(f"  Total reward after 5 steps: {total_reward:.2f}")
        print(f"  Final failures: {info.get('failures', 0)}")
        test_env.close()

    env.close()
    print("\n=== Basic Environment Example Complete ===")


if __name__ == "__main__":
    main()

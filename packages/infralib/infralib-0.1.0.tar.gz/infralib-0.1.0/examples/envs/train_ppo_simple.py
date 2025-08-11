"""Train a PPO agent on SimpleInfraEnv (POMDP).

This example demonstrates:
1. Setting up a POMDP environment with partial observability
2. Training a PPO agent with stable-baselines3
3. Evaluating the trained agent
4. Saving and loading models
"""

from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    EvalCallback,
    StopTrainingOnRewardThreshold,
)
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor

from infralib.envs.simple import SimpleInfraEnv


def create_env():
    """Create a single environment instance."""
    env = SimpleInfraEnv.from_config(
        config_path="config.yaml",
        components_path="components.csv",
        reward_scheme="cost_penalty",
        max_steps=200,
        observability="partial",  # POMDP - agent must use inspections
        action_type="multi_discrete",
        rich_display=False,
    )
    return env


def main():
    """Train PPO agent on SimpleInfraEnv."""
    print("=== Training PPO on SimpleInfraEnv (POMDP) ===")

    # Create output directory
    output_dir = Path("output/ppo_simple")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Environment parameters
    num_envs = 4  # Number of parallel environments
    total_timesteps = 100_000  # Reduced for faster testing
    seed = 42

    # Create vectorized training environment
    print(f"Creating {num_envs} parallel environments...")
    train_env = make_vec_env(create_env, n_envs=num_envs, seed=seed)

    # Create evaluation environment
    eval_env = SimpleInfraEnv.from_config(
        config_path="config.yaml",
        components_path="components.csv",
        reward_scheme="cost_penalty",
        max_steps=200,
        observability="partial",
        action_type="multi_discrete",
        rich_display=False,
    )
    eval_env = Monitor(eval_env)

    # PPO hyperparameters optimized for infrastructure maintenance
    model = PPO(
        "MlpPolicy",
        train_env,
        learning_rate=3e-4,
        n_steps=2048 // num_envs,  # Adjust for parallel envs
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,  # Encourage exploration
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=str(output_dir / "tensorboard"),
        seed=seed,
        device="cpu",
    )

    print(f"Model created with policy: {model.policy}")
    print(f"Total parameters: {sum(p.numel() for p in model.policy.parameters()):,}")

    # Optional: Stop training when reward threshold is reached
    reward_threshold_callback = StopTrainingOnRewardThreshold(
        reward_threshold=-500,  # Stop when mean reward > -500
        verbose=1,
    )

    # Setup evaluation callback with threshold callback nested
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(output_dir),
        log_path=str(output_dir),
        eval_freq=10_000 // num_envs,  # Evaluate every 10k training steps
        deterministic=True,
        render=False,
        n_eval_episodes=20,
        callback_after_eval=reward_threshold_callback,
    )

    # Train the model
    print(f"\nStarting training for {total_timesteps:,} timesteps...")
    print(f"Training on {num_envs} parallel environments")
    print(f"Environment: {eval_env.unwrapped.n_components} components, WeibullDynamics")

    model.learn(
        total_timesteps=total_timesteps, callback=eval_callback, progress_bar=True
    )

    # Save final model
    final_model_path = output_dir / "ppo_final_model"
    model.save(str(final_model_path))
    print(f"\nFinal model saved to: {final_model_path}")

    # Evaluate the trained model
    print("\n=== Evaluating Trained Model ===")

    # Load the best model for evaluation
    best_model_path = output_dir / "best_model"
    if best_model_path.exists():
        print("Loading best model for evaluation...")
        model = PPO.load(str(best_model_path))

    # Evaluate policy
    mean_reward, std_reward = evaluate_policy(
        model, eval_env, n_eval_episodes=50, deterministic=True
    )

    print(f"Mean evaluation reward: {mean_reward:.2f} (+/- {std_reward:.2f})")

    # Test a single episode with rich display
    print("\n=== Testing Single Episode with Rich Display ===")
    test_env = SimpleInfraEnv.from_config(
        config_path="config.yaml",
        components_path="components.csv",
        reward_scheme="cost_penalty",
        max_steps=50,  # Shorter episode for demo
        observability="partial",
        action_type="multi_discrete",
        rich_display=True,  # Enable rich display for final demo
    )

    obs, info = test_env.reset(seed=123)
    total_reward = 0

    print("Running trained agent with rich display...")
    for step in range(50):
        # Use trained policy
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = test_env.step(action)
        total_reward += reward

        if terminated or truncated:
            print(f"Episode ended after {step + 1} steps")
            break

    print(f"Trained agent total reward: {total_reward:.2f}")
    print(f"Final failures: {info.get('failures', 0)}")
    print(f"Final budget: {info.get('budget_remaining', 0):.0f}")

    # Cleanup
    train_env.close()
    eval_env.close()
    test_env.close()

    print("\n=== Training Complete ===")
    print(f"Models saved in: {output_dir}")
    print(f"Tensorboard logs: {output_dir}/tensorboard")
    print("Run: tensorboard --logdir output/ppo_simple/tensorboard")


if __name__ == "__main__":
    main()

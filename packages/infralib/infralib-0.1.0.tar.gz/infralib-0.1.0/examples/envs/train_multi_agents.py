"""Train multiple RL agents on both SimpleInfraEnv (POMDP) and SimpleInfraMDPEnv (MDP).

This comprehensive example demonstrates:
1. Training PPO, A2C, and DQN on both POMDP and MDP environments
2. Comparing performance across different algorithms and environment types
3. Saving models and generating performance plots
4. Using different reward schemes and configurations
"""

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from stable_baselines3 import A2C, DQN, PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor

from infralib.envs.simple import SimpleInfraEnv, SimpleInfraMDPEnv

# Algorithm configurations
ALGORITHM_CONFIGS = {
    "PPO": {
        "class": PPO,
        "policy": "MlpPolicy",
        "hyperparams": {
            "learning_rate": 3e-4,
            "n_steps": 512,  # Reduced for faster training
            "batch_size": 64,
            "n_epochs": 10,
            "gamma": 0.99,
            "gae_lambda": 0.95,
            "clip_range": 0.2,
            "ent_coef": 0.01,
        },
        "compatible_envs": ["pomdp", "mdp"],
    },
    "A2C": {
        "class": A2C,
        "policy": "MlpPolicy",
        "hyperparams": {
            "learning_rate": 7e-4,
            "n_steps": 5,
            "gamma": 0.99,
            "gae_lambda": 1.0,
            "ent_coef": 0.01,
        },
        "compatible_envs": ["pomdp", "mdp"],
    },
    "DQN": {
        "class": DQN,
        "policy": "MlpPolicy",
        "hyperparams": {
            "learning_rate": 1e-4,
            "buffer_size": 50000,
            "learning_starts": 1000,
            "batch_size": 64,
            "tau": 1.0,
            "gamma": 0.99,
            "exploration_fraction": 0.3,
            "exploration_final_eps": 0.05,
        },
        "compatible_envs": ["mdp"],  # DQN works better with discrete action spaces
    },
}


def create_pomdp_env(rank: int = 0, seed: int = 0, reward_scheme: str = "cost_penalty"):
    """Create POMDP environment (SimpleInfraEnv)."""

    def _init():
        env = SimpleInfraEnv.from_config(
            config_path="config.yaml",
            components_path="components.csv",
            reward_scheme=reward_scheme,
            max_steps=150,
            observability="partial",
            action_type="discrete",  # Use discrete for DQN compatibility
            rich_display=False,
        )
        return env

    return _init


def create_mdp_env(rank: int = 0, seed: int = 0, reward_scheme: str = "margin"):
    """Create MDP environment (SimpleInfraMDPEnv)."""

    def _init():
        env = SimpleInfraMDPEnv.from_config(
            config_path="config.yaml",
            components_path="components.csv",
            reward_scheme=reward_scheme,
            max_steps=150,
            action_type="discrete",
            rich_display=False,
        )
        return env

    return _init


def train_agent(
    algorithm: str,
    env_type: str,
    output_dir: Path,
    total_timesteps: int = 50000,
    seed: int = 42,
) -> dict:
    """Train a single agent and return results."""

    print(f"\n=== Training {algorithm} on {env_type.upper()} ===")

    # Create run directory
    run_dir = output_dir / f"{algorithm}_{env_type}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Get algorithm configuration
    config = ALGORITHM_CONFIGS[algorithm]

    # Check compatibility
    if env_type not in config["compatible_envs"]:
        print(f"Skipping {algorithm} on {env_type} (not compatible)")
        return {"skipped": True}

    # Create environments
    num_envs = 2 if algorithm in ["PPO", "A2C"] else 1  # DQN doesn't use parallel envs

    if env_type == "pomdp":
        train_env = make_vec_env(create_pomdp_env, n_envs=num_envs, seed=seed)
        eval_env = SimpleInfraEnv.from_config(
            config_path="config.yaml",
            components_path="components.csv",
            reward_scheme="cost_penalty",
            max_steps=150,
            observability="partial",
            action_type="discrete",
            rich_display=False,
        )
    else:  # mdp
        train_env = make_vec_env(create_mdp_env, n_envs=num_envs, seed=seed)
        eval_env = SimpleInfraMDPEnv.from_config(
            config_path="config.yaml",
            components_path="components.csv",
            reward_scheme="margin",
            max_steps=150,
            action_type="discrete",
            rich_display=False,
        )

    eval_env = Monitor(eval_env)

    # Adjust hyperparameters for parallel environments
    hyperparams = config["hyperparams"].copy()
    if "n_steps" in hyperparams and num_envs > 1:
        hyperparams["n_steps"] = hyperparams["n_steps"] // num_envs

    # Create model
    model_class = config["class"]
    model = model_class(
        config["policy"],
        train_env,
        verbose=0,
        tensorboard_log=str(run_dir / "tensorboard"),
        seed=seed,
        device="cpu",
        **hyperparams,
    )

    # Setup evaluation callback
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(run_dir),
        log_path=str(run_dir),
        eval_freq=5000 // num_envs,
        deterministic=True,
        render=False,
        n_eval_episodes=10,
        verbose=0,
    )

    # Train the model
    start_time = time.time()
    print(f"Training {algorithm} on {env_type} for {total_timesteps:,} steps...")

    model.learn(
        total_timesteps=total_timesteps, callback=eval_callback, progress_bar=False
    )

    training_time = time.time() - start_time

    # Save final model
    model.save(str(run_dir / f"{algorithm}_{env_type}_final"))

    # Evaluate final model
    mean_reward, std_reward = evaluate_policy(
        model, eval_env, n_eval_episodes=20, deterministic=True
    )

    # Cleanup
    train_env.close()
    eval_env.close()

    # Return results
    results = {
        "algorithm": algorithm,
        "env_type": env_type,
        "mean_reward": mean_reward,
        "std_reward": std_reward,
        "training_time": training_time,
        "total_timesteps": total_timesteps,
        "num_envs": num_envs,
        "hyperparams": hyperparams,
        "skipped": False,
    }

    # Save results
    with open(run_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"  Mean reward: {mean_reward:.2f} (+/- {std_reward:.2f})")
    print(f"  Training time: {training_time:.1f}s")

    return results


def create_comparison_plots(results: list[dict], output_dir: Path):
    """Create comparison plots of training results."""

    # Filter out skipped results
    valid_results = [r for r in results if not r.get("skipped", False)]

    if not valid_results:
        print("No valid results to plot")
        return

    # Create DataFrame
    df = pd.DataFrame(valid_results)

    # Plot 1: Mean reward comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Bar plot of mean rewards
    for env_type in df["env_type"].unique():
        env_data = df[df["env_type"] == env_type]
        x_pos = np.arange(len(env_data))

        _bars = ax1.bar(
            x_pos,
            env_data["mean_reward"],
            yerr=env_data["std_reward"],
            label=env_type.upper(),
            alpha=0.7,
            capsize=5,
        )

        # Add algorithm labels
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(env_data["algorithm"])

    ax1.set_ylabel("Mean Evaluation Reward")
    ax1.set_title("Algorithm Performance Comparison")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Training time comparison
    for env_type in df["env_type"].unique():
        env_data = df[df["env_type"] == env_type]
        ax2.scatter(
            env_data["training_time"],
            env_data["mean_reward"],
            label=env_type.upper(),
            s=100,
            alpha=0.7,
        )

        # Add algorithm labels
        for _idx, row in env_data.iterrows():
            ax2.annotate(
                row["algorithm"],
                (row["training_time"], row["mean_reward"]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=9,
            )

    ax2.set_xlabel("Training Time (seconds)")
    ax2.set_ylabel("Mean Evaluation Reward")
    ax2.set_title("Performance vs Training Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "performance_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Create results summary table
    summary = df[
        ["algorithm", "env_type", "mean_reward", "std_reward", "training_time"]
    ].copy()
    summary["mean_reward"] = summary["mean_reward"].round(2)
    summary["std_reward"] = summary["std_reward"].round(2)
    summary["training_time"] = summary["training_time"].round(1)

    # Save summary
    summary.to_csv(output_dir / "results_summary.csv", index=False)

    print("\nResults Summary:")
    print(summary.to_string(index=False))


def demonstrate_best_agent(results: list[dict], output_dir: Path):
    """Demonstrate the best performing agent."""

    valid_results = [r for r in results if not r.get("skipped", False)]

    if not valid_results:
        print("No results available for demonstration")
        return

    # Find best performing agent
    best_result = max(valid_results, key=lambda x: x["mean_reward"])

    print("\n=== Demonstrating Best Agent ===")
    print(f"Best: {best_result['algorithm']} on {best_result['env_type'].upper()}")
    print(f"Mean reward: {best_result['mean_reward']:.2f}")

    # Load the best model
    algorithm = best_result["algorithm"]
    env_type = best_result["env_type"]

    model_path = output_dir / f"{algorithm}_{env_type}" / "best_model"

    if not model_path.exists():
        model_path = (
            output_dir / f"{algorithm}_{env_type}" / f"{algorithm}_{env_type}_final"
        )

    if not model_path.exists():
        print("Best model not found for demonstration")
        return

    # Load model
    model_class = ALGORITHM_CONFIGS[algorithm]["class"]
    model = model_class.load(str(model_path))

    # Create environment for demonstration
    if env_type == "pomdp":
        demo_env = SimpleInfraEnv.from_config(
            config_path="config.yaml",
            components_path="components.csv",
            reward_scheme="cost_penalty",
            max_steps=100,
            observability="partial",
            action_type="discrete",
            rich_display=True,  # Enable rich display
        )
    else:
        demo_env = SimpleInfraMDPEnv.from_config(
            config_path="config.yaml",
            components_path="components.csv",
            reward_scheme="margin",
            max_steps=100,
            action_type="discrete",
            rich_display=True,
        )

    # Run demonstration
    obs, info = demo_env.reset(seed=123)
    total_reward = 0

    print(
        f"Running {algorithm} on {env_type.upper()} with {demo_env.n_components} components..."
    )

    for step in range(100):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = demo_env.step(action)
        total_reward += reward

        if terminated or truncated:
            print(f"Episode ended after {step + 1} steps")
            break

    print(f"Demonstration reward: {total_reward:.2f}")
    print(f"Final failures: {info.get('failures', 0)}")
    print(f"Final budget: {info.get('budget_remaining', 0):.0f}")

    demo_env.close()


def main():
    """Run comprehensive multi-agent training experiment."""

    print("=== Multi-Agent Infrastructure Maintenance Training ===")
    print("Training PPO, A2C, and DQN on both POMDP and MDP environments")
    print("Using WeibullDynamics with component-specific parameters")

    # Create output directory
    output_dir = Path("output/multi_agent_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Training parameters
    total_timesteps = 50000  # Reduced for faster execution
    seed = 42

    # Train all algorithms on all compatible environments
    results = []

    for algorithm in ALGORITHM_CONFIGS.keys():
        for env_type in ["pomdp", "mdp"]:
            try:
                result = train_agent(
                    algorithm=algorithm,
                    env_type=env_type,
                    output_dir=output_dir,
                    total_timesteps=total_timesteps,
                    seed=seed,
                )
                results.append(result)
            except Exception as e:
                print(f"Error training {algorithm} on {env_type}: {e}")
                results.append(
                    {
                        "algorithm": algorithm,
                        "env_type": env_type,
                        "skipped": True,
                        "error": str(e),
                    }
                )

    # Create comparison plots and summary
    create_comparison_plots(results, output_dir)

    # Demonstrate best agent
    demonstrate_best_agent(results, output_dir)

    print("\n=== Training Complete ===")
    print(f"Results saved in: {output_dir}")
    print(f"Performance comparison plot: {output_dir}/performance_comparison.png")
    print(f"Results summary: {output_dir}/results_summary.csv")


if __name__ == "__main__":
    main()

"""Analyze and visualize reinforcement learning training results.

This script provides comprehensive analysis of RL training results including:
1. Training reward curves comparison
2. Policy evaluation and visualization
3. Component-level maintenance strategy analysis
"""

import glob
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.interpolate import interp1d
from stable_baselines3 import A2C, DQN, PPO

from infralib.envs.simple import SimpleInfraEnv
from infralib.visualize import (
    plot_action_distribution,
    plot_component_states_comparison,
    plot_state_budget_history,
    set_plot_style,
)


def plot_training_rewards(
    data_path: str,
    methods: list[str] | None = None,
    seeds: list[int] | None = None,
    save_path: str | None = None,
    max_steps: float = 2e6,
    show: bool = False,
) -> plt.Figure:
    """
    Plot training rewards comparison across different RL methods.

    Parameters
    ----------
    data_path : str
        Path to the output directory containing training data
    methods : list of str, optional
        List of methods to compare (default: ["PPO", "A2C", "DQN"])
    seeds : list of int, optional
        List of random seeds used (default: [0, 42, 100])
    save_path : str, optional
        Path to save the figure
    max_steps : float
        Maximum number of training steps to plot
    show : bool
        Whether to show the plot

    Returns
    -------
    fig : matplotlib.figure.Figure
        The generated figure
    """
    if methods is None:
        methods = ["PPO", "A2C", "DQN"]
    if seeds is None:
        seeds = [0, 42, 100]

    # Set publication-quality style
    plt.style.use("seaborn-v0_8-paper")
    sns.set_style(
        {
            "axes.facecolor": "#f0f0f8",
            "grid.color": ".8",
            "grid.linestyle": ":",
            "axes.spines.left": True,
            "axes.spines.bottom": True,
            "axes.spines.right": False,
            "axes.spines.top": False,
        }
    )

    colors = ["#1f77b4", "#2ca02c", "#ff7f0e"]  # Blue, green, orange
    sns.set_palette(colors)

    all_data = []

    # Collect data from all runs
    for method_name in methods:
        for seed in seeds:
            run_dirs = glob.glob(
                os.path.join(data_path, method_name, f"seed_{seed}", "run_*")
            )
            for run_dir in run_dirs:
                monitor_file = os.path.join(run_dir, "train_monitor.csv")
                if os.path.exists(monitor_file):
                    monitor_data = pd.read_csv(monitor_file, skiprows=1)
                    steps = monitor_data["l"].cumsum()
                    mask = steps <= max_steps
                    steps = steps[mask]
                    rewards = monitor_data["r"][mask]

                    if len(steps) == 0:
                        continue

                    # Interpolate for common x-axis
                    common_steps = np.linspace(0, max_steps, num=500)
                    interp_func = interp1d(
                        steps,
                        rewards,
                        kind="previous",
                        bounds_error=False,
                        fill_value=(rewards.iloc[0], np.nan),
                    )
                    interp_rewards = interp_func(common_steps)

                    # Apply smoothing
                    window = 50
                    interp_rewards = (
                        pd.Series(interp_rewards)
                        .rolling(window=window, min_periods=1, center=True)
                        .mean()
                        .values
                    )

                    df = pd.DataFrame(
                        {
                            "Steps": common_steps,
                            "Reward": interp_rewards,
                            "Method": method_name,
                            "Seed": seed,
                            "Run": f"run_{run_dir}",
                        }
                    )
                    all_data.append(df)

    if not all_data:
        print(f"No training data found in {data_path}")
        return None

    plot_data = pd.concat(all_data, ignore_index=True)

    # Create figure
    fig = plt.figure(figsize=(10, 6))

    sns.lineplot(
        data=plot_data,
        x="Steps",
        y="Reward",
        hue="Method",
        errorbar=("ci", 95),
        estimator="mean",
        lw=2,
    )

    plt.title("Training Rewards Comparison", fontsize=14)
    plt.xlabel("Training Steps", fontsize=12)
    plt.ylabel("Average Reward", fontsize=12)

    # Format x-axis to show millions
    current_values = plt.gca().get_xticks()
    plt.gca().set_xticklabels([f"{x / 1e6:.1f}M" for x in current_values])

    # Customize legend
    plt.legend(
        title="Method",
        loc="lower right",
        frameon=True,
        framealpha=0.9,
        facecolor="white",
        edgecolor="none",
    )

    plt.grid(True, which="major", linestyle=":", alpha=0.5)
    plt.tight_layout()

    if save_path:
        # Save both PNG and PDF versions
        base_path = Path(save_path)
        png_path = base_path.with_suffix(".png")
        pdf_path = base_path.with_suffix(".pdf")

        plt.savefig(str(png_path), dpi=300, bbox_inches="tight")
        plt.savefig(str(pdf_path), dpi=300, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def load_trained_model(run_path: str) -> tuple[object, str]:
    """
    Load a trained model from a run directory.

    Parameters
    ----------
    run_path : str
        Path to the run directory

    Returns
    -------
    model : object
        The loaded model
    method_name : str
        Name of the RL method
    """
    # Load metadata to get the method name
    metadata_file = os.path.join(run_path, "metadata.txt")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Metadata file not found in {run_path}")

    with open(metadata_file) as f:
        lines = f.readlines()
        method_line = [line for line in lines if "Method" in line]
        if not method_line:
            raise ValueError("Method name not found in metadata")
        method_name = method_line[0].strip().split(": ")[1]

    # Map method names to classes
    method_classes = {"PPO": PPO, "A2C": A2C, "DQN": DQN}
    model_class = method_classes.get(method_name)

    if model_class is None:
        raise ValueError(f"Unknown method: {method_name}")

    # Load the model
    model_path = os.path.join(run_path, f"{method_name}_model")
    if not os.path.exists(model_path + ".zip"):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = model_class.load(model_path)

    return model, method_name


def evaluate_trained_policy(
    model: object, env: SimpleInfraEnv, max_steps: int = 200, seed: int = 100
) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Evaluate a trained policy on the environment.

    Parameters
    ----------
    model : object
        Trained RL model
    env : SimpleInfraEnv
        Environment to evaluate on
    max_steps : int
        Maximum number of steps
    seed : int
        Random seed

    Returns
    -------
    state_history : np.ndarray
        State history array
    action_history : np.ndarray
        Action history array
    total_reward : float
        Total accumulated reward
    """
    obs, info = env.reset(seed=seed)

    state_history = [env.simulator.states.copy()]
    action_history = []
    total_reward = 0

    for step in range(max_steps):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)

        state_history.append(env.simulator.states.copy())
        action_history.append(action.copy())
        total_reward += reward

        if terminated or truncated:
            print(f"Episode ended after {step + 1} steps")
            break

    return np.array(state_history), np.array(action_history), total_reward


def simulate_baseline_policies(
    env: SimpleInfraEnv, max_steps: int = 200, seed: int = 100
) -> dict[str, tuple[np.ndarray, np.ndarray, float]]:
    """
    Simulate baseline policies for comparison.

    Parameters
    ----------
    env : SimpleInfraEnv
        Environment to simulate on
    max_steps : int
        Maximum number of steps
    seed : int
        Random seed

    Returns
    -------
    results : dict
        Dictionary with results for each baseline policy
    """
    results = {}

    # No-action baseline
    env.reset(seed=seed)
    state_history = [env.simulator.states.copy()]
    action_history = []
    total_reward = 0

    for _step in range(max_steps):
        action = np.zeros(env.n_components, dtype=int)  # All zeros = no action
        obs, reward, terminated, truncated, info = env.step(action)

        state_history.append(env.simulator.states.copy())
        action_history.append(action.copy())
        total_reward += reward

        if terminated or truncated:
            break

    results["No-Action"] = (
        np.array(state_history),
        np.array(action_history),
        total_reward,
    )

    # Rule-based policy (inspect every 10 steps, repair if close to failure)
    env.reset(seed=seed)
    state_history = [env.simulator.states.copy()]
    action_history = []
    total_reward = 0

    for step in range(max_steps):
        action = np.zeros(env.n_components, dtype=int)

        if step % 10 == 0:
            # Inspect all components
            action[:] = 1
        elif step % 10 == 1:
            # After inspection, repair if needed
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
                            env.simulator.failure_conditions[component_type]
                            / 100.0
                            * 10
                        )  # Convert to 0-10 scale
                    else:
                        # Single-type case
                        failure_threshold = (
                            env.simulator.failure_conditions[0] / 100.0 * 10
                        )  # Convert to 0-10 scale
                else:
                    # Fallback: Use a simple threshold for failure (state <= 2)
                    failure_threshold = 2

                if current_state[i] <= failure_threshold * 1.2:  # 20% margin
                    action[i] = 2  # Repair

        obs, reward, terminated, truncated, info = env.step(action)

        state_history.append(env.simulator.states.copy())
        action_history.append(action.copy())
        total_reward += reward

        if terminated or truncated:
            break

    results["Rule-Based"] = (
        np.array(state_history),
        np.array(action_history),
        total_reward,
    )

    return results


def main():
    """Main analysis pipeline."""
    # Configuration
    output_dir = Path("output")
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    config_path = "config.yaml"
    components_path = "components.csv"

    # Check if output directory exists
    if not output_dir.exists():
        print(f"Output directory {output_dir} not found. Please train models first.")
        return

    # Set plot style
    set_plot_style()

    # 1. Plot training rewards comparison
    print("=== Plotting Training Rewards ===")
    plot_training_rewards(
        data_path=str(output_dir),
        save_path=str(figures_dir / "training_rewards_comparison.png"),
        show=False,
    )
    print(
        f"Saved training rewards plot to {figures_dir / 'training_rewards_comparison.png'}"
    )

    # 2. Find best model (using most recent run of each method)
    print("\n=== Loading Best Models ===")
    best_models = {}

    for method in ["PPO", "A2C", "DQN"]:
        method_dir = output_dir / method
        if method_dir.exists():
            # Find most recent run
            run_dirs = list(method_dir.glob("seed_*/run_*"))
            if run_dirs:
                latest_run = max(run_dirs, key=os.path.getmtime)
                try:
                    model, _ = load_trained_model(str(latest_run))
                    best_models[method] = model
                    print(f"Loaded {method} model from {latest_run}")
                except Exception as e:
                    print(f"Failed to load {method} model: {e}")

    if not best_models:
        print("No trained models found. Please train models first.")
        return

    # 3. Evaluate policies
    print("\n=== Evaluating Policies ===")

    # Create environment
    eval_env = SimpleInfraEnv.from_config(
        config_path=config_path,
        components_path=components_path,
        reward_scheme="cost_penalty",
        max_steps=200,
        observability="partial",
        action_type="multi_discrete",
        rich_display=False,
    )

    # Evaluate each trained model
    policy_results = {}
    for method_name, model in best_models.items():
        print(f"Evaluating {method_name}...")
        state_hist, action_hist, total_reward = evaluate_trained_policy(
            model, eval_env, max_steps=200, seed=100
        )
        policy_results[method_name] = (state_hist, action_hist, total_reward)
        print(f"  Total reward: {total_reward:.2f}")

    # Evaluate baseline policies
    print("Evaluating baseline policies...")
    baseline_results = simulate_baseline_policies(eval_env, max_steps=200, seed=100)
    for name, (_, _, total_reward) in baseline_results.items():
        print(f"  {name}: {total_reward:.2f}")

    # 4. Visualize results
    print("\n=== Generating Visualizations ===")

    # Plot state and budget history for best performing policy
    if policy_results:
        best_method = max(policy_results.keys(), key=lambda k: policy_results[k][2])
        print(f"Best performing method: {best_method}")

        # Run a fresh simulation for visualization
        eval_env.reset(seed=100)
        obs, _ = eval_env.reset(seed=100)
        for _step in range(200):
            action, _ = best_models[best_method].predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = eval_env.step(action)
            if terminated or truncated:
                break

        # Plot simulator history
        plot_state_budget_history(
            eval_env.simulator,
            num_steps=200,
            save_path=str(figures_dir / "best_policy_history.png"),
            show=False,
        )
        print(f"Saved policy history plot to {figures_dir / 'best_policy_history.png'}")

    # Compare policies on a specific component
    all_results = {**policy_results, **baseline_results}
    state_histories = [r[0] for r in all_results.values()]
    action_histories = [r[1] for r in all_results.values()]
    labels = list(all_results.keys())

    # Plot comparison for first component
    plot_component_states_comparison(
        state_histories=state_histories,
        action_histories=action_histories,
        labels=labels,
        component_idx=0,
        max_steps=200,
        save_path=str(figures_dir / "component_0_comparison.png"),
        show=False,
    )
    print(f"Saved component comparison to {figures_dir / 'component_0_comparison.png'}")

    # Plot action distribution for best policy
    if policy_results:
        _, best_actions, _ = policy_results[best_method]
        plot_action_distribution(
            best_actions,
            save_path=str(figures_dir / "best_policy_actions.png"),
            show=False,
        )
        print(f"Saved action distribution to {figures_dir / 'best_policy_actions.png'}")

    print("\n=== Analysis Complete ===")
    print(f"All visualizations saved to {figures_dir}")


if __name__ == "__main__":
    main()

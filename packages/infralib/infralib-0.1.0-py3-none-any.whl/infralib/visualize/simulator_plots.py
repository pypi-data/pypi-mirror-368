"""Matplotlib/Seaborn visualization utilities for infrastructure simulators."""

from typing import Any

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MaxNLocator


def set_plot_style(
    style: str = "whitegrid", context: str = "paper", font_scale: float = 1.5
):
    """Set consistent plot style for publication-quality figures.

    Parameters
    ----------
    style : str
        Seaborn style preset
    context : str
        Seaborn context for scaling
    font_scale : float
        Font scaling factor
    """
    sns.set_style(style)
    sns.set_context(context, font_scale=font_scale)
    plt.rcParams.update(
        {
            "figure.dpi": 100,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def plot_state_budget_history(
    simulator: Any,
    num_steps: int,
    save_path: str | None = None,
    show: bool = True,
    figsize: tuple[int, int] = (14, 15),
) -> plt.Figure:
    """
    Plot the distribution of component states over time, budget changes, and action counts.

    This visualization provides a comprehensive view of the simulation history including:
    - Distribution of component states (violin plot)
    - Budget evolution over time
    - Action counts per timestep

    Parameters
    ----------
    simulator : Simulator
        The simulator instance after simulation with state_history, budget_history,
        and action_history attributes
    num_steps : int
        Number of time steps in the simulation
    save_path : str, optional
        Path to save the figure
    show : bool
        Whether to display the plot
    figsize : tuple
        Figure size (width, height)

    Returns
    -------
    fig : matplotlib.figure.Figure
        The generated figure
    """
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({"figure.dpi": 100})

    # Extract data from simulator
    state_history_array = np.array(simulator.history["states"])
    time_steps = np.arange(len(state_history_array))

    # Create figure with three subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize, sharex=True)

    # --- Top plot: State distribution ---
    num_components = state_history_array.shape[1]
    data = {
        "Time Step": np.repeat(time_steps, num_components),
        "State": state_history_array.flatten(),
    }
    df = pd.DataFrame(data)

    sns.violinplot(
        x="Time Step",
        y="State",
        data=df,
        inner="quartile",
        ax=ax1,
        density_norm="width",
        cut=0,
    )

    ax1.set_title("Distribution of Component States Over Time", fontsize=16, pad=20)
    ax1.set_ylabel("State", fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)

    # --- Middle plot: Budget changes ---
    budget_changes = np.array(simulator.history["budget_remaining"])
    ax2.plot(
        time_steps,
        budget_changes,
        marker="o",
        color="darkred",
        alpha=0.7,
        linewidth=2,
        markersize=5,
    )
    ax2.fill_between(time_steps, budget_changes, alpha=0.2, color="red")
    ax2.set_title("Budget Changes Over Time", fontsize=16, pad=20)
    ax2.set_ylabel("Budget", fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
    ax2.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)

    # --- Bottom plot: Action counts ---
    # Pad actions with zeros at the beginning since first state has no actions
    if simulator.history["actions"]:
        action_history = np.array(simulator.history["actions"])
        # Add a zero action at the beginning to match states
        action_history = np.vstack([np.zeros_like(action_history[0]), action_history])
    else:
        # No actions taken yet
        action_history = np.zeros((len(time_steps), simulator.n_components))

    action_names = ["Do Nothing", "Inspect", "Repair", "Replace"]
    colors = ["blue", "green", "orange", "red"]
    markers = ["o", "s", "^", "D"]

    legend_handles = []
    for action_type in range(4):
        action_counts = np.sum(action_history == action_type, axis=1)
        if np.any(action_counts > 0):
            # Ensure x and y have the same length
            plot_time_steps = time_steps[: len(action_counts)]
            scatter = ax3.scatter(
                plot_time_steps,
                action_counts,
                color=colors[action_type],
                marker=markers[action_type],
                alpha=0.7,
                s=50,
            )
            legend_handles.append((scatter, action_names[action_type]))

    ax3.set_title("Action Counts Over Time", fontsize=16, pad=20)
    ax3.set_xlabel("Time Step", fontsize=14)
    ax3.set_ylabel("Number of Actions", fontsize=14)
    ax3.grid(True, alpha=0.3)

    # Create horizontal legend above the plot
    if legend_handles:
        legend_elements = [handle for handle, _ in legend_handles]
        legend_labels = [label for _, label in legend_handles]
        ax3.legend(
            legend_elements,
            legend_labels,
            bbox_to_anchor=(0.5, 1.25),
            loc="center",
            ncol=len(legend_handles),
            fontsize=12,
        )

    ax3.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()

    return fig


def plot_component_states_comparison(
    state_histories: list[np.ndarray],
    action_histories: list[np.ndarray] | None = None,
    labels: list[str] | None = None,
    failure_conditions: np.ndarray | None = None,
    component_idx: int = 0,
    type_indices: np.ndarray | None = None,
    max_steps: int | None = None,
    save_path: str | None = None,
    show: bool = True,
    figsize: tuple[int, int] | None = None,
) -> plt.Figure:
    """
    Plot and compare condition index over time for a specific component across different policies.

    This is useful for comparing how different control strategies affect individual
    component degradation and maintenance.

    Parameters
    ----------
    state_histories : list of np.ndarray
        State history for each policy/strategy. Shape: (timesteps, n_components)
    action_histories : list of np.ndarray, optional
        Action history for each policy. Shape: (timesteps, n_components)
    labels : list of str, optional
        Labels for each policy/strategy
    failure_conditions : np.ndarray, optional
        Failure thresholds for each component type
    component_idx : int
        Index of component to visualize
    type_indices : np.ndarray, optional
        Mapping from component index to component type
    max_steps : int, optional
        Maximum number of steps to show
    save_path : str, optional
        Path to save the figure
    show : bool
        Whether to display the plot
    figsize : tuple, optional
        Figure size (width, height)

    Returns
    -------
    fig : matplotlib.figure.Figure
        The generated figure
    """
    set_plot_style()

    num_methods = len(state_histories)
    time_steps = np.arange(len(state_histories[0]))

    if max_steps:
        time_steps = time_steps[:max_steps]

    if labels is None:
        labels = [f"Method {i+1}" for i in range(num_methods)]

    if figsize is None:
        figsize = (12, 4 * num_methods)

    fig, axes = plt.subplots(num_methods, 1, figsize=figsize, sharex=True)
    if num_methods == 1:
        axes = [axes]

    # Color scheme for actions
    uiuc_orange = (255 / 255.0, 85 / 255.0, 46 / 255.0)
    action_colors = {0: "gray", 1: "green", 2: uiuc_orange, 3: "blue"}
    action_labels = {0: "No Action", 1: "Inspect", 2: "Repair", 3: "Replace"}

    for idx, ax in enumerate(axes):
        # Extract component history
        state_history = state_histories[idx][: len(time_steps), component_idx]
        label = labels[idx]

        # Plot condition index
        ax.plot(
            time_steps,
            state_history,
            ".-",
            color="black",
            linewidth=2,
            alpha=1.0,
            label="Condition Index",
        )

        # Overlay actions if provided
        if action_histories is not None:
            action_history = action_histories[idx][: len(time_steps), component_idx]
            unique_actions = np.unique(action_history)
            for action in unique_actions:
                indices = np.where(action_history == action)[0]
                if len(indices) > 0:
                    states = state_history[indices]
                    ax.scatter(
                        indices,
                        states,
                        color=action_colors.get(action, "black"),
                        s=70,
                        alpha=0.9,
                        label=action_labels.get(action, f"Action {action}"),
                    )

        # Plot failure threshold if provided
        if failure_conditions is not None and type_indices is not None:
            failure_condition = failure_conditions[type_indices[component_idx]]
            ax.axhline(
                failure_condition,
                color="red",
                linestyle="--",
                linewidth=1.5,
                alpha=0.6,
                label="Failure Threshold",
            )
        elif failure_conditions is not None:
            # Single failure threshold for all components
            ax.axhline(
                failure_conditions[0] if len(failure_conditions) > 0 else 2.0,
                color="red",
                linestyle="--",
                linewidth=1.5,
                alpha=0.6,
                label="Failure Threshold",
            )

        ax.set_xlim(0, len(time_steps) - 1)
        ax.set_ylim(0, np.max(state_history) + 10)
        ax.set_title(label, fontsize=14)
        ax.set_ylabel("Condition Index", fontsize=12)
        ax.grid(True, alpha=0.3)

        if idx == num_methods - 1:
            ax.set_xlabel("Time Steps", fontsize=12)

        # Remove duplicate labels in legend
        handles, labels_legend = ax.get_legend_handles_labels()
        by_label = dict(zip(labels_legend, handles, strict=False))
        ax.legend(by_label.values(), by_label.keys(), loc="best", fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()

    return fig


def plot_action_distribution(
    action_history: np.ndarray,
    save_path: str | None = None,
    show: bool = True,
    figsize: tuple[int, int] = (10, 6),
) -> plt.Figure:
    """
    Plot the distribution of actions taken during simulation.

    Parameters
    ----------
    action_history : np.ndarray
        Action history array. Shape: (timesteps, n_components)
    save_path : str, optional
        Path to save the figure
    show : bool
        Whether to display the plot
    figsize : tuple
        Figure size (width, height)

    Returns
    -------
    fig : matplotlib.figure.Figure
        The generated figure
    """
    set_plot_style()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    action_names = ["Do Nothing", "Inspect", "Repair", "Replace"]
    colors = ["blue", "green", "orange", "red"]

    # Count total actions
    action_counts = np.bincount(action_history.flatten(), minlength=4)

    # Pie chart
    non_zero_actions = action_counts > 0
    ax1.pie(
        action_counts[non_zero_actions],
        labels=[action_names[i] for i in range(4) if non_zero_actions[i]],
        colors=[colors[i] for i in range(4) if non_zero_actions[i]],
        autopct="%1.1f%%",
        startangle=90,
    )
    ax1.set_title("Overall Action Distribution")

    # Actions over time
    time_steps = np.arange(action_history.shape[0])
    for action_type in range(4):
        action_counts_time = np.sum(action_history == action_type, axis=1)
        if np.any(action_counts_time > 0):
            ax2.plot(
                time_steps,
                action_counts_time,
                label=action_names[action_type],
                color=colors[action_type],
                alpha=0.7,
                linewidth=2,
            )

    ax2.set_title("Action Counts Over Time")
    ax2.set_xlabel("Time Step")
    ax2.set_ylabel("Number of Actions")
    ax2.legend(loc="best")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()

    return fig

"""Static visualization plots for infrastructure simulation data."""

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PlotGenerator:
    """Generate various plots for infrastructure simulation analysis."""

    def __init__(self):
        self.default_colors = px.colors.qualitative.Set1
        self.template = "plotly_white"

    def plot_component_states(
        self,
        states_history: list[np.ndarray],
        title: str = "Component States Over Time",
    ) -> go.Figure:
        """Plot component state evolution over time."""
        states_array = np.array(states_history)  # Shape: (timesteps, components)

        fig = go.Figure()

        # Plot mean state
        fig.add_trace(
            go.Scatter(
                x=list(range(len(states_history))),
                y=np.mean(states_array, axis=1),
                mode="lines+markers",
                name="Mean State",
                line=dict(color="blue", width=3),
            )
        )

        # Plot min/max envelope
        fig.add_trace(
            go.Scatter(
                x=list(range(len(states_history))),
                y=np.max(states_array, axis=1),
                mode="lines",
                name="Max State",
                line=dict(color="lightblue", width=1),
                fill=None,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=list(range(len(states_history))),
                y=np.min(states_array, axis=1),
                mode="lines",
                name="Min State",
                line=dict(color="lightblue", width=1),
                fill="tonexty",
                fillcolor="rgba(173, 216, 230, 0.2)",
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Time Step",
            yaxis_title="Component State",
            template=self.template,
            hovermode="x unified",
        )

        return fig

    def plot_budget_usage(
        self,
        budget_history: list[float],
        cost_history: list[np.ndarray],
        title: str = "Budget Usage Over Time",
    ) -> go.Figure:
        """Plot budget usage and spending patterns."""
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Remaining Budget", "Cost per Step"),
            vertical_spacing=0.1,
        )

        # Remaining budget
        fig.add_trace(
            go.Scatter(
                x=list(range(len(budget_history))),
                y=budget_history,
                mode="lines+markers",
                name="Remaining Budget",
                line=dict(color="green", width=2),
            ),
            row=1,
            col=1,
        )

        # Cost per step
        step_costs = [np.sum(costs) for costs in cost_history]
        fig.add_trace(
            go.Scatter(
                x=list(range(len(step_costs))),
                y=step_costs,
                mode="lines+markers",
                name="Cost per Step",
                line=dict(color="red", width=2),
            ),
            row=2,
            col=1,
        )

        fig.update_xaxes(title_text="Time Step", row=2, col=1)
        fig.update_yaxes(title_text="Budget", row=1, col=1)
        fig.update_yaxes(title_text="Cost", row=2, col=1)

        fig.update_layout(title=title, template=self.template, height=600)

        return fig

    def plot_failure_analysis(
        self, states_history: list[np.ndarray], title: str = "Failure Analysis"
    ) -> go.Figure:
        """Plot failure counts and patterns over time."""
        states_array = np.array(states_history)
        failure_counts = np.sum(states_array == 0, axis=1)

        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Cumulative Failures", "Failure Rate"),
            vertical_spacing=0.1,
        )

        # Cumulative failures
        fig.add_trace(
            go.Scatter(
                x=list(range(len(failure_counts))),
                y=failure_counts,
                mode="lines+markers",
                name="Failed Components",
                line=dict(color="darkred", width=2),
                fill="tonexty",
            ),
            row=1,
            col=1,
        )

        # Failure rate (new failures per step)
        failure_rate = np.diff(failure_counts, prepend=0)
        fig.add_trace(
            go.Bar(
                x=list(range(len(failure_rate))),
                y=failure_rate,
                name="New Failures",
                marker_color="red",
            ),
            row=2,
            col=1,
        )

        fig.update_xaxes(title_text="Time Step", row=2, col=1)
        fig.update_yaxes(title_text="Failed Components", row=1, col=1)
        fig.update_yaxes(title_text="New Failures", row=2, col=1)

        fig.update_layout(title=title, template=self.template, height=600)

        return fig

    def plot_action_heatmap(
        self, actions_history: list[np.ndarray], title: str = "Action Heatmap"
    ) -> go.Figure:
        """Plot heatmap of actions taken over time and components."""
        if not actions_history:
            return go.Figure().add_annotation(text="No action data available")

        actions_array = np.array(actions_history)  # Shape: (timesteps, components)

        fig = go.Figure(
            data=go.Heatmap(
                z=actions_array.T,  # Transpose for components on y-axis
                x=list(range(actions_array.shape[0])),
                y=list(range(actions_array.shape[1])),
                colorscale="Viridis",
                hovertemplate="Time: %{x}<br>Component: %{y}<br>Action: %{z}<extra></extra>",
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Time Step",
            yaxis_title="Component ID",
            template=self.template,
        )

        return fig

    def plot_hierarchy_metrics(
        self, hierarchy_metrics: dict[str, dict], title: str = "Hierarchy Performance"
    ) -> go.Figure:
        """Plot hierarchy-based performance metrics."""
        if not hierarchy_metrics:
            return go.Figure().add_annotation(text="No hierarchy data available")

        fig = make_subplots(
            rows=len(hierarchy_metrics),
            cols=1,
            subplot_titles=list(hierarchy_metrics.keys()),
            vertical_spacing=0.1,
        )

        for i, (level_name, level_data) in enumerate(hierarchy_metrics.items(), 1):
            if isinstance(level_data, dict):
                nodes = list(level_data.keys())
                mean_conditions = [
                    level_data[node].get("mean_condition", 0) for node in nodes
                ]

                fig.add_trace(
                    go.Bar(
                        x=nodes,
                        y=mean_conditions,
                        name=f"{level_name} Mean Condition",
                        marker_color=self.default_colors[i % len(self.default_colors)],
                    ),
                    row=i,
                    col=1,
                )

        fig.update_layout(
            title=title, template=self.template, height=200 * len(hierarchy_metrics)
        )

        return fig

    def plot_learning_curves(
        self, training_data: dict[str, list], title: str = "RL Training Progress"
    ) -> go.Figure:
        """Plot RL training learning curves."""
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Episode Rewards",
                "Episode Lengths",
                "Mean Reward (100ep)",
                "Success Rate",
            ),
            vertical_spacing=0.1,
        )

        if "episode_rewards" in training_data:
            rewards = training_data["episode_rewards"]
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(rewards))),
                    y=rewards,
                    mode="lines",
                    name="Episode Reward",
                    line=dict(color="blue", width=1),
                ),
                row=1,
                col=1,
            )

            # Rolling mean
            if len(rewards) > 100:
                rolling_mean = pd.Series(rewards).rolling(100).mean()
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(rolling_mean))),
                        y=rolling_mean,
                        mode="lines",
                        name="100ep Mean",
                        line=dict(color="red", width=2),
                    ),
                    row=2,
                    col=1,
                )

        if "episode_lengths" in training_data:
            lengths = training_data["episode_lengths"]
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(lengths))),
                    y=lengths,
                    mode="lines",
                    name="Episode Length",
                    line=dict(color="green", width=1),
                ),
                row=1,
                col=2,
            )

        if "success_rate" in training_data:
            success_rates = training_data["success_rate"]
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(success_rates))),
                    y=success_rates,
                    mode="lines+markers",
                    name="Success Rate",
                    line=dict(color="orange", width=2),
                ),
                row=2,
                col=2,
            )

        fig.update_layout(title=title, template=self.template, height=600)

        return fig

    def plot_comparison_algorithms(
        self, algorithm_results: dict[str, dict], title: str = "Algorithm Comparison"
    ) -> go.Figure:
        """Compare performance of different RL algorithms."""
        fig = make_subplots(
            rows=1,
            cols=3,
            subplot_titles=("Final Performance", "Sample Efficiency", "Stability"),
            horizontal_spacing=0.1,
        )

        algorithms = list(algorithm_results.keys())
        colors = self.default_colors[: len(algorithms)]

        # Final performance comparison
        final_rewards = [
            algorithm_results[alg].get("final_reward", 0) for alg in algorithms
        ]
        fig.add_trace(
            go.Bar(
                x=algorithms, y=final_rewards, name="Final Reward", marker_color=colors
            ),
            row=1,
            col=1,
        )

        # Sample efficiency (steps to convergence)
        convergence_steps = [
            algorithm_results[alg].get("convergence_steps", 0) for alg in algorithms
        ]
        fig.add_trace(
            go.Bar(
                x=algorithms,
                y=convergence_steps,
                name="Steps to Convergence",
                marker_color=colors,
            ),
            row=1,
            col=2,
        )

        # Stability (reward std)
        reward_stds = [
            algorithm_results[alg].get("reward_std", 0) for alg in algorithms
        ]
        fig.add_trace(
            go.Bar(
                x=algorithms, y=reward_stds, name="Reward Std Dev", marker_color=colors
            ),
            row=1,
            col=3,
        )

        fig.update_layout(
            title=title, template=self.template, height=400, showlegend=False
        )

        return fig

    def create_performance_report(
        self, simulation_data: dict[str, Any]
    ) -> dict[str, go.Figure]:
        """Create a comprehensive performance report with multiple plots."""
        plots = {}

        if "states_history" in simulation_data:
            plots["states"] = self.plot_component_states(
                simulation_data["states_history"]
            )
            plots["failures"] = self.plot_failure_analysis(
                simulation_data["states_history"]
            )

        if "budget_history" in simulation_data and "cost_history" in simulation_data:
            plots["budget"] = self.plot_budget_usage(
                simulation_data["budget_history"], simulation_data["cost_history"]
            )

        if "actions_history" in simulation_data:
            plots["actions"] = self.plot_action_heatmap(
                simulation_data["actions_history"]
            )

        if "hierarchy_metrics" in simulation_data:
            plots["hierarchy"] = self.plot_hierarchy_metrics(
                simulation_data["hierarchy_metrics"]
            )

        if "training_data" in simulation_data:
            plots["learning"] = self.plot_learning_curves(
                simulation_data["training_data"]
            )

        if "algorithm_results" in simulation_data:
            plots["comparison"] = self.plot_comparison_algorithms(
                simulation_data["algorithm_results"]
            )

        return plots

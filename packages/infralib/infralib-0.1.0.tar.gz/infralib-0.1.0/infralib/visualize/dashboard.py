"""Real-time dashboard for infrastructure simulation monitoring."""

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from ..simulator import Simulator
from .network import NetworkVisualizer
from .plots import PlotGenerator


@dataclass
class DashboardState:
    """Container for dashboard state data."""

    simulator: Simulator = None
    is_running: bool = False
    current_step: int = 0
    max_steps: int = 1000
    step_delay: float = 0.1

    # History for plotting
    states_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    budget_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    cost_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    failure_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    action_history: deque = field(default_factory=lambda: deque(maxlen=1000))


class SimulatorDashboard:
    """Real-time dashboard for monitoring infrastructure simulation."""

    def __init__(self):
        self.plot_generator = PlotGenerator()
        self.network_viz = NetworkVisualizer()
        self.state = DashboardState()

        # Initialize session state
        if "dashboard_state" not in st.session_state:
            st.session_state.dashboard_state = self.state
        else:
            self.state = st.session_state.dashboard_state

    def setup_sidebar(self):
        """Setup dashboard sidebar controls."""
        st.sidebar.header("Simulation Controls")

        # Simulation parameters
        n_components = st.sidebar.number_input(
            "Number of Components", min_value=5, max_value=1000, value=50
        )

        self.state.max_steps = st.sidebar.number_input(
            "Max Steps", min_value=100, max_value=10000, value=1000
        )

        self.state.step_delay = st.sidebar.slider(
            "Step Delay (seconds)", min_value=0.01, max_value=2.0, value=0.1, step=0.01
        )

        # Policy selection
        policy_type = st.sidebar.selectbox(
            "Policy Type", ["Random", "Reactive", "Preventive", "RL Agent"]
        )

        # Control buttons
        col1, col2 = st.sidebar.columns(2)

        start_button = col1.button("Start", disabled=self.state.is_running)
        stop_button = col2.button("Stop", disabled=not self.state.is_running)
        reset_button = st.sidebar.button("Reset")

        return {
            "n_components": n_components,
            "policy_type": policy_type,
            "start_button": start_button,
            "stop_button": stop_button,
            "reset_button": reset_button,
        }

    def create_policy_function(self, policy_type: str, n_components: int) -> Callable:
        """Create policy function based on selected type."""
        if policy_type == "Random":

            def random_policy(obs):
                return np.random.randint(0, 3, size=n_components)

        elif policy_type == "Reactive":

            def reactive_policy(obs):
                # Extract states from observation
                states = obs[:n_components] * 10  # Denormalize
                # Repair if state <= 3, inspect if state <= 6, else do nothing
                actions = np.zeros(n_components, dtype=int)
                actions[states <= 3] = 2  # Repair
                actions[(states > 3) & (states <= 6)] = 1  # Inspect
                return actions

        elif policy_type == "Preventive":

            def preventive_policy(obs):
                # Extract states and time since inspection
                states = obs[:n_components] * 10
                time_since_inspection = obs[n_components : 2 * n_components] * 100
                actions = np.zeros(n_components, dtype=int)
                # Repair if critical, inspect if old or degraded
                actions[states <= 2] = 2  # Emergency repair
                actions[(states <= 5) | (time_since_inspection >= 10)] = 1  # Inspect
                return actions

        else:  # RL Agent (placeholder)

            def rl_policy(obs):
                # Simple heuristic for now
                states = obs[:n_components] * 10
                actions = np.zeros(n_components, dtype=int)
                actions[states <= 4] = np.random.choice(
                    [1, 2], size=np.sum(states <= 4)
                )
                return actions

        return locals()[f"{policy_type.lower().replace(' ', '_')}_policy"]

    def initialize_simulator(self, n_components: int):
        """Initialize simulator with default configuration."""
        from ..models.budget import FixedBudget
        from ..models.cost import SimpleCost
        from ..models.dynamics import WeibullDynamics

        # Create models
        dynamics = WeibullDynamics()
        cost = SimpleCost()
        budget = FixedBudget(initial_budget=10000)

        # Create simulator
        self.state.simulator = Simulator(
            dynamics=dynamics, cost=cost, budget=budget, seed=42
        )

        # Reset simulator
        self.state.simulator.reset(n_components)
        self.state.current_step = 0

        # Clear history
        self.state.states_history.clear()
        self.state.budget_history.clear()
        self.state.cost_history.clear()
        self.state.failure_history.clear()
        self.state.action_history.clear()

        # Add initial state
        initial_state = self.state.simulator.states.copy()
        self.state.states_history.append(initial_state)
        self.state.budget_history.append(self.state.simulator.budget.available())
        self.state.failure_history.append(np.sum(initial_state == 0))

    def run_simulation_step(self, policy_fn: Callable):
        """Run one simulation step."""
        if not self.state.simulator or not self.state.is_running:
            return

        # Get observation and action
        obs = self.state.simulator.get_observation()
        actions = policy_fn(obs)

        # Take step
        states, info = self.state.simulator.step(actions)

        # Update history
        self.state.states_history.append(states.copy())
        self.state.budget_history.append(info["budget_remaining"])
        self.state.cost_history.append(info["costs"])
        self.state.failure_history.append(info["failures"])
        self.state.action_history.append(actions.copy())

        self.state.current_step += 1

        # Stop if max steps reached or budget depleted
        if (
            self.state.current_step >= self.state.max_steps
            or info["budget_remaining"] <= 0
        ):
            self.state.is_running = False

    def display_key_metrics(self):
        """Display key simulation metrics."""
        if not self.state.simulator:
            st.info("Initialize simulator to see metrics")
            return

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Current Step",
                self.state.current_step,
                delta=f"/{self.state.max_steps}",
            )

        with col2:
            current_failures = (
                self.state.failure_history[-1] if self.state.failure_history else 0
            )
            st.metric(
                "Failed Components",
                current_failures,
                delta=f"{current_failures}/{len(self.state.simulator.states) if self.state.simulator else 0}",
            )

        with col3:
            current_budget = (
                self.state.budget_history[-1] if self.state.budget_history else 0
            )
            st.metric(
                "Remaining Budget",
                f"${current_budget:.0f}",
                delta=f"{current_budget/10000*100:.1f}%"
                if current_budget > 0
                else "0%",
            )

        with col4:
            if len(self.state.states_history) > 0:
                current_states = self.state.states_history[-1]
                mean_condition = np.mean(current_states)
                st.metric(
                    "Mean Condition",
                    f"{mean_condition:.1f}/10",
                    delta=f"Min: {np.min(current_states)}",
                )

    def display_real_time_plots(self):
        """Display real-time plots."""
        if len(self.state.states_history) < 2:
            st.info("Run simulation to see real-time plots")
            return

        # Convert deque to lists for plotting
        states_list = list(self.state.states_history)
        budget_list = list(self.state.budget_history)
        cost_list = [np.sum(costs) for costs in self.state.cost_history]
        failure_list = list(self.state.failure_history)

        # Two columns for plots
        col1, col2 = st.columns(2)

        with col1:
            # Component states over time
            states_array = np.array(states_list)
            fig_states = go.Figure()

            fig_states.add_trace(
                go.Scatter(
                    x=list(range(len(states_list))),
                    y=np.mean(states_array, axis=1),
                    mode="lines",
                    name="Mean State",
                    line=dict(color="blue", width=2),
                )
            )

            fig_states.add_trace(
                go.Scatter(
                    x=list(range(len(states_list))),
                    y=np.min(states_array, axis=1),
                    mode="lines",
                    name="Min State",
                    line=dict(color="red", width=1),
                )
            )

            fig_states.update_layout(
                title="Component States",
                xaxis_title="Time Step",
                yaxis_title="State",
                height=300,
            )

            st.plotly_chart(fig_states, use_container_width=True)

        with col2:
            # Budget and failures
            fig_budget = go.Figure()

            fig_budget.add_trace(
                go.Scatter(
                    x=list(range(len(budget_list))),
                    y=budget_list,
                    mode="lines",
                    name="Budget",
                    line=dict(color="green", width=2),
                    yaxis="y",
                )
            )

            fig_budget.add_trace(
                go.Scatter(
                    x=list(range(len(failure_list))),
                    y=failure_list,
                    mode="lines",
                    name="Failures",
                    line=dict(color="red", width=2),
                    yaxis="y2",
                )
            )

            fig_budget.update_layout(
                title="Budget & Failures",
                xaxis_title="Time Step",
                yaxis=dict(title="Budget", side="left"),
                yaxis2=dict(title="Failures", side="right", overlaying="y"),
                height=300,
            )

            st.plotly_chart(fig_budget, use_container_width=True)

        # Component state heatmap
        if len(states_list) > 5:
            recent_states = np.array(states_list[-min(50, len(states_list)) :])

            fig_heatmap = go.Figure(
                data=go.Heatmap(
                    z=recent_states.T,
                    colorscale="RdYlGn",
                    zmin=0,
                    zmax=10,
                    hovertemplate="Step: %{x}<br>Component: %{y}<br>State: %{z}<extra></extra>",
                )
            )

            fig_heatmap.update_layout(
                title="Recent Component States (Heatmap)",
                xaxis_title="Recent Time Steps",
                yaxis_title="Component ID",
                height=400,
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)

    def run(self):
        """Main dashboard run loop."""
        st.set_page_config(
            page_title="InfraLib Simulator Dashboard", page_icon="🏗️", layout="wide"
        )

        st.title("🏗️ InfraLib Simulator Dashboard")
        st.markdown("Real-time infrastructure simulation monitoring and control")

        # Setup sidebar controls
        controls = self.setup_sidebar()

        # Handle button clicks
        if controls["reset_button"]:
            self.state.is_running = False
            self.state.current_step = 0
            if self.state.simulator:
                self.state.simulator = None
            st.experimental_rerun()

        if controls["start_button"]:
            if not self.state.simulator:
                self.initialize_simulator(controls["n_components"])
            self.state.is_running = True

        if controls["stop_button"]:
            self.state.is_running = False

        # Main dashboard content
        self.display_key_metrics()

        st.markdown("---")

        # Real-time plots
        self.display_real_time_plots()

        # Run simulation step if active
        if self.state.is_running and self.state.simulator:
            policy_fn = self.create_policy_function(
                controls["policy_type"], controls["n_components"]
            )

            self.run_simulation_step(policy_fn)
            time.sleep(self.state.step_delay)
            st.experimental_rerun()

        # Update session state
        st.session_state.dashboard_state = self.state


def launch_dashboard():
    """Launch the Streamlit dashboard."""
    dashboard = SimulatorDashboard()
    dashboard.run()


if __name__ == "__main__":
    launch_dashboard()

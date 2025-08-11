"""Tests for infrastructure management environments."""

from pathlib import Path

import gymnasium as gym
import numpy as np
import pytest

from infralib.envs.base import BaseInfraEnv
from infralib.envs.simple import SimpleInfraEnv, SimpleInfraMDPEnv, load_config_data
from infralib.models.budget import FixedBudget
from infralib.models.cost import SimpleCost
from infralib.models.dynamics import MarkovDynamics

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "data"
CONFIG_PATH = TEST_DATA_DIR / "config.yaml"
COMPONENTS_PATH = TEST_DATA_DIR / "components.csv"


class TestConfigLoader:
    """Test configuration loading functionality."""

    def test_load_config_data(self):
        """Test loading configuration from files."""
        params = load_config_data(str(CONFIG_PATH), str(COMPONENTS_PATH))

        # Check basic structure
        assert isinstance(params, dict)
        assert "simulation_seed" in params
        assert "initial_budget" in params
        assert "component_types" in params
        assert "failure_conditions" in params

        # Check component data
        assert len(params["component_types"]) == 5
        assert len(params["failure_conditions"]) == 5
        assert len(params["inspect_costs"]) == 5

        # Check derived data
        assert len(params["component_ids"]) == sum(params["num_components_per_type"])

    def test_load_config_data_file_not_found(self):
        """Test handling of missing files."""
        with pytest.raises(FileNotFoundError):
            load_config_data("nonexistent.yaml", str(COMPONENTS_PATH))

        with pytest.raises(FileNotFoundError):
            load_config_data(str(CONFIG_PATH), "nonexistent.csv")


class SimpleTestEnv(BaseInfraEnv):
    """Simple test environment for base class testing."""

    def _create_models(self):
        dynamics = MarkovDynamics(n_states=10, base_deterioration_rate=0.1)
        cost = SimpleCost(inspect_cost=10, repair_cost=100, replace_cost=1000)
        budget = FixedBudget(initial_budget=5000)
        return dynamics, cost, budget, None, None

    def _compute_reward(self, sim_info):
        return -sim_info["total_cost"] - sim_info["failures"] * 100


class TestBaseInfraEnv:
    """Test the base infrastructure environment class."""

    def test_base_env_initialization(self):
        """Test base environment initialization."""
        env = SimpleTestEnv(n_components=3, max_steps=50)

        assert env.n_components == 3
        assert env.max_steps == 50
        assert env.observability == "full"
        assert env.action_type == "multi_discrete"
        assert env.simulator is not None

    def test_action_space_multi_discrete(self):
        """Test multi-discrete action space."""
        env = SimpleTestEnv(n_components=3, action_type="multi_discrete")
        assert isinstance(env.action_space, gym.spaces.MultiDiscrete)
        assert len(env.action_space.nvec) == 3
        assert all(n == 4 for n in env.action_space.nvec)

    def test_action_space_discrete(self):
        """Test discrete action space."""
        env = SimpleTestEnv(n_components=2, action_type="discrete")
        assert isinstance(env.action_space, gym.spaces.Discrete)
        assert env.action_space.n == 4**2  # 16 combinations

    def test_action_space_box(self):
        """Test box action space."""
        env = SimpleTestEnv(n_components=3, action_type="box")
        assert isinstance(env.action_space, gym.spaces.Box)
        assert env.action_space.shape == (3,)

    def test_observation_space(self):
        """Test observation space definition."""
        env = SimpleTestEnv(n_components=3, observability="full")
        assert isinstance(env.observation_space, gym.spaces.Box)
        assert env.observation_space.dtype == np.float32

    def test_reset(self):
        """Test environment reset."""
        env = SimpleTestEnv(n_components=3)
        obs, info = env.reset()

        assert isinstance(obs, np.ndarray)
        assert obs.dtype == np.float32
        assert isinstance(info, dict)
        assert env.current_step == 0
        assert not env.terminated
        assert not env.truncated

    def test_reset_with_seed(self):
        """Test reproducible reset with seed."""
        env = SimpleTestEnv(n_components=3)
        obs1, _ = env.reset(seed=42)
        obs2, _ = env.reset(seed=42)
        np.testing.assert_array_equal(obs1, obs2)

    def test_reset_with_initial_states(self):
        """Test reset with custom initial states."""
        env = SimpleTestEnv(n_components=3)
        initial_states = np.array([8, 6, 4])
        obs, info = env.reset(options={"initial_states": initial_states})

        # Check that simulator states were set correctly
        np.testing.assert_array_equal(env.simulator.states, initial_states)

    def test_step_multi_discrete(self):
        """Test step with multi-discrete actions."""
        env = SimpleTestEnv(n_components=3, action_type="multi_discrete")
        env.reset()

        action = np.array([0, 1, 2])
        obs, reward, terminated, truncated, info = env.step(action)

        assert isinstance(obs, np.ndarray)
        assert obs.dtype == np.float32
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
        assert env.current_step == 1

    def test_step_discrete(self):
        """Test step with discrete actions."""
        env = SimpleTestEnv(n_components=2, action_type="discrete")
        env.reset()

        action = 5  # Should decode to [1, 1] in base 4
        obs, reward, terminated, truncated, info = env.step(action)

        assert isinstance(obs, np.ndarray)
        assert isinstance(reward, float)

    def test_step_box(self):
        """Test step with box actions."""
        env = SimpleTestEnv(n_components=2, action_type="box")
        env.reset()

        action = np.array([0.7, 2.3])  # Should round to [1, 2]
        obs, reward, terminated, truncated, info = env.step(action)

        assert isinstance(obs, np.ndarray)
        assert isinstance(reward, float)

    def test_step_invalid_action_length(self):
        """Test step with invalid action length."""
        env = SimpleTestEnv(n_components=3, action_type="multi_discrete")
        env.reset()

        with pytest.raises(ValueError, match="Multi-discrete action length"):
            env.step(np.array([0, 1]))  # Too short

    def test_step_on_terminated_env(self):
        """Test step on already terminated environment."""
        env = SimpleTestEnv(n_components=3)
        env.reset()
        env.terminated = True

        with pytest.raises(RuntimeError, match="Cannot call step"):
            env.step(np.array([0, 0, 0]))

    def test_termination_conditions(self):
        """Test default termination conditions."""
        env = SimpleTestEnv(n_components=2, max_steps=3)
        env.reset()

        # Test max steps truncation
        for _ in range(3):
            obs, reward, terminated, truncated, info = env.step(np.array([0, 0]))

        assert truncated
        assert env.current_step == 3

    def test_render_modes(self):
        """Test different render modes."""
        env = SimpleTestEnv(n_components=2, render_mode="human")
        env.reset()

        # Should not raise error
        result = env.render()
        assert result is None

        env.render_mode = "rgb_array"
        result = env.render()
        assert isinstance(result, np.ndarray)
        assert result.shape == (64, 64, 3)
        assert result.dtype == np.uint8

    def test_close(self):
        """Test environment cleanup."""
        env = SimpleTestEnv(n_components=2, render_mode="human")
        env.reset()
        env.step(np.array([0, 1]))

        # Should not raise error
        env.close()
        assert len(env.render_history) == 0


class TestSimpleInfraEnv:
    """Test SimpleInfraEnv functionality."""

    def test_initialization_with_config(self):
        """Test initialization with config files."""
        env = SimpleInfraEnv(
            config_path=str(CONFIG_PATH), components_path=str(COMPONENTS_PATH)
        )

        assert env.n_components == 5  # Sum of num_components_per_type
        assert hasattr(env, "params")
        assert env.params["initial_budget"] == 2000
        assert len(env.component_types) == 5

    def test_initialization_without_config(self):
        """Test initialization with default parameters."""
        env = SimpleInfraEnv()

        assert env.n_components == 5
        assert hasattr(env, "params")
        assert env.params["initial_budget"] == 2000

    def test_from_config_classmethod(self):
        """Test creating environment from config using classmethod."""
        env = SimpleInfraEnv.from_config(
            config_path=str(CONFIG_PATH),
            components_path=str(COMPONENTS_PATH),
            reward_scheme="survival",
            max_steps=200,
        )

        assert env.reward_scheme == "survival"
        assert env.max_steps == 200

    def test_reward_schemes(self):
        """Test different reward schemes."""
        env = SimpleInfraEnv(reward_scheme="cost_penalty", max_steps=10)
        env.reset()

        # Create mock sim_info
        sim_info = {"total_cost": 100.0, "failures": 1, "mean_condition": 7.0}

        reward = env._compute_reward(sim_info)
        assert isinstance(reward, float)

        # Test survival scheme
        env.reward_scheme = "survival"
        reward = env._compute_reward(sim_info)
        assert isinstance(reward, float)

        # Test condition scheme
        env.reward_scheme = "condition"
        reward = env._compute_reward(sim_info)
        assert isinstance(reward, float)

    def test_component_specific_termination(self):
        """Test termination with component-specific failure thresholds."""
        env = SimpleInfraEnv(
            config_path=str(CONFIG_PATH), components_path=str(COMPONENTS_PATH)
        )
        env.reset()

        # Mock simulation info with some components failed
        sim_info = {"budget_remaining": 1000, "failures": 0}

        # Set one component to fail (below threshold)
        env.simulator.states[0] = 30  # Below threshold of 40

        terminated, truncated = env._check_termination(sim_info)
        assert terminated  # Should terminate due to component failure

    def test_action_space_sampling(self):
        """Test that sampled actions work correctly."""
        env = SimpleInfraEnv(
            config_path=str(CONFIG_PATH),
            components_path=str(COMPONENTS_PATH),
            action_type="discrete",
        )
        env.reset()

        for _ in range(5):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)

            if terminated or truncated:
                env.reset()


class TestSimpleInfraMDPEnv:
    """Test SimpleInfraMDPEnv functionality."""

    def test_initialization_with_config(self):
        """Test MDP environment initialization with config."""
        env = SimpleInfraMDPEnv(
            config_path=str(CONFIG_PATH), components_path=str(COMPONENTS_PATH)
        )

        assert env.n_components == 5
        assert env.observability == "full"  # MDP uses full observability
        assert hasattr(env, "max_states")
        assert env.max_states == 100  # From config (101 states, 0-indexed)

    def test_margin_observation(self):
        """Test that observations include component margins."""
        env = SimpleInfraMDPEnv(
            config_path=str(CONFIG_PATH), components_path=str(COMPONENTS_PATH)
        )
        obs, info = env.reset()

        # Observation should be: [margins..., budget]
        assert len(obs) == env.n_components + 1

        # Last element should be normalized budget
        budget_norm = obs[-1]
        assert 0 <= budget_norm <= 1

        # First n_components elements should be margins
        margins = obs[:-1]
        assert len(margins) == env.n_components

    def test_margin_calculation(self):
        """Test margin calculation accuracy."""
        env = SimpleInfraMDPEnv(
            config_path=str(CONFIG_PATH), components_path=str(COMPONENTS_PATH)
        )

        # Set specific states for testing
        test_states = np.array([50, 60, 70, 80, 90])  # All above threshold of 40
        env.reset()
        env.simulator.states = test_states

        obs = env._get_observation()
        margins = obs[:-1]  # All but budget

        # Calculate expected margins: (state - threshold) / (max_state - threshold)
        expected_margins = (test_states - 40) / (100 - 40)

        np.testing.assert_array_almost_equal(margins, expected_margins, decimal=5)

    def test_margin_reward_schemes(self):
        """Test different margin-based reward schemes."""
        env = SimpleInfraMDPEnv(reward_scheme="margin", max_steps=10)
        env.reset()

        sim_info = {"total_cost": 50.0, "failures": 0}
        reward = env._compute_reward(sim_info)
        assert isinstance(reward, float)

        # Test weighted margin scheme
        env.reward_scheme = "weighted_margin"
        reward = env._compute_reward(sim_info)
        assert isinstance(reward, float)

        # Test binary scheme
        env.reward_scheme = "binary"
        reward = env._compute_reward(sim_info)
        assert isinstance(reward, float)

    def test_margin_termination(self):
        """Test termination based on negative margins."""
        env = SimpleInfraMDPEnv(
            config_path=str(CONFIG_PATH), components_path=str(COMPONENTS_PATH)
        )
        env.reset()

        # Set one component to fail (below threshold)
        env.simulator.states[0] = 30  # Below threshold of 40 -> negative margin

        sim_info = {"budget_remaining": 1000}
        terminated, truncated = env._check_termination(sim_info)

        assert terminated  # Should terminate due to negative margin

    def test_from_config_classmethod(self):
        """Test creating MDP environment from config."""
        env = SimpleInfraMDPEnv.from_config(
            config_path=str(CONFIG_PATH),
            components_path=str(COMPONENTS_PATH),
            reward_scheme="weighted_margin",
        )

        assert env.reward_scheme == "weighted_margin"
        assert env.observability == "full"

    def test_multi_discrete_actions(self):
        """Test MDP environment with multi-discrete actions."""
        env = SimpleInfraMDPEnv(
            config_path=str(CONFIG_PATH),
            components_path=str(COMPONENTS_PATH),
            action_type="multi_discrete",
        )
        env.reset()

        action = np.array([0, 1, 2, 0, 0])  # Adjust for 5 components in test data
        obs, reward, terminated, truncated, info = env.step(action)

        assert len(obs) == 6  # 5 margins + 1 budget
        assert isinstance(reward, float)


class TestEnvironmentComparison:
    """Test comparing POMDP vs MDP environments."""

    def test_observation_differences(self):
        """Test that POMDP and MDP have different observations."""
        pomdp_env = SimpleInfraEnv(
            config_path=str(CONFIG_PATH),
            components_path=str(COMPONENTS_PATH),
            observability="partial",
        )

        mdp_env = SimpleInfraMDPEnv(
            config_path=str(CONFIG_PATH), components_path=str(COMPONENTS_PATH)
        )

        pomdp_obs, _ = pomdp_env.reset(seed=42)
        mdp_obs, _ = mdp_env.reset(seed=42)

        # Should have different observation formats
        assert len(pomdp_obs) != len(mdp_obs) or not np.allclose(pomdp_obs, mdp_obs)

    def test_action_space_consistency(self):
        """Test that both environments support same action spaces."""
        for action_type in ["multi_discrete", "discrete"]:
            pomdp_env = SimpleInfraEnv(
                config_path=str(CONFIG_PATH),
                components_path=str(COMPONENTS_PATH),
                action_type=action_type,
            )
            mdp_env = SimpleInfraMDPEnv(
                config_path=str(CONFIG_PATH),
                components_path=str(COMPONENTS_PATH),
                action_type=action_type,
            )

            # Action spaces should be identical
            assert type(pomdp_env.action_space) is type(mdp_env.action_space)

            if action_type == "multi_discrete":
                assert np.array_equal(
                    pomdp_env.action_space.nvec, mdp_env.action_space.nvec
                )
            elif action_type == "discrete":
                assert pomdp_env.action_space.n == mdp_env.action_space.n


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

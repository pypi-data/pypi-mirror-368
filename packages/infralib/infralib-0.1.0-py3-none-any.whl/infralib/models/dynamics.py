"""Deterioration dynamics models with unified interface."""

import numba
import numpy as np
from scipy.stats import weibull_min

from .base import BaseModel, ModelContext


class DynamicsModel(BaseModel):
    """Base class for deterioration dynamics with unified interface."""

    def compute(self, context: ModelContext) -> np.ndarray:
        """Compute next states using context.

        Args:
            context: Must contain states and actions

        Returns:
            next_states: Array of next states
        """
        if context.actions is None:
            raise ValueError("Actions required in context for dynamics computation")

        self.validate_context(context)
        return self._compute_dynamics(context)

    def _compute_dynamics(self, context: ModelContext) -> np.ndarray:
        """Internal dynamics computation to be implemented by subclasses."""
        raise NotImplementedError

    def step(self, states: np.ndarray, actions: np.ndarray) -> np.ndarray:
        """Legacy interface for backward compatibility."""
        context = ModelContext(states=states, actions=actions)
        return self.compute(context)


class WeibullDynamics(DynamicsModel):
    """Weibull deterioration dynamics with validation."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "n_states": (int, (2, 1000), "Number of discrete states"),
            "shape": (float, (0.5, 10.0), "Weibull shape parameter (single type)"),
            "scale": (float, (1.0, 100.0), "Weibull scale parameter (single type)"),
            "shapes": (list, (0.5, 10.0), "List of Weibull shape parameters per type"),
            "scales": (list, (1.0, 100.0), "List of Weibull scale parameters per type"),
            "repair_effectiveness": (float, (0.1, 1.0), "Repair effectiveness (0-1)"),
            "type_indices": (
                list,
                (0, 100),
                "Array mapping component index to type index",
            ),
        }

    def __init__(
        self,
        n_states: int = 10,
        shape: float = None,
        scale: float = None,
        shapes: list = None,
        scales: list = None,
        type_indices: np.ndarray = None,
        repair_effectiveness: float = 0.7,
        seed: int | None = None,
    ):
        # Handle both single-type and multi-type cases
        if shapes is not None and scales is not None:
            # Multi-type case
            if type_indices is None:
                raise ValueError(
                    "type_indices required when using multi-type parameters"
                )
            self.is_multi_type = True
        else:
            # Single-type case - use defaults if not provided
            if shape is None:
                shape = 2.5
            if scale is None:
                scale = 15.0
            shapes = [shape]
            scales = [scale]
            if type_indices is None:
                type_indices = np.array([0])  # Single type
            self.is_multi_type = False

        # Only pass non-None values to avoid validation issues
        params_dict = {
            "n_states": n_states,
            "shapes": shapes,
            "scales": scales,
            "type_indices": type_indices,
            "repair_effectiveness": repair_effectiveness,
        }

        # Add single-type parameters only if they're not None (for backward compatibility)
        if shape is not None:
            params_dict["shape"] = shape
        if scale is not None:
            params_dict["scale"] = scale

        super().__init__(**params_dict)

        if seed is not None:
            np.random.seed(seed)

    def _setup(self):
        """Setup transition matrices after validation."""
        self.n_states = self.params["n_states"]
        self.shapes = self.params["shapes"]
        self.scales = self.params["scales"]
        self.type_indices = np.array(self.params["type_indices"])
        self.repair_effectiveness = self.params["repair_effectiveness"]

        # Validate parameters
        if len(self.shapes) != len(self.scales):
            raise ValueError("Number of shapes must match number of scales")

        self.n_types = len(self.shapes)
        self._build_transition_matrices()

    def _build_transition_matrices(self):
        """Build transition probability matrices for each component type and action."""
        # Shape: (n_types, n_actions, n_states, n_states) for multi-type or (n_actions, n_states, n_states) for single-type
        if self.n_types == 1:
            # Single-type case: maintain backward compatibility
            self.transition_matrices = np.zeros((4, self.n_states, self.n_states))
            shape, scale = self.shapes[0], self.scales[0]

            # Do nothing and inspect: Weibull-based deterioration
            for action in [0, 1]:
                for state in range(self.n_states):
                    if state == 0:  # Failed components stay failed
                        self.transition_matrices[action, state, 0] = 1.0
                    else:
                        # Weibull-based deterioration probabilities
                        # Adjust scale to be more reasonable for 0-100 state space
                        effective_scale = scale / 10.0  # Scale down by factor of 10
                        prob_stay = weibull_min.sf(1, shape, scale=effective_scale)
                        prob_deteriorate = 1 - prob_stay
                        self.transition_matrices[action, state, state] = prob_stay
                        if state > 0:
                            self.transition_matrices[action, state, state - 1] = (
                                prob_deteriorate
                            )

            # Repair: improve state probabilistically
            for state in range(self.n_states):
                if state == 0:  # Can't repair failed component
                    self.transition_matrices[2, state, 0] = 1.0
                else:
                    improvement = int(
                        self.repair_effectiveness * (self.n_states - state)
                    )
                    new_state = min(self.n_states - 1, state + improvement)
                    self.transition_matrices[2, state, new_state] = 1.0

            # Replace: restore to perfect condition
            for state in range(self.n_states):
                self.transition_matrices[3, state, self.n_states - 1] = 1.0
        else:
            # Multi-type case: separate matrices per type
            self.transition_matrices = np.zeros(
                (self.n_types, 4, self.n_states, self.n_states)
            )

            for type_idx in range(self.n_types):
                shape = self.shapes[type_idx]
                scale = self.scales[type_idx]

                # Do nothing and inspect: Weibull-based deterioration
                for action in [0, 1]:
                    for state in range(self.n_states):
                        if state == 0:  # Failed components stay failed
                            self.transition_matrices[type_idx, action, state, 0] = 1.0
                        else:
                            # Weibull-based deterioration probabilities
                            # Adjust scale to be more reasonable for 0-100 state space
                            effective_scale = scale / 10.0  # Scale down by factor of 10
                            prob_stay = weibull_min.sf(1, shape, scale=effective_scale)
                            prob_deteriorate = 1 - prob_stay
                            self.transition_matrices[type_idx, action, state, state] = (
                                prob_stay
                            )
                            if state > 0:
                                self.transition_matrices[
                                    type_idx, action, state, state - 1
                                ] = prob_deteriorate

                # Repair: improve state probabilistically
                for state in range(self.n_states):
                    if state == 0:  # Can't repair failed component
                        self.transition_matrices[type_idx, 2, state, 0] = 1.0
                    else:
                        improvement = int(
                            self.repair_effectiveness * (self.n_states - state)
                        )
                        new_state = min(self.n_states - 1, state + improvement)
                        self.transition_matrices[type_idx, 2, state, new_state] = 1.0

                # Replace: restore to perfect condition
                for state in range(self.n_states):
                    self.transition_matrices[type_idx, 3, state, self.n_states - 1] = (
                        1.0
                    )

    def _compute_dynamics(self, context: ModelContext) -> np.ndarray:
        """Compute next states using transition matrices."""
        states = context.states
        actions = context.actions
        next_states = np.zeros_like(states)

        if self.n_types == 1:
            # Single-type case: use original logic
            for i, (state, action) in enumerate(zip(states, actions, strict=False)):
                probs = self.transition_matrices[action, state, :]
                next_states[i] = np.random.choice(self.n_states, p=probs)
        else:
            # Multi-type case: use type-specific matrices
            for i, (state, action) in enumerate(zip(states, actions, strict=False)):
                component_type = self.type_indices[i]
                probs = self.transition_matrices[component_type, action, state, :]
                next_states[i] = np.random.choice(self.n_states, p=probs)

        return next_states

    def reset(self, context: ModelContext | None = None):
        """Reset dynamics model (rebuild matrices if needed)."""
        self._build_transition_matrices()


class MarkovDynamics(DynamicsModel):
    """Markov chain dynamics with custom transition matrices."""

    @classmethod
    def get_parameter_spec(cls):
        return {
            "n_states": (int, (2, 1000), "Number of states"),
            "base_deterioration_rate": (
                float,
                (0.0, 1.0),
                "Base transition probability",
            ),
            "repair_effectiveness": (float, (0.1, 1.0), "Repair effectiveness"),
        }

    def __init__(
        self,
        n_states: int = 10,
        base_deterioration_rate: float = 0.1,
        repair_effectiveness: float = 0.7,
        seed: int | None = None,
    ):
        super().__init__(
            n_states=n_states,
            base_deterioration_rate=base_deterioration_rate,
            repair_effectiveness=repair_effectiveness,
        )

        if seed is not None:
            np.random.seed(seed)

    def _setup(self):
        """Setup transition matrices after validation."""
        self.n_states = self.params["n_states"]
        self.base_deterioration_rate = self.params["base_deterioration_rate"]
        self.repair_effectiveness = self.params["repair_effectiveness"]

        self._build_transition_matrices()

    def _build_transition_matrices(self):
        """Build simple Markov transition matrices."""
        self.transition_matrices = np.zeros((4, self.n_states, self.n_states))

        # Do nothing and inspect: linear deterioration
        for action in [0, 1]:
            for state in range(self.n_states):
                if state == 0:
                    self.transition_matrices[action, state, 0] = 1.0
                else:
                    stay_prob = 1 - self.base_deterioration_rate
                    deteriorate_prob = self.base_deterioration_rate

                    self.transition_matrices[action, state, state] = stay_prob
                    self.transition_matrices[action, state, max(0, state - 1)] = (
                        deteriorate_prob
                    )

        # Repair and replace (similar to Weibull)
        for state in range(self.n_states):
            if state == 0:
                self.transition_matrices[2, state, 0] = 1.0
            else:
                improvement = int(self.repair_effectiveness * (self.n_states - state))
                new_state = min(self.n_states - 1, state + improvement)
                self.transition_matrices[2, state, new_state] = 1.0

            self.transition_matrices[3, state, self.n_states - 1] = 1.0

    def _compute_dynamics(self, context: ModelContext) -> np.ndarray:
        """Compute next states using transition matrices."""
        states = context.states
        actions = context.actions
        next_states = np.zeros_like(states)

        for i, (state, action) in enumerate(zip(states, actions, strict=False)):
            probs = self.transition_matrices[action, state, :]
            next_states[i] = np.random.choice(self.n_states, p=probs)

        return next_states

    def reset(self, context: ModelContext | None = None):
        """Reset dynamics model (rebuild matrices if needed)."""
        self._build_transition_matrices()


@numba.jit(nopython=True, parallel=True)
def _fast_transition(states, actions, transition_matrices, n_components, n_states):
    """Fast numba-compiled transition function."""
    next_states = np.zeros(n_components, dtype=np.int32)

    for i in numba.prange(n_components):
        state = states[i]
        action = actions[i]

        # Simple sampling without full probability array
        rand_val = np.random.random()
        cum_prob = 0.0

        for next_state in range(n_states):
            cum_prob += transition_matrices[action, state, next_state]
            if rand_val <= cum_prob:
                next_states[i] = next_state
                break

    return next_states


class FastWeibullDynamics(WeibullDynamics):
    """Numba-optimized version of Weibull dynamics for large-scale simulation."""

    def _compute_dynamics(self, context: ModelContext) -> np.ndarray:
        """Fast vectorized state transition using numba."""
        return _fast_transition(
            context.states,
            context.actions,
            self.transition_matrices,
            len(context.states),
            self.n_states,
        )

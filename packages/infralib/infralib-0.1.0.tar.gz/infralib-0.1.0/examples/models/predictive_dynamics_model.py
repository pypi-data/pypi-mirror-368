"""Example of predictive dynamics model using metadata for deterioration forecasting."""

import numpy as np

from infralib.models.base import ModelContext
from infralib.models.dynamics import DynamicsModel


class PredictiveDynamics(DynamicsModel):
    """Dynamics model that uses metadata to predict and adjust deterioration rates."""

    @classmethod
    def get_required_models(cls) -> list[str]:
        """Requires metadata for predictive features."""
        return ["metadata"]

    @classmethod
    def get_parameter_spec(cls):
        return {
            "n_states": (int, (2, 100), "Number of discrete states"),
            "base_deterioration_rate": (float, (0.0, 1.0), "Base deterioration rate"),
            "age_factor": (float, (0.0, 0.1), "Age-based deterioration increase"),
            "usage_factor": (float, (0.0, 0.05), "Usage-based deterioration factor"),
            "environment_factors": (
                dict,
                {},
                "Environment-specific deterioration multipliers",
            ),
        }

    def __init__(
        self,
        n_states: int = 10,
        base_deterioration_rate: float = 0.1,
        age_factor: float = 0.02,
        usage_factor: float = 0.01,
    ):
        super().__init__(
            n_states=n_states,
            base_deterioration_rate=base_deterioration_rate,
            age_factor=age_factor,
            usage_factor=usage_factor,
        )

        # Default environment factors
        self.environment_factors = {
            "indoor": 1.0,
            "outdoor": 1.3,
            "coastal": 1.6,
            "industrial": 1.4,
            "arctic": 1.2,
            "desert": 1.5,
        }

        # Material-specific factors
        self.material_factors = {
            "steel": 1.0,
            "aluminum": 0.8,
            "plastic": 1.2,
            "concrete": 0.9,
            "composite": 0.7,
        }

    def _setup(self):
        """Setup predictive dynamics parameters."""
        self.n_states = self.params["n_states"]
        self.base_rate = self.params["base_deterioration_rate"]
        self.age_factor = self.params["age_factor"]
        self.usage_factor = self.params["usage_factor"]

        # Track component history for learning
        self.deterioration_history: dict[int, list[float]] = {}
        self.maintenance_history: dict[int, list[int]] = {}

    def _compute_dynamics(self, context: ModelContext) -> np.ndarray:
        """Compute predictive dynamics using metadata features."""
        states = context.states
        actions = context.actions
        n_components = len(states)
        next_states = states.copy()

        # Calculate component-specific deterioration rates
        deterioration_rates = self._calculate_deterioration_rates(context)

        for i in range(n_components):
            current_state = states[i]
            action = actions[i]
            deterioration_rate = deterioration_rates[i]

            # Update deterioration history
            if i not in self.deterioration_history:
                self.deterioration_history[i] = []
                self.maintenance_history[i] = []

            self.deterioration_history[i].append(deterioration_rate)
            self.maintenance_history[i].append(action)

            # Keep only recent history (last 50 steps)
            if len(self.deterioration_history[i]) > 50:
                self.deterioration_history[i] = self.deterioration_history[i][-50:]
                self.maintenance_history[i] = self.maintenance_history[i][-50:]

            # Apply actions
            if action in [0, 1]:  # Do nothing or inspect
                if current_state > 0 and np.random.random() < deterioration_rate:
                    # Predictive deterioration with learned patterns
                    deterioration_amount = self._predict_deterioration_amount(
                        i, current_state
                    )
                    next_states[i] = max(0, current_state - deterioration_amount)

            elif action == 2:  # Repair
                if current_state > 0:
                    repair_effectiveness = self._calculate_repair_effectiveness(
                        i, context
                    )
                    improvement = int(
                        repair_effectiveness * (self.n_states - current_state)
                    )
                    next_states[i] = min(self.n_states - 1, current_state + improvement)

            elif action == 3:  # Replace
                next_states[i] = self.n_states - 1

        return next_states

    def _calculate_deterioration_rates(self, context: ModelContext) -> np.ndarray:
        """Calculate component-specific deterioration rates using metadata."""
        n_components = len(context.states)
        rates = np.full(n_components, self.base_rate)

        if not context.metadata:
            return rates

        for i in range(n_components):
            component_rate = self.base_rate

            # Age-based deterioration
            try:
                age = context.metadata.get_component_attribute(i, "age")
                if age is not None:
                    # Exponential age effect
                    component_rate *= 1 + self.age_factor * age
            except (KeyError, AttributeError):
                pass

            # Usage-based deterioration
            try:
                usage_hours = context.metadata.get_component_attribute(i, "usage_hours")
                if usage_hours is not None:
                    # Linear usage effect
                    component_rate *= 1 + self.usage_factor * usage_hours / 1000.0
            except (KeyError, AttributeError):
                pass

            # Environment-based deterioration
            try:
                environment = context.metadata.get_component_attribute(i, "environment")
                if environment and environment in self.environment_factors:
                    component_rate *= self.environment_factors[environment]
            except (KeyError, AttributeError):
                pass

            # Material-based deterioration
            try:
                material = context.metadata.get_component_attribute(i, "material")
                if material and material in self.material_factors:
                    component_rate *= self.material_factors[material]
            except (KeyError, AttributeError):
                pass

            # Load factor (high load = faster deterioration)
            try:
                load_factor = context.metadata.get_component_attribute(i, "load_factor")
                if load_factor is not None:
                    component_rate *= 1 + 0.5 * load_factor  # 0-1 load factor
            except (KeyError, AttributeError):
                pass

            rates[i] = min(component_rate, 0.9)  # Cap at 90% chance

        return rates

    def _predict_deterioration_amount(
        self, component_id: int, current_state: int
    ) -> int:
        """Predict deterioration amount based on historical patterns."""
        # Simple prediction: usually 1, but sometimes more based on conditions
        base_deterioration = 1

        # Check if this component has a history of rapid deterioration
        if component_id in self.deterioration_history:
            recent_rates = self.deterioration_history[component_id][
                -10:
            ]  # Last 10 observations
            if len(recent_rates) >= 5:
                avg_recent_rate = np.mean(recent_rates)
                if avg_recent_rate > self.base_rate * 2:
                    # Component is deteriorating faster than normal
                    if (
                        np.random.random() < 0.3
                    ):  # 30% chance of accelerated deterioration
                        base_deterioration = 2

        # State-dependent deterioration (worse condition = more vulnerable)
        if current_state <= 3:
            if (
                np.random.random() < 0.2
            ):  # 20% chance of rapid deterioration when in poor condition
                base_deterioration = min(2, current_state)

        return base_deterioration

    def _calculate_repair_effectiveness(
        self, component_id: int, context: ModelContext
    ) -> float:
        """Calculate repair effectiveness based on component metadata."""
        base_effectiveness = 0.7

        if not context.metadata:
            return base_effectiveness

        # Check repair history - frequent repairs might be less effective
        if component_id in self.maintenance_history:
            recent_repairs = sum(
                1
                for action in self.maintenance_history[component_id][-10:]
                if action == 2
            )
            if recent_repairs > 3:
                base_effectiveness *= 0.8  # Reduced effectiveness from frequent repairs

        # Material affects repair effectiveness
        try:
            material = context.metadata.get_component_attribute(
                component_id, "material"
            )
            material_effectiveness = {
                "steel": 1.0,
                "aluminum": 0.9,
                "plastic": 0.6,  # Harder to repair effectively
                "concrete": 0.8,
                "composite": 1.1,  # Modern materials repair better
            }
            if material in material_effectiveness:
                base_effectiveness *= material_effectiveness[material]
        except (KeyError, AttributeError):
            pass

        # Age affects repair effectiveness (older components harder to repair)
        try:
            age = context.metadata.get_component_attribute(component_id, "age")
            if age is not None and age > 10:
                base_effectiveness *= max(0.5, 1.0 - 0.02 * (age - 10))
        except (KeyError, AttributeError):
            pass

        return max(0.3, min(1.0, base_effectiveness))  # Clamp between 30% and 100%

    def get_deterioration_forecast(
        self, component_id: int, steps_ahead: int = 10
    ) -> list[float]:
        """Forecast deterioration probability for future steps."""
        if (
            component_id not in self.deterioration_history
            or not self.deterioration_history[component_id]
        ):
            return [self.base_rate] * steps_ahead

        # Simple trend-based forecast
        recent_rates = self.deterioration_history[component_id][-5:]
        if len(recent_rates) >= 3:
            # Linear trend extrapolation
            trend = (recent_rates[-1] - recent_rates[0]) / len(recent_rates)
            forecast = []
            for i in range(steps_ahead):
                predicted_rate = recent_rates[-1] + trend * i
                forecast.append(max(0.01, min(0.9, predicted_rate)))
            return forecast
        else:
            return [np.mean(recent_rates)] * steps_ahead

    def reset(self, context: ModelContext | None = None):
        """Reset predictive model and clear history."""
        self.deterioration_history.clear()
        self.maintenance_history.clear()


if __name__ == "__main__":
    from infralib.models.metadata import (
        FieldDefinition,
        GeneralMetadata,
    )

    # Setup metadata with predictive features
    predictive_fields = [
        FieldDefinition("id", int, required=True),
        FieldDefinition("age", float, default_value=0.0),
        FieldDefinition("usage_hours", float, default_value=0.0),
        FieldDefinition("environment", str, default_value="indoor"),
        FieldDefinition("material", str, default_value="steel"),
        FieldDefinition("load_factor", float, default_value=0.5),
    ]

    metadata = GeneralMetadata(predictive_fields)

    # Add components with different characteristics
    components_data = [
        {
            "id": 0,
            "age": 2.0,
            "usage_hours": 5000,
            "environment": "indoor",
            "material": "steel",
            "load_factor": 0.3,
        },
        {
            "id": 1,
            "age": 8.0,
            "usage_hours": 15000,
            "environment": "coastal",
            "material": "aluminum",
            "load_factor": 0.7,
        },
        {
            "id": 2,
            "age": 15.0,
            "usage_hours": 30000,
            "environment": "industrial",
            "material": "plastic",
            "load_factor": 0.9,
        },
        {
            "id": 3,
            "age": 1.0,
            "usage_hours": 1000,
            "environment": "indoor",
            "material": "composite",
            "load_factor": 0.2,
        },
    ]

    for comp_data in components_data:
        metadata.add_component(comp_data["id"], comp_data)

    # Create predictive dynamics model
    predictive_dynamics = PredictiveDynamics(
        n_states=10, base_deterioration_rate=0.1, age_factor=0.02, usage_factor=0.01
    )

    # Simulate several time steps to build history
    print("=== Predictive Dynamics Simulation ===")

    states = np.array([8, 6, 4, 9])  # Initial states

    for step in range(5):
        # Mix of actions
        actions = np.array([0, 1, 2, 0])  # Various maintenance actions

        context = ModelContext(
            states=states, actions=actions, metadata=metadata, time_step=step
        )

        # Calculate deterioration rates
        deterioration_rates = predictive_dynamics._calculate_deterioration_rates(
            context
        )

        print(f"\nStep {step + 1}:")
        print(f"Current states: {states}")
        print(f"Actions: {actions}")
        print(f"Deterioration rates: {deterioration_rates}")

        # Compute next states
        next_states = predictive_dynamics.compute(context)
        print(f"Next states: {next_states}")

        states = next_states

    print("\n=== Deterioration Forecasts ===")
    for comp_id in range(4):
        forecast = predictive_dynamics.get_deterioration_forecast(
            comp_id, steps_ahead=5
        )
        comp_data = components_data[comp_id]
        print(
            f"Component {comp_id} (age: {comp_data['age']}, env: {comp_data['environment']}):"
        )
        print(f"  5-step deterioration forecast: {[f'{r:.3f}' for r in forecast]}")

    print("\n=== Component Characteristics Impact ===")
    print("Young indoor steel component (ID 0): Lower deterioration rate")
    print(
        "Old coastal aluminum component (ID 1): Higher deterioration due to age and environment"
    )
    print("Very old industrial plastic component (ID 2): Highest deterioration rate")
    print("New indoor composite component (ID 3): Lowest deterioration rate")

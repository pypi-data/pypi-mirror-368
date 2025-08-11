"""Unified base model architecture for InfraLib."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class ModelContext:
    """Context object passed to all models containing state and dependencies."""

    states: np.ndarray
    actions: np.ndarray | None = None
    time_step: int = 0

    dynamics: Any = None
    cost: Any = None
    budget: Any = None
    hierarchy: Any = None
    metadata: Any = None

    component_ids: np.ndarray | None = None
    history: dict[str, list] | None = None
    custom_data: dict[str, Any] | None = None

    def get_model(self, model_type: str) -> Any:
        """Get a model by type name."""
        return getattr(self, model_type, None)


class BaseModel(ABC):
    """Unified base class for all infrastructure models."""

    def __init__(self, **params):
        """Initialize with parameters and validate them."""
        self.params = params
        self._validate_init_params()
        self._setup()

    def _validate_init_params(self):
        """Validate initialization parameters."""
        spec = self.get_parameter_spec()
        for name, value in self.params.items():
            if name in spec:
                param_type, (min_val, max_val), _ = spec[name]
                if isinstance(value, (list, np.ndarray)):
                    if not all(min_val <= v <= max_val for v in value):
                        raise ValueError(
                            f"{name} values must be between {min_val} and {max_val}"
                        )
                else:
                    if not min_val <= value <= max_val:
                        raise ValueError(
                            f"{name} must be between {min_val} and {max_val}"
                        )

    @abstractmethod
    def _setup(self):
        """Setup model after parameter validation.

        Called automatically after __init__ parameter validation.
        Use this to initialize internal state, build matrices, etc.
        """
        pass

    @abstractmethod
    def compute(self, context: ModelContext) -> Any:
        """Main computation method - unified across all models.

        Args:
            context: ModelContext with current state and dependencies

        Returns:
            Model-specific output
        """
        pass

    @abstractmethod
    def reset(self, context: ModelContext | None = None):
        """Reset model to initial state.

        Args:
            context: Optional context for state-dependent resets
        """
        pass

    @classmethod
    @abstractmethod
    def get_parameter_spec(cls) -> dict[str, tuple[type, tuple[float, float], str]]:
        """Get parameter specifications.

        Returns:
            Dict of param_name -> (type, (min, max), description)
        """
        pass

    @classmethod
    def get_required_models(cls) -> list[str]:
        """List of required model dependencies.

        Override to specify which other models this one needs.
        Returns list of model names: ['dynamics', 'cost', 'hierarchy', etc.]
        """
        return []

    def validate_context(self, context: ModelContext):
        """Validate that context has required dependencies."""
        for model_name in self.get_required_models():
            if context.get_model(model_name) is None:
                raise ValueError(f"Required model '{model_name}' not found in context")

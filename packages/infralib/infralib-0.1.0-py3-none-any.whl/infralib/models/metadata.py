"""Metadata system with unified interface."""

from dataclasses import dataclass
from typing import Any

import numpy as np

from .base import BaseModel, ModelContext


@dataclass
class FieldDefinition:
    """Definition of a metadata field."""

    name: str
    field_type: type
    required: bool = False
    default_value: Any = None
    description: str = ""


class MetadataModel(BaseModel):
    """Base class for metadata models with unified interface."""

    def compute(self, context: ModelContext) -> dict[str, Any]:
        """Compute metadata-based metrics.

        Args:
            context: Contains component information

        Returns:
            Dict of metadata metrics
        """
        self.validate_context(context)
        return self._compute_metadata_metrics(context)

    def _compute_metadata_metrics(self, context: ModelContext) -> dict[str, Any]:
        """Internal computation of metadata metrics."""
        metrics = {}

        if context.states is None:
            return metrics

        n_components = len(context.states)

        for field_def in self.get_field_definitions():
            field_name = field_def.name
            try:
                values = self.get_bulk_attribute(range(n_components), field_name)
                if values is not None and len(values) > 0:
                    if np.issubdtype(values.dtype, np.number):
                        metrics[f"{field_name}_stats"] = {
                            "mean": float(np.mean(values)),
                            "std": float(np.std(values)),
                            "min": float(np.min(values)),
                            "max": float(np.max(values)),
                        }
            except (KeyError, ValueError):
                pass

        return metrics

    def get_field_definitions(self) -> list[FieldDefinition]:
        """Return list of field definitions for this metadata."""
        raise NotImplementedError

    def get_component_attribute(self, component_id: int, attribute: str) -> Any:
        """Get a specific attribute for a component."""
        raise NotImplementedError

    def get_bulk_attribute(
        self, component_ids: list[int] | np.ndarray, attribute: str
    ) -> np.ndarray:
        """Get attribute values for multiple components efficiently."""
        raise NotImplementedError

    def query_components(self, **filters) -> list[int]:
        """Query components by attributes."""
        raise NotImplementedError

    def reset(self, context: ModelContext | None = None):
        """Reset metadata model."""
        pass

    @classmethod
    def get_parameter_spec(cls) -> dict[str, tuple[type, tuple[float, float], str]]:
        """Metadata models typically don't have numeric parameters."""
        return {}

    def _setup(self):
        """Setup metadata structure."""
        pass


class GeneralMetadata(MetadataModel):
    """General-purpose metadata manager for any domain."""

    def __init__(self, field_definitions: list[FieldDefinition] | None = None):
        """Create metadata manager with field definitions."""
        self.field_definitions = field_definitions or self._default_fields()
        self.components = {}
        super().__init__()

    def _default_fields(self) -> list[FieldDefinition]:
        """Default minimal fields."""
        return [
            FieldDefinition("id", int, required=True),
            FieldDefinition("name", str, required=False, default_value=""),
            FieldDefinition("value", float, required=False, default_value=1.0),
        ]

    def _setup(self):
        """Validate field definitions."""
        self._validate_fields()

    def _validate_fields(self):
        """Ensure field definitions are valid."""
        field_names = set()
        for field in self.field_definitions:
            if field.name in field_names:
                raise ValueError(f"Duplicate field name: {field.name}")
            field_names.add(field.name)

    def get_field_definitions(self) -> list[FieldDefinition]:
        return self.field_definitions

    def add_component(self, component_id: int, metadata: dict[str, Any]):
        """Add component with metadata."""
        validated_metadata = self._validate_metadata(metadata)
        self.components[component_id] = validated_metadata

    def _validate_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Validate and fill defaults for metadata."""
        validated = {}

        for field in self.field_definitions:
            if field.name in metadata:
                validated[field.name] = metadata[field.name]
            elif field.required:
                raise ValueError(f"Required field '{field.name}' missing")
            elif field.default_value is not None:
                validated[field.name] = field.default_value

        return validated

    def get_component_attribute(self, component_id: int, attribute: str) -> Any:
        """Get a specific attribute for a component."""
        if component_id in self.components:
            return self.components[component_id].get(attribute)
        return None

    def get_bulk_attribute(
        self, component_ids: list[int] | np.ndarray, attribute: str
    ) -> np.ndarray:
        """Get attribute values for multiple components efficiently."""
        values = []
        for comp_id in component_ids:
            if comp_id in self.components:
                value = self.components[comp_id].get(attribute, 0)
                values.append(value)
            else:
                values.append(0)
        return np.array(values)

    def query_components(self, **filters) -> list[int]:
        """Query components by attributes."""
        matching = []
        for comp_id, metadata in self.components.items():
            match = True
            for key, value in filters.items():
                if metadata.get(key) != value:
                    match = False
                    break
            if match:
                matching.append(comp_id)
        return matching

    def set_component_attribute(self, component_id: int, attribute: str, value: Any):
        """Set an attribute for a component."""
        if component_id not in self.components:
            self.components[component_id] = {}
        self.components[component_id][attribute] = value

    def compute_weighted_metric(
        self, values: np.ndarray, weight_attribute: str
    ) -> float:
        """Compute weighted metric using metadata attribute as weights."""
        component_ids = range(len(values))
        weights = self.get_bulk_attribute(component_ids, weight_attribute)

        if np.sum(weights) == 0:
            return float(np.mean(values))

        return float(np.average(values, weights=weights))


class SimpleMetadata(GeneralMetadata):
    """Simple metadata with common fields."""

    def __init__(self):
        """Create metadata with common infrastructure fields."""
        fields = [
            FieldDefinition("id", int, required=True),
            FieldDefinition("name", str, default_value=""),
            FieldDefinition("type", str, default_value="standard"),
            FieldDefinition("importance", float, default_value=1.0),
            FieldDefinition("location", str, default_value=""),
        ]
        super().__init__(fields)


class KeyValueMetadata(GeneralMetadata):
    """Flexible key-value metadata storage."""

    def __init__(self):
        """Create flexible metadata that accepts any fields."""
        super().__init__([])
        self.flexible_fields = set()

    def add_component(self, component_id: int, metadata: dict[str, Any]):
        """Add component with any metadata fields."""
        self.components[component_id] = metadata
        self.flexible_fields.update(metadata.keys())

    def get_all_fields(self) -> list[str]:
        """Get all fields that have been used."""
        return list(self.flexible_fields)

    def _validate_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """No validation for flexible metadata."""
        return metadata

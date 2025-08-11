"""Hierarchy system with unified interface."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .base import BaseModel, ModelContext


@dataclass
class HierarchyLevel:
    """Definition of a hierarchy level."""

    name: str
    parent_level: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    aggregation_rules: dict[str, str] = field(default_factory=dict)


class HierarchyModel(BaseModel):
    """Base class for hierarchy models with unified interface."""

    def compute(self, context: ModelContext) -> dict[str, Any]:
        """Compute hierarchy-based metrics.

        Args:
            context: Contains states and component information

        Returns:
            Dict of hierarchy metrics and aggregations
        """
        self.validate_context(context)
        return self._compute_hierarchy_metrics(context)

    def _compute_hierarchy_metrics(self, context: ModelContext) -> dict[str, Any]:
        """Internal computation of hierarchy metrics."""
        metrics = {}

        if context.states is None:
            return metrics

        for level in self.get_hierarchy_levels():
            if level.name == "component":
                continue

            level_metrics = self._compute_level_metrics(level, context.states)
            if level_metrics:
                metrics[f"{level.name}_metrics"] = level_metrics

        return metrics

    def _compute_level_metrics(
        self, level: HierarchyLevel, states: np.ndarray
    ) -> dict[str, Any]:
        """Compute metrics for a specific hierarchy level."""
        groups = self.get_all_groups(level.name)
        metrics = {}

        for group in groups:
            components = self.get_group_components(group, level.name)
            if components:
                component_states = [
                    states[cid]
                    for cid in components
                    if isinstance(cid, int) and cid < len(states)
                ]
                if component_states:
                    metrics[group] = self._aggregate_states(component_states, level)

        return metrics

    def _aggregate_states(
        self, states: list, level: HierarchyLevel
    ) -> dict[str, float]:
        """Aggregate component states based on level rules."""
        state_array = np.array(states)

        aggregation = {
            "mean": float(np.mean(state_array)),
            "min": float(np.min(state_array)),
            "max": float(np.max(state_array)),
            "failures": int(np.sum(state_array == 0)),
        }

        for field, rule in level.aggregation_rules.items():
            if rule == "min":
                aggregation[field] = float(np.min(state_array))
            elif rule == "max":
                aggregation[field] = float(np.max(state_array))
            elif rule == "mean":
                aggregation[field] = float(np.mean(state_array))
            elif rule == "sum":
                aggregation[field] = float(np.sum(state_array))

        return aggregation

    def get_hierarchy_levels(self) -> list[HierarchyLevel]:
        """Return ordered hierarchy levels from bottom to top."""
        raise NotImplementedError

    def get_component_group(self, component_id: int, level: str) -> str | None:
        """Get the group a component belongs to at a level."""
        raise NotImplementedError

    def get_group_components(self, group_id: str, level: str) -> list[int]:
        """Get all components in a group."""
        raise NotImplementedError

    def get_all_groups(self, level: str) -> list[str]:
        """Get all group IDs at a hierarchy level."""
        raise NotImplementedError

    def get_group_property(self, group_id: str, level: str, property: str) -> Any:
        """Get a property of a hierarchy group."""
        raise NotImplementedError

    def reset(self, context: ModelContext | None = None):
        """Reset hierarchy model."""
        pass

    @classmethod
    def get_parameter_spec(cls) -> dict[str, tuple[type, tuple[float, float], str]]:
        """Hierarchy models typically don't have numeric parameters."""
        return {}

    def _setup(self):
        """Setup hierarchy structure."""
        pass


class GeneralHierarchy(HierarchyModel):
    """General-purpose hierarchy for any domain."""

    def __init__(self, level_definitions: list[HierarchyLevel] | None = None):
        """Create hierarchy with user-defined levels."""
        self.level_definitions = level_definitions or self._default_levels()
        self.assignments = {}
        self.groups = {}
        super().__init__()

    def _default_levels(self) -> list[HierarchyLevel]:
        """Default two-level hierarchy."""
        return [
            HierarchyLevel("component"),
            HierarchyLevel(
                "group", "component", aggregation_rules={"condition": "min"}
            ),
        ]

    def _setup(self):
        """Validate and setup hierarchy."""
        self._validate_hierarchy()

    def _validate_hierarchy(self):
        """Ensure hierarchy is well-formed."""
        level_names = {level.name for level in self.level_definitions}
        for level in self.level_definitions:
            if level.parent_level and level.parent_level not in level_names:
                raise ValueError(f"Parent level {level.parent_level} not found")

    def get_hierarchy_levels(self) -> list[HierarchyLevel]:
        return self.level_definitions

    def assign_component(self, component_id: int, assignments: dict[str, str]):
        """Assign component to hierarchy groups."""
        self.assignments[component_id] = assignments

        for level, group in assignments.items():
            if level not in self.groups:
                self.groups[level] = {}
            if group not in self.groups[level]:
                self.groups[level][group] = {"components": set(), "properties": {}}
            self.groups[level][group]["components"].add(component_id)

    def get_component_group(self, component_id: int, level: str) -> str | None:
        """Get the group a component belongs to at a level."""
        return self.assignments.get(component_id, {}).get(level)

    def get_group_components(self, group_id: str, level: str) -> list[int]:
        """Get all components in a group."""
        if level in self.groups and group_id in self.groups[level]:
            return list(self.groups[level][group_id]["components"])
        return []

    def get_all_groups(self, level: str) -> list[str]:
        """Get all group IDs at a hierarchy level."""
        return list(self.groups.get(level, {}).keys())

    def set_group_property(self, group_id: str, level: str, property: str, value: Any):
        """Set a property for a hierarchy group."""
        if level not in self.groups:
            self.groups[level] = {}
        if group_id not in self.groups[level]:
            self.groups[level][group_id] = {"components": set(), "properties": {}}
        self.groups[level][group_id]["properties"][property] = value

    def get_group_property(self, group_id: str, level: str, property: str) -> Any:
        """Get a property of a hierarchy group."""
        if level in self.groups and group_id in self.groups[level]:
            return self.groups[level][group_id]["properties"].get(property)
        return None

    def compute_group_metric(
        self, group_id: str, level: str, values: np.ndarray, aggregation: str = "mean"
    ) -> float:
        """Compute aggregated metric for a group."""
        components = self.get_group_components(group_id, level)
        if not components:
            return 0.0

        component_values = values[components]

        if aggregation == "mean":
            return float(np.mean(component_values))
        elif aggregation == "min":
            return float(np.min(component_values))
        elif aggregation == "max":
            return float(np.max(component_values))
        elif aggregation == "sum":
            return float(np.sum(component_values))
        elif aggregation == "weighted_mean":
            weights = [
                self.get_group_property(group_id, level, "weight") or 1.0
                for _ in components
            ]
            return float(np.average(component_values, weights=weights))
        else:
            return float(np.mean(component_values))


class SimpleHierarchy(GeneralHierarchy):
    """Simple two-level hierarchy for basic applications."""

    def __init__(self):
        """Create a simple component-system hierarchy."""
        levels = [
            HierarchyLevel("component"),
            HierarchyLevel(
                "system",
                "component",
                aggregation_rules={"condition": "min", "cost": "sum"},
            ),
        ]
        super().__init__(levels)


class MultiLevelHierarchy(GeneralHierarchy):
    """Multi-level hierarchy for complex systems."""

    def __init__(self, n_levels: int = 3):
        """Create a multi-level hierarchy.

        Args:
            n_levels: Number of hierarchy levels (including component level)
        """
        levels = [HierarchyLevel("component")]

        for i in range(1, n_levels):
            parent = f"level_{i-1}" if i > 1 else "component"
            level_name = f"level_{i}"
            levels.append(
                HierarchyLevel(
                    level_name, parent, aggregation_rules={"condition": "min"}
                )
            )

        super().__init__(levels)

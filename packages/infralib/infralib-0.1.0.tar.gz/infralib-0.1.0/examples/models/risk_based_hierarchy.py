"""Example of risk-based hierarchy model that computes risk metrics."""

from typing import Any

import numpy as np

from infralib.models.base import ModelContext
from infralib.models.hierarchy import HierarchyLevel, HierarchyModel


class RiskBasedHierarchy(HierarchyModel):
    """Hierarchy model that computes risk-based metrics using metadata."""

    @classmethod
    def get_required_models(cls) -> list[str]:
        """Uses metadata for risk calculations."""
        return ["metadata"]

    @classmethod
    def get_parameter_spec(cls):
        return {
            "risk_threshold_critical": (
                float,
                (0.0, 1.0),
                "Risk threshold for critical classification",
            ),
            "risk_threshold_high": (
                float,
                (0.0, 1.0),
                "Risk threshold for high risk classification",
            ),
            "failure_impact_weight": (
                float,
                (0.0, 1.0),
                "Weight for failure impact in risk calculation",
            ),
            "cascading_failure_multiplier": (
                float,
                (1.0, 5.0),
                "Multiplier for cascading failure risk",
            ),
        }

    def __init__(
        self,
        risk_threshold_critical: float = 0.8,
        risk_threshold_high: float = 0.6,
        failure_impact_weight: float = 0.4,
        cascading_failure_multiplier: float = 2.0,
    ):
        super().__init__(
            risk_threshold_critical=risk_threshold_critical,
            risk_threshold_high=risk_threshold_high,
            failure_impact_weight=failure_impact_weight,
            cascading_failure_multiplier=cascading_failure_multiplier,
        )

    def _setup(self):
        """Setup risk-based hierarchy."""
        # Define risk-focused hierarchy levels
        self.level_definitions = [
            HierarchyLevel(
                "component", properties={"risk_level": "str", "consequence": "str"}
            ),
            HierarchyLevel(
                "subsystem",
                "component",
                properties={"redundancy": "bool", "service_level": "str"},
                aggregation_rules={"risk": "max", "availability": "min"},
            ),
            HierarchyLevel(
                "system",
                "subsystem",
                properties={"business_criticality": "str", "recovery_time": "float"},
                aggregation_rules={"risk": "weighted_mean", "impact": "sum"},
            ),
            HierarchyLevel(
                "facility",
                "system",
                properties={"strategic_importance": "str"},
                aggregation_rules={"overall_risk": "max"},
            ),
        ]

        self.assignments = {}
        self.groups = {}
        self.risk_cache = {}  # Cache for expensive risk calculations

        # Risk parameters
        self.risk_threshold_critical = self.params["risk_threshold_critical"]
        self.risk_threshold_high = self.params["risk_threshold_high"]
        self.failure_impact_weight = self.params["failure_impact_weight"]
        self.cascading_multiplier = self.params["cascading_failure_multiplier"]

    def get_hierarchy_levels(self) -> list[HierarchyLevel]:
        return self.level_definitions

    def assign_component(self, component_id: int, assignments: dict[str, str]):
        """Assign component to risk-based hierarchy."""
        self.assignments[component_id] = assignments

        # Add to group tracking
        for level, group in assignments.items():
            if level not in self.groups:
                self.groups[level] = {}
            if group not in self.groups[level]:
                self.groups[level][group] = {"components": set(), "properties": {}}
            self.groups[level][group]["components"].add(component_id)

    def get_component_group(self, component_id: int, level: str) -> str | None:
        return self.assignments.get(component_id, {}).get(level)

    def get_group_components(self, group_id: str, level: str) -> list[int]:
        if level in self.groups and group_id in self.groups[level]:
            return list(self.groups[level][group_id]["components"])
        return []

    def get_all_groups(self, level: str) -> list[str]:
        return list(self.groups.get(level, {}).keys())

    def set_group_property(self, group_id: str, level: str, property: str, value: Any):
        """Set property for a hierarchy group."""
        if level not in self.groups:
            self.groups[level] = {}
        if group_id not in self.groups[level]:
            self.groups[level][group_id] = {"components": set(), "properties": {}}
        self.groups[level][group_id]["properties"][property] = value

    def get_group_property(self, group_id: str, level: str, property: str) -> Any:
        if level in self.groups and group_id in self.groups[level]:
            return self.groups[level][group_id]["properties"].get(property)
        return None

    def _compute_hierarchy_metrics(self, context: ModelContext) -> dict[str, Any]:
        """Compute risk-based hierarchy metrics."""
        metrics = super()._compute_hierarchy_metrics(context)

        if context.states is None or context.metadata is None:
            return metrics

        # Add risk-specific metrics
        risk_metrics = self._compute_risk_metrics(context)
        metrics.update(risk_metrics)

        return metrics

    def _compute_risk_metrics(self, context: ModelContext) -> dict[str, Any]:
        """Compute comprehensive risk metrics."""
        risk_metrics = {}

        # Component-level risk assessment
        component_risks = self._assess_component_risks(context)
        risk_metrics["component_risks"] = component_risks

        # System-level risk aggregation
        system_risks = self._assess_system_risks(context, component_risks)
        risk_metrics["system_risks"] = system_risks

        # Facility-level risk summary
        facility_risk = self._assess_facility_risk(context, system_risks)
        risk_metrics["facility_risk"] = facility_risk

        # Risk rankings and priorities
        priorities = self._compute_risk_priorities(component_risks, system_risks)
        risk_metrics["risk_priorities"] = priorities

        return risk_metrics

    def _assess_component_risks(
        self, context: ModelContext
    ) -> dict[int, dict[str, float]]:
        """Assess risk for each component."""
        component_risks = {}
        n_components = len(context.states)

        for comp_id in range(n_components):
            # Basic failure probability based on condition
            condition = context.states[comp_id]
            failure_probability = max(
                0.01, (10 - condition) / 10.0
            )  # Worse condition = higher failure prob

            # Get component metadata for impact assessment
            try:
                importance = (
                    context.metadata.get_component_attribute(comp_id, "importance")
                    or 1.0
                )
                criticality = (
                    context.metadata.get_component_attribute(comp_id, "criticality")
                    or "medium"
                )

                # Impact scoring based on criticality and importance
                impact_scores = {
                    "low": 1.0,
                    "medium": 2.0,
                    "high": 3.0,
                    "critical": 4.0,
                }
                impact = impact_scores.get(criticality, 2.0) * importance

                # Overall risk = probability × impact
                risk_score = failure_probability * impact / 4.0  # Normalize to 0-1

                # Adjust for cascading failure potential
                subsystem = self.get_component_group(comp_id, "subsystem")
                if subsystem:
                    redundancy = self.get_group_property(
                        subsystem, "subsystem", "redundancy"
                    )
                    if not redundancy:  # No redundancy = higher cascading risk
                        risk_score *= self.cascading_multiplier

                # Risk classification
                if risk_score >= self.risk_threshold_critical:
                    risk_level = "critical"
                elif risk_score >= self.risk_threshold_high:
                    risk_level = "high"
                else:
                    risk_level = "medium" if risk_score >= 0.3 else "low"

                component_risks[comp_id] = {
                    "failure_probability": failure_probability,
                    "impact": impact,
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "condition": condition,
                }

            except (KeyError, AttributeError):
                # Default risk assessment if metadata unavailable
                component_risks[comp_id] = {
                    "failure_probability": failure_probability,
                    "impact": 2.0,
                    "risk_score": failure_probability * 0.5,
                    "risk_level": "medium",
                    "condition": condition,
                }

        return component_risks

    def _assess_system_risks(
        self, context: ModelContext, component_risks: dict[int, dict[str, float]]
    ) -> dict[str, dict[str, Any]]:
        """Assess risk at system level."""
        system_risks = {}

        if "system" not in self.groups:
            return system_risks

        for system_id, system_info in self.groups["system"].items():
            components = list(system_info["components"])
            if not components:
                continue

            # Aggregate component risks
            system_failure_probs = [
                component_risks[cid]["failure_probability"]
                for cid in components
                if cid in component_risks
            ]
            system_risk_scores = [
                component_risks[cid]["risk_score"]
                for cid in components
                if cid in component_risks
            ]

            if not system_risk_scores:
                continue

            # System failure probability (at least one critical component fails)
            # For simplicity, use maximum failure probability
            system_failure_prob = (
                max(system_failure_probs) if system_failure_probs else 0.0
            )

            # System impact based on business criticality
            business_criticality = (
                self.get_group_property(system_id, "system", "business_criticality")
                or "medium"
            )
            criticality_multipliers = {
                "low": 0.5,
                "medium": 1.0,
                "high": 1.5,
                "critical": 2.0,
            }

            # Weighted risk score
            avg_component_risk = np.mean(system_risk_scores)
            system_risk_score = (
                avg_component_risk * criticality_multipliers[business_criticality]
            )

            # Recovery time impact
            recovery_time = (
                self.get_group_property(system_id, "system", "recovery_time") or 24.0
            )  # Default 24 hours
            recovery_impact = min(
                2.0, recovery_time / 24.0
            )  # Normalize recovery time impact

            final_system_risk = system_risk_score * recovery_impact

            system_risks[system_id] = {
                "failure_probability": system_failure_prob,
                "risk_score": final_system_risk,
                "business_criticality": business_criticality,
                "recovery_time": recovery_time,
                "component_count": len(components),
                "high_risk_components": len(
                    [
                        cid
                        for cid in components
                        if cid in component_risks
                        and component_risks[cid]["risk_level"] in ["high", "critical"]
                    ]
                ),
            }

        return system_risks

    def _assess_facility_risk(
        self, context: ModelContext, system_risks: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """Assess overall facility risk."""
        if not system_risks:
            return {"overall_risk": 0.0, "risk_level": "low"}

        system_risk_scores = [info["risk_score"] for info in system_risks.values()]

        # Overall facility risk (maximum system risk)
        overall_risk = max(system_risk_scores)

        # Risk distribution
        risk_distribution = {
            "critical_systems": len(
                [s for s in system_risk_scores if s >= self.risk_threshold_critical]
            ),
            "high_risk_systems": len(
                [s for s in system_risk_scores if s >= self.risk_threshold_high]
            ),
            "total_systems": len(system_risk_scores),
        }

        # Facility risk level
        if overall_risk >= self.risk_threshold_critical:
            facility_risk_level = "critical"
        elif overall_risk >= self.risk_threshold_high:
            facility_risk_level = "high"
        else:
            facility_risk_level = "medium" if overall_risk >= 0.3 else "low"

        return {
            "overall_risk": overall_risk,
            "risk_level": facility_risk_level,
            "risk_distribution": risk_distribution,
            "avg_system_risk": np.mean(system_risk_scores),
        }

    def _compute_risk_priorities(
        self,
        component_risks: dict[int, dict[str, float]],
        system_risks: dict[str, dict[str, Any]],
    ) -> dict[str, list[int]]:
        """Compute maintenance priorities based on risk."""
        # Sort components by risk score
        sorted_components = sorted(
            component_risks.items(), key=lambda x: x[1]["risk_score"], reverse=True
        )

        # Group into priority levels
        priorities = {
            "immediate": [],  # Critical risk
            "urgent": [],  # High risk
            "scheduled": [],  # Medium risk
            "routine": [],  # Low risk
        }

        for comp_id, risk_info in sorted_components:
            risk_level = risk_info["risk_level"]
            if risk_level == "critical":
                priorities["immediate"].append(comp_id)
            elif risk_level == "high":
                priorities["urgent"].append(comp_id)
            elif risk_level == "medium":
                priorities["scheduled"].append(comp_id)
            else:
                priorities["routine"].append(comp_id)

        return priorities

    def get_maintenance_recommendations(
        self, context: ModelContext
    ) -> dict[str, list[str]]:
        """Generate maintenance recommendations based on risk assessment."""
        metrics = self.compute(context)

        recommendations = {
            "immediate_actions": [],
            "preventive_actions": [],
            "monitoring_actions": [],
            "strategic_actions": [],
        }

        if "risk_priorities" in metrics:
            priorities = metrics["risk_priorities"]

            # Immediate actions for critical risk components
            for comp_id in priorities.get("immediate", []):
                recommendations["immediate_actions"].append(
                    f"Component {comp_id}: Emergency inspection and repair required"
                )

            # Preventive actions for high risk components
            for comp_id in priorities.get("urgent", []):
                recommendations["preventive_actions"].append(
                    f"Component {comp_id}: Schedule preventive maintenance within 1 week"
                )

            # Monitoring for medium risk
            for comp_id in priorities.get("scheduled", []):
                recommendations["monitoring_actions"].append(
                    f"Component {comp_id}: Increase monitoring frequency"
                )

        if "system_risks" in metrics:
            system_risks = metrics["system_risks"]
            for system_id, risk_info in system_risks.items():
                if risk_info["risk_score"] >= self.risk_threshold_critical:
                    recommendations["strategic_actions"].append(
                        f"System {system_id}: Consider redundancy improvements and backup systems"
                    )

        return recommendations

    def reset(self, context: ModelContext | None = None):
        """Reset risk calculations and cache."""
        self.risk_cache.clear()


if __name__ == "__main__":
    from infralib.models.metadata import SimpleMetadata

    # Setup risk-based hierarchy
    risk_hierarchy = RiskBasedHierarchy(
        risk_threshold_critical=0.7,
        risk_threshold_high=0.5,
        failure_impact_weight=0.4,
        cascading_failure_multiplier=1.8,
    )

    # Setup metadata with risk-relevant attributes
    metadata = SimpleMetadata()

    # Add components with different risk profiles
    components_data = [
        {
            "id": 0,
            "name": "Main Pump",
            "importance": 3.0,
            "criticality": "critical",
            "type": "pump",
        },
        {
            "id": 1,
            "name": "Backup Pump",
            "importance": 2.0,
            "criticality": "high",
            "type": "pump",
        },
        {
            "id": 2,
            "name": "Control Valve",
            "importance": 2.5,
            "criticality": "high",
            "type": "valve",
        },
        {
            "id": 3,
            "name": "Pressure Sensor",
            "importance": 1.5,
            "criticality": "medium",
            "type": "sensor",
        },
        {
            "id": 4,
            "name": "Flow Meter",
            "importance": 1.0,
            "criticality": "low",
            "type": "meter",
        },
        {
            "id": 5,
            "name": "Emergency Valve",
            "importance": 3.5,
            "criticality": "critical",
            "type": "valve",
        },
    ]

    for comp_data in components_data:
        metadata.add_component(comp_data["id"], comp_data)

    # Setup hierarchy structure
    assignments = [
        {
            "component": "comp_0",
            "subsystem": "primary_pumping",
            "system": "water_system",
            "facility": "plant_a",
        },
        {
            "component": "comp_1",
            "subsystem": "backup_pumping",
            "system": "water_system",
            "facility": "plant_a",
        },
        {
            "component": "comp_2",
            "subsystem": "flow_control",
            "system": "water_system",
            "facility": "plant_a",
        },
        {
            "component": "comp_3",
            "subsystem": "monitoring",
            "system": "control_system",
            "facility": "plant_a",
        },
        {
            "component": "comp_4",
            "subsystem": "monitoring",
            "system": "control_system",
            "facility": "plant_a",
        },
        {
            "component": "comp_5",
            "subsystem": "safety",
            "system": "safety_system",
            "facility": "plant_a",
        },
    ]

    for i, assignment in enumerate(assignments):
        risk_hierarchy.assign_component(i, assignment)

    # Set system properties
    risk_hierarchy.set_group_property(
        "primary_pumping", "subsystem", "redundancy", False
    )
    risk_hierarchy.set_group_property("backup_pumping", "subsystem", "redundancy", True)
    risk_hierarchy.set_group_property("safety", "subsystem", "redundancy", False)

    risk_hierarchy.set_group_property(
        "water_system", "system", "business_criticality", "critical"
    )
    risk_hierarchy.set_group_property(
        "water_system", "system", "recovery_time", 4.0
    )  # 4 hours
    risk_hierarchy.set_group_property(
        "control_system", "system", "business_criticality", "high"
    )
    risk_hierarchy.set_group_property(
        "control_system", "system", "recovery_time", 8.0
    )  # 8 hours
    risk_hierarchy.set_group_property(
        "safety_system", "system", "business_criticality", "critical"
    )
    risk_hierarchy.set_group_property(
        "safety_system", "system", "recovery_time", 1.0
    )  # 1 hour

    # Simulate different condition scenarios
    scenarios = [
        ("Normal Operation", np.array([8, 9, 7, 8, 9, 8])),
        ("Degraded Condition", np.array([4, 8, 5, 6, 8, 7])),
        ("Critical Situation", np.array([2, 3, 8, 7, 8, 1])),
    ]

    for scenario_name, states in scenarios:
        print(f"\n=== {scenario_name} ===")

        context = ModelContext(
            states=states, hierarchy=risk_hierarchy, metadata=metadata
        )

        # Compute risk metrics
        metrics = risk_hierarchy.compute(context)

        print(f"Component conditions: {states}")

        # Display component risks
        if "component_risks" in metrics:
            print("\nComponent Risk Assessment:")
            for comp_id, risk_info in metrics["component_risks"].items():
                comp_name = components_data[comp_id]["name"]
                print(
                    f"  {comp_name} (ID {comp_id}): {risk_info['risk_level'].upper()} risk "
                    f"(score: {risk_info['risk_score']:.3f})"
                )

        # Display system risks
        if "system_risks" in metrics:
            print("\nSystem Risk Assessment:")
            for system_id, risk_info in metrics["system_risks"].items():
                print(
                    f"  {system_id}: Risk score {risk_info['risk_score']:.3f}, "
                    f"{risk_info['high_risk_components']}/{risk_info['component_count']} high-risk components"
                )

        # Display facility risk
        if "facility_risk" in metrics:
            facility_risk = metrics["facility_risk"]
            print(
                f"\nFacility Risk: {facility_risk['risk_level'].upper()} "
                f"(score: {facility_risk['overall_risk']:.3f})"
            )

            dist = facility_risk["risk_distribution"]
            print(
                f"Risk Distribution: {dist['critical_systems']} critical, "
                f"{dist['high_risk_systems']} high-risk out of {dist['total_systems']} systems"
            )

        # Display maintenance recommendations
        recommendations = risk_hierarchy.get_maintenance_recommendations(context)
        if any(recommendations.values()):
            print("\nMaintenance Recommendations:")
            for category, actions in recommendations.items():
                if actions:
                    print(f"  {category.replace('_', ' ').title()}:")
                    for action in actions[:3]:  # Show first 3 recommendations
                        print(f"    - {action}")

    print("\n=== Risk-Based Priority Ranking ===")
    context = ModelContext(
        states=scenarios[2][1], hierarchy=risk_hierarchy, metadata=metadata
    )  # Critical situation
    metrics = risk_hierarchy.compute(context)

    if "risk_priorities" in metrics:
        priorities = metrics["risk_priorities"]
        print("Maintenance Priority Ranking:")
        for level, comp_ids in priorities.items():
            if comp_ids:
                comp_names = [components_data[cid]["name"] for cid in comp_ids]
                print(f"  {level.title()}: {', '.join(comp_names)}")

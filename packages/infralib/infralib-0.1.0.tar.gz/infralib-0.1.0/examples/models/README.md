# Custom Model Examples

This directory contains examples showing how to create custom models that leverage the unified InfraLib architecture with model dependencies.

## Examples Overview

### 1. `custom_models_with_dependencies.py`
**Basic custom models showing dependency patterns**
- `HierarchyAwareCost`: Cost model that adjusts prices based on system criticality
- `MetadataBasedDynamics`: Dynamics that vary by environmental conditions
- `IntegratedCostModel`: Complex cost model using all available dependencies

**Key Concepts:**
- Using `get_required_models()` to declare dependencies
- Accessing other models through `ModelContext`
- Graceful handling of missing dependencies

### 2. `adaptive_budget_model.py`
**Advanced budget model that adapts to system health**
- Monitors hierarchy-based system health metrics
- Automatically adjusts budget allocation based on emergencies
- Provides smooth budget transitions and health bonuses
- Includes emergency detection and response

**Features:**
- Emergency budget multipliers for critical systems
- Health-based budget bonuses for well-maintained systems
- Smooth budget transitions to avoid dramatic changes
- System-level health assessment and tracking

### 3. `predictive_dynamics_model.py`
**Machine learning-inspired dynamics with deterioration forecasting**
- Uses metadata features (age, usage, environment) for deterioration prediction
- Learns from component history to improve predictions
- Provides deterioration forecasting capabilities
- Adaptive repair effectiveness based on component characteristics

**Advanced Features:**
- Historical pattern learning and trend analysis
- Multi-factor deterioration rate calculation
- Predictive maintenance recommendations
- Material and environment-specific deterioration models

### 4. `risk_based_hierarchy.py`
**Comprehensive risk assessment and management system**
- Computes component, system, and facility-level risk scores
- Risk-based maintenance priority ranking
- Cascading failure risk assessment
- Automated maintenance recommendations

**Risk Assessment Features:**
- Multi-level risk aggregation (component → system → facility)
- Business impact and recovery time considerations
- Risk priority classification and maintenance scheduling
- Strategic recommendations for system improvements

## Usage Patterns

### Basic Custom Model Template
```python
class MyCustomModel(BaseModelType):
    @classmethod
    def get_required_models(cls):
        return ["hierarchy", "metadata"]  # Declare what you need

    def _compute_**(self, context):
        # Access dependencies
        hierarchy = context.hierarchy
        metadata = context.metadata

        # Your custom logic here
        return results
```

### Accessing Dependencies
```python
# In your compute method:
if context.hierarchy:
    system = context.hierarchy.get_component_group(comp_id, "system")
    criticality = context.hierarchy.get_group_property(system, "system", "criticality")

if context.metadata:
    importance = context.metadata.get_component_attribute(comp_id, "importance")
    age = context.metadata.get_component_attribute(comp_id, "age")
```

### Model Integration
```python
# Create all your models
dynamics = MyCustomDynamics()
cost = MyCustomCost()
budget = MyAdaptiveBudget()
hierarchy = MyRiskHierarchy()
metadata = MyMetadata()

# Create context with all models
context = ModelContext(
    states=states,
    actions=actions,
    dynamics=dynamics,
    cost=cost,
    budget=budget,
    hierarchy=hierarchy,
    metadata=metadata
)

# Models can now access each other
next_states = dynamics.compute(context)  # May use metadata
costs = cost.compute(context)           # May use hierarchy + dynamics
budget_info = budget.compute(context)   # May use hierarchy for health assessment
```

## Running Examples

Each example can be run independently:

```bash
cd examples/models

# Basic dependency patterns
python custom_models_with_dependencies.py

# Adaptive budget allocation
python adaptive_budget_model.py

# Predictive deterioration modeling
python predictive_dynamics_model.py

# Risk-based maintenance prioritization
python risk_based_hierarchy.py
```

## Key Design Principles

1. **Declare Dependencies**: Use `get_required_models()` to explicitly state what your model needs
2. **Fail Gracefully**: Check if dependencies exist before using them
3. **Context-Driven**: All models receive the same `ModelContext` with full system state
4. **Consistent Interface**: All models use `compute(context)` method
5. **Rich Information**: Models can access states, actions, time, history, and other models

## Extension Ideas

- **Weather-Aware Dynamics**: Use weather metadata to adjust deterioration
- **Economic Cost Models**: Adjust costs based on market conditions and supply chains
- **Regulatory Compliance**: Budget models that ensure compliance spending
- **Network Effect Models**: Dynamics that model component interdependencies
- **Optimization-Based Budget**: Budget allocation using mathematical optimization
- **Machine Learning Integration**: Models that learn from historical data patterns

# Simulator Examples

This directory contains examples demonstrating the enhanced `Simulator` class with model dependencies and rich terminal displays.

## Examples Overview

### 1. `basic_simulation.py`
**Simple simulation with rich status displays**

Demonstrates:
- Basic simulator setup with standard models
- Rich terminal status displays during simulation
- Simple maintenance policy implementation
- Performance metrics collection

Features:
- 20 components with random initial states
- Policy: Replace failed, repair poor condition, periodic inspections
- Real-time rich status updates
- Final performance analysis

```bash
python basic_simulation.py
```

### 2. `advanced_with_dependencies.py`
**Advanced simulation using model dependencies**

Demonstrates:
- Model dependency system with `ModelContext`
- Hierarchy-aware cost models
- Metadata-based dynamics
- Adaptive budget allocation
- Risk-based maintenance policies

Features:
- 12 components across 3 systems (1 critical, 2 normal)
- Environmental metadata (indoor, coastal, industrial)
- Emergency budget activation for critical systems
- System-level health monitoring and reporting

```bash
python advanced_with_dependencies.py
```

### 3. `batch_policy_evaluation.py`
**Policy comparison and evaluation**

Demonstrates:
- Batch policy rollout evaluation
- Statistical policy comparison
- Multiple maintenance strategies
- Performance visualization

Features:
- 4 different maintenance policies (Reactive, Preventive, Balanced, Aggressive)
- Monte Carlo evaluation with multiple rollouts
- Statistical analysis and rankings
- Matplotlib visualization (if available)

```bash
python batch_policy_evaluation.py
```

## Key Features Demonstrated

### Model Dependencies
- **ModelContext**: Unified context passed between models
- **Inter-model communication**: Models can access and use other models
- **Dependency validation**: Automatic checking of required dependencies
- **Custom models**: Using models from `examples/models/`

### Rich Terminal Displays
- **Status tables**: Real-time component and system metrics
- **Progress bars**: Budget usage visualization
- **Color coding**: Visual indicators for system health
- **Hierarchical metrics**: System and facility-level aggregations

### Advanced Policies
- **Risk-based**: Prioritize critical systems and components
- **Metadata-aware**: Use environmental and age information
- **Budget-conscious**: Adapt to budget constraints and emergencies
- **Performance-optimized**: Balance cost and reliability

### Performance Analysis
- **Comprehensive metrics**: Cost, failures, condition deterioration
- **Historical tracking**: Complete simulation history
- **Statistical evaluation**: Multi-rollout analysis with confidence intervals
- **Comparative analysis**: Policy ranking and visualization

## Model Dependencies Used

### From `infralib.models`:
- `MarkovDynamics`: Basic state transition dynamics
- `SimpleCost`: Standard maintenance cost calculations
- `FixedBudget`: Fixed budget constraints
- `SimpleHierarchy`: Component hierarchy management
- `SimpleMetadata`: Component attribute storage

### From `examples/models`:
- `HierarchyAwareCost`: Cost model using hierarchy for critical system pricing
- `MetadataBasedDynamics`: Dynamics using environmental and age factors
- `AdaptiveBudget`: Budget that adjusts based on system health

## Running the Examples

Each example is self-contained and can be run independently:

```bash
cd examples/simulator

# Basic simulation with rich displays
python basic_simulation.py

# Advanced simulation with model dependencies
python advanced_with_dependencies.py

# Policy evaluation and comparison
python batch_policy_evaluation.py
```

## Requirements

- `numpy` - Numerical computations
- `rich` - Terminal formatting and displays
- `matplotlib` (optional) - Policy comparison plots
- InfraLib models and dependencies

## Customization

### Adding New Policies
```python
def my_custom_policy(obs: np.ndarray) -> np.ndarray:
    # Extract states and inspection times
    n_components = len(obs) // 2
    states = obs[:n_components] * 10
    time_since_inspection = obs[n_components:] * 100

    actions = np.zeros(n_components, dtype=int)
    # Implement your policy logic here

    return actions
```

### Creating Custom Models
See `examples/models/` for examples of creating models with dependencies:

```python
class MyCustomModel(BaseModelType):
    @classmethod
    def get_required_models(cls):
        return ["hierarchy", "metadata"]  # Declare dependencies

    def compute(self, context):
        # Access other models via context
        hierarchy = context.hierarchy
        metadata = context.metadata
        # Implement your logic
        return results
```

### Rich Display Customization
```python
# Enable/disable rich displays
simulator = Simulator(..., rich_display=True)

# Control display during simulation
states, info = simulator.step(actions, display_status=False)

# Create custom status displays
panel, progress = simulator.create_status_display(info)
```

## Expected Output

When running these examples, you'll see:

1. **Rich status tables** with component counts, condition statistics, and failure information
2. **Budget usage progress bars** showing remaining budget and utilization
3. **Hierarchical system metrics** for infrastructure organization
4. **Emergency notifications** when adaptive budgets activate
5. **Performance summaries** with comprehensive statistics
6. **Policy comparison results** and visualizations

The rich displays provide real-time insights into the simulation progress and system health, making it easy to understand maintenance dynamics and policy effectiveness.

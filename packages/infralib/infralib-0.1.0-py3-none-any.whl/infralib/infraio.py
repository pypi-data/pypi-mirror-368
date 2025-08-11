import csv

import yaml


def load_parameters(config_file, components_file):
    """
    Loads parameters from the given CSV and YAML files.

    Args:
        config_file (str): Path to the configuration YAML file.
        components_file (str): Path to the components CSV file.

    Returns:
        dict: A dictionary containing all the parameters needed for initialization.
    """
    # Read config.yaml
    with open(config_file) as f:
        config = yaml.safe_load(f)

    # Initialize lists to store component parameters
    component_types = []
    num_instances = []
    failure_conditions = []
    inspect_costs = []
    replace_costs = []
    repair_cost_params = []
    importance_scores = []
    dynamics_scale_means = []
    dynamics_scale_sds = []
    dynamics_shape_means = []
    dynamics_shape_sds = []

    # Read components.csv
    with open(components_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            component_types.append(row["component_type"])
            num_instances.append(int(row["num_instances"]))
            failure_conditions.append(float(row["failure_condition"]))
            inspect_costs.append(float(row["inspect_cost"]))
            replace_costs.append(float(row["replace_cost"]))
            repair_cost_params.append(float(row["repair_cost_param"]))
            importance_scores.append(float(row["importance_score"]))
            dynamics_scale_means.append(float(row["dynamics_scale_mean"]))
            dynamics_scale_sds.append(float(row["dynamics_scale_sd"]))
            dynamics_shape_means.append(float(row["dynamics_shape_mean"]))
            dynamics_shape_sds.append(float(row["dynamics_shape_sd"]))

    # Build component_ids
    component_ids = []
    for t, num in zip(component_types, num_instances, strict=False):
        for i in range(num):
            component_ids.append(f"{t}{i}")

    # Compile all parameters into a dictionary
    params = {
        "simulation_seed": config["simulation_seed"],
        "initial_budget": config["initial_budget"],
        "component_types": component_types,
        "num_components_per_type": num_instances,
        "component_ids": component_ids,
        "failure_conditions": failure_conditions,
        "inspect_costs": inspect_costs,
        "replace_costs": replace_costs,
        "repair_cost_params": repair_cost_params,
        "importance_scores": importance_scores,
        "dynamics_scale_means": dynamics_scale_means,
        "dynamics_scale_sds": dynamics_scale_sds,
        "dynamics_shape_means": dynamics_shape_means,
        "dynamics_shape_sds": dynamics_shape_sds,
        "dynamics_model_params": config["dynamics_model"],
        "cost_model_params": config["cost_model"],
        "budget_model_params": config["budget_model"],
    }

    return params

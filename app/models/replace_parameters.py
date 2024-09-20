def replace_parameters(workflow_data):
    # Extract the defined parameters
    defined_parameters = workflow_data.get('parameters', {})
    
    def replace_param_value(param_value):
        """Replace the parameter reference with the actual value if it exists."""
        if isinstance(param_value, str) and param_value.startswith("$.parameters."):
            # Extract the referenced parameter name
            ref_param_name = param_value.split('.')[-1]  # Get the last part after '$.parameters.'
            
            # Replace the reference with the actual value if it exists in defined parameters
            if ref_param_name in defined_parameters:
                return defined_parameters[ref_param_name]
            else:
                return param_value  # Keep original if no replacement found
        return param_value  # Return original if not a parameter reference

    def replace_parameters_in_step(step):
        # Replace the parameters of the current step
        step_params = step.get('parameters', {})
        for param_name, param_value in step_params.items():
            step_params[param_name] = replace_param_value(param_value)

        # Recursively replace parameters in nested steps for "ParallelExecution"
        if step.get('type') == 'ParallelExecution':
            for sub_step in step.get('steps', []):
                replace_parameters_in_step(sub_step)

    # Iterate over all steps in the workflow and apply replacements
    for step in workflow_data['workflow']:
        replace_parameters_in_step(step)

    return workflow_data

def validate_parameters(workflow_data):
    # Extract the defined parameters
    defined_parameters = workflow_data.get('parameters', {})
    
    # Store validation results
    validation_results = []

    def check_parameters(step, parent_name=""):
        # Check the parameters of the current step
        step_params = step.get('parameters', {})
        
        for param_name, param_value in step_params.items():
            # Only validate parameter references starting with '$.'
            if isinstance(param_value, str) and param_value.startswith("$.parameters."):
                # Extract the referenced parameter name
                ref_param_name = param_value.split('.')[-1]  # Get the last part after '$.parameters.'
                
                # Check if the referenced parameter exists in defined_parameters
                if ref_param_name not in defined_parameters:
                    validation_results.append({
                        'step': f"{parent_name} -> {step.get('name', 'Unknown step')}",
                        'parameter': param_name,
                        'reference': param_value,
                        'error': 'Undefined parameter reference'
                    })

        # Recursively check nested steps for "ParallelExecution"
        if step.get('type') == 'ParallelExecution':
            for sub_step in step.get('steps', []):
                check_parameters(sub_step, step.get('name'))

    for step in workflow_data['workflow']:
        check_parameters(step)

    return validation_results

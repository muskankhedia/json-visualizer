# def format_parameters(params):
#     """Format parameters to display in the flowchart boxes."""
#     return "\n".join([f"{k}: {v}" for k, v in params.items()])

def format_parameters(params, root_parameters):
    """Format parameters to display in the flowchart boxes."""
    formatted_params = []
    
    for k, v in params.items():
        # If the parameter is referencing root parameters (starts with $.parameters)
        if isinstance(v, str) and v.startswith("$.parameters."):
            param_key = v.split("$.parameters.")[-1]
            
            # Check if the referenced parameter exists
            if param_key in root_parameters:
                formatted_value = f"{k}: {root_parameters[param_key]}"
            else:
                # Highlight missing parameter in red
                formatted_value = f'<font color="red">{k}: {v} (MISSING)</font>'
        else:
            formatted_value = f"{k}: {v}"
        
        formatted_params.append(formatted_value)
    
    return "<br/>".join(formatted_params)

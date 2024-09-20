def format_parameters(params):
    """Format parameters to display in the flowchart boxes."""
    return "\n".join([f"{k}: {v}" for k, v in params.items()])

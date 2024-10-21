import graphviz
from .utils import format_parameters

def draw_workflow_chart(workflow_data):
    """
    Draw the flowchart with enhanced visualization for sequential and parallel steps.
    Consolidated steps are displayed in a more structured and readable manner.
    """
    dot = graphviz.Digraph(format='png', graph_attr={'rankdir': 'TB'}, node_attr={'shape': 'rect'}, strict=True)
    
    previous_step = None  # Tracks the previous step in sequential steps
    parallel_end = None   # Tracks parallel end nodes for reconnection
    root_parameters = workflow_data.get('parameters', {})  # Root-level parameters
    
    # Iterate over the main workflow steps
    for i, step in enumerate(workflow_data['workflow']):
        step_name = step['name']  # Get the name of the step
        
        # Format parameters, if present
        if 'parameters' in step:
            parameters = step['parameters']
            params_str = format_parameters(parameters, root_parameters)
        else:
            params_str = ""
        
        # Handle Parallel Execution steps
        if step['type'] == 'ParallelExecution':
            parallel_group = []  # Will store names of parallel steps
            type_to_steps = {}  # Group sub-steps by type
            
            # Iterate through each sub-step in the parallel execution
            for sub_step in step['steps']:
                sub_step_type = sub_step['type']
                sub_step_name = sub_step['name']
                
                # Safely get 'parameters', or assign an empty dictionary if missing
                sub_parameters = sub_step.get('parameters', {})
                sub_params_str = format_parameters(sub_parameters, root_parameters)

                # Group sub-steps by their type
                if sub_step_type not in type_to_steps:
                    type_to_steps[sub_step_type] = []
                
                # Append the sub-step name and parameters for each type group
                type_to_steps[sub_step_type].append((sub_step_name, sub_params_str))
            
            # For each group of steps of the same type, create a consolidated box
            for step_type, steps in type_to_steps.items():
                with dot.subgraph() as sub:
                    sub.attr(rank='same')  # Ensure steps are ranked the same

                    # Create a more readable format using bullet points and indentation
                    formatted_steps = "<br align='left'/>".join([
                        f"• <b>{step_name}</b>: {params}" if params else f"• <b>{step_name}</b>"
                        for step_name, params in steps
                    ])
                    
                    # Create a node with the consolidated steps and parameters
                    sub.node(step_type, label=f'<<b>{step_type}</b><br align="left"/>{formatted_steps}>', shape='rect')
                    parallel_group.append(step_type)  # Add the step type to the parallel group
            
            # Connect previous step to each of the parallel nodes
            if previous_step:
                for parallel_step in parallel_group:
                    dot.edge(previous_step, parallel_step)
            
            # Mark the end of this parallel execution for later connections
            parallel_end = parallel_group
            previous_step = None  # Reset previous step for the next sequential steps

        else:  # Handle Sequential steps
            # Create a node for the current sequential step with improved formatting
            formatted_step = f'<<b>{step_name}</b><br align="left"/>{params_str}>'
            dot.node(step_name, label=formatted_step, shape='rect')
            
            # If there was a parallel execution before this step, connect the parallel end to this step
            if parallel_end:
                for parallel_step in parallel_end:
                    dot.edge(parallel_step, step_name)
                parallel_end = None  # Reset parallel end after use
            
            # Connect the previous sequential step to the current step
            if previous_step:
                dot.edge(previous_step, step_name)
            
            # Set the current step as the previous step for the next iteration
            previous_step = step_name

    return dot

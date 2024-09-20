import graphviz
from .utils import format_parameters

def draw_workflow_chart(workflow_data):
    """Draw the flowchart with support for sequential and parallel steps."""
    dot = graphviz.Digraph(format='png', graph_attr={'rankdir': 'TB'}, node_attr={'shape': 'rect'}, strict=True)
    
    previous_step = None
    parallel_end = None
    root_parameters = workflow_data.get('parameters', {})
    
    for i, step in enumerate(workflow_data['workflow']):
        step_name = step['name']
        
        # Handle parameters
        if 'parameters' in step:
            parameters = step['parameters']
            params_str = format_parameters(parameters, root_parameters)
        else:
            params_str = ""
        
        # Handle parallel execution
        if step['type'] == 'ParallelExecution':
            parallel_group = []
            type_to_steps = {}
            
            # Group steps by type within the parallel execution
            for sub_step in step['steps']:
                sub_step_type = sub_step['type']
                sub_step_name = sub_step['name']
                sub_parameters = sub_step['parameters']
                sub_params_str = format_parameters(sub_parameters, root_parameters)

                if sub_step_type not in type_to_steps:
                    type_to_steps[sub_step_type] = []
                
                # Add step parameters inside a single box for the same type
                type_to_steps[sub_step_type].append((sub_step_name, sub_params_str))
            
            # Create nodes for each type group and consolidate their parameters
            for step_type, steps in type_to_steps.items():
                with dot.subgraph() as sub:
                    sub.attr(rank='same')
                    combined_params = "<br/>".join([f"{step_name}:<br/>{params}" for step_name, params in steps])
                    sub.node(step_type, label=f'<<b>{step_type}</b><br/><br/>{combined_params}>', shape='rect')
                    parallel_group.append(step_type)
            
            # Connect previous step to all parallel nodes
            if previous_step:
                for parallel_step in parallel_group:
                    dot.edge(previous_step, parallel_step)
            
            # Store the end of the parallel execution for later convergence
            parallel_end = parallel_group
            previous_step = None  # Reset previous_step for next sequential steps

        else:  # Sequential steps
            dot.node(step_name, label=f'<<b>{step_name}</b><br/>{params_str}>', shape='rect')
            
            if parallel_end:
                # Connect all parallel nodes to the next sequential node
                for parallel_step in parallel_end:
                    dot.edge(parallel_step, step_name)
                parallel_end = None  # Reset after convergence

            if previous_step:
                dot.edge(previous_step, step_name)
            
            previous_step = step_name

    return dot

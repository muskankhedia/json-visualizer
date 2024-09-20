import graphviz
from .utils import format_parameters

def draw_workflow_chart(workflow_data):
    dot = graphviz.Digraph(format='png', graph_attr={'rankdir': 'TB'}, node_attr={'shape': 'rect'}, strict=True)
    
    previous_step = None
    parallel_end = None
    
    for i, step in enumerate(workflow_data['workflow']):
        step_name = step['name']
        
        if 'parameters' in step:
            parameters = step['parameters']
            params_str = format_parameters(parameters)
        else:
            params_str = ""

        if step['type'] == 'ParallelExecution':
            parallel_group = []
            type_to_steps = {}
            
            for sub_step in step['steps']:
                sub_step_type = sub_step['type']
                sub_step_name = sub_step['name']
                sub_parameters = sub_step['parameters']
                sub_params_str = format_parameters(sub_parameters)

                if sub_step_type not in type_to_steps:
                    type_to_steps[sub_step_type] = []
                
                type_to_steps[sub_step_type].append((sub_step_name, sub_params_str))
            
            for step_type, steps in type_to_steps.items():
                with dot.subgraph() as sub:
                    sub.attr(rank='same')
                    combined_params = "\n".join([f"{step_name}:\n{params}" for step_name, params in steps])
                    sub.node(step_type, label=f'{step_type}\n\n{combined_params}')
                    parallel_group.append(step_type)

            if previous_step:
                for parallel_step in parallel_group:
                    dot.edge(previous_step, parallel_step)

            parallel_end = parallel_group
            previous_step = None

        else:
            dot.node(step_name, label=f'{step_name}\n{params_str}')

            if parallel_end:
                for parallel_step in parallel_end:
                    dot.edge(parallel_step, step_name)
                parallel_end = None

            if previous_step:
                dot.edge(previous_step, step_name)
            
            previous_step = step_name

    return dot

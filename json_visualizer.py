import json
import graphviz

# Sample JSON representing workflow
workflow_json = {
    "workflow": [
        {"name": "Step 1", "type": "sequential", "parameters": {"task": "Start Process"}},
        {"name": "Step 2", "type": "parallel", "parameters": {"task": "Parallel Task 1"}},
        {"name": "Step 3", "type": "parallel", "parameters": {"task": "Parallel Task 2"}},
        {"name": "Step 4", "type": "sequential", "parameters": {"task": "End Process"}}
    ]
}

# Function to format parameters for node labels
def format_parameters(params):
    return "\n".join([f"{k}: {v}" for k, v in params.items()])

# Function to draw a vertical flowchart based on the workflow steps
def draw_vertical_workflow_chart(workflow_data):
    # Create a graph with top-to-bottom layout (rankdir=TB ensures vertical layout)
    dot = graphviz.Digraph(format='png', graph_attr={'rankdir': 'TB'}, strict=True)
    
    parallel_group = []  # To track parallel tasks
    previous_step = None
    
    for idx, step in enumerate(workflow_data['workflow']):
        step_name = step['name']
        parameters = step['parameters']
        params_str = format_parameters(parameters)
        
        # Add the step as a node in the flowchart with parameters in the label
        dot.node(step_name, label=f'{step_name}\n{params_str}')
        
        if step['type'] == 'parallel':
            parallel_group.append(step_name)
        else:
            # If there are parallel tasks, treat them vertically
            if parallel_group:
                # Create edges from the previous step to all parallel tasks
                for task in parallel_group:
                    dot.edge(previous_step, task)  # Connect previous step to all parallel tasks
                    
                # After parallel tasks, connect each to the next sequential step
                for task in parallel_group:
                    dot.edge(task, step_name)
                    
                parallel_group = []  # Reset the parallel group
                
            # Connect sequential steps in vertical order
            if previous_step:
                dot.edge(previous_step, step_name)
        
        previous_step = step_name
    
    if parallel_group:
        # Handle the case where parallel tasks are the last steps
        for task in parallel_group:
            dot.edge(previous_step, task)
    
    # Render the graph and save as an image
    dot.render('vertical_workflow_chart_with_params', format='png')
    print("Vertical flowchart with parameters generated and saved as 'vertical_workflow_chart_with_params.png'.")

# Draw the vertical flowchart for the provided workflow JSON
draw_vertical_workflow_chart(workflow_json)

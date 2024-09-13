import json
import graphviz

# Sample JSON data
json_data = '''
{
  "$schema": "abc",
  "contentVersion": "abc",
  "name": "abc",
  "description": "abc",
  "metadata": {
    "teamName": "abc",
    "tenantId": "abc",
    "revision": "abc",
    "userEmail": "abc"
  },
  "parameters": {},
  "workflow": [
    {
      "type": "abc",
      "name": "abc",
      "description": "abc",
      "group": "abc",
      "parameters": {
        "labId": "abc"
      }
    },
    {
      "type": "abc",
      "name": "abc",
      "description": "abc",
      "group": "abc",
      "parameters": {
        "Source": "abc",
        "ContainerName": "abc",
        "BlobPath": "abc",
        "Metadata": "abc"
      }
    }
  ]
}
'''

# Parse the JSON
data = json.loads(json_data)

# Create a new Graphviz graph
dot = graphviz.Digraph()

# Add top-level nodes
dot.node("schema", "$schema")
dot.node("contentVersion", "contentVersion")
dot.node("name", "name")
dot.node("description", "description")
dot.node("metadata", "metadata")
dot.node("parameters", "parameters")
dot.node("workflow", "workflow")

# Metadata fields
dot.node("teamName", "teamName")
dot.node("tenantId", "tenantId")
dot.node("revision", "revision")
dot.node("userEmail", "userEmail")

# Connect metadata fields to metadata node
dot.edge("metadata", "teamName")
dot.edge("metadata", "tenantId")
dot.edge("metadata", "revision")
dot.edge("metadata", "userEmail")

# Workflow steps
for i, step in enumerate(data["workflow"]):
    step_node = f"workflow_step_{i}"
    dot.node(step_node, f"Step {i+1}: {step['name']}")
    dot.edge("workflow", step_node)
    
    # Add fields for each workflow step
    for key, value in step.items():
        if key != "parameters":
            field_node = f"{step_node}_{key}"
            dot.node(field_node, f"{key}: {value}")
            dot.edge(step_node, field_node)
        else:
            # For parameters in each workflow step
            params_node = f"{step_node}_parameters"
            dot.node(params_node, "parameters")
            dot.edge(step_node, params_node)
            for param_key, param_value in step["parameters"].items():
                param_field_node = f"{params_node}_{param_key}"
                dot.node(param_field_node, f"{param_key}: {param_value}")
                dot.edge(params_node, param_field_node)

# Save and render the graph
dot.render('json_graph_output', format='png')

# Display the Graphviz source (optional)
print(dot.source)

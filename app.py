from flask import Flask, request, jsonify, send_file
import graphviz
import json
import io
import base64
import os

app = Flask(__name__)

def format_parameters(params):
    """Format parameters to display in the flowchart boxes."""
    return "\n".join([f"{k}: {v}" for k, v in params.items()])

def draw_workflow_chart(workflow_data):
    """Draw the flowchart with support for sequential and parallel steps."""
    dot = graphviz.Digraph(format='png', graph_attr={'rankdir': 'TB'}, node_attr={'shape': 'rect'}, strict=True)
    
    previous_step = None
    parallel_end = None
    
    for i, step in enumerate(workflow_data['workflow']):
        step_name = step['name']
        
        # Handle parameters
        if 'parameters' in step:
            parameters = step['parameters']
            params_str = format_parameters(parameters)
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
                sub_params_str = format_parameters(sub_parameters)

                if sub_step_type not in type_to_steps:
                    type_to_steps[sub_step_type] = []
                
                # Add step parameters inside a single box for the same type
                type_to_steps[sub_step_type].append((sub_step_name, sub_params_str))
            
            # Create nodes for each type group and consolidate their parameters
            for step_type, steps in type_to_steps.items():
                with dot.subgraph() as sub:
                    sub.attr(rank='same')
                    combined_params = "\n".join([f"{step_name}:\n{params}" for step_name, params in steps])
                    sub.node(step_type, label=f'{step_type}\n\n{combined_params}')
                    parallel_group.append(step_type)
            
            # Connect previous step to all parallel nodes
            if previous_step:
                for parallel_step in parallel_group:
                    dot.edge(previous_step, parallel_step)
            
            # Store the end of the parallel execution for later convergence
            parallel_end = parallel_group
            previous_step = None  # Reset previous_step for next sequential steps

        else:  # Sequential steps
            dot.node(step_name, label=f'{step_name}\n{params_str}')
            
            if parallel_end:
                # Connect all parallel nodes to the next sequential node
                for parallel_step in parallel_end:
                    dot.edge(parallel_step, step_name)
                parallel_end = None  # Reset after convergence

            if previous_step:
                dot.edge(previous_step, step_name)
            
            previous_step = step_name

    return dot

@app.route('/')
def index():
    return '''
        <html>
        <head>
            <title>Workflow Chart</title>
            <script>
                function uploadFile() {
                    var fileInput = document.getElementById('fileInput');
                    var formData = new FormData();
                    formData.append('file', fileInput.files[0]);
                    
                    fetch('/upload', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('chart').src = 'data:image/png;base64,' + data.image;
                            document.getElementById('result').style.display = 'block';
                        } else {
                            alert('Error: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                }
            </script>
        </head>
        <body>
            <h1>Upload JSON File</h1>
            <input type="file" id="fileInput" accept=".json">
            <button onclick="uploadFile()">Upload</button>
            <div id="result" style="display:none;">
                <h2>Workflow Chart:</h2>
                <img id="chart" src="" alt="Workflow Chart">
            </div>
        </body>
        </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})

    if file and file.filename.endswith('.json'):
        json_data = json.load(file)
        dot = draw_workflow_chart(json_data)

        img_stream = io.BytesIO(dot.pipe(format='png'))
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

        return jsonify({'success': True, 'image': img_base64})
    else:
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload a .json file.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Default to port 8000
    app.run(host='0.0.0.0', port=port, debug=True)

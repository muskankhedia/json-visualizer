from flask import Flask, request, jsonify, render_template_string, send_file
import graphviz
import json
import io
import base64
import os
import logging

app = Flask(__name__)

def format_parameters(params):
    return "\n".join([f"{k}: {v}" for k, v in params.items()])

def draw_vertical_workflow_chart(workflow_data):
    dot = graphviz.Digraph(format='png', graph_attr={'rankdir': 'TB'}, strict=True)

    def format_parameters(params):
        return "\n".join([f"{k}: {v}" for k, v in params.items()])

    def consolidate_parallel_steps(steps):
        """
        Consolidates steps with the same type within parallel execution.
        Returns a list of consolidated steps.
        """
        consolidated = {}
        
        for step in steps:
            step_type = step['type']
            if step_type not in consolidated:
                consolidated[step_type] = {
                    'name': step_type,
                    'parameters': step['parameters'].copy(),
                    'description': step.get('description', ''),
                    'group': step.get('group', ''),
                }
            else:
                # If the type already exists, merge the parameters
                for k, v in step['parameters'].items():
                    consolidated[step_type]['parameters'][k] = v
        
        return list(consolidated.values())

    def add_step(dot, step, parent=None):
        step_name = step['name']
        parameters = step['parameters']
        params_str = format_parameters(parameters)

        # Create a rectangular node for the current step
        dot.node(step_name, label=f'{step_name}\n{params_str}', shape='box', style='rounded')

        # If there's a parent step, connect it to the current step
        if parent:
            dot.edge(parent, step_name)
        
        # Handle parallel steps
        if 'steps' in step and step['type'] == 'ParallelExecution':
            # Consolidate parallel steps with the same type
            consolidated_steps = consolidate_parallel_steps(step['steps'])

            # Create a dummy node for consolidation after parallel execution
            parallel_end = f"parallel_end_{step_name}"
            dot.node(parallel_end, shape="point", width="0.1")

            # Keep track of all consolidated steps
            parallel_group = []
            for sub_step in consolidated_steps:
                # Use the consolidated step type as the node name
                sub_step_name = sub_step['name']
                sub_params_str = format_parameters(sub_step['parameters'])
                dot.node(sub_step_name, label=f'{sub_step_name}\n{sub_params_str}', shape='box', style='rounded')

                # Connect each consolidated parallel step to the parent (start of parallel block)
                dot.edge(step_name, sub_step_name)
                parallel_group.append(sub_step_name)

            # After processing parallel steps, connect all parallel steps to the dummy node
            for task in parallel_group:
                dot.edge(task, parallel_end)

            # Return the dummy node as the new parent for the next sequential step
            return parallel_end
        else:
            return step_name

    # Iterate over the workflow and add each step
    previous_step = None
    for step in workflow_data['workflow']:
        if step['type'] == 'ParallelExecution':
            # For ParallelExecution, process the steps inside and return the last step
            previous_step = add_step(dot, step, previous_step)
        else:
            # For normal steps, process them sequentially
            previous_step = add_step(dot, step, previous_step)

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
                            // Store JSON data in a variable to allow editing
                            window.workflowData = data.workflow;
                            updateParametersForm(data.workflow);
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

                function updateParametersForm(workflow) {
                    var form = document.getElementById('parametersForm');
                    form.innerHTML = '';
                    workflow.workflow.forEach((step, index) => {
                        var stepDiv = document.createElement('div');
                        stepDiv.innerHTML = `<h3>${step.name}</h3>`;
                        Object.keys(step.parameters).forEach(param => {
                            var input = document.createElement('input');
                            input.type = 'text';
                            input.name = `param_${index}_${param}`;
                            input.value = step.parameters[param];
                            stepDiv.appendChild(document.createTextNode(`${param}: `));
                            stepDiv.appendChild(input);
                            stepDiv.appendChild(document.createElement('br'));
                        });
                        form.appendChild(stepDiv);
                    });
                    var submitButton = document.createElement('button');
                    submitButton.textContent = 'Regenerate Chart';
                    submitButton.onclick = regenerateChart;
                    form.appendChild(submitButton);
                }

                function regenerateChart() {
                    var formData = new FormData();
                    window.workflowData.workflow.forEach((step, index) => {
                        Object.keys(step.parameters).forEach(param => {
                            var value = document.querySelector(`input[name="param_${index}_${param}"]`).value;
                            window.workflowData.workflow[index].parameters[param] = value;
                        });
                    });
                    formData.append('json', JSON.stringify(window.workflowData));

                    fetch('/regenerate', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('chart').src = 'data:image/png;base64,' + data.image;
                        } else {
                            alert('Error: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                }

                function downloadChart() {
                    window.location.href = '/download';
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
                <div id="parametersForm"></div>
                <br>
                <button onclick="downloadChart()">Download Chart</button>
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
        dot = draw_vertical_workflow_chart(json_data)
        
        img_stream = io.BytesIO(dot.pipe(format='png'))
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        
        return jsonify({'success': True, 'image': img_base64, 'workflow': json_data})
    else:
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload a .json file.'})

@app.route('/regenerate', methods=['POST'])
def regenerate_chart():
    json_data = request.form['json']
    workflow_data = json.loads(json_data)
    dot = draw_vertical_workflow_chart(workflow_data)
    
    img_stream = io.BytesIO(dot.pipe(format='png'))
    img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    
    return jsonify({'success': True, 'image': img_base64})

@app.route('/download', methods=['GET'])
def download_chart():
    # Fetch the latest generated chart
    with open('vertical_workflow_chart.png', 'rb') as f:
        return send_file(io.BytesIO(f.read()), mimetype='image/png', as_attachment=True, download_name='workflow_chart.png')

# Catch all exceptions and log them
@app.errorhandler(Exception)
def handle_exception(e):
    error_message = str(e)
    return f"An error occurred! {error_message}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Default to port 8000
    app.run(host='0.0.0.0', port=port)
    app.run(debug=True)

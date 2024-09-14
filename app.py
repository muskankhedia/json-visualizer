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
    
    parallel_group = []
    previous_step = None
    
    for step in workflow_data['workflow']:
        step_name = step['name']
        parameters = step['parameters']
        params_str = format_parameters(parameters)
        
        dot.node(step_name, label=f'{step_name}\n{params_str}')
        
        if step['type'] == 'parallel':
            parallel_group.append(step_name)
        else:
            if parallel_group:
                for task in parallel_group:
                    dot.edge(previous_step, task)
                for task in parallel_group:
                    dot.edge(task, step_name)
                parallel_group = []
                
            if previous_step:
                dot.edge(previous_step, step_name)
        
        previous_step = step_name
    
    if parallel_group:
        for task in parallel_group:
            dot.edge(previous_step, task)
    
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
    # You can also print the full traceback if needed
    return f"An error occurred! {error_message}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Default to port 8000
    app.run(host='0.0.0.0', port=port)
    app.run(debug=True)

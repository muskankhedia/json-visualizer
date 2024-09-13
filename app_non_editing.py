from flask import Flask, request, jsonify, render_template_string, send_file
import graphviz
import json
import io
import base64

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
        dot = draw_vertical_workflow_chart(json_data)
        
        # Save the chart to a byte stream
        img_stream = io.BytesIO(dot.pipe(format='png'))
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        
        return jsonify({'success': True, 'image': img_base64})
    else:
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload a .json file.'})

if __name__ == '__main__':
    app.run(debug=True)

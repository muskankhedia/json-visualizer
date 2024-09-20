from flask import Blueprint, request, jsonify, render_template
from .chart import draw_workflow_chart
import json
import io
import base64

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
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

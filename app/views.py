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
    # Hardcoded JSON data instead of reading from uploaded file
    json_data = {
        "name": "Test json",
        "description": "Test json.",
        "contentVersion": "1.0.0",
        "$schema": "basic schema",
        "metadata": {
            "revision": "v3"
        },
        "parameters": {
            "vcPackage": "",
            "abbBmcVersion": "",
            "abbBmcFile": ""
        },
        "workflow": [
            {
                "type": "Type 1",
                "name": "Initialize experiment environment.",
                "description": "New desc",
                "group": "Group A",
                "parameters": {
                    "param1": "1345",
                    "param2": "1423"
                }
            },
            {
                "type": "ParallelExecution",
                "name": "Update phase 1 FWs for L10",
                "group": "Group A",
                "description": "New desc",
                "parameters": {},
                "steps": [
                    {
                        "type": "Type 3",
                        "name": "Perform BIOS OOB firmware update.",
                        "description": "New desc",
                        "group": "Group A",
                        "parameters": {
                            "param1": "val1"
                        }
                    },
                    {
                        "type": "Type 3",
                        "name": "Perform BIOS OOB firmware update.",
                        "description": "New desc",
                        "group": "Group A",
                        "parameters": {
                            "param2": "val2"
                        }
                    },
                    {
                        "type": "Type 2",
                        "name": "Perfm OOB firmware update for SoC Cerberus",
                        "description": "Updates the current firmware version on the Rack SCM.",
                        "group": "Group A",
                        "parameters": {
                            "param1": "val1"
                        }
                    }
                ]
            },
            {
                "type": "Vega.Execution.Providers.Reporting.LogComplianceResultsProvider",
                "name": "Consolidate Compliance Results",
                "description": "Logs compliance results to the results explorer",
                "group": "Group A",
                "parameters": {}
            }
        ]
    }


    # Use the hardcoded JSON data
    dot = draw_workflow_chart(json_data)

    img_stream = io.BytesIO(dot.pipe(format='png'))
    img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    return jsonify({'success': True, 'image': img_base64})


# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'success': False, 'error': 'No file part'})

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'success': False, 'error': 'No selected file'})

#     if file and file.filename.endswith('.json'):
#         json_data = json.load(file)
#         dot = draw_workflow_chart(json_data)

#         img_stream = io.BytesIO(dot.pipe(format='png'))
#         img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

#         return jsonify({'success': True, 'image': img_base64})
#     else:
#         return jsonify({'success': False, 'error': 'Invalid file format. Please upload a .json file.'})
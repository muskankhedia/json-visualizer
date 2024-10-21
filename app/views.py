from flask import Blueprint, request, jsonify, render_template
from .chart import draw_workflow_chart
from app.models.validate import validate_parameters
from app.models.replace_parameters import replace_parameters
import json
import io
import base64

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/uploadExample', methods=['POST'])
def upload_example_file():
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
            "vcPackage": "123",
            "abbBmcVersion": "456",
            "abbBmcFile": "789"
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
                            "param1": "$.parameters.vcPackaage"
                        }
                    },
                    {
                        "type": "Type 3",
                        "name": "Perform BIOS OOB firmware update.",
                        "description": "New desc",
                        "group": "Group A",
                        "parameters": {
                            "param2": "$.parameters.abbBmcVersion"
                        }
                    },
                    {
                        "type": "Type 2",
                        "name": "Perfm OOB firmware update for SoC Cerberus",
                        "description": "Updates the current firmware version on the Rack SCM.",
                        "group": "Group A",
                        "parameters": {
                            "param1": "$.parameters.abbBmcFile"
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


    # Validate parameters
    # validation_errors = validate_parameters(json_data)
    # if validation_errors:
    #     return jsonify({'success': False, 'errors': validation_errors})

    # # If validation passes, proceed with chart generation
    # dot = draw_workflow_chart(json_data)

    # img_stream = io.BytesIO(dot.pipe(format='png'))
    # img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    # return jsonify({'success': True, 'image': img_base64})

    # Replace parameter references with actual values
    updated_json = replace_parameters(json_data)

    # If needed, you can validate the updated_json here

    # Proceed with chart generation using the updated JSON
    dot = draw_workflow_chart(updated_json)

    img_stream = io.BytesIO(dot.pipe(format='png'))
    img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    return jsonify({'success': True, 'image': img_base64, 'updated_json': updated_json})


@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})

    if file and file.filename.endswith('.json'):
        json_data = json.load(file)
        updated_json = replace_parameters(json_data)

        # print updated_json

        # If needed, you can validate the updated_json here

        # Proceed with chart generation using the updated JSON
        dot = draw_workflow_chart(updated_json)

        img_stream = io.BytesIO(dot.pipe(format='png'))
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

        return jsonify({'success': True, 'image': img_base64, 'updated_json': updated_json})
    else:
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload a .json file.'})
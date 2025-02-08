from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import json
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_style_violations(filename):
    with open('sources.mlb', 'w') as f:
        f.write(filename)
    result = subprocess.run(['./millet', '.'], capture_output=True, text=True)
    sanitized_stderr = re.sub('\x1b[[0-9;]*m', '', result.stderr)
    if sanitized_stderr == '':
        sanitized_stderr = 'no errors!'
    return sanitized_stderr

def sml_errored(s):
    t = s.lower()
    return 'error' in t or 'exception' in t

def run_testcases(filename, tests_file):
    # read all lines in tests.sml
    with open(tests_file) as f:
        lines = [line.rstrip() + ';' for line in f]
    test_results = []
    # run the tests
    for line in lines:
        try:
            result = subprocess.run(['./smlnj', filename], input=line, capture_output=True, text=True, timeout=5)
            test_results.append(not sml_errored(result.stdout))
        except subprocess.TimeoutExpired:
            test_results.append(False)
    assert len(test_results) == len(lines)
    return test_results

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    fname = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(fname)

    try:
        return jsonify({            
            'style': check_style_violations(fname),
            'tests': run_testcases(fname, 'tests.sml')})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

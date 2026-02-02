import os
import subprocess
import json
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, template_folder='templates', static_folder='static')

# Use temporary directories for results in web mode
UPLOAD_FOLDER = '/tmp/results/uploads'
OUTPUT_FOLDER = '/tmp/results/renders'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('studio.html')

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    threshold = float(request.form.get('threshold', 0.6))
    
    input_path = os.path.join(UPLOAD_FOLDER, 'input.wav')
    file.save(input_path)

    # Execute Track A (Transcribe)
    cmd_a = [
        "python3", "-u", "pipeline/transcribe.py",
        "--input", input_path,
        "--outdir", OUTPUT_FOLDER,
        "--threshold", str(threshold),
        "--seed", "42"
    ]
    
    try:
        subprocess.run(cmd_a, check=True, capture_output=True, text=True)

        diag_path = os.path.join(OUTPUT_FOLDER, "transcription_diagnostics.json")
        diagnostics = {}
        if os.path.exists(diag_path):
            with open(diag_path, 'r') as f:
                diagnostics = json.load(f)

        return jsonify({
            'status': 'success',
            'diagnostics': diagnostics
        })
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Transcription Failed', 'details': e.stderr}), 500

@app.route('/api/render', methods=['POST'])
def render():
    humanize = request.form.get('humanize') == 'true'
    seed = int(request.form.get('seed', 42))

    input_path = os.path.join(UPLOAD_FOLDER, 'input.wav')
    midi_path = os.path.join(OUTPUT_FOLDER, 'transcription.mid')
    wav_path = os.path.join(OUTPUT_FOLDER, 'rendered.wav')
    json_path = os.path.join(OUTPUT_FOLDER, 'metrics.json')

    # Execute Track B (Render)
    cmd_b = [
        "python3", "-u", "pipeline/render.py",
        "--midi", midi_path,
        "--out", wav_path,
        "--seed", str(seed)
    ]
    if humanize:
        cmd_b.append("--humanize")

    try:
        subprocess.run(cmd_b, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Rendering Failed', 'details': e.stderr}), 500

    # Calculate Metrics
    subprocess.run([
        "python3", "pipeline/metrics.py",
        "--ref", input_path, "--hyp", wav_path,
        "--midi", midi_path, "--out", json_path
    ])

    metrics = {}
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            metrics = json.load(f)

    return jsonify({
        'status': 'success',
        'metrics': metrics,
        'audio_url': '/results/rendered.wav'
    })

@app.route('/results/<path:filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

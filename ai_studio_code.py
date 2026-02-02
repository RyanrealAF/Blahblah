import os
import subprocess
import json
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = '/results/uploads'
OUTPUT_FOLDER = '/results/renders'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('studio.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    path = os.path.join(UPLOAD_FOLDER, 'input.wav')
    file.save(path)
    return jsonify({'status': 'uploaded', 'path': path})

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    
    # 1. Parse UI Knobs
    threshold = float(data.get('threshold', 0.5))
    humanize = "--humanize" if data.get('humanize', False) else ""
    seed = int(data.get('seed', 42))
    
    input_path = os.path.join(UPLOAD_FOLDER, 'input.wav')
    midi_path = os.path.join(OUTPUT_FOLDER, 'transcription.mid')
    wav_path = os.path.join(OUTPUT_FOLDER, 'rendered.wav')
    json_path = os.path.join(OUTPUT_FOLDER, 'metrics.json')

    logs = []

    # 2. Execute Track A (Transcribe)
    cmd_a = [
        "python3", "-u", "pipeline/transcribe.py",
        "--input", input_path,
        "--outdir", OUTPUT_FOLDER,
        "--threshold", str(threshold),
        "--seed", str(seed)
    ]
    
    try:
        logs.append(f"> Executing Track A (Threshold: {threshold})...")
        subprocess.run(cmd_a, check=True, capture_output=True, text=True)
        logs.append("> Transcription Complete.")
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Transcription Failed', 'details': e.stderr}), 500

    # 3. Execute Track B (Render)
    cmd_b = [
        "python3", "-u", "pipeline/render.py",
        "--midi", midi_path,
        "--out", wav_path,
        "--seed", str(seed)
    ]
    if humanize:
        cmd_b.append("--humanize")
        logs.append(f"> Executing Track B (Humanization: ON)...")
    else:
        logs.append(f"> Executing Track B (Humanization: OFF)...")

    try:
        subprocess.run(cmd_b, check=True, capture_output=True, text=True)
        logs.append("> Rendering Complete.")
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Rendering Failed', 'details': e.stderr}), 500

    # 4. Load Metrics (The Sonic Truth)
    metrics = {}
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            metrics = json.load(f)
    else:
        # Run metrics if not present
        subprocess.run([
            "python3", "pipeline/metrics.py",
            "--ref", input_path, "--hyp", wav_path, 
            "--midi", midi_path, "--out", json_path
        ])
        with open(json_path, 'r') as f:
            metrics = json.load(f)

    return jsonify({
        'status': 'success',
        'logs': "\n".join(logs),
        'metrics': metrics,
        'audio_url': '/results/rendered.wav'
    })

@app.route('/results/<path:filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
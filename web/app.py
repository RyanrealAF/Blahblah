import os
import subprocess
import json
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import tempfile

# Add project root to path to allow imports from pipeline
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.transcribe import transcribe as run_transcribe
from pipeline.render import render as run_render

if getattr(sys, 'frozen', False):
    # PyInstaller mode
    base_dir = sys._MEIPASS
    app = Flask(__name__, template_folder=os.path.join(base_dir, 'web', 'templates'), static_folder=os.path.join(base_dir, 'web', 'static'))
else:
    # Dev mode
    app = Flask(__name__, template_folder='templates', static_folder='static')

# Use temporary directories for results in web mode
temp_base = os.path.join(tempfile.gettempdir(), 'blahblah_studio')
UPLOAD_FOLDER = os.path.join(temp_base, 'uploads')
OUTPUT_FOLDER = os.path.join(temp_base, 'renders')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class PipelineArgs:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

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

    try:
        # Execute Track A (Transcribe) directly
        args = PipelineArgs(
            input=input_path,
            outdir=OUTPUT_FOLDER,
            threshold=threshold,
            seed=42
        )
        # Redirect stdout/stderr if needed, or just run
        run_transcribe(args)

        diag_path = os.path.join(OUTPUT_FOLDER, "transcription_diagnostics.json")
        diagnostics = {}
        if os.path.exists(diag_path):
            with open(diag_path, 'r') as f:
                diagnostics = json.load(f)

        return jsonify({
            'status': 'success',
            'diagnostics': diagnostics
        })
    except Exception as e:
        return jsonify({'error': 'Transcription Failed', 'details': str(e)}), 500

@app.route('/api/render', methods=['POST'])
def render():
    humanize = request.form.get('humanize') == 'true'
    seed = int(request.form.get('seed', 42))

    input_path = os.path.join(UPLOAD_FOLDER, 'input.wav')
    midi_path = os.path.join(OUTPUT_FOLDER, 'transcription.mid')
    wav_path = os.path.join(OUTPUT_FOLDER, 'rendered.wav')
    json_path = os.path.join(OUTPUT_FOLDER, 'metrics.json')

    try:
        # Execute Track B (Render) directly
        args = PipelineArgs(
            midi=midi_path,
            out=wav_path,
            seed=seed,
            humanize=humanize
        )
        run_render(args)
    except Exception as e:
        return jsonify({'error': 'Rendering Failed', 'details': str(e)}), 500

    # Calculate Metrics
    # Note: metrics.py needs similar refactoring to be importable. 
    # For now, we skip metrics in frozen mode if the script isn't bundled or python isn't available.
    if not getattr(sys, 'frozen', False):
        try:
            subprocess.run([
                sys.executable, "pipeline/metrics.py",
                "--ref", input_path, "--hyp", wav_path,
                "--midi", midi_path, "--out", json_path
            ], check=False)
        except Exception:
            pass

    metrics = {}
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            metrics = json.load(f)
    else:
        # Mock metrics if calculation skipped
        metrics = {"spectral_mse": 0.0, "note_f1": 0.0, "mfcc_dist": 0.0}

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

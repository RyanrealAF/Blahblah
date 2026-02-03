import os
import json
import shutil
import argparse
import traceback
from flask import Flask, render_template, request, jsonify, send_from_directory

from pipeline.separate import separate as separate_func
from pipeline.transcribe import transcribe as transcribe_func
from pipeline.render import render as render_func
from pipeline.metrics import main as metrics_func

app = Flask(__name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = '/tmp/results/uploads'
OUTPUT_FOLDER = '/tmp/results/renders'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('studio.html')

@app.route('/api/separate', methods=['POST'])
def separate():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    input_path = os.path.join(UPLOAD_FOLDER, 'input.wav')
    file.save(input_path)

    try:
        separate_args = argparse.Namespace(
            input=input_path,
            outdir=OUTPUT_FOLDER,
            seed=42
        )
        separate_func(separate_args)
        
        diag_path = os.path.join(OUTPUT_FOLDER, "separation_diagnostics.json")
        diagnostics = {}
        if os.path.exists(diag_path):
            with open(diag_path, 'r') as f:
                diagnostics = json.load(f)

        # Return stem URLs
        stems = {}
        for stem in diagnostics.get("stems_created", []):
            stems[stem] = f"/results/stems/{stem}.wav"

        return jsonify({
            'status': 'success',
            'diagnostics': diagnostics,
            'stems_created': diagnostics.get("stems_created", []),
            'stems': stems
        })
    except Exception as e:
        return jsonify({'error': 'Separation Failed', 'details': traceback.format_exc()}), 500

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    threshold = float(request.form.get('threshold', 0.6))
    stem = request.form.get('stem')

    if stem:
        input_path = os.path.join(OUTPUT_FOLDER, "stems", f"{stem}.wav")
    else:
        if 'file' in request.files:
            file = request.files['file']
            input_path = os.path.join(UPLOAD_FOLDER, 'input.wav')
            file.save(input_path)
        else:
            input_path = os.path.join(UPLOAD_FOLDER, 'input.wav')

    if not os.path.exists(input_path):
        return jsonify({'error': f'Input file not found: {input_path}'}), 400

    try:
        transcribe_args = argparse.Namespace(
            input=input_path,
            outdir=OUTPUT_FOLDER,
            threshold=threshold,
            seed=42
        )
        transcribe_func(transcribe_args)
        
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
        return jsonify({'error': 'Transcription Failed', 'details': traceback.format_exc()}), 500

@app.route('/api/render', methods=['POST'])
def render():
    humanize = request.form.get('humanize') == 'true'
    seed = int(request.form.get('seed', 42))

    input_path = os.path.join(UPLOAD_FOLDER, 'input.wav')
    midi_path = os.path.join(OUTPUT_FOLDER, 'transcription.mid')
    wav_path = os.path.join(OUTPUT_FOLDER, 'rendered.wav')
    json_path = os.path.join(OUTPUT_FOLDER, 'metrics.json')

    try:
        render_args = argparse.Namespace(
            midi=midi_path,
            out=wav_path,
            seed=seed,
            humanize=humanize
        )
        render_func(render_args)
    except Exception as e:
        return jsonify({'error': 'Rendering Failed', 'details': traceback.format_exc()}), 500

    try:
        metrics_args = argparse.Namespace(
            ref=input_path,
            hyp=wav_path,
            midi=midi_path,
            out=json_path
        )
        metrics_func(metrics_args)
    except Exception as e:
        print(f"[!] Metrics calculation failed: {e}\n{traceback.format_exc()}")

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

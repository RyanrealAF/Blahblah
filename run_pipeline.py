#!/usr/bin/env python3
"""
Windows-compatible pipeline runner for Blahblah project.
Replaces the bash script functionality for Windows users.
"""

import os
import sys
import subprocess
import json
import argparse

def run_pipeline(input_file="tests/test_piano.wav", output_dir="results", seed=42):
    """Run the complete Blahblah pipeline."""
    print(f"[*] System Start. Seed: {seed}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save environment info
    env_info = {
        "seed": seed,
        "python_version": sys.version,
        "numpy_version": None,
        "torch_version": None
    }
    try:
        import numpy
        env_info["numpy_version"] = numpy.__version__
    except ImportError:
        pass
    try:
        import torch
        env_info["torch_version"] = torch.__version__
    except ImportError:
        pass
    
    with open(os.path.join(output_dir, "env.json"), "w") as f:
        json.dump(env_info, f, indent=2)
    
    # 1. Track A: WAV -> MIDI (Transcribe)
    print("[*] Track A: Transcribing...")
    transcribe_cmd = [
        sys.executable, "-u", "pipeline/transcribe.py",
        "--input", input_file,
        "--outdir", output_dir,
        "--seed", str(seed),
        "--threshold", "0.6"
    ]
    subprocess.run(transcribe_cmd, check=True)
    
    # 2. Track B: MIDI -> WAV (Render)
    print("[*] Track B: Rendering...")
    midi_path = os.path.join(output_dir, "transcription.mid")
    rendered_path = os.path.join(output_dir, "rendered.wav")
    render_cmd = [
        sys.executable, "-u", "pipeline/render_simple.py",
        "--midi", midi_path,
        "--out", rendered_path,
        "--seed", str(seed),
        "--humanize"
    ]
    subprocess.run(render_cmd, check=True)
    
    # 3. Evaluation
    print("[*] Calculating Metrics...")
    metrics_path = os.path.join(output_dir, "metrics.json")
    metrics_cmd = [
        sys.executable, "-u", "pipeline/metrics.py",
        "--ref", input_file,
        "--hyp", rendered_path,
        "--midi", midi_path,
        "--out", metrics_path
    ]
    subprocess.run(metrics_cmd, check=True)
    
    print(f"[*] Pipeline Complete. Check {metrics_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Blahblah pipeline")
    parser.add_argument("--input", default="tests/test_piano.wav", help="Input WAV file")
    parser.add_argument("--output", default="results", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    
    run_pipeline(args.input, args.output, args.seed)
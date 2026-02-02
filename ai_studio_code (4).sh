#!/usr/bin/env bash
set -euo pipefail
INPUT="$1"
OUTPUT_DIR="$2"
mkdir -p "$OUTPUT_DIR"

python -u pipeline/transcribe.py --input "$INPUT" --outdir "$OUTPUT_DIR" --seed 42
python -u pipeline/render.py --midi "$OUTPUT_DIR/transcription.mid" --out "$OUTPUT_DIR/rendered.wav" --seed 42
python -u pipeline/metrics.py --ref "$INPUT" --hyp "$OUTPUT_DIR/rendered.wav" --out "$OUTPUT_DIR/metrics.json"

Dockerfile Key Points

Base: ubuntu:22.04

Pin Python, packages, and system libraries.

ENV PYTHONHASHSEED=42

ENTRYPOINT: run.sh

Optional: CUDA-enabled, CPU fallback.

Minimal image: only runtime + dependencies.


Failure Demo (60s)

0–15s: Normal WAV → MIDI → WAV; show spectrogram overlay.

15–35s: Adversarial input; partial output, JSON diagnostics.

35–60s: Graceful degradation; render safe subset + humanization; explain failure honesty.


README.md Outline

1. Overview


2. Architecture (Track A + Track B)


3. Metrics & evaluation


4. Ablation proof summary


5. Determinism & reproducibility


6. Usage (run.sh <input> <output>)


7. Human listening test & CSV results


8. Environment info + seed logs
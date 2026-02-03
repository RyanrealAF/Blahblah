#!/usr/bin/env bash
set -euo pipefail

# USAGE:
# CLI MODE: ./run.sh <input_wav> <output_dir> [seed]
# WEB MODE: ./run.sh --ui

if [[ "${1:-}" == "--ui" ]]; then
    echo "[*] Starting Neural Audio Lab UI on http://localhost:5000"
    exec python3 web/app.py
fi

INPUT_FILE="${1:-/data/input.wav}"
OUTPUT_DIR="${2:-results}"
SEED=${3:-42}

echo "[*] CLI Mode. Input: $INPUT_FILE"
mkdir -p "$OUTPUT_DIR"

# Save environment info
echo "{\"seed\": $SEED, \"python_version\": \"$(python3 --version)\", \"numpy_version\": \"$(python3 -c "import numpy; print(numpy.__version__)")\"}" > "$OUTPUT_DIR/env.json"

# 0. Track S: Source Separation
echo "[*] Track S: Separating Stems..."
python3 -u pipeline/separate.py \
    --input "$INPUT_FILE" \
    --outdir "$OUTPUT_DIR" \
    --seed "$SEED"

# 1. Track A: WAV -> MIDI (Transcribe)
# By default, transcribe the original file in CLI mode
echo "[*] Track A: Transcribing..."
python3 -u pipeline/transcribe.py \
    --input "$INPUT_FILE" \
    --outdir "$OUTPUT_DIR" \
    --seed "$SEED" \
    --threshold 0.6

# 2. Track B: MIDI -> WAV (Render)
echo "[*] Track B: Rendering..."
python3 -u pipeline/render.py \
    --midi "$OUTPUT_DIR/transcription.mid" \
    --out "$OUTPUT_DIR/rendered.wav" \
    --seed "$SEED" \
    --humanize

# 3. Evaluation
echo "[*] Calculating Metrics..."
python3 -u pipeline/metrics.py \
    --ref "$INPUT_FILE" \
    --hyp "$OUTPUT_DIR/rendered.wav" \
    --midi "$OUTPUT_DIR/transcription.mid" \
    --out "$OUTPUT_DIR/metrics.json"

echo "[*] Pipeline Complete. Check $OUTPUT_DIR/metrics.json"

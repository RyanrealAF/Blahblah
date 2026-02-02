#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" == "--ui" ]; then
    echo "[*] Starting Studio UI on http://localhost:8000"
    exec uvicorn app:app --host 0.0.0.0 --port 8000
else
    # Existing CLI Logic
    INPUT_FILE="${1:-/data/input.wav}"
    OUTPUT_DIR="${2:-results}"
    SEED="${3:-42}"
    
    echo "[*] CLI Mode. Input: $INPUT_FILE"
    # ... (Rest of existing CLI logic)
    python3 -u pipeline/transcribe.py --input "$INPUT_FILE" --outdir "$OUTPUT_DIR" --seed "$SEED"
    python3 -u pipeline/render.py --midi "$OUTPUT_DIR/transcription.mid" --out "$OUTPUT_DIR/rendered.wav" --seed "$SEED" --humanize
    python3 -u pipeline/metrics.py --ref "$INPUT_FILE" --hyp "$OUTPUT_DIR/rendered.wav" --midi "$OUTPUT_DIR/transcription.mid" --out "$OUTPUT_DIR/metrics.json"
fi
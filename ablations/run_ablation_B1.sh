#!/bin/bash
# Ablation B1: Remove Humanization
INPUT="${1:-tests/test_piano.wav}"
OUT="results/ablation_B1"
mkdir -p "$OUT"

echo "[*] Running Ablation B1 (No Humanization)"

# Transcribe normally
python3 pipeline/transcribe.py --input "$INPUT" --outdir "$OUT"

# Render WITHOUT humanize flag
python3 pipeline/render.py --midi "$OUT/transcription.mid" --out "$OUT/no_human.wav" --seed 42 

# Run metrics
python3 pipeline/metrics.py --ref "$INPUT" --hyp "$OUT/no_human.wav" --midi "$OUT/transcription.mid" --out "$OUT/metrics.json"

echo "Ablation B1 Complete. Compare $OUT/no_human.wav with baseline."

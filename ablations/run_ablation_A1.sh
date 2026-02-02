#!/bin/bash
# Ablation A1: Remove CQT/Spectral features (Simulated by high threshold)
INPUT="${1:-tests/test_piano.wav}"
OUT="results/ablation_A1"
mkdir -p "$OUT"

echo "[*] Running Ablation A1 (Reduced Features/High Threshold)"

# Transcribe with very high threshold
python3 pipeline/transcribe.py --input "$INPUT" --outdir "$OUT" --threshold 0.9

# Render normally
python3 pipeline/render.py --midi "$OUT/transcription.mid" --out "$OUT/rendered.wav" --seed 42 --humanize

# Run metrics
python3 pipeline/metrics.py --ref "$INPUT" --hyp "$OUT/rendered.wav" --midi "$OUT/transcription.mid" --out "$OUT/metrics.json"

echo "Ablation A1 Complete. Check results in $OUT"

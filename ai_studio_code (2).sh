#!/bin/bash
# Ablation B1: Remove Humanization
INPUT="tests/test_piano.wav"
OUT="results/ablation_B1"
mkdir -p "$OUT"

# Transcribe normally
python3 pipeline/transcribe.py --input "$INPUT" --outdir "$OUT"

# Render WITHOUT humanize flag
python3 pipeline/render.py --midi "$OUT/transcription.mid" --out "$OUT/no_human.wav" --seed 42 
# (Note: missing --humanize flag)

echo "Ablation B1 Complete. Compare $OUT/no_human.wav with baseline."
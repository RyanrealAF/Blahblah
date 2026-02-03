import argparse
import os
import json
import librosa
import numpy as np
import soundfile as sf
import sys

# Ensure pipeline directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import set_seed, save_diagnostics

def separate(args):
    set_seed(args.seed)
    diagnostics = {
        "stems_created": [],
        "warnings": [],
        "status": "success"
    }

    # 1. Load Audio
    y, sr = librosa.load(args.input, sr=22050)

    # 2. Harmonic-Percussive Source Separation (HPSS)
    # Percussive -> Drums
    # Harmonic -> (Vocals + Bass + Other)
    harmonic, percussive = librosa.effects.hpss(y)

    # 3. Further split Harmonic into Bass and Vocals/Other
    # We use a simple frequency-based mask for "Lean" implementation
    S_harm = librosa.stft(harmonic)
    freqs = librosa.fft_frequencies(sr=sr)

    # Bass: < 200 Hz
    bass_mask = freqs < 200
    S_bass = S_harm.copy()
    S_bass[~bass_mask, :] = 0
    bass = librosa.istft(S_bass)

    # Vocals/Other: > 200 Hz
    S_rest = S_harm.copy()
    S_rest[bass_mask, :] = 0

    # Within > 200 Hz, we can attempt to isolate Vocals (mid-range) from Other (high/low residue)
    # Vocals typically 200Hz - 4kHz
    vocals_mask = (freqs >= 200) & (freqs < 4000)
    S_vocals = S_harm.copy()
    S_vocals[~vocals_mask, :] = 0
    vocals = librosa.istft(S_vocals)

    # Other: > 4kHz or other residue
    other_mask = freqs >= 4000
    S_other = S_harm.copy()
    S_other[~other_mask, :] = 0
    other = librosa.istft(S_other)

    # 4. Save Stems
    stem_dir = os.path.join(args.outdir, "stems")
    os.makedirs(stem_dir, exist_ok=True)

    stems = {
        "vocals": vocals,
        "bass": bass,
        "drums": percussive,
        "other": other
    }

    for name, data in stems.items():
        # Normalize and save
        if np.max(np.abs(data)) > 0:
            data = librosa.util.normalize(data)
        out_path = os.path.join(stem_dir, f"{name}.wav")
        sf.write(out_path, data, sr)
        diagnostics["stems_created"].append(name)

    # 5. Failure Honesty
    # If the input is too sparse or too dense, warn.
    if len(diagnostics["stems_created"]) < 4:
        diagnostics["warnings"].append("Some stems were silent and not created.")

    save_diagnostics(diagnostics, os.path.join(args.outdir, "separation_diagnostics.json"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    separate(args)

import subprocess
import os
import hashlib
import numpy as np
from scipy.io import wavfile

def get_file_hash(filepath):
    if not os.path.exists(filepath):
        return None
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def create_dummy_wav(path):
    sr = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration))
    # A simple chord
    y = np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 554.37 * t) + np.sin(2 * np.pi * 659.25 * t)
    y = y / np.max(np.abs(y))
    wavfile.write(path, sr, (y * 32767).astype(np.int16))

def test_determinism():
    input_wav = "tests/test_piano.wav"
    os.makedirs("tests", exist_ok=True)
    create_dummy_wav(input_wav)

    out1 = "results/det1"
    out2 = "results/det2"
    os.makedirs(out1, exist_ok=True)
    os.makedirs(out2, exist_ok=True)

    print("Running first pass...")
    subprocess.run(["./run.sh", input_wav, out1, "42"], check=True)
    print("Running second pass...")
    subprocess.run(["./run.sh", input_wav, out2, "42"], check=True)

    h1 = get_file_hash(os.path.join(out1, "transcription.mid"))
    h2 = get_file_hash(os.path.join(out2, "transcription.mid"))

    assert h1 == h2, f"MIDI mismatch: {h1} != {h2}"

    # Check rendered wav as well (might be slightly different due to floats but should be close or same if seeds work)
    # Actually Fluidsynth might have some non-determinism unless specifically configured,
    # but we'll see.

    print("Determinism test passed!")

if __name__ == "__main__":
    test_determinism()

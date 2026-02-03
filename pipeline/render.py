import argparse
import mido
import numpy as np
import scipy.io.wavfile
import subprocess
import os
import sys

# Ensure pipeline directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import set_seed, save_diagnostics

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller. """
    if getattr(sys, 'frozen', False):
        # We are running in a bundle, resources are in the temp folder
        base_path = sys._MEIPASS
    else:
        # We are running in a normal Python environment
        # Assume script is in Blahblah/pipeline/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    return os.path.join(base_path, relative_path)

def apply_humanization(mid, seed):
    """
    Injects micro-timing jitter and velocity curves.
    """
    rng = np.random.RandomState(seed)
    
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                # Velocity Humanization: Gaussian jitter
                jitter = int(rng.normal(0, 5)) 
                msg.velocity = np.clip(msg.velocity + jitter, 1, 127)
                
                # Timing Humanization (simulated by adjusting deltas)
                # In a more complex implementation, we'd jitter msg.time
                time_jitter = int(rng.normal(0, 2))
                msg.time = max(0, msg.time + time_jitter)
    return mid

def render(args):
    set_seed(args.seed)
    diagnostics = {"polyphony_overflow": 0, "rendered_voices": 0}
    
    # 1. Parse MIDI
    mid = mido.MidiFile(args.midi)
    
    # 2. Humanization (Expressiveness)
    if args.humanize:
        mid = apply_humanization(mid, args.seed)
    
    # Save temp humanized MIDI
    temp_midi = args.midi.replace(".mid", "_humanized.mid")
    mid.save(temp_midi)
    
    # 3. Synthesis (using FluidSynth as the reliable backend)
    # We use FluidSynth here for container robustness.
    # Locate bundled resources for Windows executable compatibility.
    soundfont = get_resource_path(os.path.join('data', 'FluidR3_GM.sf2'))

    # On Windows, we expect a bundled fluidsynth.exe
    if sys.platform == "win32":
        fluidsynth_exe = get_resource_path(os.path.join('vendor', 'fluidsynth', 'bin', 'fluidsynth.exe'))
    else: # Assume it's in PATH on Linux/macOS
        fluidsynth_exe = "fluidsynth"

    if not os.path.exists(soundfont):
        diagnostics["error"] = f"Soundfont file not found at {soundfont}"
        save_diagnostics(diagnostics, args.out.replace(".wav", "_diagnostics.json"))
        print(f"[!] {diagnostics['error']}")
        return

    cmd = [
        fluidsynth_exe, "-ni", soundfont, temp_midi,
        "-F", args.out, "-r", "44100", "-g", "1.0"
    ]
    
    try:
        # Use capture_output to get stdout/stderr if an error occurs
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except Exception as e:
        diagnostics["error"] = str(e)
    
    # 4. Minimal Mixing (Post-FX)
    # Load WAV, apply slight reverb/compression simulation via scipy/numpy
    if os.path.exists(args.out):
        sr, audio = scipy.io.wavfile.read(args.out)

        # Convert to float for processing
        audio = audio.astype(np.float32) / 32768.0

        # Stereo spread simulation (duplicate mono to stereo with slight delay)
        if len(audio.shape) == 1:
            # Create a 2ms delay for one channel
            delay_samples = int(sr * 0.002)
            left = audio
            right = np.zeros_like(audio)
            right[delay_samples:] = audio[:-delay_samples]
            audio = np.stack([left, right], axis=1)

        # Subtle compression
        threshold = 0.8
        ratio = 2.0
        mask = np.abs(audio) > threshold
        audio[mask] = np.sign(audio[mask]) * (threshold + (np.abs(audio[mask]) - threshold) / ratio)

        # Back to int16
        audio = (audio * 32767.0).astype(np.int16)
        scipy.io.wavfile.write(args.out, sr, audio)
    
    save_diagnostics(diagnostics, args.out.replace(".wav", "_diagnostics.json"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--midi', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--humanize', action='store_true')
    args = parser.parse_args()
    render(args)

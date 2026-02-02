import argparse
import mido
import numpy as np
import scipy.io.wavfile
import os
import sys

# Ensure pipeline directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import set_seed, save_diagnostics

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

def render_simple(args):
    """Simple MIDI to WAV renderer using basic sine waves."""
    set_seed(args.seed)
    diagnostics = {"polyphony_overflow": 0, "rendered_voices": 0}
    
    # 1. Parse MIDI
    mid = mido.MidiFile(args.midi)
    
    # 2. Humanization (Expressiveness)
    if args.humanize:
        mid = apply_humanization(mid, args.seed)
    
    # 3. Simple synthesis using sine waves
    sample_rate = 44100
    total_samples = 0
    
    # Calculate total duration
    for track in mid.tracks:
        time = 0
        for msg in track:
            if hasattr(msg, 'time'):
                time += msg.time
                total_samples = max(total_samples, int(time * sample_rate / 500))  # rough conversion
    
    # Create audio buffer
    audio = np.zeros(total_samples, dtype=np.float32)
    
    # Generate sine wave for each note
    for track in mid.tracks:
        current_time = 0
        for msg in track:
            if hasattr(msg, 'time'):
                current_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                # Calculate note frequency
                note_freq = 440 * (2 ** ((msg.note - 69) / 12))
                
                # Calculate start and end samples
                start_sample = int(current_time * sample_rate / 500)
                end_sample = start_sample + int(1.0 * sample_rate)  # 1 second duration
                
                if end_sample > len(audio):
                    end_sample = len(audio)
                
                # Generate sine wave
                t = np.linspace(0, 1.0, end_sample - start_sample, False)
                note_wave = np.sin(2 * np.pi * note_freq * t)
                
                # Apply envelope (fade in/out)
                envelope = np.ones_like(note_wave)
                attack_samples = int(0.05 * sample_rate)
                release_samples = int(0.1 * sample_rate)
                
                if attack_samples > 0:
                    attack_len = min(attack_samples, len(envelope))
                    envelope[:attack_len] = np.linspace(0, 1, attack_len)
                if release_samples > 0:
                    release_len = min(release_samples, len(envelope))
                    envelope[-release_len:] = np.linspace(1, 0, release_len)
                
                # Add to audio buffer
                audio[start_sample:end_sample] += note_wave * envelope * (msg.velocity / 127.0)
                diagnostics["rendered_voices"] += 1
    
    # Normalize audio
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
    
    # Convert to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # Save as stereo
    stereo_audio = np.column_stack([audio_int16, audio_int16])
    scipy.io.wavfile.write(args.out, sample_rate, stereo_audio)
    
    save_diagnostics(diagnostics, args.out.replace(".wav", "_diagnostics.json"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--midi', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--humanize', action='store_true')
    args = parser.parse_args()
    render_simple(args)
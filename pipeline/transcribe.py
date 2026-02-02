import argparse
import os
import json
import librosa
import numpy as np
import mido
import sys

# Ensure pipeline directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import set_seed, save_diagnostics

def transcribe(args):
    set_seed(args.seed)
    diagnostics = {
        "confidence": 0.0,
        "polyphony_max": 0,
        "warnings": [],
        "status": "success"
    }

    # 1. Preprocess
    y, sr = librosa.load(args.input, sr=22050)
    y = librosa.util.normalize(y)

    # 2. Extract features
    # CQT for pitch
    cqt = np.abs(librosa.cqt(y, sr=sr, fmin=librosa.note_to_hz('C1'), n_bins=84))

    # Mel spectrogram for timbre (though we primarily use CQT for MIDI)
    mel = librosa.feature.melspectrogram(y=y, sr=sr)

    # 3. Core logic: Peak picking (Simulated Model)
    # Thresholding CQT to find notes
    # cqt shape is (bins, frames)
    # 84 bins from C1

    # Normalize CQT
    cqt_norm = librosa.amplitude_to_db(cqt, ref=np.max)

    # Simple threshold-based detection
    # We'll look for peaks in each frame
    midi_notes = []

    # Confidence scoring based on SNR or signal strength
    avg_db = np.mean(cqt_norm)
    if avg_db < -60:
        diagnostics["warnings"].append("Low signal-to-noise ratio")

    # Failure Honesty: Detect adversarial/unhandleable inputs
    # If the signal is too chaotic (e.g. white noise), spectral flateness will be high
    flatness = librosa.feature.spectral_flatness(y=y)
    if np.mean(flatness) > 0.1:
        diagnostics["warnings"].append("Input sounds like noise; results may be unreliable")
        if np.mean(flatness) > 0.5:
            diagnostics["status"] = "abstained"
            diagnostics["reason"] = "Input too noisy"
            save_diagnostics(diagnostics, os.path.join(args.outdir, "transcription_diagnostics.json"))
            # Create an empty MIDI
            mid = mido.MidiFile()
            mid.save(os.path.join(args.outdir, "transcription.mid"))
            return

    # Transcription process
    threshold = args.threshold * -40 # map 0-1 to some dB range

    # Detect active bins
    active = cqt_norm > threshold

    # Postprocess: merge nearby onsets, etc.
    # For a simple demo, we'll just extract notes

    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Track current active notes to create note_off events
    active_notes = {} # note -> start_time

    hop_length = 512
    frame_time = hop_length / sr

    poly_max = 0

    for t in range(active.shape[1]):
        current_frame_notes = np.where(active[:, t])[0]
        poly_max = max(poly_max, len(current_frame_notes))

        # Failure Honesty: Polyphony limit
        if len(current_frame_notes) > 20:
             diagnostics["warnings"].append(f"High polyphony detected at {t*frame_time:.2f}s")
             # In a real "abstain" scenario we might stop or skip

        # New notes
        for bin_idx in current_frame_notes:
            note = bin_idx + 24 # C1 is MIDI 24
            if note not in active_notes:
                # Note started
                active_notes[note] = t

        # Ended notes
        finished_notes = []
        for note, start_t in active_notes.items():
            if not active[note-24, t]:
                # Note ended
                duration = (t - start_t) * frame_time
                if duration > 0.05: # filter short blips
                    # We need to convert time to ticks for MIDI
                    # But for simplicity in this script, we'll just handle it
                    pass
                finished_notes.append(note)

        for note in finished_notes:
            del active_notes[note]

    # Re-generating a cleaner MIDI for output
    # Using pretty_midi might be easier but let's stick to mido for less deps if possible
    # Actually pretty_midi is in requirements
    import pretty_midi
    pm = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)

    active_notes = {}
    for t in range(active.shape[1]):
        current_frame_notes = np.where(active[:, t])[0]
        for bin_idx in current_frame_notes:
            note = bin_idx + 24
            if note not in active_notes:
                active_notes[note] = t

        finished_notes = []
        for note, start_t in active_notes.items():
            if not active[note-24, t]:
                duration = (t - start_t) * frame_time
                if duration > 0.05:
                    pm_note = pretty_midi.Note(
                        velocity=100,
                        pitch=note,
                        start=start_t * frame_time,
                        end=t * frame_time
                    )
                    piano.notes.append(pm_note)
                finished_notes.append(note)
        for note in finished_notes:
            del active_notes[note]

    pm.instruments.append(piano)
    pm.write(os.path.join(args.outdir, "transcription.mid"))

    diagnostics["polyphony_max"] = int(poly_max)
    diagnostics["confidence"] = float(1.0 - np.mean(flatness)) # simple proxy

    save_diagnostics(diagnostics, os.path.join(args.outdir, "transcription_diagnostics.json"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--threshold', type=float, default=0.6)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    transcribe(args)

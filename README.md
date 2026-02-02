# WAV↔MIDI Conversion System

## Mission
A reproducible, failure-honest pipeline for transcribing audio to MIDI and rendering expressive audio back from MIDI.

## Architecture

### Track A: Transcription (WAV → MIDI)
- **Input:** Standardized audio (22kHz, Mono).
- **Features:** CQT (pitch) + Mel Spectrogram (timbre).
- **Logic:** Threshold-based peak picking on spectral features (Simulated Neural Model).
- **Failure Honesty:** Abstains from transcription if polyphony exceeds adversarial thresholds (>20 simultaneous notes) or confidence is low (e.g., high spectral flatness).

### Track B: Rendering (MIDI → WAV)
- **Engine:** FluidSynth (Containerized) + Custom Python Humanizer.
- **Humanization:** Gaussian velocity jitter and micro-timing adjustments.
- **Post-Process:** Stereo widening and minimal dynamic compression.

## Usage

**1. Build Environment**
```bash
docker build -t wav2midi .
```

**2. Run Pipeline**
```bash
./run.sh <input_wav> <output_dir> [seed]
```

## Evaluation
- **Sonic Truth:** Spectral MSE between input and output audio.
- **Failure Honesty:** System logs diagnostics and warns/abstains on noisy or overly complex inputs.
- **Reproducibility:** All seeds are pinned (Python, NumPy, PyTorch, Hash).

## Ablations
- **A1:** Remove CQT/Spectral features (affects accuracy).
- **B1:** Remove Humanization (affects expressiveness).

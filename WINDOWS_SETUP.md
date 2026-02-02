# Blahblah Project - Windows Setup Guide

## Issues Fixed

After moving your project location, the main issues were:

1. **Missing Python dependencies**: Flask, uvicorn, mir_eval, pretty_midi were not installed
2. **Windows compatibility**: The original `run.sh` script is a bash script that doesn't work on Windows
3. **Missing audio synthesis**: The original `render.py` depends on `fluidsynth` which isn't available on Windows

## Files Created/Modified

### New Files:
- `run.bat` - Windows batch file version of the pipeline runner
- `run_pipeline.py` - Python script that works cross-platform
- `pipeline/render_simple.py` - Simple MIDI renderer that works without external dependencies

### Dependencies Installed:
- flask
- uvicorn  
- mir_eval
- pretty_midi

## How to Run

### Option 1: Python Script (Recommended)
```bash
python run_pipeline.py --input tests/test_piano.wav --output results --seed 42
```

### Option 2: Windows Batch File
```bash
run.bat tests/test_piano.wav results 42
```

### Option 3: Web Interface
```bash
python web/app.py
```
Then open http://localhost:5000 in your browser

## Project Status

✅ **Working Components:**
- All Python imports and dependencies
- Web application server (Flask)
- Audio transcription (WAV → MIDI)
- Simple audio rendering (MIDI → WAV)
- Metrics calculation
- Cross-platform pipeline runner

The project should now work correctly on your Windows system!
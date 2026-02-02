@echo off
setlocal

REM USAGE: run.bat <input_wav> <output_dir> [seed]

set INPUT_FILE=%1
set OUTPUT_DIR=%2
set SEED=%3

if "%INPUT_FILE%"=="" set INPUT_FILE=tests/test_piano.wav
if "%OUTPUT_DIR%"=="" set OUTPUT_DIR=results
if "%SEED%"=="" set SEED=42

echo [*] System Start. Seed: %SEED%
mkdir "%OUTPUT_DIR%" 2>nul

REM Save environment info
echo {"seed": %SEED%, "python_version": "%PYTHON_VERSION%"} > "%OUTPUT_DIR%\env.json"

REM 1. Track A: WAV -> MIDI (Transcribe)
echo [*] Track A: Transcribing...
python -u pipeline/transcribe.py --input "%INPUT_FILE%" --outdir "%OUTPUT_DIR%" --seed %SEED% --threshold 0.6

REM 2. Track B: MIDI -> WAV (Render)
echo [*] Track B: Rendering...
python -u pipeline/render.py --midi "%OUTPUT_DIR%\transcription.mid" --out "%OUTPUT_DIR%\rendered.wav" --seed %SEED% --humanize

REM 3. Evaluation
echo [*] Calculating Metrics...
python -u pipeline/metrics.py --ref "%INPUT_FILE%" --hyp "%OUTPUT_DIR%\rendered.wav" --midi "%OUTPUT_DIR%\transcription.mid" --out "%OUTPUT_DIR%\metrics.json"

echo [*] Pipeline Complete. Check %OUTPUT_DIR%\metrics.json
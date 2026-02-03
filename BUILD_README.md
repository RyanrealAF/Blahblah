# Blahblah Build Instructions

This document explains how to build the Blahblah standalone Windows executable.

## Prerequisites

1. **Python 3.9+** installed and in PATH
2. **PyInstaller** (will be installed automatically by build script)
3. **Required Python packages** (listed in requirements.txt)
4. **NSIS** (optional, for creating installer)

## Build Process

### Method 1: Using the Build Script (Recommended)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the build script:**
   ```bash
   python build_exe.py
   ```

3. **The build script will:**
   - Check for required dependencies
   - Create an icon file if needed
   - Build the standalone executable using PyInstaller
   - Create an NSIS installer script

4. **Find your executable:**
   - Location: `dist/blahblah.exe`

### Method 2: Manual PyInstaller Build

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build using the spec file:**
   ```bash
   pyinstaller blahblah.spec
   ```

3. **Or build directly:**
   ```bash
   pyinstaller --onefile --windowed --name blahblah main.py
   ```

## Usage

### CLI Mode
```bash
blahblah.exe --input input.wav --output results/ --threshold 0.7 --humanize --seed 123
```

### Web Mode
```bash
blahblah.exe --web
```

### Web Mode with Custom Port
```bash
blahblah.exe --web --port 8080
```

## Creating an Installer

1. **Install NSIS** from https://nsis.sourceforge.io/

2. **Run the installer script:**
   ```bash
   makensis installer.nsi
   ```

3. **Find your installer:**
   - Location: `Blahblah_Installer.exe`

## Troubleshooting

### Missing Dependencies
If you get import errors, ensure all packages from `requirements.txt` are installed:
```bash
pip install -r requirements.txt
```

### PyInstaller Issues
- Ensure PyInstaller is up to date
- Try building in a clean virtual environment
- Check that all hidden imports are correctly specified in the spec file

### Audio Processing Issues
- Ensure `libsndfile-1.dll` is available in Windows System32
- Ensure FluidSynth is installed for MIDI rendering
- Check that the soundfont file is accessible

### Large Executable Size
The executable will be large (~100-200MB) due to:
- PyTorch and scientific computing libraries
- Audio processing dependencies
- Web framework and server components

## File Structure

```
Blahblah/
├── main.py                    # Main entry point
├── blahblah.spec             # PyInstaller configuration
├── build_exe.py              # Build automation script
├── dist/                     # Build output directory
│   └── blahblah.exe          # Standalone executable
├── installer.nsi             # NSIS installer script
├── pipeline/                 # Core processing modules
├── web/                      # Web interface
└── requirements.txt          # Python dependencies
```

## System Requirements

- **Windows 10/11** (64-bit recommended)
- **4GB RAM** minimum (8GB recommended for audio processing)
- **1GB free disk space** for the executable
- **Python 3.9+** (only needed for building, not for running)

## Notes

- The executable includes both CLI and web server functionality
- Web interface runs on `http://localhost:5000` by default
- All dependencies are bundled - no installation required on target machines
- The executable is self-contained and portable
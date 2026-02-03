#!/usr/bin/env python3
"""
Build script for creating the Blahblah standalone Windows executable.
"""
import os
import sys
import subprocess
import shutil

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyInstaller
        print(f"[*] PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("[!] PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Check if required Python packages are installed
    print("[*] Checking Python packages from requirements.txt...")
    try:
        with open('requirements.txt', 'r') as f:
            required_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print("[!] requirements.txt not found. Cannot check dependencies.")
        return False
    
    for package in required_packages:
        try:
            __import__(package.split('==')[0].split('>')[0].split('<')[0]) # Handle version specifiers
            print(f"[*] {package} found")
        except ImportError:
            print(f"[!] {package} not found. Please install it.")
            return False
    
    return True

def create_icon():
    """Create a simple icon file if it doesn't exist."""
    if not os.path.exists('icon.ico'):
        try:
            from PIL import Image, ImageDraw
            # Create a simple icon
            img = Image.new('RGB', (256, 256), color='black')
            d = ImageDraw.Draw(img)
            d.rectangle([0, 0, 256, 256], fill='black')
            d.text((50, 100), "BLAH", fill='white')
            img.save('icon.ico')
            print("[*] Created icon.ico")
        except ImportError:
            print("[!] PIL not available, skipping icon creation")
            # Create a dummy icon file
            with open('icon.ico', 'wb') as f:
                f.write(b'\x00' * 1024)

def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("[*] Building Blahblah executable...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Run PyInstaller with the spec file
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        'blahblah.spec'
    ]
    
    print(f"[*] Running: {' '.join(cmd)}")
    
    try:
        # Run with real-time output, like in the debug script
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 universal_newlines=True, bufsize=1)

        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())

        process.wait()

        if process.returncode == 0:
            print("[*] Build successful!")
            return True
        print(f"[!] Build failed with return code: {process.returncode}")
        return False

def create_installer():
    """Create a simple installer using NSIS or Inno Setup."""
    print("[*] Creating installer...")
    
    # Create installer script
    installer_script = """[Setup]
AppName=Blahblah Audio Processing
AppVersion=1.0.0
DefaultDirName={pf}\\Blahblah
DefaultGroupName=Blahblah
OutputDir=.
OutputBaseFilename=Blahblah_Installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\\blahblah.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\Blahblah"; Filename: "{app}\\blahblah.exe"
Name: "{commondesktop}\\Blahblah"; Filename: "{app}\\blahblah.exe"

[Run]
Filename: "{app}\\blahblah.exe"; Description: "Run Blahblah"; Flags: nowait postinstall skipifsilent
"""
    
    with open('installer.nsi', 'w') as f:
        f.write(installer_script)
    
    print("[*] Created installer.nsi")
    print("[*] To create the installer, run: makensis installer.nsi")
    print("[*] (Requires NSIS to be installed)")

def main():
    """Main build process."""
    print("[*] Blahblah Build Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py') or not os.path.exists('blahblah.spec'):
        print("[!] Error: Please run this script from the Blahblah project root directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("[!] Missing dependencies. Please install them and try again.")
        sys.exit(1)
    
    # Create icon
    create_icon()
    
    # Build executable
    if build_executable():
        print("[*] Executable built successfully!")
        
        # Create installer
        create_installer()
        
        print("\n[*] Build complete!")
        print("[*] Executable location: dist/blahblah.exe")
        print("[*] To create installer: makensis installer.nsi")
    else:
        print("[!] Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
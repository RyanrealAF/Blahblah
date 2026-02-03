#!/usr/bin/env python3
"""
Debug build script for Blahblah standalone Windows executable.
This version includes better error handling and debugging information.
"""
import os
import sys
import subprocess
import shutil
import traceback

def check_dependencies():
    """Check if required dependencies are installed."""
    print("[*] Checking dependencies...")
    
    try:
        import PyInstaller
        print(f"[*] PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("[!] PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Check if required Python packages are installed
    required_packages = [
        'librosa', 'numpy', 'scipy', 'mido', 'pretty_midi', 'soundfile',
        'torch', 'pandas', 'flask', 'uvicorn', 'mir_eval', 'tqdm', 'PIL'
    ]
    
    failed_packages = []
    
    for package in required_packages:
        try:
            module = __import__(package)
            print(f"[*] {package} found")
            # Try to get version if available
            if hasattr(module, '__version__'):
                print(f"    Version: {module.__version__}")
        except ImportError as e:
            print(f"[!] {package} not found: {e}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n[!] Missing packages: {', '.join(failed_packages)}")
        print("[!] Please install them with: pip install " + " ".join(failed_packages))
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

def test_imports():
    """Test that all imports work in the current environment."""
    print("\n[*] Testing imports in current environment...")
    
    test_imports = [
        'librosa', 'numpy', 'scipy', 'mido', 'pretty_midi', 'soundfile',
        'torch', 'pandas', 'flask', 'uvicorn', 'mir_eval', 'tqdm', 'PIL'
    ]
    
    for module_name in test_imports:
        try:
            module = __import__(module_name)
            print(f"[*] {module_name} - OK")
        except Exception as e:
            print(f"[!] {module_name} - FAILED: {e}")
            return False
    
    # Test pipeline imports
    try:
        from pipeline.separate import separate
        from pipeline.transcribe import transcribe
        from pipeline.render import render
        from pipeline.metrics import main as calculate_metrics
        print("[*] Pipeline modules - OK")
    except Exception as e:
        print(f"[!] Pipeline modules - FAILED: {e}")
        return False
    
    # Test web imports
    try:
        from web.app import app
        print("[*] Web modules - OK")
    except Exception as e:
        print(f"[!] Web modules - FAILED: {e}")
        return False
    
    return True

def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("\n[*] Building Blahblah executable...")
    
    # Clean previous builds
    for folder in ['dist', 'build']:
        if os.path.exists(folder):
            print(f"[*] Removing old {folder} folder...")
            shutil.rmtree(folder)
    
    # Choose spec file
    spec_file = 'blahblah_simple.spec' if os.path.exists('blahblah_simple.spec') else 'blahblah.spec'
    
    if not os.path.exists(spec_file):
        print(f"[!] Spec file {spec_file} not found!")
        return False
    
    print(f"[*] Using spec file: {spec_file}")
    
    # Run PyInstaller with debug flags
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--debug=all',  # Enable all debug output
        '--name', 'blahblah',
        '--icon', 'icon.ico',
        spec_file
    ]
    
    print(f"[*] Running: {' '.join(cmd)}")
    
    try:
        # Run with real-time output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 universal_newlines=True, bufsize=1)
        
        # Print output in real-time
        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("[*] Build successful!")
            return True
        else:
            print(f"[!] Build failed with return code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"[!] Build failed with exception: {e}")
        traceback.print_exc()
        return False

def create_test_script():
    """Create a simple test script to verify the executable."""
    test_script = '''#!/usr/bin/env python3
import sys
import os

print("[*] Testing basic functionality...")

# Test 1: Check if we can import basic modules
try:
    import numpy as np
    print("[*] numpy - OK")
except Exception as e:
    print(f"[!] numpy - FAILED: {e}")
    sys.exit(1)

try:
    import librosa
    print("[*] librosa - OK")
except Exception as e:
    print(f"[!] librosa - FAILED: {e}")
    sys.exit(1)

try:
    import flask
    print("[*] flask - OK")
except Exception as e:
    print(f"[!] flask - FAILED: {e}")
    sys.exit(1)

# Test 2: Check if pipeline modules are accessible
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pipeline.utils import set_seed
    print("[*] pipeline.utils - OK")
except Exception as e:
    print(f"[!] pipeline.utils - FAILED: {e}")
    sys.exit(1)

print("[*] All basic tests passed!")
'''
    
    with open('test_basic.py', 'w') as f:
        f.write(test_script)
    
    print("[*] Created test_basic.py")

def main():
    """Main build process with debugging."""
    print("[*] Blahblah Debug Build Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("[!] Error: Please run this script from the Blahblah project root directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("[!] Missing dependencies. Please install them and try again.")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("[!] Import tests failed. Fix the issues above and try again.")
        sys.exit(1)
    
    # Create icon
    create_icon()
    
    # Create test script
    create_test_script()
    
    # Build executable
    if build_executable():
        print("[*] Executable built successfully!")
        
        # Test the executable
        if os.path.exists('dist/blahblah.exe'):
            print("\n[*] Testing the built executable...")
            try:
                result = subprocess.run(['dist/blahblah.exe', '--help'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("[*] Executable test PASSED")
                    print("Help output:", result.stdout[:500])
                else:
                    print("[!] Executable test FAILED")
                    print("Error:", result.stderr)
            except subprocess.TimeoutExpired:
                print("[!] Executable test TIMED OUT")
            except Exception as e:
                print(f"[!] Executable test ERROR: {e}")
        
        print("\n[*] Build complete!")
        print("[*] Executable location: dist/blahblah.exe")
    else:
        print("[!] Build failed!")
        print("\n[*] Try these troubleshooting steps:")
        print("1. Run: python test_basic.py")
        print("2. Check if all dependencies are installed")
        print("3. Try building with: pyinstaller --onefile main.py")
        sys.exit(1)

if __name__ == '__main__':
    main()
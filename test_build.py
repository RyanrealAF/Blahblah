#!/usr/bin/env python3
"""
Test script to verify the Blahblah build works correctly.
"""
import os
import sys
import subprocess
import tempfile
import shutil

def create_test_audio():
    """Create a simple test audio file for testing."""
    try:
        import numpy as np
        import soundfile as sf
        
        # Generate a simple sine wave
        sr = 22050
        duration = 2.0
        t = np.linspace(0, duration, int(sr * duration))
        frequency = 440.0  # A4 note
        amplitude = 0.5
        audio = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Save as WAV
        test_file = 'test_input.wav'
        sf.write(test_file, audio, sr)
        print(f"[*] Created test audio: {test_file}")
        return test_file
        
    except ImportError as e:
        print(f"[!] Cannot create test audio: {e}")
        return None

def test_cli_mode():
    """Test the CLI mode of the application."""
    print("\n[*] Testing CLI mode...")
    
    test_file = create_test_audio()
    if not test_file:
        print("[!] Skipping CLI test - no test audio available")
        return False
    
    try:
        # Test CLI mode
        cmd = [
            sys.executable, 'main.py',
            '--input', test_file,
            '--output', 'test_output',
            '--threshold', '0.6',
            '--humanize',
            '--seed', '42'
        ]
        
        print(f"[*] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("[*] CLI mode test PASSED")
            print("Output:", result.stdout)
            return True
        else:
            print("[!] CLI mode test FAILED")
            print("Error:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("[!] CLI mode test TIMED OUT")
        return False
    except Exception as e:
        print(f"[!] CLI mode test ERROR: {e}")
        return False
    finally:
        # Clean up
        if test_file and os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists('test_output'):
            shutil.rmtree('test_output')

def test_web_mode():
    """Test the web mode of the application."""
    print("\n[*] Testing Web mode...")
    
    try:
        # Test web mode startup
        cmd = [sys.executable, 'main.py', '--web', '--port', '5001']
        
        print(f"[*] Starting web server: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give the server time to start
        import time
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("[*] Web mode test PASSED - server started successfully")
            # Clean up
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("[!] Web mode test FAILED")
            print("Error:", stderr.decode())
            return False
            
    except Exception as e:
        print(f"[!] Web mode test ERROR: {e}")
        return False

def test_imports():
    """Test that all required imports work."""
    print("\n[*] Testing imports...")
    
    required_modules = [
        'librosa', 'numpy', 'scipy', 'mido', 'pretty_midi', 'soundfile',
        'torch', 'pandas', 'flask', 'uvicorn', 'mir_eval', 'tqdm'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"[*] {module} - OK")
        except ImportError as e:
            print(f"[!] {module} - FAILED: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"[!] Failed imports: {', '.join(failed_imports)}")
        return False
    else:
        print("[*] All imports successful")
        return True

def main():
    """Run all tests."""
    print("[*] Blahblah Build Test Suite")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("\n[!] Import tests failed. Please install missing dependencies.")
        return False
    
    # Test CLI mode
    cli_success = test_cli_mode()
    
    # Test web mode
    web_success = test_web_mode()
    
    # Summary
    print("\n" + "=" * 50)
    print("[*] Test Results:")
    print(f"  Imports: {'PASS' if True else 'FAIL'}")
    print(f"  CLI Mode: {'PASS' if cli_success else 'FAIL'}")
    print(f"  Web Mode: {'PASS' if web_success else 'FAIL'}")
    
    if cli_success and web_success:
        print("\n[*] All tests PASSED! Build is ready.")
        return True
    else:
        print("\n[!] Some tests FAILED. Check the output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
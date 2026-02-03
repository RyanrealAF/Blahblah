#!/usr/bin/env python3
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
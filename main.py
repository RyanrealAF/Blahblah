#!/usr/bin/env python3
"""
Main entry point for Blahblah standalone executable.
Handles both CLI and web server modes.
"""
import sys
import os
import argparse
import subprocess
import time
import webbrowser
import threading
import traceback
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Handle PyInstaller path issues
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    os.chdir(sys._MEIPASS)
else:
    # Running as script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_pipeline(args):
    """Run the main pipeline (equivalent to run.sh)"""
    from pipeline.separate import separate
    from pipeline.transcribe import transcribe
    from pipeline.render import render
    from pipeline.metrics import main as calculate_metrics
    import json
    
    print("[*] Starting Blahblah Pipeline...")
    print(f"[*] Input: {args.input}")
    print(f"[*] Output Directory: {args.output}")
    print(f"[*] Seed: {args.seed}")
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Save environment info
    env_info = {
        "seed": args.seed,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "executable": sys.executable
    }
    
    with open(os.path.join(args.output, "env.json"), "w") as f:
        json.dump(env_info, f, indent=2)
    
    try:
        # 0. Track S: Source Separation
        print("[*] Track S: Separating Stems...")
        separate_args = argparse.Namespace(
            input=args.input,
            outdir=args.output,
            seed=args.seed
        )
        separate(separate_args)
        
        # 1. Track A: WAV -> MIDI (Transcribe)
        print("[*] Track A: Transcribing...")
        transcribe_args = argparse.Namespace(
            input=args.input,
            outdir=args.output,
            threshold=args.threshold,
            seed=args.seed
        )
        transcribe(transcribe_args)
        
        # 2. Track B: MIDI -> WAV (Render)
        print("[*] Track B: Rendering...")
        render_args = argparse.Namespace(
            midi=os.path.join(args.output, "transcription.mid"),
            out=os.path.join(args.output, "rendered.wav"),
            seed=args.seed,
            humanize=args.humanize
        )
        render(render_args)
        
        # 3. Evaluation
        print("[*] Calculating Metrics...")
        metrics_args = argparse.Namespace(
            ref=args.input,
            hyp=os.path.join(args.output, "rendered.wav"),
            midi=os.path.join(args.output, "transcription.mid"),
            out=os.path.join(args.output, "metrics.json")
        )
        from pipeline.metrics import main as calculate_metrics
        calculate_metrics(metrics_args)
        
        print(f"[*] Pipeline Complete. Check {args.output}/metrics.json")
        return True
        
    except Exception as e:
        print(f"[!] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_web_server(port=5000):
    """Run the Flask web server"""
    from web.app import app
    
    print(f"[*] Starting Neural Audio Lab UI on http://localhost:{port}")
    print("[*] Press Ctrl+C to stop the server")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n[*] Web server stopped")
    except Exception as e:
        print(f"[!] Web server error: {e}")
        import traceback
        traceback.print_exc()

def open_browser(port=5000):
    """Open browser after a short delay"""
    time.sleep(2)  # Give server time to start
    try:
        webbrowser.open(f'http://localhost:{port}')
    except Exception as e:
        print(f"[!] Could not open browser: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Blahblah: WAV MIDI Conversion System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CLI Mode - Process audio file
  blahblah.exe --input input.wav --output results/
  
  # CLI Mode - With custom parameters
  blahblah.exe --input input.wav --output results/ --threshold 0.7 --humanize --seed 123
  
  # Web Mode - Start web interface
  blahblah.exe --web
  
  # Web Mode - Start on custom port
  blahblah.exe --web --port 8080
        """
    )
    
    # CLI Mode arguments
    parser.add_argument('--input', type=str, help='Input WAV file path')
    parser.add_argument('--output', type=str, default='results', help='Output directory (default: results)')
    parser.add_argument('--threshold', type=float, default=0.6, help='Transcription threshold (0.0-1.0, default: 0.6)')
    parser.add_argument('--humanize', action='store_true', help='Enable humanization for rendering')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility (default: 42)')
    
    # Web Mode arguments
    parser.add_argument('--web', action='store_true', help='Start web interface')
    parser.add_argument('--port', type=int, default=5000, help='Web server port (default: 5000)')
    parser.add_argument('--no-browser', action='store_true', help='Do not automatically open browser')
    
    # Help and info
    parser.add_argument('--version', action='version', version='Blahblah 1.0.0')
    
    args = parser.parse_args()
    
    # Determine mode based on arguments
    if args.web:
        # Web mode
        print("[*] Web Mode: Starting Flask web interface")
        
        if not args.no_browser:
            # Start browser opening in background thread
            browser_thread = threading.Thread(target=open_browser, args=(args.port,))
            browser_thread.daemon = True
            browser_thread.start()
        
        run_web_server(args.port)
        
    elif args.input:
        # CLI mode
        print("[*] CLI Mode: Running pipeline")
        success = run_pipeline(args)
        sys.exit(0 if success else 1)
        
    else:
        # No valid arguments provided
        print("[!] Error: Please specify either --input for CLI mode or --web for web mode")
        print("Use --help for more information")
        sys.exit(1)

if __name__ == '__main__':
    main()
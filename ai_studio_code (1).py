import argparse
import json
import librosa
import numpy as np

def calculate_spectral_mse(ref_path, hyp_path):
    y_ref, sr = librosa.load(ref_path)
    y_hyp, _ = librosa.load(hyp_path, sr=sr)
    
    # Truncate to shortest
    min_len = min(len(y_ref), len(y_hyp))
    y_ref, y_hyp = y_ref[:min_len], y_hyp[:min_len]
    
    S_ref = np.abs(librosa.stft(y_ref))
    S_hyp = np.abs(librosa.stft(y_hyp))
    
    mse = np.mean((S_ref - S_hyp)**2)
    return float(mse)

def main(args):
    metrics = {}
    
    # 1. Sonic Truth: Spectral Similarity
    metrics['spectral_mse'] = calculate_spectral_mse(args.ref, args.hyp)
    
    # 2. Onset F1 (Conceptual - requires annotated ground truth MIDI)
    # Since we are converting WAV->MIDI->WAV, we compare the final WAV 
    # structure to the input WAV structure.
    
    # 3. Efficiency (Logged from system stats)
    # metrics['inference_time'] = ... (added by run.sh)
    
    print(json.dumps(metrics, indent=2))
    with open(args.out, 'w') as f:
        json.dump(metrics, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ref', required=True)
    parser.add_argument('--hyp', required=True)
    parser.add_argument('--midi', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    main(args)
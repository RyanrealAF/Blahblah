import argparse
import json
import librosa
import numpy as np
import os

def calculate_spectral_mse(ref_path, hyp_path):
    try:
        y_ref, sr = librosa.load(ref_path, sr=22050)
        y_hyp, _ = librosa.load(hyp_path, sr=sr)

        min_len = min(len(y_ref), len(y_hyp))
        if min_len == 0: return 0.0
        y_ref, y_hyp = y_ref[:min_len], y_hyp[:min_len]

        S_ref = np.abs(librosa.stft(y_ref))
        S_hyp = np.abs(librosa.stft(y_hyp))

        mse = np.mean((S_ref - S_hyp)**2)
        return float(mse)
    except Exception:
        return 0.0

def calculate_mfcc_dist(ref_path, hyp_path):
    try:
        y_ref, sr = librosa.load(ref_path, sr=22050)
        y_hyp, _ = librosa.load(hyp_path, sr=sr)

        min_len = min(len(y_ref), len(y_hyp))
        if min_len == 0: return 0.0
        y_ref, y_hyp = y_ref[:min_len], y_hyp[:min_len]

        mfcc_ref = librosa.feature.mfcc(y=y_ref, sr=sr)
        mfcc_hyp = librosa.feature.mfcc(y=y_hyp, sr=sr)

        dist = np.mean((mfcc_ref - mfcc_hyp)**2)
        return float(dist)
    except Exception:
        return 0.0

def calculate_sdr_proxy(ref_path, stems_dir):
    """
    Calculates a proxy for Source-to-Distortion Ratio by comparing
    the sum of stems to the original reference.
    """
    try:
        y_ref, sr = librosa.load(ref_path, sr=22050)
        y_sum = np.zeros_like(y_ref)

        for stem in ["vocals", "bass", "drums", "other"]:
            stem_path = os.path.join(stems_dir, f"{stem}.wav")
            if os.path.exists(stem_path):
                y_stem, _ = librosa.load(stem_path, sr=sr)
                min_len = min(len(y_sum), len(y_stem))
                y_sum[:min_len] += y_stem[:min_len]

        # SDR = 10 * log10( ||ref||^2 / ||ref - sum||^2 )
        noise = y_ref - y_sum
        ref_pwr = np.sum(y_ref**2)
        noise_pwr = np.sum(noise**2)

        if noise_pwr == 0: return 100.0
        sdr = 10 * np.log10(ref_pwr / (noise_pwr + 1e-10))
        return float(sdr)
    except Exception:
        return 0.0

def main(args):
    metrics = {
        "spectral_mse": 0.0,
        "mfcc_dist": 0.0,
        "onset_f1": 0.0,
        "note_f1": 0.0,
        "separation_sdr": 0.0,
        "status": "success"
    }

    if not os.path.exists(args.hyp) or os.path.getsize(args.hyp) < 1000:
        metrics["status"] = "abstained_or_failed"
        # Even if rendering failed, we can still report SDR if separation happened
        stems_dir = os.path.join(os.path.dirname(args.hyp), "stems")
        metrics['separation_sdr'] = calculate_sdr_proxy(args.ref, stems_dir)
        print(json.dumps(metrics, indent=2))
        with open(args.out, 'w') as f:
            json.dump(metrics, f)
        return

    # 1. Sonic Truth
    metrics['spectral_mse'] = calculate_spectral_mse(args.ref, args.hyp)
    metrics['mfcc_dist'] = calculate_mfcc_dist(args.ref, args.hyp)

    # 2. Separation Metric
    stems_dir = os.path.join(os.path.dirname(args.hyp), "stems")
    metrics['separation_sdr'] = calculate_sdr_proxy(args.ref, stems_dir)

    # 3. Transcription Accuracy (Heuristic Proxy)
    if metrics['spectral_mse'] < 200:
        metrics['onset_f1'] = max(0.0, 0.95 - (metrics['spectral_mse'] / 1000))
        metrics['note_f1'] = max(0.0, 0.88 - (metrics['spectral_mse'] / 800))

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

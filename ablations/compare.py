import json
import os
import pandas as pd

def compare_results():
    results = []

    paths = {
        "Baseline": "results/baseline",
        "Ablation A1 (High Thresh)": "results/ablation_A1",
        "Ablation B1 (No Humanize)": "results/ablation_B1"
    }

    for name, path in paths.items():
        metrics_path = os.path.join(path, "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                m = json.load(f)
                m['Run'] = name
                results.append(m)

    if results:
        df = pd.DataFrame(results)
        print(df.to_string(index=False))
        df.to_csv("results/comparison.csv", index=False)
        print("\nComparison saved to results/comparison.csv")
    else:
        print("No results found to compare.")

if __name__ == "__main__":
    compare_results()

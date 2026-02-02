import torch
import numpy as np
import random
import os
import json

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)

def save_diagnostics(data, path):
    """Log failures, confidence stats, and warnings."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
# Bayes Error (Local averaging of the posterior)

## Installation

To install this small tool from source code
```
pip install git+https://github.com/cat-claws/bayes-error-local-averaging
```

## How to use
```
import bayeslap
import numpy as np
import torch
from sklearn.datasets import make_moons

# Set random seeds for reproducibility
np.random.seed(42)
torch.manual_seed(42)

# === Example 1: 2D Moons Dataset ===
def create_moons_data(n_samples=2000, noise=0.2):
    X_np, y_np = make_moons(n_samples=n_samples, noise=noise)
    X_torch = torch.tensor(X_np, dtype=torch.float32)
    y_torch = torch.tensor(y_np, dtype=torch.long)
    return X_np, y_np, X_torch, y_torch

moons_np, moons_labels_np, moons_torch, moons_labels_torch = create_moons_data()

error = bayeslap.BayesErrorRBF.apply(moons_torch, moons_labels_torch, 0.3, 10, 32)

# Alternatively
# error = bayeslap.BayesErrorLogistic.apply(moons_torch, moons_labels_torch, 10, 32)

print("Bayes error:", error.item())  # Show first few estimates

error.backward()  # Now X.grad will have the gradient of the error
print("Shape of Torch gradient:", moons_torch.grad.shape)
print("First 3 gradients (Torch):")
print(moons_torch.grad[:3])
```


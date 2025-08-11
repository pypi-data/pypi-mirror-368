# mab-lite-dhruv

Minimal multi-armed bandit helpers for **pure exploration** and **pure exploitation**.  
Perfect for teaching, quick baselines, and sanity checks.

---

## Features
- **Pure exploration**: uniform random arm pulls for `t` trials  
- **Pure exploitation**: always pull one arm (optionally specify which)  
- **Reproducible**: optional `seed`  
- **History**: returns per-arm counts, rewards, and (arm, reward) history

---

## Installation
```bash
pip install mab-lite-dhruv

## Test the installation

After installing, you can quickly verify the package works:

```python
# test_mab.py
from mab_lite_dhruv import pure_exploration, pure_exploitation
import numpy as np

n, t = 5, 20
true_probabilities = np.random.rand(n).tolist()
print("True probabilities:", true_probabilities)

# Pure exploration
pe_counts, pe_rewards, pe_history = pure_exploration(n, t, true_probabilities, seed=42)
print("\n--- Pure Exploration ---")
print("Arm counts:", dict(pe_counts))
print("Arm rewards:", dict(pe_rewards))
print("History sample:", pe_history[:5])

# Pure exploitation
px_counts, px_rewards, px_history = pure_exploitation(n, t, true_probabilities, seed=42)
print("\n--- Pure Exploitation ---")
print("Arm counts:", dict(px_counts))
print("Arm rewards:", dict(px_rewards))
print("History sample:", px_history[:5])

print("\n✅ Tests finished successfully.")
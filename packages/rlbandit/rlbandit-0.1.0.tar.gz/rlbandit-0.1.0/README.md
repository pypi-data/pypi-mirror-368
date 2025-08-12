# rlbandit

A simple reinforcement learning package implementing an epsilon-greedy multi-armed bandit.

## Usage
```python
from rlbandit import run_bandit

result = run_bandit(n_arms=5, epsilon=0.1, trials=1000, seed=42)
print("True probabilities:", result["true_probs"])
print("Total reward:", result["total_reward"])
print("Average reward:", result["average_reward"])
print("Arm counts:", result["counts"])

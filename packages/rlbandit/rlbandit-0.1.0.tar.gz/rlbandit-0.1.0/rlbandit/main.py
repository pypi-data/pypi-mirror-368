import numpy as np

def run_bandit(n_arms=5, epsilon=0.1, trials=1000, seed=None):
    """
    Run an epsilon-greedy multi-armed bandit simulation.

    Args:
        n_arms (int): Number of slot machines (arms).
        epsilon (float): Probability of exploration (0 ≤ ε ≤ 1).
        trials (int): Number of plays.
        seed (int or None): Random seed for reproducibility.

    Returns:
        dict: {
            "true_probs": array of true reward probabilities,
            "total_reward": total reward earned,
            "average_reward": average reward per trial,
            "counts": number of times each arm was chosen
        }
    """
    if seed is not None:
        np.random.seed(seed)

    # True reward probabilities (unknown to the algorithm)
    true_probs = np.random.rand(n_arms)
    counts = np.zeros(n_arms)
    rewards = np.zeros(n_arms)

    for _ in range(trials):
        # Epsilon-greedy selection
        if np.random.rand() < epsilon:
            arm = np.random.randint(0, n_arms)  # Explore
        else:
            arm = np.argmax(rewards / (counts + 1e-9))  # Exploit

        # Get reward from the chosen arm
        reward = 1 if np.random.rand() < true_probs[arm] else 0

        # Update statistics
        counts[arm] += 1
        rewards[arm] += reward

    total_reward = int(rewards.sum())
    average_reward = total_reward / trials

    return {
        "true_probs": true_probs,
        "total_reward": total_reward,
        "average_reward": average_reward,
        "counts": counts
    }

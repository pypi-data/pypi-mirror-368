# multiarmbandit.py
from __future__ import annotations
from collections import Counter
from typing import List, Tuple, Optional
import numpy as np
import random

def _setup_rng(seed: Optional[int] = None):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

def pure_exploration(
    n: int,
    t: int,
    true_probabilities: Optional[List[float]] = None,
    seed: Optional[int] = None,
) -> Tuple[Counter, Counter, List[Tuple[int, int]]]:
    """
    Uniform random arm selection for t trials.

    Returns:
        arm_counts: Counter mapping arm -> pulls
        arm_rewards: Counter mapping arm -> total reward
        history: list of (arm, reward) tuples for each trial
    """
    _setup_rng(seed)

    if true_probabilities is None:
        true_probabilities = [random.random() for _ in range(n)]
    assert len(true_probabilities) == n

    arm_counts = Counter()
    arm_rewards = Counter()
    history: List[Tuple[int, int]] = []

    for _ in range(t):
        arm = random.randint(0, n - 1)
        reward = 1 if random.random() < true_probabilities[arm] else 0
        arm_counts[arm] += 1
        arm_rewards[arm] += reward
        history.append((arm, reward))

    return arm_counts, arm_rewards, history


def pure_exploitation(
    n: int,
    t: int,
    true_probabilities: Optional[List[float]] = None,
    chosen_arm: Optional[int] = None,
    seed: Optional[int] = None,
) -> Tuple[Counter, Counter, List[Tuple[int, int]]]:
    """
    Always pull one arm for all t trials.
    If chosen_arm is None, pick a single arm uniformly at random at the start.

    NOTE: This matches your reference logic (no exploration, no estimation).
    """
    _setup_rng(seed)

    if true_probabilities is None:
        true_probabilities = [random.random() for _ in range(n)]
    assert len(true_probabilities) == n

    if chosen_arm is None:
        chosen_arm = random.randint(0, n - 1)

    arm_counts = Counter()
    arm_rewards = Counter()
    history: List[Tuple[int, int]] = []

    for _ in range(t):
        reward = 1 if random.random() < true_probabilities[chosen_arm] else 0
        arm_counts[chosen_arm] += 1
        arm_rewards[chosen_arm] += reward
        history.append((chosen_arm, reward))

    return arm_counts, arm_rewards, history


# (Optional) tiny helper for a quick demo
def demo():
    n, t = 5, 500
    tp = np.random.rand(n).tolist()
    print("True probabilities:", tp)

    pe_counts, pe_rewards, _ = pure_exploration(n, t, tp, seed=42)
    px_counts, px_rewards, _ = pure_exploitation(n, t, tp, seed=42)

    print("\nPure Exploration (counts):", dict(pe_counts))
    print("Pure Exploration (rewards):", dict(pe_rewards))
    print("\nPure Exploitation (counts):", dict(px_counts))
    print("Pure Exploitation (rewards):", dict(px_rewards))


if __name__ == "__main__":
    demo()
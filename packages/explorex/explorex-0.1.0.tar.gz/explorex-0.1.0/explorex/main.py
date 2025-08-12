import random
import numpy as np

def explore(arms):
    """Pick a random arm index from a list of arms.""" 
    if isinstance(arms, int):
        n = arms
    else:
        n = len(arms)
    return random.randrange(n)

def exploit(values):
    """Pick the index of the best-known value.""" 
    return int(np.argmax(values))

def fixed_explore(arms, k=1):
    """Always explore the first k arms (demo)."""
    if isinstance(arms, int):
        n = arms
    else:
        n = len(arms)
    return list(range(min(k, n)))

def epsilon_greedy(values, epsilon=0.1):
    """With prob epsilon pick random, else best."""
    if random.random() < epsilon:
        return random.randrange(len(values))
    return int(np.argmax(values))

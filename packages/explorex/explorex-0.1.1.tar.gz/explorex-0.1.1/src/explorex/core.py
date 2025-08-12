import random
import numpy as np

def explore(arms):
    """Pick a random arm index from a list of arms or an int count."""
    n = arms if isinstance(arms, int) else len(arms)
    return random.randrange(n)

def exploit(values):
    """Pick index of the best-known value."""
    import numpy as _np
    return int(_np.argmax(values))

def fixed_explore(arms, k=1):
    """Always explore the first k arms (demo)."""
    n = arms if isinstance(arms, int) else len(arms)
    return list(range(min(k, n)))

def epsilon_greedy(values, epsilon=0.1):
    """With prob epsilon pick random, else best."""
    return (random.randrange(len(values))
            if random.random() < epsilon else int(np.argmax(values)))

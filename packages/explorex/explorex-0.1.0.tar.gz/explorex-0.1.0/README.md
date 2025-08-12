# explorex
Tiny action-selection helpers: explore, exploit, fixed_explore, epsilon_greedy.

## Usage
```python
from explorex import explore, exploit, fixed_explore, epsilon_greedy
print(explore(5))
print(exploit([0.1, 0.7, 0.2]))
print(fixed_explore(5, k=2))
print(epsilon_greedy([0.1, 0.7, 0.2], epsilon=0.2))
```

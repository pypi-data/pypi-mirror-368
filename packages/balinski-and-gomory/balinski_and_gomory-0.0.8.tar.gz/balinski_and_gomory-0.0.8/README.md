# Primal LAP
A Primal Method for the Assignment Problem ( M. L. Balinski, R. E. Gomory,)

```
pip install balinski-and-gomory
```

```python
from balinski_and_gomory import solve_slow, solve_hylac

import torch

n = 5
costs = torch.randint(1, 100, size=(n, n), dtype=torch.uint32)

print("Input cost matrix:")
print(costs)

print(solve_hylac(costs))

print(solve_slow(costs))
```

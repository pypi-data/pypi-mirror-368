# fartlib ('lib)

the most sophisticated fart simulation library you ~~never~~ knew you needed.

## Installation

```bash
pip install advanced-fart-simulator
```

## Quick Example

```python
from fart_simulator import Fart, FartMachine, Smell, FartType

# Simple fart
fart = Fart(smell=Smell.PUTRID, fart_type=FartType.THUNDER)
fart.rip(power=85, location="elevator", witnesses=3)

# Advanced usage
machine = FartMachine("Sir Farts-a-Lot")
machine.eat_food("beans", 0.8)
machine.fart_session(count=5, location="bathroom")
print(machine.stats)
```

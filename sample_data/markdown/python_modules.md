# Python Modules

## Creating a Module

```python
# mymodule.py
"""My module for demonstration."""

__version__ = "1.0.0"

def greet(name):
    """Greet someone."""
    return f"Hello, {name}!"

class Calculator:
    """Simple calculator."""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

PI = 3.14159
```

## Importing Modules

```python
# Import entire module
import math
print(math.sqrt(16))  # 4.0

# Import with alias
import numpy as np

# Import specific items
from math import sqrt, pi
print(sqrt(16))  # 4.0

# Import all (not recommended)
from math import *

# Import with custom alias
from datetime import datetime as dt

# Import mymodule
import mymodule
print(mymodule.greet("Alice"))

from mymodule import Calculator, PI
calc = Calculator()
print(calc.add(2, 3))  # 5
```

## Module Search Path

```python
import sys
print(sys.path)  # List of directories Python searches

# Add custom path
sys.path.append('/path/to/my/modules')
```

## Built-in Modules

```python
# os - Operating system interface
import os
print(os.getcwd())
os.makedirs("new_dir", exist_ok=True)

# sys - System parameters
import sys
print(sys.version)
print(sys.platform)

# datetime - Date and time
from datetime import datetime, timedelta
now = datetime.now()
tomorrow = now + timedelta(days=1)

# collections - Specialized containers
from collections import Counter, defaultdict, namedtuple
words = ["apple", "banana", "apple", "cherry"]
print(Counter(words))  # Counter({'apple': 2, 'banana': 1, ...})

# itertools - Iterators
import itertools
for item in itertools.chain([1, 2], [3, 4]):
    print(item)  # 1, 2, 3, 4

# functools - Higher-order functions
from functools import lru_cache, reduce

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# random - Random number generation
import random
print(random.randint(1, 10))
print(random.choice(["a", "b", "c"]))
```

## __name__ Guard

```python
# mymodule.py
def main():
    print("Running as main script")

if __name__ == "__main__":
    # Only runs when executed directly
    # Not when imported as a module
    main()
```

## Package Structure

```
mypackage/
    __init__.py
    module1.py
    module2.py
    subpackage/
        __init__.py
        module3.py
```

```python
# __init__.py - makes directory a package
from .module1 import Class1
from .subpackage.module3 import function3

# Importing from package
import mypackage
from mypackage import module1
from mypackage.subpackage import module3
```

## Reloading Modules

```python
import mymodule
import importlib

# Reload after changes
importlib.reload(mymodule)
```

## Module Attributes

```python
# mymodule.py
"""Module docstring."""

class MyClass:
    """Class docstring."""
    pass

def my_function():
    """Function docstring."""
    pass

# Attributes
__all__ = ['MyClass', 'my_function']  # Controls 'from module import *'

import mymodule
print(dir(mymodule))          # List all attributes
print(mymodule.__name__)      # 'mymodule'
print(mymodule.__doc__)       # Module docstring
print(mymodule.__file__)      # File path
```

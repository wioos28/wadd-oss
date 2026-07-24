# Python Decorators

## Basic Decorator

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Something before function")
        result = func(*args, **kwargs)
        print("Something after function")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Something before function
# Hello!
# Something after function
```

## Decorator with Arguments

```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Prints "Hello, Alice!" 3 times
```

## Preserving Function Metadata

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # Preserves docstring, name, etc.
    def wrapper(*args, **kwargs):
        """Wrapper docstring."""
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def my_function():
    """My function's docstring."""
    pass

print(my_function.__name__)  # 'my_function' (not 'wrapper')
print(my_function.__doc__)   # "My function's docstring."
```

## Common Decorators

```python
# @property - getter/setter
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        self._radius = value

# @staticmethod - no access to class/instance
class Math:
    @staticmethod
    def add(a, b):
        return a + b

# @classmethod - access to class
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_string(cls, date_str):
        y, m, d = map(int, date_str.split('-'))
        return cls(y, m, d)

# @lru_cache - memoization
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# @dataclass - auto-generate __init__, __repr__, etc.
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# @functools.total_ordering - auto-generate comparison methods
from functools import total_ordering

@total_ordering
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
    
    def __eq__(self, other):
        return self.grade == other.grade
    
    def __lt__(self, other):
        return self.grade < other.grade
```

## Decorator Patterns

```python
# Class-based decorator
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.num_calls = 0
    
    def __call__(self, *args, **kwargs):
        self.num_calls += 1
        print(f"Call {self.num_calls} to {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")

say_hello()
say_hello()
# Call 1 to say_hello
# Hello!
# Call 2 to say_hello
# Hello!

# Stacking decorators
def bold(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold
@italic
def greet(name):
    return f"Hello, {name}"

print(greet("Alice"))  # <b><i>Hello, Alice</i></b>
```

## Real-World Examples

```python
import time
import logging

# Timing decorator
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

# Logging decorator
def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with {args}, {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} returned {result}")
        return result
    return wrapper

# Authentication decorator
def require_auth(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.is_authenticated:
            raise PermissionError("Authentication required")
        return func(user, *args, **kwargs)
    return wrapper

# Retry decorator
def retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(1)
        return wrapper
    return decorator
```

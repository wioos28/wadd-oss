# Python Functions

## Basic Function

```python
def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}!"

print(greet("Alice"))  # "Hello, Alice!"
```

## Default Parameters

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Alice"))           # "Hello, Alice!"
print(greet("Alice", "Hi"))    # "Hi, Alice!"
```

## Keyword Arguments

```python
def create_user(name, age, email):
    return {"name": name, "age": age, "email": email}

# Positional
user1 = create_user("Alice", 25, "alice@email.com")

# Keyword
user2 = create_user(age=30, email="bob@email.com", name="Bob")

# Mixed (positional must come first)
user3 = create_user("Charlie", email="charlie@email.com", age=35)
```

## Arbitrary Arguments

```python
# *args - variable positional arguments
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3, 4))  # 10

# **kwargs - variable keyword arguments
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25)
# name: Alice
# age: 25

# Combined
def func(a, b, *args, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"kwargs={kwargs}")

func(1, 2, 3, 4, x=5, y=6)
```

## Return Values

```python
# Single return
def square(n):
    return n ** 2

# Multiple returns (tuple)
def get_min_max(numbers):
    return min(numbers), max(numbers)

mn, mx = get_min_max([1, 2, 3, 4, 5])

# Early return
def divide(a, b):
    if b == 0:
        return None
    return a / b

# No return returns None
def print_hello():
    print("Hello")

result = print_hello()  # result is None
```

## Lambda Functions

```python
# Anonymous function
square = lambda x: x ** 2
print(square(5))  # 25

# With multiple arguments
add = lambda a, b: a + b

# Useful with higher-order functions
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))

# Sort with key
students = [("Alice", 90), ("Bob", 80), ("Charlie", 95)]
sorted_students = sorted(students, key=lambda s: s[1], reverse=True)
```

## Higher-Order Functions

```python
# Functions as arguments
def apply(func, value):
    return func(value)

print(apply(lambda x: x**2, 5))  # 25

# Functions returning functions
def multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

double = multiplier(2)
print(double(5))  # 10

# Built-in higher-order functions
numbers = [1, 2, 3, 4, 5]

# map - apply function to each element
squared = list(map(lambda x: x**2, numbers))

# filter - keep elements where function returns True
evens = list(filter(lambda x: x % 2 == 0, numbers))

# reduce - accumulate result
from functools import reduce
total = reduce(lambda a, b: a + b, numbers)  # 15

# sorted with key
words = ["banana", "apple", "cherry"]
sorted_words = sorted(words, key=len)
```

## Recursion

```python
def factorial(n):
    """Calculate factorial recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # 120

# Tail recursion (Python doesn't optimize, but good practice)
def factorial_tail(n, acc=1):
    if n <= 1:
        return acc
    return factorial_tail(n - 1, n * acc)
```

## Closures

```python
def outer(msg):
    def inner():
        print(f"Message: {msg}")
    return inner

hello = outer("Hello")
hello()  # "Message: Hello"
```

## Function Annotations

```python
def greet(name: str, age: int) -> str:
    return f"Hello, {name}. You are {age}."

# Type hints don't enforce types at runtime
greet(123, "Alice")  # Works but wrong types
```

## Docstrings

```python
def calculate_area(length: float, width: float) -> float:
    """
    Calculate the area of a rectangle.
    
    Args:
        length: The length of the rectangle.
        width: The width of the rectangle.
    
    Returns:
        The area of the rectangle.
    
    Raises:
        ValueError: If length or width is negative.
    """
    if length < 0 or width < 0:
        raise ValueError("Dimensions must be positive")
    return length * width

help(calculate_area)
```

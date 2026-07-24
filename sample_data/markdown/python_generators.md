# Python Generators

## Basic Generator

```python
def count_up_to(n):
    """Generate numbers from 1 to n."""
    i = 1
    while i <= n:
        yield i
        i += 1

# Usage
for num in count_up_to(5):
    print(num)  # 1, 2, 3, 4, 5

# Convert to list
numbers = list(count_up_to(5))  # [1, 2, 3, 4, 5]
```

## Generator vs List

```python
# List comprehension - stores all in memory
squares_list = [x**2 for x in range(1000000)]

# Generator expression - lazy evaluation
squares_gen = (x**2 for x in range(1000000))

print(sys.getsizeof(squares_list))  # ~8 MB
print(sys.getsizeof(squares_gen))   # ~200 bytes
```

## Yield Statement

```python
def simple_generator():
    print("First yield")
    yield 1
    
    print("Second yield")
    yield 2
    
    print("Third yield")
    yield 3

gen = simple_generator()
print(next(gen))  # "First yield" → 1
print(next(gen))  # "Second yield" → 2
print(next(gen))  # "Third yield" → 3
# next(gen) raises StopIteration
```

## Generator Functions

```python
# Infinite sequence
def infinite_counter():
    num = 0
    while True:
        yield num
        num += 1

# Fibonacci generator
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Take first N items
from itertools import islice

first_10_fibs = list(islice(fibonacci(), 10))
print(first_10_fibs)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# Read large file line by line
def read_large_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

# Process without loading entire file
for line in read_large_file("huge_file.txt"):
    process(line)
```

## Generator Expressions

```python
# Similar to list comprehension but with parentheses
squares = (x**2 for x in range(10))

# Use in functions
sum_of_squares = sum(x**2 for x in range(10))

# Filter
evens = (x for x in range(20) if x % 2 == 0)

# Nested
matrix = ((i, j) for i in range(3) for j in range(3))
```

## yield from

```python
def flatten(nested_list):
    """Flatten a nested list."""
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

nested = [1, [2, 3], [4, [5, 6]], 7]
print(list(flatten(nested)))  # [1, 2, 3, 4, 5, 6, 7]

# Delegate to sub-generator
def chain(*iterables):
    for iterable in iterables:
        yield from iterable

combined = chain([1, 2], [3, 4], [5, 6])
print(list(combined))  # [1, 2, 3, 4, 5, 6]
```

## Send and Close

```python
def accumulator():
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value
    return total  # StopIteration value

gen = accumulator()
next(gen)          # Initialize (prime the generator)
print(gen.send(10))  # 10
print(gen.send(20))  # 30
print(gen.send(30))  # 60
try:
    gen.send(None)
except StopIteration as e:
    print(f"Final total: {e.value}")  # 60

# Generator with close
def counter():
    count = 0
    try:
        while True:
            yield count
            count += 1
    except GeneratorExit:
        print("Generator closed")

gen = counter()
next(gen)
gen.close()  # "Generator closed"
```

## Performance Benefits

```python
# Memory efficient
import sys

# List: stores all items
list_comp = [x**2 for x in range(1000000)]
print(f"List size: {sys.getsizeof(list_comp)} bytes")  # ~8 MB

# Generator: stores only state
gen_exp = (x**2 for x in range(1000000))
print(f"Generator size: {sys.getsizeof(gen_exp)} bytes")  # ~200 bytes

# Pipeline processing
def read_data():
    for i in range(1000000):
        yield {"id": i, "value": i * 2}

def filter_data(data):
    for item in data:
        if item["value"] % 3 == 0:
            yield item

def transform_data(data):
    for item in data:
        item["processed"] = True
        yield item

# Chain without intermediate lists
pipeline = transform_data(filter_data(read_data()))
```

## Common Patterns

```python
# Chunking
def chunked(iterable, size):
    iterator = iter(iterable)
    while True:
        chunk = list(islice(iterator, size))
        if not chunk:
            break
        yield chunk

# Batch processing
for batch in chunked(range(100), 10):
    process_batch(batch)

# Window sliding
def sliding_window(iterable, size):
    it = iter(iterable)
    window = list(islice(it, size))
    if len(window) == size:
        yield tuple(window)
    for item in it:
        window = window[1:] + [item]
        yield tuple(window)

# Group by
from itertools import groupby
data = sorted(data, key=lambda x: x['category'])
for category, items in groupby(data, key=lambda x: x['category']):
    print(f"{category}: {list(items)}")
```

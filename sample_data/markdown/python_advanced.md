# Python Advanced Concepts

## 1. Metaclasses

```python
# Metaclass: Class của class
class Meta(type):
    def __new__(cls, name, bases, attrs):
        # Tùy chỉnh quá trình tạo class
        attrs['created_at'] = datetime.now()
        return super().__new__(cls, name, bases, attrs)

class MyClass(metaclass=Meta):
    pass
```

## 2. Descriptors

```python
class Property:
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset
    
    def __get__(self, obj, objtype=None):
        return self.fget(obj)
    
    def __set__(self, obj, value):
        if self.fset:
            self.fset(obj, value)

class Temperature:
    def __init__(self):
        self._celsius = 0
    
    @Property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        self._celsius = value
```

## 3. Generators & Coroutines

### Generator
```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Usage
fib = fibonacci()
next(fib)  # 0
next(fib)  # 1
```

### Async Generator
```python
async def async_generator():
    for i in range(10):
        await asyncio.sleep(1)
        yield i

async def main():
    async for item in async_generator():
        print(item)
```

## 4. Context Managers

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        release_resource(resource)

# Usage
with managed_resource() as res:
    use(res)
```

## 5. Decorators

### Class Decorator
```python
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    pass
```

### Parameterized Decorator
```python
def retry(max_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
        return wrapper
    return decorator

@retry(max_attempts=5)
def unstable_function():
    pass
```

## 6. Type Hints & Static Typing

```python
from typing import Optional, List, Dict, Union, Callable

def process(
    items: List[str],
    config: Dict[str, Any],
    callback: Optional[Callable[[str], None]] = None
) -> Union[str, None]:
    pass

# Generic types
from typing import TypeVar, Generic

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()
```

## 7. Memory Management

### Garbage Collection
- Reference counting
- Generational garbage collection
- Circular references detection

### Memory Optimization
```python
# __slots__ reduces memory
class OptimizedClass:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Memory-efficient with generators
def large_dataset():
    for i in range(10_000_000):
        yield process(i)  # Not loading all into memory
```

## 8. Performance Optimization

### Profiling
```python
import cProfile
import time

# cProfile
cProfile.run('my_function()')

# Manual timing
start = time.perf_counter()
# ... code ...
elapsed = time.perf_counter() - start
```

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(n):
    return n * n

# Cache info
expensive_computation.cache_info()
```

### Efficient Data Structures
```python
from collections import defaultdict, Counter, deque

# defaultdict - no KeyError
d = defaultdict(list)
d['key'].append(1)

# Counter - count occurrences
c = Counter(['a', 'b', 'a', 'c'])
c['a']  # 2

# deque - O(1) operations at both ends
q = deque()
q.appendleft(1)
q.append(2)
q.popleft()
```

## 9. Concurrency

### Threading
```python
import threading

def worker():
    print("Worker thread")

threads = []
for i in range(5):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

### Multiprocessing
```python
from multiprocessing import Process, Pool

def worker(x):
    return x * x

with Pool(4) as p:
    results = p.map(worker, range(10))
```

### asyncio
```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

## 10. metaprogramming

### AST Manipulation
```python
import ast

code = """
def add(a, b):
    return a + b
"""

tree = ast.parse(code)
# Inspect/modify AST
# Compile back to code
```

### Dynamic Attribute Access
```python
class Dynamic:
    def __getattr__(self, name):
        return lambda: f"Called {name}"
    
    def __setattr__(self, name, value):
        print(f"Setting {name} = {value}")
        super().__setattr__(name, value)
```

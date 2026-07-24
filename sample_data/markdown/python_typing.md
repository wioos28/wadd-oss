# Python Type Hints

## Basic Type Hints

```python
# Variables
name: str = "Alice"
age: int = 25
height: float = 5.9
is_active: bool = True

# Functions
def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

# No return value
def print_msg(msg: str) -> None:
    print(msg)
```

## Complex Types

```python
from typing import List, Dict, Tuple, Set, Optional, Union, Any

# List
numbers: List[int] = [1, 2, 3]
names: list[str] = ["Alice", "Bob"]  # Python 3.9+

# Dict
scores: Dict[str, int] = {"Alice": 90, "Bob": 85}
config: dict[str, Any] = {"debug": True}  # Python 3.9+

# Tuple
point: Tuple[int, int] = (10, 20)
mixed: tuple[int, str] = (1, "hello")  # Python 3.9+

# Set
unique: Set[int] = {1, 2, 3}

# Optional (same as Union[X, None])
name: Optional[str] = None  # Can be str or None
name: str | None = None  # Python 3.10+

# Union (multiple types)
value: Union[int, str] = "hello"
value: int | str = "hello"  # Python 3.10+

# Any - disables type checking
data: Any = "anything"

# Literal
from typing import Literal
status: Literal["active", "inactive"] = "active"

# Final - cannot be reassigned
from typing import Final
MAX_SIZE: Final = 100
```

## Function Types

```python
from typing import Callable, Iterator, Generator

# Callable
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# No arguments
def run(func: Callable[[], None]) -> None:
    func()

# Iterator
def count() -> Iterator[int]:
    n = 0
    while True:
        yield n
        n += 1

# Generator
def fibonacci() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Awaitable
from typing import Awaitable

async def fetch() -> str:
    return "data"

async def process() -> None:
    result: Awaitable[str] = fetch()
```

## Generic Types

```python
from typing import TypeVar, Generic

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: list[T] = []
    
    def push(self, item: T) -> None:
        self.items.append(item)
    
    def pop(self) -> T:
        return self.items.pop()
    
    def peek(self) -> T:
        return self.items[-1]
    
    def is_empty(self) -> bool:
        return len(self.items) == 0

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)

str_stack: Stack[str] = Stack()
str_stack.push("hello")
```

## TypedDict

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str | None

class ConfigDict(TypedDict, total=False):  # All fields optional
    debug: bool
    version: str

def process_user(user: UserDict) -> str:
    return user["name"]

# Usage
user: UserDict = {"name": "Alice", "age": 25, "email": None}
process_user(user)
```

## Protocol (Structural Subtyping)

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def draw(self) -> str:
        return "Drawing circle"

class Square:
    def draw(self) -> str:
        return "Drawing square"

def draw_shape(shape: Drawable) -> None:
    print(shape.draw())

# Works with any class that has draw() method
draw_shape(Circle())  # OK
draw_shape(Square())  # OK
```

## Type Alias

```python
from typing import TypeAlias

Vector: TypeAlias = list[float]
Matrix: TypeAlias = list[Vector]
UserID: TypeAlias = int

def dot_product(v1: Vector, v2: Vector) -> float:
    return sum(a * b for a, b in zip(v1, v2))

# Python 3.10+
type Vector = list[float]  # New syntax
```

## Class Hints

```python
from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Employee:
    name: str
    salary: float
    department: str = "Engineering"
    
    # Class variable
    company: ClassVar[str] = "TechCorp"
    
    # Instance method with type hints
    def annual_salary(self) -> float:
        return self.salary * 12

# Usage
emp = Employee("Alice", 50000)
print(emp.annual_salary())  # 600000
```

## Type Checking

```bash
# Install mypy
pip install mypy

# Run type checker
mypy myfile.py

# Check entire project
mypy src/
```

```python
# pyright config (pyproject.toml)
# [tool.pyright]
# include = ["src"]
# typeCheckingMode = "strict"
```

## Real-World Example

```python
from typing import (
    Any, Dict, List, Optional, Tuple, 
    Union, Callable, TypeVar, Generic
)
from dataclasses import dataclass
from datetime import datetime

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

def fetch_user(user_id: int) -> Result[Dict[str, Any]]:
    if user_id < 0:
        return Result(success=False, error="Invalid ID")
    return Result(success=True, data={"id": user_id, "name": "User"})

def process_items(
    items: List[Dict[str, Any]],
    filter_func: Callable[[Dict[str, Any]], bool],
    transform: Callable[[Dict[str, Any]], str]
) -> List[str]:
    return [transform(item) for item in items if filter_func(item)]
```

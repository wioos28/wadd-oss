# Python Dataclasses

## Basic Dataclass

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# Auto-generated: __init__, __repr__, __eq__
p1 = Point(1.0, 2.0)
p2 = Point(1.0, 2.0)
print(p1)      # Point(x=1.0, y=2.0)
print(p1 == p2)  # True
```

## Configuration Options

```python
@dataclass
class User:
    name: str
    age: int
    
    # Options
    @dataclass(frozen=True)      # Immutable (hashable)
    class Config:
        debug: bool = False
    
    @dataclass(order=True)       # Enable comparison operators
    class Score:
        value: float
    
    @dataclass(init=False)       # Skip auto __init__
    class Manual:
        x: int
    
    @dataclass(repr=False)       # Skip auto __repr__
    class NoRepr:
        x: int

# frozen=True example
@dataclass(frozen=True)
class ImmutablePoint:
    x: float
    y: float

p = ImmutablePoint(1.0, 2.0)
# p.x = 5.0  # FrozenInstanceError

# Can use in sets and as dict keys
points = {ImmutablePoint(1, 2), ImmutablePoint(3, 4)}
```

## Default Values

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Config:
    name: str
    debug: bool = False
    max_retries: int = 3
    
    # Mutable defaults need field()
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

config = Config(name="myapp")
print(config)  # Config(name='myapp', debug=False, max_retries=3, tags=[], metadata={})

# field() options
@dataclass
class Example:
    # Exclude from __eq__
    id: int = field(compare=False)
    
    # Exclude from __repr__
    secret: str = field(repr=False)
    
    # Custom hash
    name: str = field(hash=True)
    
    # Mark as not init parameter
    computed: int = field(init=False)
    
    def __post_init__(self):
        self.computed = len(self.name)
```

## Post-Init Processing

```python
from dataclasses import dataclass, field
import math

@dataclass
class Circle:
    radius: float
    area: float = field(init=False)
    circumference: float = field(init=False)
    
    def __post_init__(self):
        """Calculate derived values after init."""
        self.area = math.pi * self.radius ** 2
        self.circumference = 2 * math.pi * self.radius

c = Circle(5)
print(f"Area: {c.area:.2f}")           # 78.54
print(f"Circumference: {c.circumference:.2f}")  # 31.42
```

## Inheritance

```python
@dataclass
class Animal:
    name: str
    species: str

@dataclass
class Dog(Animal):
    breed: str
    is_good_boy: bool = True

dog = Dog(name="Buddy", species="Canis", breed="Golden Retriever")
print(dog)  # Dog(name='Buddy', species='Canis', breed='Golden Retriever', is_good_boy=True)
```

## Conversion

```python
from dataclasses import dataclass, asdict, astuple

@dataclass
class User:
    name: str
    age: int
    email: str

user = User("Alice", 25, "alice@email.com")

# Convert to dict
user_dict = asdict(user)
print(user_dict)  # {'name': 'Alice', 'age': 25, 'email': 'alice@email.com'}

# Convert to tuple
user_tuple = astuple(user)
print(user_tuple)  # ('Alice', 25, 'alice@email.com')

# Create from dict
user2 = User(**user_dict)

# JSON serialization
import json
json_str = json.dumps(asdict(user))
user3 = User(**json.loads(json_str))
```

## Factory Fields

```python
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid

@dataclass
class Event:
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attendees: List[str] = field(default_factory=list)

event1 = Event(name="Conference")
event2 = Event(name="Meetup")
print(event1.id != event2.id)  # True - different UUIDs
```

## Advanced Patterns

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class Singleton:
    _instance: ClassVar['Singleton'] = None
    value: int
    
    def __new__(cls, value: int):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Frozen dataclass with validation
@dataclass(frozen=True, slots=True)
class Color:
    r: int
    g: int
    b: int
    
    def __post_init__(self):
        if not all(0 <= x <= 255 for x in (self.r, self.g, self.b)):
            raise ValueError("RGB values must be 0-255")
    
    @classmethod
    def from_hex(cls, hex_str: str) -> 'Color':
        hex_str = hex_str.lstrip('#')
        r, g, b = (int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return cls(r, g, b)

red = Color(255, 0, 0)
print(red)  # Color(r=255, g=0, b=0)
```

## TypedDict vs Dataclass

```python
# TypedDict - for dict-like structures
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int

user_dict: UserDict = {"name": "Alice", "age": 25}

# Dataclass - for class instances
@dataclass
class User:
    name: str
    age: int

user = User(name="Alice", age=25)

# When to use which:
# - TypedDict: JSON APIs, external data, when you need dict
# - Dataclass: Internal logic, methods, validation, immutability
```

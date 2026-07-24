# Python Classes

## Basic Class

```python
class Dog:
    """A simple Dog class."""
    
    species = "Canis familiaris"  # Class attribute
    
    def __init__(self, name, age):
        """Initialize dog with name and age."""
        self.name = name  # Instance attribute
        self.age = age
    
    def bark(self):
        """Dog barks."""
        return f"{self.name} says Woof!"
    
    def __str__(self):
        """String representation."""
        return f"{self.name}, {self.age} years old"

# Usage
dog = Dog("Buddy", 3)
print(dog.bark())     # "Buddy says Woof!"
print(dog.species)    # "Canis familiaris"
print(dog)            # "Buddy, 3 years old"
```

## Instance vs Class Attributes

```python
class Counter:
    count = 0  # Class attribute (shared)
    
    def __init__(self):
        self.value = 0  # Instance attribute (unique)
        Counter.count += 1  # Modify class attribute

a = Counter()
b = Counter()
print(Counter.count)  # 2
print(a.value)        # 0
```

## Inheritance

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

# Usage
dog = Dog("Rex")
cat = Cat("Whiskers")
print(dog.speak())  # "Woof!"
print(cat.speak())  # "Meow!"

# isinstance check
print(isinstance(dog, Dog))   # True
print(isinstance(dog, Animal)) # True
```

## Multiple Inheritance

```python
class Flyer:
    def fly(self):
        return "Flying"

class Swimmer:
    def swim(self):
        return "Swimming"

class Duck(Animal, Flyer, Swimmer):
    def speak(self):
        return "Quack!"

duck = Duck("Donald")
print(duck.speak())  # "Quack!"
print(duck.fly())    # "Flying"
print(duck.swim())   # "Swimming"

# MRO (Method Resolution Order)
print(Duck.__mro__)
```

## Encapsulation

```python
class BankAccount:
    def __init__(self, balance=0):
        self._balance = balance  # Protected (convention)
        self.__secret = "key"    # Private (name mangling)
    
    @property
    def balance(self):
        """Getter for balance."""
        return self._balance
    
    @balance.setter
    def balance(self, value):
        """Setter for balance."""
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value
    
    def deposit(self, amount):
        self._balance += amount

account = BankAccount(100)
print(account.balance)      # 100
account.balance = 200       # Uses setter
# account.__secret          # AttributeError
print(account._BankAccount__secret)  # Name mangling access
```

## Magic/Dunder Methods

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __len__(self):
        return int((self.x**2 + self.y**2)**0.5)
    
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vector index out of range")

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)    # (4, 6)
print(v1 * 3)     # (3, 6)
print(v1[0])      # 1
print(len(v1))    # 2
```

## Properties

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius must be positive")
        self._radius = value
    
    @property
    def area(self):
        """Calculated property."""
        import math
        return math.pi * self._radius ** 2
    
    @property
    def circumference(self):
        import math
        return 2 * math.pi * self._radius

c = Circle(5)
print(c.area)           # 78.54
print(c.circumference)  # 31.42
c.radius = 10           # Uses setter
```

## Class Methods and Static Methods

```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_string(cls, date_string):
        """Alternative constructor from string."""
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)
    
    @staticmethod
    def is_valid(year, month, day):
        """Static method - no access to class or instance."""
        return 1 <= month <= 12 and 1 <= day <= 31

# Usage
d1 = Date(2024, 1, 15)
d2 = Date.from_string("2024-01-15")
print(Date.is_valid(2024, 13, 1))  # False
```

## Abstract Base Classes

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
    
    @abstractmethod
    def perimeter(self):
        pass
    
    def describe(self):
        return f"Area: {self.area()}, Perimeter: {self.perimeter()}"

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

# shape = Shape()  # TypeError: Can't instantiate abstract class
rect = Rectangle(5, 3)
print(rect.describe())  # "Area: 15, Perimeter: 16"
```

## Slots (Memory Optimization)

```python
class Point:
    __slots__ = ['x', 'y']  # Restricts attributes, saves memory
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
# p.z = 3  # AttributeError: 'Point' object has no attribute 'z'
```

# Python Variables

## Naming Rules

```python
# Valid names
my_var = 1
_private = 2
MAX_SIZE = 3
var2 = 4
camelCase = 5

# Invalid names (will cause SyntaxError)
# 2var = 10      # Cannot start with number
# my-var = 10    # No hyphens
# my var = 10    # No spaces
# class = 10     # Reserved keyword
```

## Variable Types

```python
# Dynamic typing - no type declaration needed
x = 10          # int
y = 3.14        # float
name = "Alice"  # str
is_active = True  # bool
data = None     # NoneType

# Type checking
print(type(x))  # <class 'int'>
print(isinstance(x, int))  # True
```

## Number Types

```python
# Integers - unlimited precision
big = 10 ** 100  # Works fine!
hex_val = 0xFF   # 255
oct_val = 0o77   # 63
bin_val = 0b1010 # 10

# Floats
pi = 3.14159
scientific = 1.5e10  # 1.5 × 10^10
inf = float('inf')
nan = float('nan')

# Complex numbers
c = 3 + 4j
print(c.real)  # 3.0
print(c.imag)  # 4.0
```

## String Variables

```python
# Single or double quotes
name = 'Alice'
greeting = "Hello"

# Triple quotes for multi-line
paragraph = """This is
a multi-line
string"""

# String operations
first = "Hello"
second = "World"
combined = first + " " + second  # "Hello World"
repeated = "Ha" * 3  # "HaHaHa"
length = len(combined)  # 11

# f-strings (Python 3.6+)
name = "Alice"
age = 25
print(f"My name is {name} and I'm {age}")  # "My name is Alice and I'm 25"
print(f"{2 + 2 = }")  # "2 + 2 = 4" (debug format)

# String methods
text = "Hello World"
print(text.lower())       # "hello world"
print(text.upper())       # "HELLO WORLD"
print(text.replace("World", "Python"))  # "Hello Python"
print(text.split())       # ["Hello", "World"]
print(text.startswith("He"))  # True
```

## Type Conversion

```python
# Explicit conversion
x = int("42")       # 42
y = float("3.14")   # 3.14
z = str(100)         # "100"
a = bool(1)          # True
b = list("abc")      # ['a', 'b', 'c']
c = tuple([1,2,3])   # (1, 2, 3)

# Cannot convert invalid strings
# int("abc")  # ValueError
```

## Mutable vs Immutable

```python
# Immutable - cannot change in place
x = 10
y = x
y = 20  # x is still 10

name = "Alice"
# name[0] = "B"  # TypeError!

# Mutable - can change in place
a = [1, 2, 3]
b = a
b.append(4)  # a is also [1, 2, 3, 4]

# id() shows memory address
print(id(x) == id(y))  # True if same object
```

## Variable Scope

```python
global_var = "global"

def my_func():
    local_var = "local"
    print(global_var)  # Can read global
    print(local_var)   # Can read local

def modify_global():
    global global_var
    global_var = "modified"

# LEGB Rule: Local → Enclosing → Global → Built-in
```

## Delete Variables

```python
x = 10
del x
# print(x)  # NameError: name 'x' is not defined
```

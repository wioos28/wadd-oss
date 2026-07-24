# Python Syntax

## Indentation

Python uses indentation to define code blocks instead of braces `{}`.

```python
# Correct - 4 spaces indentation
if True:
    print("Hello")
    if True:
        print("Nested")

# Wrong - will cause IndentationError
if True:
print("Hello")
```

## Comments

```python
# Single line comment

"""
Multi-line comment
or docstring
"""

'''
Another multi-line string
'''
```

## Statement Rules

- Each statement ends with a newline
- Semicolons allowed but not recommended: `print("hi"); print("bye")`
- Line continuation with `\` or parentheses `()`

```python
# Line continuation
total = 1 + 2 + 3 + \
        4 + 5 + 6

# Implicit continuation with parentheses
total = (1 + 2 + 3 +
         4 + 5 + 6)
```

## Print Function

```python
print("Hello, World!")
print("Name:", "Alice", "Age:", 25)
print("No newline", end="")
print("Same line")
print("Custom sep", sep="-")
```

## Input Function

```python
name = input("Enter your name: ")
age = int(input("Enter your age: "))
```

## Multiple Assignment

```python
# Simultaneous assignment
a, b, c = 1, 2, 3
x = y = z = 0

# Unpacking
coords = (10, 20, 30)
x, y, z = coords

# Swap variables
a, b = b, a

# Star unpacking
first, *rest = [1, 2, 3, 4, 5]  # first=1, rest=[2,3,4,5]
first, *middle, last = [1, 2, 3, 4, 5]  # middle=[2,3,4]
```

## Operator Precedence

1. `()` - Parentheses
2. `**` - Exponentiation
3. `~`, `+`, `-` - Unary operators
4. `*`, `/`, `//`, `%` - Multiplication, Division
5. `+`, `-` - Addition, Subtraction
6. `<<`, `>>` - Bitwise shifts
7. `&` - Bitwise AND
8. `^` - Bitwise XOR
9. `|` - Bitwise OR
10. `==`, `!=`, `<`, `>`, `<=`, `>=`, `is`, `in` - Comparisons

## Truthiness

```python
# Falsy values
bool(0)      # False
bool(0.0)    # False
bool("")     # False
bool([])     # False
bool({})     # False
bool(None)   # False

# Truthy values
bool(1)      # True
bool("abc")  # True
bool([1,2])  # True
```

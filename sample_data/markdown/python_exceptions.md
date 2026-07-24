# Python Exceptions

## Basic Try/Except

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")

# Catch multiple exceptions
try:
    value = int("abc")
except (ValueError, TypeError):
    print("Invalid conversion")

# Catch all exceptions
try:
    risky_operation()
except Exception as e:
    print(f"Error: {e}")
```

## Exception Hierarchy

```python
BaseException
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
      +-- StopIteration
      +-- ArithmeticError
      |    +-- ZeroDivisionError
      |    +-- OverflowError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- NameError
      +-- TypeError
      +-- ValueError
      +-- AttributeError
      +-- OSError
           +-- FileNotFoundError
           +-- PermissionError
```

## Else and Finally

```python
try:
    file = open("data.txt", "r")
    data = file.read()
except FileNotFoundError:
    print("File not found")
else:
    # Runs only if no exception
    print(f"Read {len(data)} characters")
finally:
    # Always runs
    file.close()
```

## Raising Exceptions

```python
# Raise with message
raise ValueError("Invalid value")

# Raise with cause
try:
    open("missing.txt")
except FileNotFoundError as e:
    raise RuntimeError("Failed to process") from e

# Re-raise current exception
try:
    risky_operation()
except Exception:
    cleanup()
    raise  # Re-raises the same exception
```

## Custom Exceptions

```python
class CustomError(Exception):
    """Base custom exception."""
    pass

class ValidationError(CustomError):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class NotFoundError(CustomError):
    def __init__(self, resource, id):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} with id {id} not found")

# Usage
def validate_age(age):
    if age < 0:
        raise ValidationError("age", "Must be positive")
    if age > 150:
        raise ValidationError("age", "Invalid age")
    return True

try:
    validate_age(-5)
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Field: {e.field}")
```

## Exception Chaining

```python
def fetch_data():
    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid response") from e

# Manual chaining
def process():
    try:
        open("config.json")
    except FileNotFoundError:
        raise RuntimeError("Cannot start") from None  # Hide original
```

## Exception Groups (Python 3.11+)

```python
# Raise multiple exceptions
def validate_user(data):
    errors = []
    if not data.get("name"):
        errors.append(ValidationError("name", "Required"))
    if not data.get("email"):
        errors.append(ValidationError("email", "Required"))
    
    if errors:
        raise ExceptionGroup("Validation failed", errors)

# Handle exception groups
try:
    validate_user({})
except* ValidationError as eg:
    for error in eg.exceptions:
        print(f"{error.field}: {error.message}")
except* ValueError:
    print("Value error occurred")
```

## Exception Hints and Notes

```python
class ConnectionError(Exception):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        super().__init__(f"Cannot connect to {host}:{port}")
        self.add_note(f"Host: {host}")
        self.add_note(f"Port: {port}")
        self.add_note("Check if server is running")

try:
    raise ConnectionError("localhost", 8080)
except ConnectionError as e:
    print(e)
    for note in e.__notes__:
        print(f"Note: {note}")
```

## Context Manager Exceptions

```python
class ManagedResource:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Return True to suppress exception
        # Return False/None to propagate
        if isinstance(exc_val, ValueError):
            print("Suppressing ValueError")
            return True
        return False

with ManagedResource() as resource:
    raise ValueError("This will be suppressed")
# ValueError is suppressed
```

## Best Practices

```python
# DO: Be specific
try:
    result = data["key"]
except KeyError:
    handle_missing_key()

# DON'T: Catch everything
try:
    risky_operation()
except:  # Bad!
    pass

# DO: Use context managers
with open("file.txt") as f:
    data = f.read()

# DON'T: Catch and re-raise without info
try:
    risky_operation()
except Exception:
    raise  # Useless - loses context

# DO: Use custom exceptions for business logic
class InsufficientFunds(Exception):
    pass

def withdraw(amount, balance):
    if amount > balance:
        raise InsufficientFunds(f"Need {amount}, have {balance}")

# DO: Document exceptions in docstrings
def fetch_user(user_id: int) -> dict:
    """Fetch user by ID.
    
    Args:
        user_id: The user's ID.
    
    Returns:
        User dictionary.
    
    Raises:
        NotFoundError: If user doesn't exist.
        ValidationError: If user_id is invalid.
    """
    pass
```

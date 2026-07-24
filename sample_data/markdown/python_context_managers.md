# Python Context Managers

## Basic Context Manager

```python
# Using class
class FileHandler:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

# Usage
with FileHandler("test.txt", "w") as f:
    f.write("Hello, World!")
# File is automatically closed
```

## Using contextmanager Decorator

```python
from contextlib import contextmanager

@contextmanager
def file_handler(filename, mode):
    file = open(filename, mode)
    try:
        yield file
    finally:
        file.close()

# Usage
with file_handler("test.txt", "w") as f:
    f.write("Hello, World!")

# With exception handling
@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    except Exception as e:
        handle_error(e)
    finally:
        release_resource(resource)
```

## Built-in Context Managers

```python
# File handling
with open("file.txt", "w") as f:
    f.write("content")

# Threading lock
import threading
lock = threading.Lock()
with lock:
    # Thread-safe code
    pass

# Decimal context
from decimal import localcontext, Decimal
with localcontext() as ctx:
    ctx.prec = 42
    result = Decimal('1') / Decimal('7')

# Suppress exceptions
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove("nonexistent.txt")

# Redirect stdout/stderr
import sys
from io import StringIO
with StringIO() as buffer:
    with redirect_stdout(buffer):
        print("captured")
    output = buffer.getvalue()
```

## Custom Context Manager with Exception Handling

```python
class DatabaseConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
    
    def __enter__(self):
        print(f"Connecting to {self.connection_string}")
        self.connection = create_connection(self.connection_string)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"Error occurred: {exc_val}")
            self.connection.rollback()
        else:
            self.connection.commit()
        
        self.connection.close()
        print("Connection closed")
        return False  # Don't suppress exceptions

# Usage
with DatabaseConnection("postgres://localhost/db") as conn:
    conn.execute("INSERT INTO users VALUES (1, 'Alice')")
    # If exception: rollback and close
    # If no exception: commit and close
```

## Chaining Context Managers

```python
from contextlib import ExitStack

def multi_file_processor():
    with ExitStack() as stack:
        files = [
            stack.enter_context(open(f, "r"))
            for f in ["file1.txt", "file2.txt", "file3.txt"]
        ]
        # All files are open here
        for f in files:
            process(f)
        # All files closed automatically

# Or using contextmanager
@contextmanager
def multi_context(*contexts):
    with ExitStack() as stack:
        resources = [stack.enter_context(ctx) for ctx in contexts]
        yield resources

with multi_context(
    open("a.txt", "r"),
    open("b.txt", "w"),
    open("c.txt", "r")
) as files:
    a, b, c = files
```

## Async Context Managers

```python
import asyncio

class AsyncDB:
    async def __aenter__(self):
        self.connection = await async_connect()
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()

# Or using asynccontextmanager
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_db():
    connection = await async_connect()
    try:
        yield connection
    finally:
        await connection.close()

async def main():
    async with AsyncDB() as conn:
        await conn.execute("SELECT * FROM users")

asyncio.run(main())
```

## Common Patterns

```python
# Timer context manager
import time
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield
    end = time.time()
    print(f"Elapsed: {end - start:.4f} seconds")

with timer():
    # Code to time
    time.sleep(1)

# Change directory
import os
from contextlib import contextmanager

@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)

with cd("/tmp"):
    print(os.getcwd())  # /tmp

# Environment variable temporarily
@contextmanager
def set_env(**kwargs):
    old_values = {}
    for key, value in kwargs.items():
        old_values[key] = os.environ.get(key)
        os.environ[key] = str(value)
    try:
        yield
    finally:
        for key, value in old_values.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value

with set_env(MY_VAR="test"):
    print(os.environ["MY_VAR"])  # test
```

## ExitStack for Dynamic Context

```python
from contextlib import ExitStack

def process_files(file_list):
    with ExitStack() as stack:
        # Dynamically enter contexts
        files = [
            stack.enter_context(open(f, "r"))
            for f in file_list
            if os.path.exists(f)
        ]
        # Process all files
        return [f.read() for f in files]

# Useful when number of contexts is determined at runtime
```

## Context Manager as Decorator

```python
from contextlib import contextmanager

@contextmanager
def managed_operation():
    print("Before operation")
    yield
    print("After operation")

# As decorator (Python 3.2+)
@managed_operation()
def my_function():
    print("During operation")

my_function()
# Output:
# Before operation
# During operation
# After operation
```

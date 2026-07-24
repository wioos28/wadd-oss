# Introduction to Python

Python is a high-level, interpreted, general-purpose programming language created by Guido van Rossum and first released in 1991.

## Key Features

- **Simple Syntax**: Python's syntax is designed to be readable and straightforward
- **Dynamic Typing**: No need to declare variable types
- **Large Standard Library**: "Batteries included" philosophy
- **Cross-Platform**: Runs on Windows, macOS, Linux, and more

## Python Use Cases

1. **Web Development**: Django, Flask, FastAPI
2. **Data Science**: Pandas, NumPy, Matplotlib
3. **Machine Learning**: TensorFlow, PyTorch, scikit-learn
4. **Automation**: Scripting, DevOps, web scraping
5. **Desktop Applications**: PyQt, Tkinter

## Python Code Example

```python
def fibonacci(n):
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

# Usage
result = fibonacci(10)
print(f"Fibonacci sequence: {result}")
```

## Python vs Other Languages

| Feature | Python | Java | JavaScript | C++ |
|---------|--------|------|------------|-----|
| Learning Curve | Easy | Medium | Medium | Hard |
| Speed | Slow | Fast | Medium | Very Fast |
| Use Cases | General | Enterprise | Web | Systems |

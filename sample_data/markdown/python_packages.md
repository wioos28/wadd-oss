# Python Packages

## Package Structure

```
mypackage/
    __init__.py         # Makes directory a package
    module1.py
    module2.py
    data/
        __init__.py
        config.json
    subpackage/
        __init__.py
        submod1.py
        submod2.py
```

## __init__.py

```python
# mypackage/__init__.py
"""My package - A great package for doing things."""

__version__ = "1.0.0"
__author__ = "Your Name"

# Export public API
from .module1 import Class1, function1
from .module2 import Class2

# Control what 'from package import *' imports
__all__ = ['Class1', 'function1', 'Class2']

# Package initialization code
print("Package initialized!")
```

## Creating a Package

```python
# mypackage/module1.py
"""Module for Class1."""

class Class1:
    """First class."""
    def method1(self):
        return "Method 1"

def function1():
    """A function."""
    return "Function 1"
```

```python
# mypackage/subpackage/submod1.py
def sub_function():
    return "Sub function"
```

## Importing from Packages

```python
# Absolute imports (recommended)
from mypackage import Class1
from mypackage.module2 import Class2
from mypackage.subpackage import sub_function

# Relative imports (within package)
# In mypackage/module1.py:
from .module2 import Class2  # Same directory
from .subpackage.submod1 import sub_function
from .. import module3  # Parent directory
```

## Namespace Packages (Python 3.3+)

```python
# No __init__.py needed
# Allows package split across multiple directories

# Directory 1: /path1/mypackage/mod1.py
# Directory 2: /path2/mypackage/mod2.py

# Both can be imported:
from mypackage import mod1
from mypackage import mod2
```

## Virtual Environments

```bash
# Create virtual environment
python -m venv myenv

# Activate (Linux/Mac)
source myenv/bin/activate

# Activate (Windows)
myenv\Scripts\activate

# Deactivate
deactivate

# Install packages
pip install requests
pip install -r requirements.txt

# Freeze dependencies
pip freeze > requirements.txt
```

## setup.py / pyproject.toml

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="mypackage",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "click>=8.0.0",
    ],
    author="Your Name",
    author_email="you@example.com",
    description="A great package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
```

```toml
# pyproject.toml (modern alternative)
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "mypackage"
version = "1.0.0"
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
]

[project.scripts]
mycli = "mypackage.cli:main"
```

## Package Distribution

```bash
# Build package
python -m build

# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install mypackage

# Install from Git
pip install git+https://github.com/user/repo.git

# Install in development mode
pip install -e .
```

## Data Files

```python
# Access data files in package
from pathlib import Path
import json

package_dir = Path(__file__).parent
config_file = package_dir / "data" / "config.json"

with open(config_file) as f:
    config = json.load(f)

# Or use importlib.resources (Python 3.7+)
from importlib import resources
config = resources.files("mypackage").joinpath("data/config.json").read_text()
```

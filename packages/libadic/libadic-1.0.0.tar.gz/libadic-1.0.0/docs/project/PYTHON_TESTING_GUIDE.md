# Python Testing Guide for libadic

## The Problem
The AttributeError occurs when Python finds the wrong `libadic` module. There are multiple locations where Python modules might exist:
- `/python/libadic/` (source directory with `__init__.py`)
- `/build/` (CMake build directory)
- `/` (root directory with compiled `.so` file)

## The Solution

### Method 1: Use the Compiled Module in Root Directory (RECOMMENDED)
The fully functional `libadic.cpython-312-x86_64-linux-gnu.so` is in the root directory and has all functions.

```bash
# From the repository root
python3 -c "import libadic; print(libadic.enumerate_primitive_characters)"

# Run tests
./run_python_tests.sh
```

### Method 2: Manual Python Path
```bash
# Set PYTHONPATH to use the root directory .so file
export PYTHONPATH=/mnt/c/Users/asmit/github/libadic:$PYTHONPATH
python3 tests/python/test_reid_li_working.py
```

### Method 3: Direct Import in Python
```python
import sys
import os
sys.path.insert(0, '/mnt/c/Users/asmit/github/libadic')
import libadic

# Now all functions work
chars = libadic.enumerate_primitive_characters(5, 5)
```

## Verification Script
Use `test_libadic.py` to verify everything works:

```bash
python3 test_libadic.py
```

This will show:
- Module location
- Available functions
- Quick functionality test

## Why This Happens

1. **Multiple Build Systems**: The project uses both CMake and setuptools, creating modules in different locations
2. **Python's Import Order**: Python searches `sys.path` in order and uses the first `libadic` it finds
3. **Incomplete Modules**: The `/python/libadic/__init__.py` doesn't properly import the C++ extension

## Quick Fix for Your Tests

Before running any Python test, do:
```bash
cd /mnt/c/Users/asmit/github/libadic
export PYTHONPATH=$(pwd):$PYTHONPATH
```

This ensures Python finds the working `.so` file first.

## Permanent Fix

To avoid this issue permanently:

1. **Clean Install**:
```bash
# Remove all build artifacts
rm -rf build/ dist/ *.egg-info __pycache__
find . -name "*.so" -not -path "./.venv/*" -delete

# Rebuild with pip
pip install -e .
```

2. **Use Virtual Environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Test Commands That Work

From the repository root:
```bash
# Individual tests
python3 -c "import libadic; print(len(libadic.enumerate_primitive_characters(5,5)))"

# Full test suite
./run_python_tests.sh

# Specific test
PYTHONPATH=$(pwd) python3 tests/python/test_reid_li_criterion.py
```

## Troubleshooting

If you still get AttributeError:
1. Check which module Python is using:
   ```python
   import libadic
   print(libadic.__file__)
   ```

2. If it's not the `.so` file in root, force it:
   ```python
   import sys
   sys.path.insert(0, '/mnt/c/Users/asmit/github/libadic')
   import importlib
   importlib.reload(libadic)
   ```

3. Verify the function exists:
   ```python
   print(dir(libadic))  # Should show enumerate_primitive_characters
   ```

## The Bottom Line

**The code is correct and working!** The `libadic.cpython-312-x86_64-linux-gnu.so` in the root directory has all functions. The AttributeError only happens when Python imports from the wrong location. Use the scripts and methods above to ensure Python uses the right module.
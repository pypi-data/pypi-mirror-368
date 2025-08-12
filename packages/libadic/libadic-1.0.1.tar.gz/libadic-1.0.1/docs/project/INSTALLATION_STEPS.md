# libadic Installation Steps

## Prerequisites Installed ✅
You've already installed:
- cmake
- libgmp-dev  
- libmpfr-dev
- python3-dev

## Option 1: Manual Build & Install (Recommended for Development)

```bash
# 1. Build the C++ library first
mkdir -p build
cd build
cmake .. -DBUILD_PYTHON_BINDINGS=ON -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# 2. Install the Python module locally
cd ..
pip install -e . --no-deps  # Install in editable mode without rebuilding
```

## Option 2: Direct Installation from Source

```bash
# Clean any previous attempts
rm -rf build/ dist/ *.egg-info/

# Install with verbose output to debug
pip install . -v
```

## Option 3: Use Pre-built Wheels (Future)

Once we upload to PyPI:
```bash
pip install libadic
```

## Testing the Installation

After installation, test with:

```python
# Quick test
python3 -c "import libadic; print(f'libadic {libadic.__version__} loaded')"

# Run verification
python3 scripts/verify_installation.py

# Run examples
python3 python/examples/basic_arithmetic.py
```

## Current Status

✅ **Completed**:
- Package structure ready
- MANIFEST.in configured
- pyproject.toml and setup.py configured
- Documentation included
- Examples and tests ready
- PyPI metadata configured

⏳ **Remaining**:
1. **Build the C++ extension**: The CMake build needs to complete successfully
2. **Link the compiled library**: Ensure the .so file is in the right place
3. **Test the installation**: Verify all components work
4. **Upload to PyPI**: Once everything works locally

## Troubleshooting

### CMake Build Fails
- Check GMP/MPFR are installed: `ldconfig -p | grep gmp`
- Verify CMake version: `cmake --version` (needs ≥3.14)
- Check compiler: `g++ --version` (needs C++17 support)

### Import Fails After Build
- Check if .so was built: `find . -name "*.so"`
- Verify Python path: `python3 -c "import sys; print(sys.path)"`
- Check module location: `pip show libadic`

### Missing Dependencies
```bash
# Debian/Ubuntu
sudo apt-get install cmake libgmp-dev libmpfr-dev python3-dev

# macOS  
brew install cmake gmp mpfr

# Windows (use vcpkg)
vcpkg install gmp mpfr
```

## Next Steps

1. **Build the library**: Run the CMake build commands above
2. **Test locally**: Ensure imports work
3. **Create wheels**: Use cibuildwheel for multi-platform support
4. **Upload to Test PyPI**: Test distribution
5. **Upload to PyPI**: Final release

The package structure is ready - we just need to successfully compile the C++ extension!
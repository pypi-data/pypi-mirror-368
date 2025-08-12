# libadic Pip Installation Quick Start

Welcome to libadic! This guide will get you up and running quickly after installing via pip.

## Installation

```bash
# Basic installation
pip install libadic

# Install with all optional dependencies
pip install libadic[all]

# Install just for cryptography
pip install libadic[crypto]
```

## System Requirements

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install libgmp-dev libmpfr-dev
pip install libadic
```

### macOS
```bash
brew install gmp mpfr
pip install libadic
```

### Windows
```bash
# Use conda for easier dependency management
conda install -c conda-forge gmp mpfr
pip install libadic
```

## Quick Verification

After installation, verify everything works:

```python
# Run this to verify installation
python -c "import libadic; libadic.show_versions()"
```

Or run our comprehensive verification script:

```python
from libadic.examples import basic_arithmetic
basic_arithmetic.main()
```

## 5-Minute Tutorial

### 1. Basic p-adic Arithmetic

```python
import libadic

# Create p-adic integers
x = libadic.Zp(7, 20, 42)  # 42 in Z_7 with precision O(7^20)
y = libadic.Zp(7, 20, 13)  # 13 in Z_7

# Arithmetic operations
z = x + y * libadic.Zp(7, 20, 2)
print(f"Result: {z}")
print(f"p-adic digits: {z.digits()}")
```

### 2. Quantum-Resistant Cryptography

```python
from libadic.crypto import PadicLattice, SecurityLevel

# Create secure lattice cryptosystem
lattice = PadicLattice(SecurityLevel.LEVEL_1)  # 128-bit security
lattice.generate_keys()

# Encrypt a message
message = [1, 2, 3, 4, 5]
ciphertext = lattice.encrypt(message)
decrypted = lattice.decrypt(ciphertext)

print(f"Original:  {message}")
print(f"Decrypted: {decrypted[:len(message)]}")
print(f"Success:   {message == decrypted[:len(message)]}")
```

### 3. Special Mathematical Functions

```python
# p-adic Gamma function (Morita's definition)
gamma_val = libadic.gamma_p(5, 7, 20)
print(f"Γ_7(5) = {gamma_val}")

# Dirichlet characters for the Reid-Li criterion
chars = libadic.enumerate_primitive_characters(7, 7)
print(f"Found {len(chars)} primitive characters mod 7")

# p-adic L-functions
if chars:
    L_val = libadic.kubota_leopoldt(0, chars[0], 20)
    print(f"L_7(0, χ) = {L_val}")
```

### 4. Elliptic Curves and BSD Conjecture

```python
# Elliptic curve y² = x³ - x
E = libadic.EllipticCurve(0, -1)
point = E.Point(1, 0)
doubled = E.double_point(point)
print(f"2 * (1,0) = {doubled}")

# BSD conjecture verification (if available)
try:
    bsd_result = libadic.verify_bsd_rank_0(E, 7, precision=15)
    print(f"BSD verification: {bsd_result}")
except:
    print("BSD verification not available in this build")
```

## Security Levels

libadic provides multiple cryptographic security levels:

| Level   | Security | Prime Size | Dimension | Use Case           |
|---------|----------|------------|-----------|-------------------|
| DEMO    | Testing  | 5          | 256       | Learning/testing  |
| LEVEL_1 | 128-bit  | 2^31-1     | 512       | Standard security |
| LEVEL_3 | 192-bit  | 2^61-1     | 768       | High security     |
| LEVEL_5 | 256-bit  | 2^89-1     | 1024      | Maximum security  |

## Common Issues & Solutions

### Import Error: "No module named 'libadic'"
```bash
# Check installation
pip list | grep libadic

# Reinstall if needed
pip uninstall libadic
pip install libadic
```

### CMake/Build Errors
```bash
# Install development dependencies first
# Ubuntu/Debian:
sudo apt-get install cmake libgmp-dev libmpfr-dev python3-dev

# macOS:
brew install cmake gmp mpfr

# Then reinstall
pip install --no-cache-dir libadic
```

### Performance Issues
- Use `SecurityLevel.DEMO` for testing/learning
- Use `SecurityLevel.LEVEL_1` for production (fastest secure level)
- Enable compiler optimizations: `export CMAKE_BUILD_TYPE=Release`

## Next Steps

- 📖 **Documentation**: Check the [full API reference](https://github.com/IguanAI/libadic/blob/main/docs/API_REFERENCE.md)
- 🔐 **Cryptography**: Explore the [crypto API guide](https://github.com/IguanAI/libadic/blob/main/PYTHON_CRYPTO_API.md)
- 🧮 **Mathematics**: Read about [p-adic mathematics](https://github.com/IguanAI/libadic/blob/main/docs/MATHEMATICAL_REFERENCE.md)
- 🔬 **Research**: Learn about the [Reid-Li criterion](https://github.com/IguanAI/libadic/blob/main/VALIDATION_REPORT.md)

## Examples Repository

Run these example scripts to explore libadic:

```python
# Basic arithmetic examples
python -m libadic.examples.basic_arithmetic

# Complete crypto API demo
python -m libadic.examples.crypto_api_demo

# Verify installation
python -m libadic.scripts.verify_installation
```

## Getting Help

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/IguanAI/libadic/issues)
- 💬 **Questions**: Use GitHub Discussions
- 📧 **Contact**: info@iguan.ai

---

**Welcome to the future of p-adic mathematics and post-quantum cryptography!** 🎉
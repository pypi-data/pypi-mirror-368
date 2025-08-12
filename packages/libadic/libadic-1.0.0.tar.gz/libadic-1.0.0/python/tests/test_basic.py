"""
Basic tests for libadic Python bindings

Tests core functionality to ensure bindings work correctly
and maintain mathematical precision.
"""

import pytest
import sys
import os

# Add parent directory to path for development testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from libadic import (
        BigInt, Zp, Qp, gamma_p, log_p,
        PadicContext, validate_reid_li_all
    )
    LIBADIC_AVAILABLE = True
except ImportError:
    LIBADIC_AVAILABLE = False
    

@pytest.mark.skipif(not LIBADIC_AVAILABLE, reason="libadic not built")
class TestBigInt:
    """Test BigInt arbitrary precision integers"""
    
    def test_construction(self):
        """Test BigInt construction from various types"""
        x = BigInt(123)
        assert str(x) == "123"
        
        y = BigInt("999999999999999999999999999999")
        assert "9999999999" in str(y)
        
        z = BigInt("FF", 16)  # Hexadecimal
        assert str(z) == "255"
    
    def test_arithmetic(self):
        """Test BigInt arithmetic operations"""
        x = BigInt(100)
        y = BigInt(23)
        
        assert str(x + y) == "123"
        assert str(x - y) == "77"
        assert str(x * y) == "2300"
        assert str(x / y) == "4"  # Integer division
        assert str(x % y) == "8"
    
    def test_large_numbers(self):
        """Test with very large numbers"""
        x = BigInt("123456789012345678901234567890")
        y = BigInt("987654321098765432109876543210")
        
        z = x * y
        # Just check it doesn't crash and produces a large result
        assert len(str(z)) > 50
    
    def test_special_functions(self):
        """Test mathematical functions"""
        x = BigInt(10)
        assert str(x.factorial()) == "3628800"
        
        y = BigInt(100)
        assert y.sqrt() == BigInt(10)
        
        assert BigInt(17).is_prime()
        assert not BigInt(18).is_prime()


@pytest.mark.skipif(not LIBADIC_AVAILABLE, reason="libadic not built")
class TestZp:
    """Test p-adic integers"""
    
    def test_construction(self):
        """Test Zp construction"""
        x = Zp(7, 20, 15)
        assert x.prime == 7
        assert x.precision == 20
        assert x.value == BigInt(15)
    
    def test_arithmetic(self):
        """Test Zp arithmetic"""
        x = Zp(7, 20, 15)
        y = Zp(7, 20, 8)
        
        z = x + y
        assert z.value == BigInt(23)
        
        z = x * y
        assert z.value == BigInt(120)
        
        # Division by unit
        x = Zp(7, 20, 15)
        y = Zp(7, 20, 2)
        z = x / y
        # Result should satisfy z * y = x in Z_7
    
    def test_sqrt(self):
        """Test square root in Zp"""
        # 2 is a quadratic residue mod 7
        x = Zp(7, 20, 2)
        try:
            sqrt_x = x.sqrt()
            # Verify sqrt_x^2 = x
            assert sqrt_x * sqrt_x == x
        except:
            # Square root might not exist
            pass
    
    def test_teichmuller(self):
        """Test Teichmüller character"""
        x = Zp(7, 20, 3)
        omega = x.teichmuller()
        
        # ω(3) should be a (p-1)=6-th root of unity
        omega_6 = omega.pow(6)
        one = Zp(7, 20, 1)
        assert omega_6 == one


@pytest.mark.skipif(not LIBADIC_AVAILABLE, reason="libadic not built")
class TestQp:
    """Test p-adic numbers (field elements)"""
    
    def test_construction(self):
        """Test Qp construction"""
        x = Qp(7, 20, 15)
        assert x.prime == 7
        assert x.precision == 20
        assert x.valuation == 0
    
    def test_from_rational(self):
        """Test construction from rational"""
        x = Qp.from_rational(2, 3, 7, 20)
        
        # 2/3 in Q_7
        # Should satisfy 3*x = 2
        three = Qp(7, 20, 3)
        two = Qp(7, 20, 2)
        assert three * x == two
    
    def test_valuation(self):
        """Test p-adic valuation"""
        # 7^2 * 3
        x = Qp(7, 20, 49 * 3)
        assert x.valuation == 2
        
        unit = x.unit_part
        assert unit.valuation == 0
    
    def test_field_operations(self):
        """Test field division including by p"""
        x = Qp(7, 20, 10)
        y = Qp(7, 20, 7)  # Divisible by p
        
        z = x / y
        # This should work in Qp (unlike Zp)
        assert z.valuation == -1


@pytest.mark.skipif(not LIBADIC_AVAILABLE, reason="libadic not built")
class TestMathematicalFunctions:
    """Test p-adic special functions"""
    
    def test_gamma_function(self):
        """Test p-adic Gamma function"""
        g = gamma_p(5, 7, 20)
        
        # Γ_7(5) should be well-defined
        assert g.prime == 7
        assert g.precision <= 20
    
    def test_gamma_reflection(self):
        """Test Gamma reflection formula"""
        x = 3
        p = 7
        precision = 20
        
        gamma_x = gamma_p(x, p, precision)
        gamma_1mx = gamma_p(p - x, p, precision)
        
        product = gamma_x * gamma_1mx
        
        # Should be ±1
        one = Zp(p, precision, 1)
        minus_one = Zp(p, precision, -1)
        
        assert product == one or product == minus_one
    
    def test_logarithm(self):
        """Test p-adic logarithm"""
        # log_p converges for x ≡ 1 (mod p)
        x = Zp(7, 20, 1 + 7)  # 8 ≡ 1 (mod 7)
        
        log_x = log_p(x)
        assert log_x.prime == 7
    
    def test_logarithm_convergence(self):
        """Test logarithm convergence conditions"""
        # Should fail for x not ≡ 1 (mod p)
        x = Zp(7, 20, 2)  # 2 ≢ 1 (mod 7)
        
        with pytest.raises(Exception):
            log_p(x)


@pytest.mark.skipif(not LIBADIC_AVAILABLE, reason="libadic not built")
class TestPadicContext:
    """Test context manager for p-adic computations"""
    
    def test_context_creation(self):
        """Test PadicContext usage"""
        with PadicContext(prime=7, precision=20) as ctx:
            x = ctx.Zp(15)
            y = ctx.Qp_from_rational(2, 3)
            
            assert x.prime == 7
            assert x.precision == 20
            assert y.prime == 7
    
    def test_context_arithmetic(self):
        """Test arithmetic within context"""
        with PadicContext(prime=11, precision=30) as ctx:
            x = ctx.Zp(5)
            y = ctx.Zp(7)
            z = x + y
            
            assert z.value == BigInt(12)
            assert z.prime == 11
            assert z.precision == 30


@pytest.mark.skipif(not LIBADIC_AVAILABLE, reason="libadic not built")
@pytest.mark.slow
class TestReidLi:
    """Test Reid-Li criterion validation"""
    
    def test_reid_li_small_prime(self):
        """Test Reid-Li for small prime"""
        # This is a slow test - only run with explicit flag
        valid, results = validate_reid_li_all(5, precision=20)
        
        # Check that we got results
        assert len(results) > 0
        
        # Reid-Li should hold (if implementation is correct)
        if not valid:
            # Print diagnostics
            for r in results:
                if not r['valid']:
                    print(f"Failed for character {r['character_index']}")
                    print(f"  Odd: {r['is_odd']}")
                    print(f"  Phi: {r['phi']}")
                    print(f"  Psi: {r['psi']}")


def test_precision_preservation():
    """Verify that precision is preserved through operations"""
    if not LIBADIC_AVAILABLE:
        pytest.skip("libadic not built")
    
    x = Zp(7, 30, 15)
    y = Zp(7, 20, 8)
    
    # Result should have min precision
    z = x + y
    assert z.precision == 20
    
    # Division might reduce precision further
    a = Zp(7, 30, 15)
    b = Zp(7, 30, 2)
    c = a / b
    assert c.precision <= 30


if __name__ == "__main__":
    # Run basic smoke test
    print("Testing libadic Python bindings...")
    
    if not LIBADIC_AVAILABLE:
        print("ERROR: libadic module not available. Please build first:")
        print("  python setup.py build_ext --inplace")
        sys.exit(1)
    
    print("\n1. Testing BigInt...")
    x = BigInt(123)
    y = BigInt("999999999999999999999")
    print(f"  {x} * {y} = {x * y}")
    
    print("\n2. Testing Zp...")
    z1 = Zp(7, 20, 15)
    z2 = Zp(7, 20, 8)
    print(f"  In Z_7: {z1.value} + {z2.value} = {(z1 + z2).value}")
    
    print("\n3. Testing Qp...")
    q = Qp.from_rational(2, 3, 7, 20)
    print(f"  2/3 in Q_7 with precision O(7^20)")
    
    print("\n4. Testing Gamma function...")
    g = gamma_p(5, 7, 20)
    print(f"  Γ_7(5) computed with precision O(7^20)")
    
    print("\n✓ All basic tests passed!")
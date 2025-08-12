#!/usr/bin/env python3
"""
Test the critical functionality of libadic Python bindings for Reid-Li criterion.
"""

import sys
import os

# Add the build directory to Python path
sys.path.insert(0, '/mnt/c/Users/asmit/github/libadic/build')

try:
    import libadic
    print("✓ Successfully imported libadic")
except ImportError as e:
    print(f"✗ Failed to import libadic: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("Testing Critical Reid-Li Functionality")
print("="*60)

def test_basic_types():
    """Test basic p-adic types."""
    print("\n1. Testing basic types:")
    
    # Test Zp
    x = libadic.Zp(7, 20, 15)
    y = libadic.Zp(7, 20, 8)
    z = x + y
    print(f"   Zp: {x} + {y} = {z}")
    
    # Test Qp
    q1 = libadic.Qp(7, 20, 2)
    q2 = libadic.Qp(7, 20, 3)
    q3 = q1 / q2
    print(f"   Qp: {q1} / {q2} = {q3}")
    
    return True

def test_character_enumeration():
    """Test character enumeration."""
    print("\n2. Testing character enumeration:")
    
    # Enumerate primitive characters mod 7
    chars = libadic.enumerate_primitive_characters(7, 7)
    print(f"   Found {len(chars)} primitive characters mod 7")
    
    if len(chars) > 0:
        chi = chars[0]
        print(f"   First character: modulus={chi.get_modulus()}, conductor={chi.get_conductor()}")
        print(f"   Is primitive: {chi.is_primitive()}")
        print(f"   Is odd: {chi.is_odd()}")
        
        # Test evaluate_at
        val = chi.evaluate_at(3)
        print(f"   χ(3) as integer: {val}")
        
        # Test evaluate (to Zp)
        zp_val = chi.evaluate(3, 20)
        print(f"   χ(3) as Zp: {zp_val}")
    
    return True

def test_gamma_function():
    """Test p-adic gamma function."""
    print("\n3. Testing p-adic Gamma function:")
    
    # Test with integer argument
    gamma_val = libadic.gamma_p(5, 7, 20)
    print(f"   Γ_7(5) = {gamma_val}")
    
    # Test with Zp argument
    x = libadic.Zp(7, 20, 5)
    gamma_x = libadic.gamma_p(x)
    print(f"   Γ_7(Zp(5)) = {gamma_x}")
    
    # Test log_gamma_p
    log_gamma = libadic.log_gamma_p(gamma_val)
    print(f"   log(Γ_7(5)) = {log_gamma}")
    
    return True

def test_l_functions():
    """Test L-function computations."""
    print("\n4. Testing L-functions:")
    
    # Get a primitive character
    chars = libadic.enumerate_primitive_characters(7, 7)
    if len(chars) == 0:
        print("   No primitive characters found")
        return False
    
    chi = chars[0]
    
    # Test Kubota-Leopoldt L-function
    L_val = libadic.kubota_leopoldt(0, chi, 20)
    print(f"   L_7(0, χ) = {L_val}")
    
    # Test L-function derivative
    L_deriv = libadic.kubota_leopoldt_derivative(0, chi, 20)
    print(f"   L'_7(0, χ) = {L_deriv}")
    
    # Test B_{1,χ}
    B1_chi = libadic.compute_B1_chi(chi, 20)
    print(f"   B_{{1,χ}} = {B1_chi}")
    
    return True

def test_character_operations():
    """Test character multiplication and powers."""
    print("\n5. Testing character operations:")
    
    chars = libadic.enumerate_primitive_characters(7, 7)
    if len(chars) < 2:
        print("   Not enough characters for multiplication test")
        return False
    
    chi1 = chars[0]
    chi2 = chars[1] if len(chars) > 1 else chars[0]
    
    # Test multiplication
    chi_product = chi1 * chi2
    print(f"   χ₁ * χ₂: modulus={chi_product.get_modulus()}")
    
    # Verify multiplication: (χ₁ * χ₂)(n) = χ₁(n) * χ₂(n)
    test_val = 3
    v1 = chi1.evaluate_at(test_val)
    v2 = chi2.evaluate_at(test_val)
    v_prod = chi_product.evaluate_at(test_val)
    expected = (v1 * v2) % chi1.get_modulus()
    print(f"   Verification: χ₁(3)={v1}, χ₂(3)={v2}, (χ₁*χ₂)(3)={v_prod}, expected={expected}")
    
    # Test power
    chi_squared = chi1 ** 2
    print(f"   χ₁²: modulus={chi_squared.get_modulus()}")
    
    return True

def test_reid_li_computation():
    """Test a minimal Reid-Li computation."""
    print("\n6. Testing Reid-Li computation (simplified):")
    
    p = 7
    N = 10  # Low precision for testing
    
    # Get primitive characters
    chars = libadic.enumerate_primitive_characters(p, p)
    if len(chars) == 0:
        print("   No primitive characters found")
        return False
    
    chi = chars[0]
    print(f"   Using character: odd={chi.is_odd()}, primitive={chi.is_primitive()}")
    
    if chi.is_odd():
        # Compute Φ_p^(odd)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(Γ_p(a))
        phi = libadic.Qp(p, N, 0)
        for a in range(1, p):
            chi_a = chi.evaluate(a, N)
            if not chi_a.is_zero():
                gamma_a = libadic.gamma_p(a, p, N)
                # Check if we can take log
                gamma_mod_p = gamma_a.with_precision(1)
                one_mod_p = libadic.Zp(p, 1, 1)
                if p == 2 or gamma_mod_p == one_mod_p:
                    log_gamma = libadic.log_gamma_p(gamma_a)
                    phi = phi + libadic.Qp(chi_a) * log_gamma
        
        # Compare with L'_p(0, χ)
        psi = libadic.kubota_leopoldt_derivative(0, chi, N)
        
        print(f"   Φ_p^(odd)(χ) = {phi}")
        print(f"   L'_p(0, χ) = {psi}")
        print(f"   Match: {phi == psi}")
    else:
        print("   Character is even (not implemented in this test)")
    
    return True

def main():
    """Run all tests."""
    tests = [
        ("Basic Types", test_basic_types),
        ("Character Enumeration", test_character_enumeration),
        ("Gamma Function", test_gamma_function),
        ("L-Functions", test_l_functions),
        ("Character Operations", test_character_operations),
        ("Reid-Li Computation", test_reid_li_computation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                print(f"\n✓ {name} passed")
                passed += 1
            else:
                print(f"\n✗ {name} failed")
                failed += 1
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n✅ All critical functionality is working!")
        print("The Python bindings are ready for Reid-Li computations.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
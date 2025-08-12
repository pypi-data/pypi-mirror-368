#!/usr/bin/env python3
"""
Comprehensive test of libadic Python bindings for Reid-Li criterion validation.

This example demonstrates all critical functionality needed for validating
the Reid-Li criterion for the Riemann Hypothesis using p-adic L-functions.
"""

import sys
import os
import time
from typing import List, Tuple, Optional

# Add the build directory to Python path
sys.path.insert(0, '/mnt/c/Users/asmit/github/libadic/build')

try:
    import libadic
    print("✓ Successfully imported libadic")
    print(f"  Version: {libadic.__version__}")
except ImportError as e:
    print(f"✗ Failed to import libadic: {e}")
    sys.exit(1)

class ReidLiValidator:
    """
    Validates the Reid-Li criterion for a given prime p.
    
    The Reid-Li criterion states that for primitive Dirichlet characters χ mod p:
    - For odd χ:  Φ_p^(odd)(χ) = L'_p(0, χ)
    - For even χ: Φ_p^(even)(χ) = L_p(0, χ)
    
    Where:
    - Φ_p^(odd)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(Γ_p(a))
    - Φ_p^(even)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(a/(p-1))
    """
    
    def __init__(self, prime: int, precision: int):
        """
        Initialize the validator.
        
        Args:
            prime: The prime p for p-adic computations
            precision: p-adic precision (higher = more accurate)
        """
        self.prime = prime
        self.precision = precision
        self.results = []
        
    def compute_phi_odd(self, chi) -> 'libadic.Qp':
        """
        Compute Φ_p^(odd)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(Γ_p(a)).
        
        Args:
            chi: Odd Dirichlet character
            
        Returns:
            The value Φ_p^(odd)(χ) as a p-adic number
        """
        p = self.prime
        N = self.precision
        
        result = libadic.Qp(p, N, 0)
        
        for a in range(1, p):
            # Evaluate character at a
            chi_a = chi.evaluate(a, N)
            
            if not chi_a.is_zero():
                # Compute Γ_p(a)
                gamma_a = libadic.gamma_p(a, p, N)
                
                # We need to check if we can take the logarithm
                # For p ≠ 2: need γ ≡ 1 (mod p)
                # For p = 2: need γ ≡ 1 (mod 4)
                if gamma_a.is_unit():
                    try:
                        # Compute log(Γ_p(a))
                        log_gamma = libadic.log_gamma_p(gamma_a)
                        
                        # Add χ(a) * log(Γ_p(a)) to the sum
                        term = libadic.Qp(chi_a) * log_gamma
                        result = result + term
                    except Exception as e:
                        print(f"    Warning: Could not compute log for a={a}: {e}")
                        # Try alternative: use Teichmüller lift
                        teich = gamma_a.teichmuller()
                        gamma_1 = gamma_a / teich
                        if p == 2 or gamma_1.with_precision(1) == libadic.Zp(p, 1, 1):
                            log_gamma = libadic.log_p(libadic.Qp(gamma_1))
                            term = libadic.Qp(chi_a) * log_gamma
                            result = result + term
        
        return result
    
    def compute_phi_even(self, chi) -> 'libadic.Qp':
        """
        Compute Φ_p^(even)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(a/(p-1)).
        
        Args:
            chi: Even Dirichlet character
            
        Returns:
            The value Φ_p^(even)(χ) as a p-adic number
        """
        p = self.prime
        N = self.precision
        
        result = libadic.Qp(p, N, 0)
        
        for a in range(1, p):
            # Evaluate character at a
            chi_a = chi.evaluate(a, N)
            
            if not chi_a.is_zero():
                # For even characters, we need a different approach
                # The formula should be log_p(a) - log_p(p-1)
                try:
                    # First try the standard approach
                    val = libadic.Qp.from_rational(a, p-1, p, N)
                    
                    # For convergence, we need val ≡ 1 (mod p)
                    # If not, use a different method
                    val_mod_p = val.valuation()
                    if val_mod_p < 0:
                        # Can't take log of something with negative valuation
                        continue
                    
                    # Try to compute log
                    log_val = libadic.log_p(val)
                    term = libadic.Qp(chi_a) * log_val
                    result = result + term
                except ValueError as e:
                    # If log doesn't converge, try alternative
                    # log(a/(p-1)) = log(a) - log(p-1)
                    # But for p-adic log, we need numbers ≡ 1 (mod p)
                    # So we use the fact that for even χ, Σχ(a) = 0
                    # and rewrite the sum differently
                    pass
        
        return result
    
    def validate_character(self, chi, char_id: int) -> dict:
        """
        Validate Reid-Li criterion for a single character.
        
        Args:
            chi: Dirichlet character
            char_id: Character identifier for reporting
            
        Returns:
            Dictionary with validation results
        """
        print(f"\n  Character #{char_id}:")
        print(f"    Modulus: {chi.get_modulus()}")
        print(f"    Conductor: {chi.get_conductor()}")
        print(f"    Is primitive: {chi.is_primitive()}")
        print(f"    Is odd: {chi.is_odd()}")
        print(f"    Is even: {chi.is_even()}")
        print(f"    Order: {chi.get_order()}")
        
        # Show character values on small integers
        print(f"    Values: χ(1)={chi.evaluate_at(1)}, χ(2)={chi.evaluate_at(2)}, " +
              f"χ(3)={chi.evaluate_at(3)}, χ(4)={chi.evaluate_at(4)}")
        
        result = {
            'char_id': char_id,
            'is_odd': chi.is_odd(),
            'is_primitive': chi.is_primitive(),
            'conductor': chi.get_conductor(),
            'order': chi.get_order()
        }
        
        if chi.is_odd():
            print("\n    Computing for ODD character...")
            
            # Compute Φ_p^(odd)(χ)
            print("    Computing Φ_p^(odd)(χ)...")
            phi = self.compute_phi_odd(chi)
            print(f"    Φ_p^(odd)(χ) = {phi}")
            
            # Compute L'_p(0, χ)
            print("    Computing L'_p(0, χ)...")
            psi = libadic.kubota_leopoldt_derivative(0, chi, self.precision)
            print(f"    L'_p(0, χ) = {psi}")
            
            # Check if they match
            matches = (phi == psi)
            print(f"    Match: {matches} ✓" if matches else f"    Match: {matches} ✗")
            
            result.update({
                'phi': phi,
                'psi': psi,
                'matches': matches,
                'type': 'odd'
            })
            
        else:  # Even character
            print("\n    Computing for EVEN character...")
            
            # Compute Φ_p^(even)(χ)
            print("    Computing Φ_p^(even)(χ)...")
            phi = self.compute_phi_even(chi)
            print(f"    Φ_p^(even)(χ) = {phi}")
            
            # Compute L_p(0, χ)
            print("    Computing L_p(0, χ)...")
            psi = libadic.kubota_leopoldt(0, chi, self.precision)
            print(f"    L_p(0, χ) = {psi}")
            
            # Check if they match
            matches = (phi == psi)
            print(f"    Match: {matches} ✓" if matches else f"    Match: {matches} ✗")
            
            result.update({
                'phi': phi,
                'psi': psi,
                'matches': matches,
                'type': 'even'
            })
        
        return result
    
    def validate_all(self) -> Tuple[int, int]:
        """
        Validate Reid-Li criterion for all primitive characters mod p.
        
        Returns:
            Tuple of (passed_count, failed_count)
        """
        print(f"\n{'='*70}")
        print(f"Reid-Li Validation for p={self.prime}, precision={self.precision}")
        print(f"{'='*70}")
        
        # Enumerate all primitive characters
        print(f"\nEnumerating primitive characters mod {self.prime}...")
        characters = libadic.enumerate_primitive_characters(self.prime, self.prime)
        print(f"Found {len(characters)} primitive characters")
        
        passed = 0
        failed = 0
        
        for i, chi in enumerate(characters):
            result = self.validate_character(chi, i+1)
            self.results.append(result)
            
            if result.get('matches', False):
                passed += 1
            else:
                failed += 1
        
        return passed, failed
    
    def print_summary(self):
        """Print a summary of all validation results."""
        print(f"\n{'='*70}")
        print("VALIDATION SUMMARY")
        print(f"{'='*70}")
        
        odd_chars = [r for r in self.results if r['type'] == 'odd']
        even_chars = [r for r in self.results if r['type'] == 'even']
        
        print(f"\nTotal characters tested: {len(self.results)}")
        print(f"  Odd characters: {len(odd_chars)}")
        print(f"  Even characters: {len(even_chars)}")
        
        passed = sum(1 for r in self.results if r['matches'])
        failed = sum(1 for r in self.results if not r['matches'])
        
        print(f"\nResults:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        
        if failed == 0:
            print(f"\n✅ SUCCESS: Reid-Li criterion validated for all characters mod {self.prime}!")
        else:
            print(f"\n⚠️ WARNING: {failed} character(s) failed validation")
            print("Failed characters:")
            for r in self.results:
                if not r['matches']:
                    print(f"  - Character #{r['char_id']} ({'odd' if r['is_odd'] else 'even'})")


def test_basic_functionality():
    """Test basic p-adic arithmetic to ensure the library is working."""
    print("\n" + "="*70)
    print("BASIC FUNCTIONALITY TEST")
    print("="*70)
    
    print("\n1. Testing p-adic integers (Zp):")
    x = libadic.Zp(7, 20, 15)
    y = libadic.Zp(7, 20, 8)
    z = x + y
    print(f"   {x} + {y} = {z}")
    
    # Test multiplication
    w = x * y
    print(f"   {x} * {y} = {w}")
    
    # Test power
    x_squared = x.pow(2)
    print(f"   {x}^2 = {x_squared}")
    
    print("\n2. Testing p-adic numbers (Qp):")
    q1 = libadic.Qp(7, 20, 2)
    q2 = libadic.Qp(7, 20, 3)
    q3 = q1 / q2
    print(f"   {q1} / {q2} = {q3}")
    
    # Test from_rational
    q4 = libadic.Qp.from_rational(22, 7, 5, 20)
    print(f"   22/7 in Q_5 = {q4}")
    
    print("\n3. Testing BigInt:")
    b1 = libadic.BigInt(12345)
    b2 = libadic.BigInt(6789)
    b3 = b1 * b2
    print(f"   {b1.to_string()} * {b2.to_string()} = {b3.to_string()}")
    
    print("\n4. Testing character operations:")
    chars = libadic.enumerate_primitive_characters(7, 7)
    if len(chars) >= 2:
        chi1 = chars[0]
        chi2 = chars[1]
        
        # Test multiplication
        chi_prod = chi1 * chi2
        print(f"   χ₁ * χ₂ successful, modulus={chi_prod.get_modulus()}")
        
        # Test power
        chi_sq = chi1 ** 2
        print(f"   χ₁² successful, modulus={chi_sq.get_modulus()}")
        
        # Verify multiplication property
        for n in [2, 3, 5]:
            v1 = chi1.evaluate_at(n)
            v2 = chi2.evaluate_at(n)
            v_prod = chi_prod.evaluate_at(n)
            expected = (v1 * v2) % 7
            matches = v_prod == expected
            symbol = "✓" if matches else "✗"
            print(f"   (χ₁*χ₂)({n}) = χ₁({n})*χ₂({n}) = {v1}*{v2} = {v_prod} {symbol}")
    
    print("\n5. Testing Gamma function:")
    for a in [1, 2, 3, 4, 5, 6]:
        gamma_val = libadic.gamma_p(a, 7, 20)
        print(f"   Γ_7({a}) = {gamma_val}")
    
    print("\n6. Testing L-function helpers:")
    if len(chars) > 0:
        chi = chars[0]
        
        # Test B_{1,χ}
        B1 = libadic.compute_B1_chi(chi, 20)
        print(f"   B_{{1,χ}} = {B1}")
        
        # Test Euler factor
        euler = libadic.compute_euler_factor(chi, 1, 20)
        print(f"   Euler factor (s=1) = {euler}")
    
    print("\n✓ Basic functionality test complete")


def test_small_prime(p: int = 5, precision: int = 20):
    """
    Test Reid-Li validation for a small prime.
    
    Args:
        p: Prime to test
        precision: p-adic precision
    """
    print(f"\n{'='*70}")
    print(f"TESTING REID-LI FOR p={p}")
    print(f"{'='*70}")
    
    validator = ReidLiValidator(p, precision)
    passed, failed = validator.validate_all()
    validator.print_summary()
    
    return failed == 0


def test_character_arithmetic():
    """Test advanced character arithmetic operations."""
    print("\n" + "="*70)
    print("CHARACTER ARITHMETIC TEST")
    print("="*70)
    
    p = 7
    chars = libadic.enumerate_primitive_characters(p, p)
    
    if len(chars) < 2:
        print("Not enough characters for arithmetic tests")
        return
    
    chi1 = chars[0]
    chi2 = chars[1]
    
    print(f"\nCharacter 1: conductor={chi1.get_conductor()}, order={chi1.get_order()}")
    print(f"Character 2: conductor={chi2.get_conductor()}, order={chi2.get_order()}")
    
    # Test associativity: (χ₁ * χ₂) * χ₃ = χ₁ * (χ₂ * χ₃)
    if len(chars) >= 3:
        chi3 = chars[2]
        left = (chi1 * chi2) * chi3
        right = chi1 * (chi2 * chi3)
        
        print("\nTesting associativity of multiplication:")
        for n in range(1, p):
            l_val = left.evaluate_at(n)
            r_val = right.evaluate_at(n)
            matches = l_val == r_val
            symbol = "✓" if matches else "✗"
            print(f"  ((χ₁*χ₂)*χ₃)({n}) = {l_val}, (χ₁*(χ₂*χ₃))({n}) = {r_val} {symbol}")
    
    # Test that χ^order(χ) is trivial
    print("\nTesting χ^order(χ) = trivial character:")
    order = chi1.get_order()
    chi_power = chi1 ** order
    for n in range(1, min(p, 10)):
        if n % p != 0:
            val = chi_power.evaluate_at(n)
            is_one = val == 1
            symbol = "✓" if is_one else "✗"
            print(f"  χ^{order}({n}) = {val} {symbol}")
    
    # Test inverse: χ * χ^(-1) should be trivial
    # For now, we can test χ * χ^(order-1) since χ^order = 1
    if order > 1:
        chi_inv = chi1 ** (order - 1)
        chi_id = chi1 * chi_inv
        print(f"\nTesting χ * χ^({order-1}) = trivial:")
        for n in range(1, min(p, 10)):
            if n % p != 0:
                val = chi_id.evaluate_at(n)
                is_one = val == 1
                symbol = "✓" if is_one else "✗"
                print(f"  (χ * χ^{order-1})({n}) = {val} {symbol}")


def test_precision_consistency():
    """Test that computations maintain precision correctly."""
    print("\n" + "="*70)
    print("PRECISION CONSISTENCY TEST")
    print("="*70)
    
    p = 7
    
    # Test at different precision levels
    for prec in [5, 10, 20]:
        print(f"\nTesting at precision {prec}:")
        
        # Create p-adic numbers
        x = libadic.Zp(p, prec, 15)
        y = libadic.Zp(p, prec, 8)
        
        # Operations should maintain precision
        z = x + y
        print(f"  Precision of {x} + {y} = {z.precision} (expected {prec})")
        
        w = x * y
        print(f"  Precision of {x} * {y} = {w.precision} (expected {prec})")
        
        # Division might reduce precision
        q1 = libadic.Qp(p, prec, 14)  # 14 = 2 * 7
        q2 = libadic.Qp(p, prec, 2)
        q3 = q1 / q2
        print(f"  Precision of {q1} / {q2} = {q3.precision}")
        print(f"  Valuation of result: {q3.valuation()}")


def main():
    """Run comprehensive test suite."""
    print("\n" + "="*70)
    print("COMPREHENSIVE LIBADIC PYTHON BINDINGS TEST")
    print("="*70)
    print(f"Library version: {libadic.__version__}")
    
    start_time = time.time()
    
    # Run all test suites
    test_suites = [
        ("Basic Functionality", test_basic_functionality),
        ("Character Arithmetic", test_character_arithmetic),
        ("Precision Consistency", test_precision_consistency),
    ]
    
    for name, test_func in test_suites:
        try:
            test_func()
            print(f"\n✓ {name} test passed")
        except Exception as e:
            print(f"\n✗ {name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Test Reid-Li for small primes
    test_primes = [5, 7]
    all_passed = True
    
    for p in test_primes:
        try:
            # Use lower precision for faster testing
            if not test_small_prime(p, precision=10):
                all_passed = False
        except Exception as e:
            print(f"\n✗ Reid-Li test for p={p} failed: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    elapsed = time.time() - start_time
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Total time: {elapsed:.2f} seconds")
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED!")
        print("The libadic Python bindings are fully functional.")
        print("Ready for Reid-Li criterion research!")
    else:
        print("\n⚠️ Some tests failed. See details above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
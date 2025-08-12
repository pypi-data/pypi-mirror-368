#!/usr/bin/env python3
"""
precision_management.py

Demonstrates precision tracking, propagation, and management in p-adic arithmetic.
Shows how to handle precision loss and optimize computations.

Author: libadic team
"""

import sys
import time
from typing import Tuple, List

# Add libadic to path
sys.path.insert(0, '/mnt/c/Users/asmit/github/libadic/build')

try:
    import libadic
except ImportError:
    print("Error: libadic module not found. Please build the library first.")
    sys.exit(1)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(title)
    print('='*60)


def demonstrate_precision_basics():
    """Show basic precision concepts in p-adic arithmetic."""
    
    print_section("PRECISION BASICS")
    
    p = 7
    
    print(f"\nPrecision in Z_{p} and Q_{p}:")
    print("-"*40)
    
    # Different precision levels
    low = libadic.Zp(p, 5, 123)
    medium = libadic.Zp(p, 20, 123)
    high = libadic.Zp(p, 100, 123)
    
    print(f"Same value (123) with different precisions:")
    print(f"  Low (5):    knows 123 mod {p}^5 = {p**5}")
    print(f"  Medium (20): knows 123 mod {p}^20 ≈ {p**20:.2e}")
    print(f"  High (100):  knows 123 mod {p}^100 ≈ {p**100:.2e}")
    
    # Show digits
    print(f"\np-adic digits of 123 in base {p}:")
    print(f"  First 10 digits: {medium.digits()[:10]}")
    print(f"  Meaning: 123 = {medium.digits()[0]} + {medium.digits()[1]}×{p} + {medium.digits()[2]}×{p}² + ...")
    
    # Precision is explicit
    print(f"\nPrecision is tracked explicitly:")
    print(f"  low.precision = {low.precision}")
    print(f"  medium.precision = {medium.precision}")
    print(f"  high.precision = {high.precision}")


def demonstrate_precision_propagation():
    """Show how precision propagates through operations."""
    
    print_section("PRECISION PROPAGATION RULES")
    
    p = 5
    
    # Create numbers with different precisions
    x = libadic.Zp(p, 30, 17)  # precision 30
    y = libadic.Zp(p, 20, 23)  # precision 20
    z = libadic.Zp(p, 25, 11)  # precision 25
    
    print(f"\nInitial precisions:")
    print(f"  x: precision {x.precision}")
    print(f"  y: precision {y.precision}")
    print(f"  z: precision {z.precision}")
    
    # Rule 1: Binary operations take minimum
    print(f"\nRule 1: Binary operations → min(prec₁, prec₂)")
    
    operations = [
        ("x + y", x + y),
        ("x - y", x - y),
        ("x * y", x * y),
        ("y + z", y + z),
        ("x * z", x * z),
    ]
    
    for expr, result in operations:
        print(f"  {expr:8s} → precision {result.precision}")
    
    # Rule 2: Chain of operations
    print(f"\nRule 2: Chains of operations")
    
    result1 = x + y  # precision = min(30, 20) = 20
    result2 = result1 * z  # precision = min(20, 25) = 20
    result3 = result2 + x  # precision = min(20, 30) = 20
    
    print(f"  (x + y) → precision {result1.precision}")
    print(f"  (x + y) * z → precision {result2.precision}")
    print(f"  ((x + y) * z) + x → precision {result3.precision}")
    print(f"  Final precision: {result3.precision} (limited by weakest link)")
    
    # Rule 3: Division in Qp
    print(f"\nRule 3: Division and valuations")
    
    q1 = libadic.Qp(p, 30, 50)  # 50 = 2×5², valuation 2
    q2 = libadic.Qp(p, 25, 5)   # 5 = 5¹, valuation 1
    q3 = q1 / q2  # valuation = 2-1 = 1
    
    print(f"  50 ÷ 5 in Q_{p}:")
    print(f"    Precisions: {q1.precision} ÷ {q2.precision} → {q3.precision}")
    print(f"    Valuations: {q1.valuation} - {q2.valuation} = {q3.valuation}")


def precision_loss_examples():
    """Demonstrate scenarios where precision is lost."""
    
    print_section("PRECISION LOSS SCENARIOS")
    
    p = 7
    base_prec = 20
    
    print(f"\nScenario 1: Subtraction of close numbers")
    print("-"*40)
    
    # When numbers are close, leading digits cancel
    x = libadic.Zp(p, base_prec, 1000)
    y = libadic.Zp(p, base_prec, 999)
    diff = x - y
    
    print(f"  {x.value} - {y.value} = {diff.value}")
    print(f"  Precision: {x.precision} - {y.precision} → {diff.precision}")
    print(f"  No precision loss here (both have same precision)")
    
    print(f"\nScenario 2: Mixed precision arithmetic")
    print("-"*40)
    
    high_prec = libadic.Zp(p, 50, 42)
    low_prec = libadic.Zp(p, 10, 7)
    
    result = high_prec * low_prec
    print(f"  High precision ({high_prec.precision}) × Low precision ({low_prec.precision})")
    print(f"  Result precision: {result.precision}")
    print(f"  Lost {high_prec.precision - result.precision} digits of precision!")
    
    print(f"\nScenario 3: Long computation chains")
    print("-"*40)
    
    # Start with high precision
    x = libadic.Zp(p, 100, 3)
    
    # Introduce low precision number
    y = libadic.Zp(p, 15, 5)
    
    # Chain of operations
    temp1 = x * x  # Still precision 100
    temp2 = temp1 + y  # Drops to precision 15!
    temp3 = temp2 * x  # Still precision 15
    
    print(f"  Starting precision: {x.precision}")
    print(f"  x² → precision {temp1.precision}")
    print(f"  x² + y (low prec) → precision {temp2.precision}")
    print(f"  (x² + y) × x → precision {temp3.precision}")
    print(f"  Final: Lost {x.precision - temp3.precision} digits!")


def planning_precision_strategy():
    """Show how to plan precision for complex computations."""
    
    print_section("PRECISION PLANNING STRATEGIES")
    
    p = 11
    target_precision = 20
    
    print(f"\nGoal: Compute result to precision {target_precision}")
    
    # Strategy 1: Work with extra precision
    print(f"\nStrategy 1: Add precision buffer")
    print("-"*40)
    
    buffer = 10
    working_precision = target_precision + buffer
    
    print(f"  Target precision: {target_precision}")
    print(f"  Buffer: {buffer}")
    print(f"  Working precision: {working_precision}")
    
    # Do computation with buffer
    x = libadic.Zp(p, working_precision, 123)
    y = libadic.Zp(p, working_precision, 456)
    
    # Complex computation
    result = x * y + x * x - y
    
    # Reduce to target
    final = result.with_precision(target_precision)
    
    print(f"  Computation precision: {result.precision}")
    print(f"  Final precision: {final.precision}")
    print(f"  ✓ Achieved target precision")
    
    # Strategy 2: Track precision requirements
    print(f"\nStrategy 2: Track precision requirements")
    print("-"*40)
    
    def compute_with_tracking(values: List[int], p: int, min_precision: int) -> libadic.Zp:
        """Compute sum of products maintaining minimum precision."""
        
        # Ensure all inputs have sufficient precision
        numbers = [libadic.Zp(p, min_precision + 5, v) for v in values]
        
        result = libadic.Zp(p, min_precision + 5, 0)
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                result = result + numbers[i] * numbers[j]
        
        # Check we maintained precision
        if result.precision >= min_precision:
            print(f"  ✓ Maintained minimum precision {min_precision}")
        else:
            print(f"  ✗ Lost precision: {result.precision} < {min_precision}")
        
        return result.with_precision(min_precision)
    
    values = [12, 34, 56, 78]
    result = compute_with_tracking(values, p, target_precision)
    
    # Strategy 3: Precision-aware algorithms
    print(f"\nStrategy 3: Precision-aware algorithms")
    print("-"*40)
    
    def newton_with_precision(f, df, x0: libadic.Zp, target_prec: int) -> libadic.Zp:
        """Newton's method with precision management."""
        
        p = x0.prime
        current_prec = 2
        x = x0.with_precision(current_prec)
        
        print(f"  Newton iteration with doubling precision:")
        
        while current_prec < target_prec:
            # Double precision each iteration
            current_prec = min(2 * current_prec, target_prec)
            
            # Increase precision for this iteration
            x = x.with_precision(current_prec)
            
            # Newton step (simplified)
            # x = x - f(x)/df(x)
            
            print(f"    Iteration: precision {current_prec}")
        
        return x
    
    x0 = libadic.Zp(p, 2, 3)
    # Demonstration only (would need actual f, df)
    print("  (Newton iteration demonstration)")


def precision_in_special_functions():
    """Show precision behavior in special functions."""
    
    print_section("PRECISION IN SPECIAL FUNCTIONS")
    
    p = 7
    precision = 20
    
    print(f"\n1. Gamma Function")
    print("-"*40)
    
    x = libadic.Zp(p, precision, 5)
    gamma_x = libadic.gamma_p(x)
    
    print(f"  Input precision: {x.precision}")
    print(f"  Γ_p(x) precision: {gamma_x.precision}")
    print(f"  Precision preserved: {gamma_x.precision == x.precision}")
    
    print(f"\n2. Square Root (Hensel Lifting)")
    print("-"*40)
    
    a = libadic.Zp(p, precision, 2)
    sqrt_a = a.sqrt()
    
    print(f"  Input precision: {a.precision}")
    print(f"  √a precision: {sqrt_a.precision}")
    
    # Verify
    check = sqrt_a * sqrt_a
    print(f"  Verification (√a)²: precision {check.precision}")
    
    print(f"\n3. Logarithm Convergence")
    print("-"*40)
    
    # log_p requires special convergence conditions
    x = libadic.Qp(p, precision, 1 + p)  # 1 + p ≡ 1 (mod p)
    
    try:
        log_x = libadic.log_p(x)
        print(f"  log_p({x.value}) computed")
        print(f"  Input precision: {x.precision}")
        print(f"  Output precision: {log_x.precision}")
    except Exception as e:
        print(f"  Failed: {e}")
    
    print(f"\n4. L-functions")
    print("-"*40)
    
    chars = libadic.enumerate_primitive_characters(5, 5)
    if chars:
        chi = chars[0]
        L_val = libadic.kubota_leopoldt(0, chi, precision)
        print(f"  L_p(0, χ) computed")
        print(f"  Requested precision: {precision}")
        print(f"  Result precision: {L_val.precision}")


def precision_optimization_benchmark():
    """Benchmark impact of precision on performance."""
    
    print_section("PRECISION VS PERFORMANCE")
    
    p = 17
    test_value = 123456789
    
    print(f"\nBenchmarking arithmetic at different precisions:")
    print("-"*40)
    
    precisions = [10, 20, 50, 100, 200]
    iterations = 1000
    
    for prec in precisions:
        x = libadic.Zp(p, prec, test_value)
        y = libadic.Zp(p, prec, test_value + 1)
        
        start = time.time()
        
        for _ in range(iterations):
            z = x * y
            w = z + x
            v = w - y
        
        elapsed = time.time() - start
        ops_per_sec = (iterations * 3) / elapsed
        
        print(f"  Precision {prec:3d}: {elapsed:.3f}s ({ops_per_sec:.0f} ops/sec)")
    
    print(f"\nMemory usage estimate:")
    print("-"*40)
    
    for prec in precisions:
        # Rough estimate: each p-adic digit needs log2(p) bits
        bits_per_digit = len(bin(p)) - 2
        total_bits = prec * bits_per_digit
        total_bytes = total_bits // 8
        
        print(f"  Precision {prec:3d}: ~{total_bytes} bytes per number")


def adaptive_precision_example():
    """Demonstrate adaptive precision strategies."""
    
    print_section("ADAPTIVE PRECISION")
    
    p = 13
    
    print(f"\nAdaptive precision for iterative computation:")
    print("-"*40)
    
    def iterative_computation(initial: int, p: int, target_prec: int):
        """Example: Computing a fixed point with increasing precision."""
        
        print(f"  Target precision: {target_prec}")
        
        # Start with low precision
        current_prec = 4
        x = libadic.Zp(p, current_prec, initial)
        
        # Gradually increase precision
        while current_prec < target_prec:
            # Do some computation
            x_new = (x * x + libadic.Zp(p, current_prec, 1)) / libadic.Zp(p, current_prec, 2)
            
            # Check convergence (simplified)
            if current_prec >= 8:  # Arbitrary check
                # Increase precision
                current_prec = min(current_prec * 2, target_prec)
                x = x_new.with_precision(current_prec)
                print(f"    Precision increased to {current_prec}")
            else:
                x = x_new
                current_prec = min(current_prec * 2, target_prec)
        
        return x
    
    result = iterative_computation(3, p, 32)
    print(f"  Final precision: {result.precision}")
    
    print(f"\nPrecision-aware caching:")
    print("-"*40)
    
    class PrecisionCache:
        """Cache values at different precision levels."""
        
        def __init__(self):
            self.cache = {}
        
        def get(self, key: str, p: int, precision: int) -> libadic.Zp:
            """Get cached value, recomputing if needed."""
            
            if key in self.cache:
                cached_val, cached_prec = self.cache[key]
                if cached_prec >= precision:
                    # Use cached value, reducing precision if needed
                    return cached_val.with_precision(precision)
            
            # Compute with some extra precision
            buffer = 5
            value = self._compute(key, p, precision + buffer)
            self.cache[key] = (value, precision + buffer)
            
            return value.with_precision(precision)
        
        def _compute(self, key: str, p: int, precision: int) -> libadic.Zp:
            """Compute the value (placeholder)."""
            # Example computation
            if key == "special_value":
                return libadic.Zp(p, precision, 42)
            return libadic.Zp(p, precision, 0)
    
    cache = PrecisionCache()
    
    # First request: computes and caches
    val1 = cache.get("special_value", p, 10)
    print(f"  First request (prec 10): computed and cached")
    
    # Second request: uses cache
    val2 = cache.get("special_value", p, 8)
    print(f"  Second request (prec 8): used cache")
    
    # Third request: needs recomputation
    val3 = cache.get("special_value", p, 20)
    print(f"  Third request (prec 20): recomputed with higher precision")


def precision_recommendations():
    """Provide recommendations for precision management."""
    
    print_section("PRECISION RECOMMENDATIONS")
    
    recommendations = """
1. PLANNING PRECISION
   • Add 10-20% buffer for complex computations
   • Consider precision loss in divisions
   • Track minimum precision requirements
   
2. OPTIMIZATION STRATEGIES
   • Use minimum necessary precision
   • Cache high-precision values
   • Increase precision adaptively
   
3. COMMON PITFALLS
   • Mixing different precisions unknowingly
   • Not accounting for precision loss in chains
   • Over-specifying precision (wastes memory/time)
   
4. BEST PRACTICES
   • Always check output precision
   • Use with_precision() to explicitly manage
   • Document precision requirements
   • Test with various precision levels
   
5. SPECIAL CASES
   • Logarithm: Needs x ≡ 1 (mod p) convergence
   • Division: Can reduce precision with valuations
   • Series: Precision determines truncation point
   
6. PERFORMANCE TIPS
   • Precision ≤ 50: Fast for most operations
   • Precision > 100: Consider if really needed
   • Precision > 1000: Use specialized algorithms
"""
    
    print(recommendations)


def main():
    """Main demonstration routine."""
    
    print("="*60)
    print("PRECISION MANAGEMENT IN P-ADIC ARITHMETIC")
    print("="*60)
    
    # Basic concepts
    demonstrate_precision_basics()
    
    # Propagation rules
    demonstrate_precision_propagation()
    
    # Precision loss
    precision_loss_examples()
    
    # Planning strategies
    planning_precision_strategy()
    
    # Special functions
    precision_in_special_functions()
    
    # Performance impact
    precision_optimization_benchmark()
    
    # Adaptive strategies
    adaptive_precision_example()
    
    # Recommendations
    precision_recommendations()
    
    print("\n" + "="*60)
    print("PRECISION MANAGEMENT DEMONSTRATION COMPLETE")
    print("="*60)
    
    print("\nKey Takeaways:")
    print("  • Precision = min(input precisions) for operations")
    print("  • Plan with buffer for complex computations")
    print("  • Higher precision = slower performance")
    print("  • Use adaptive precision for efficiency")
    print("  • Always verify output precision meets requirements")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
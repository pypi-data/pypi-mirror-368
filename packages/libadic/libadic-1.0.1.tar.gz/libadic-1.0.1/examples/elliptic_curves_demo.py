#!/usr/bin/env python3
"""
Elliptic Curves and p-adic L-functions Demonstration

This script demonstrates the elliptic curve functionality in libadic,
including point arithmetic, L-function computations, and applications
to number theory problems.
"""

import libadic
import time

def demo_basic_elliptic_curves():
    """Demonstrate basic elliptic curve operations"""
    print("\n" + "="*60)
    print("Basic Elliptic Curve Operations")
    print("="*60)
    
    # Create curve y² = x³ + ax + b
    a, b = 0, -1
    E = libadic.EllipticCurve(a, b)
    
    print(f"\nCurve: y² = x³ + {a}x + {b}")
    print(f"String form: {E.to_string()}")
    print(f"LaTeX form: {E.to_latex()}")
    
    # Compute invariants
    print("\nInvariants:")
    print(f"  Discriminant: {E.get_discriminant()}")
    j_num, j_den = E.get_j_invariant()
    print(f"  j-invariant: {j_num}/{j_den}")
    print(f"  Conductor: {E.get_conductor()}")
    
    # Test some points
    print("\nPoint validation:")
    test_points = [(2, 3), (0, 1), (0, -1), (1, 0), (2, -3)]
    
    for x, y in test_points:
        on_curve = E.contains_point(libadic.BigInt(x), libadic.BigInt(y))
        print(f"  ({x}, {y}): {'✓ On curve' if on_curve else '✗ Not on curve'}")
    
    # Point arithmetic
    print("\nPoint arithmetic:")
    P = libadic.EllipticCurve.Point(libadic.BigInt(2), libadic.BigInt(3))
    Q = libadic.EllipticCurve.Point(libadic.BigInt(0), libadic.BigInt(1))
    
    print(f"  P = ({P.X}, {P.Y})")
    print(f"  Q = ({Q.X}, {Q.Y})")
    
    # Addition
    R = E.add_points(P, Q)
    print(f"  P + Q = ({R.X}, {R.Y})")
    
    # Doubling
    P2 = E.double_point(P)
    print(f"  2P = ({P2.X}, {P2.Y})")
    
    # Scalar multiplication
    P5 = E.scalar_multiply(P, libadic.BigInt(5))
    print(f"  5P = ({P5.X}, {P5.Y})")
    
    # Negation
    neg_P = E.negate_point(P)
    print(f"  -P = ({neg_P.X}, {neg_P.Y})")
    
    # Verify P + (-P) = O
    sum_zero = E.add_points(P, neg_P)
    print(f"  P + (-P) = {'O (infinity)' if sum_zero.is_infinity() else f'({sum_zero.X}, {sum_zero.Y})'}")

def demo_torsion_subgroup():
    """Demonstrate torsion subgroup computation"""
    print("\n" + "="*60)
    print("Torsion Subgroup Analysis")
    print("="*60)
    
    # Test several curves with known torsion
    test_curves = [
        (0, -1, "11a1"),    # Torsion Z/5Z
        (1, 0, "32a2"),     # Torsion Z/2Z
        (-1, 1, "14a1"),    # Torsion Z/6Z
    ]
    
    for a, b, label in test_curves:
        E = libadic.EllipticCurve(a, b)
        print(f"\nCurve {label}: y² = x³ + {a}x + {b}")
        
        # Compute torsion
        torsion_points = E.compute_torsion_points()
        torsion_order = E.get_torsion_order()
        
        print(f"  Torsion order: {torsion_order}")
        print(f"  Torsion points:")
        
        for T in torsion_points:
            if T.is_infinity():
                print(f"    O (point at infinity)")
            else:
                print(f"    ({T.X}, {T.Y})")
                
                # Verify it's actually torsion
                nT = E.scalar_multiply(T, libadic.BigInt(torsion_order))
                assert nT.is_infinity(), f"Point ({T.X}, {T.Y}) is not {torsion_order}-torsion!"
        
        # Check Mazur's theorem
        if torsion_order > 16:
            print(f"  ⚠ Warning: Torsion > 16 violates Mazur's theorem!")

def demo_l_series():
    """Demonstrate L-series computation"""
    print("\n" + "="*60)
    print("L-series Coefficients")
    print("="*60)
    
    # Create curve
    E = libadic.EllipticCurve(0, -1)  # Conductor 11
    print(f"\nCurve: {E.to_string()}")
    print(f"Conductor N = {E.get_conductor()}")
    
    # Compute a_p for small primes
    print("\nL-series coefficients a_p:")
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    
    for p in primes:
        ap = E.get_ap(p)
        reduction = E.reduction_type(p)
        
        # Interpret reduction type
        if reduction == 1:
            red_str = "good"
        elif reduction == 0:
            red_str = "additive"
        elif reduction == -1:
            red_str = "split mult."
        else:
            red_str = "non-split mult."
        
        print(f"  a_{p:2d} = {ap:3d}  ({red_str} reduction)")
    
    # Compute more coefficients using multiplicativity
    print("\nExtended L-series coefficients a_n:")
    an_coeffs = E.compute_an_coefficients(30)
    
    for n in range(1, min(31, len(an_coeffs))):
        print(f"  a_{n:2d} = {an_coeffs[n]:3d}")
    
    # Functional equation sign (root number)
    print("\nFunctional equation:")
    # The sign determines whether L(E, 1) = 0
    # For rank 0 curves, sign should be +1
    print(f"  Expected sign: +1 for even rank, -1 for odd rank")

def demo_padic_points():
    """Demonstrate p-adic point arithmetic"""
    print("\n" + "="*60)
    print("p-adic Point Arithmetic")
    print("="*60)
    
    # Setup
    E = libadic.EllipticCurve(0, -1)
    p = 7
    precision = 20
    
    print(f"\nCurve: {E.to_string()}")
    print(f"Working in Q_{p} with precision {precision}")
    
    # Create p-adic points
    x1 = libadic.Qp(p, precision, 2)
    y1 = libadic.Qp(p, precision, 3)
    P = libadic.EllipticCurve.PadicPoint(x1, y1)
    
    x2 = libadic.Qp(p, precision, 0)
    y2 = libadic.Qp(p, precision, 1)
    Q = libadic.EllipticCurve.PadicPoint(x2, y2)
    
    print(f"\np-adic points:")
    print(f"  P = ({P.x}, {P.y})")
    print(f"  Q = ({Q.x}, {Q.y})")
    
    # p-adic addition
    R = E.add_points_padic(P, Q, p, precision)
    print(f"\nP + Q = ({R.x}, {R.y})")
    
    # p-adic doubling
    P2 = E.double_point_padic(P, p, precision)
    print(f"2P = ({P2.x}, {P2.y})")
    
    # Scalar multiplication
    P5 = E.scalar_multiply_padic(P, libadic.BigInt(5), p, precision)
    print(f"5P = ({P5.x}, {P5.y})")
    
    # Verify arithmetic consistency
    print("\nVerifying arithmetic consistency:")
    
    # Check 2P + 3P = 5P
    P3 = E.scalar_multiply_padic(P, libadic.BigInt(3), p, precision)
    sum_2_3 = E.add_points_padic(P2, P3, p, precision)
    
    # Compare x-coordinates (sufficient for verification)
    diff_x = (sum_2_3.x - P5.x)
    print(f"  |2P + 3P - 5P|_p = {diff_x.valuation()} (should be large)")

def demo_padic_l_functions():
    """Demonstrate p-adic L-function computations"""
    print("\n" + "="*60)
    print("p-adic L-functions for Elliptic Curves")
    print("="*60)
    
    # Test curve (conductor 11, rank 0)
    E = libadic.EllipticCurve(0, -1)
    print(f"\nCurve: {E.to_string()}")
    print(f"Conductor: {E.get_conductor()}")
    
    # Test at several primes
    primes = [3, 5, 7]
    precision = 30
    
    for p in primes:
        print(f"\nPrime p = {p}:")
        
        # Check reduction type
        reduction = E.reduction_type(p)
        if reduction == 1:
            print(f"  Reduction: good ordinary")
        elif reduction == 0:
            print(f"  Reduction: additive")
        elif reduction == -1:
            print(f"  Reduction: split multiplicative")
        else:
            print(f"  Reduction: non-split multiplicative")
        
        # Compute L_p(E, 1) - special value for BSD
        L_p_1 = libadic.EllipticLFunctions.L_p_at_one(E, p, precision)
        print(f"  L_p(E, 1) = {L_p_1}")
        
        # Compute p-adic period
        omega_p = libadic.EllipticLFunctions.p_adic_period(E, p, precision)
        print(f"  Ω_p = {omega_p}")
        
        # Analytic rank
        rank_p = libadic.EllipticLFunctions.compute_analytic_rank(E, p, precision)
        print(f"  Analytic rank: {rank_p}")
        
        # For exceptional primes, compute L-invariant
        if reduction == -1:  # Split multiplicative
            L_inv = libadic.EllipticLFunctions.L_invariant(E, p, precision)
            print(f"  L-invariant (exceptional zero): {L_inv}")

def demo_rank_computation():
    """Demonstrate algebraic and analytic rank computation"""
    print("\n" + "="*60)
    print("Rank Computation")
    print("="*60)
    
    # Test curves with known ranks
    test_curves = [
        (libadic.EllipticCurve(0, -1), "11a1", 0),
        (libadic.EllipticCurve.curve_37a1(), "37a1", 1),
        (libadic.EllipticCurve.curve_389a1(), "389a1", 2),
    ]
    
    for E, label, expected_rank in test_curves:
        print(f"\nCurve {label}: {E.to_string()}")
        print(f"  Conductor: {E.get_conductor()}")
        
        # Algebraic rank (if computable)
        alg_rank = E.compute_algebraic_rank()
        if alg_rank >= 0:
            print(f"  Algebraic rank: {alg_rank}")
        else:
            print(f"  Algebraic rank: Unable to compute")
        
        # Analytic rank via L-function
        p = 5
        precision = 30
        analytic_rank = libadic.EllipticLFunctions.compute_analytic_rank(E, p, precision)
        print(f"  p-adic analytic rank (p={p}): {analytic_rank}")
        
        # Compare with expected
        print(f"  Expected rank: {expected_rank}")
        if alg_rank >= 0 and alg_rank == expected_rank:
            print(f"  ✓ Algebraic rank matches!")
        if analytic_rank == expected_rank:
            print(f"  ✓ Analytic rank matches!")

def demo_cm_curves():
    """Demonstrate curves with complex multiplication"""
    print("\n" + "="*60)
    print("Complex Multiplication")
    print("="*60)
    
    # Curves with CM
    cm_curves = [
        (0, 1, -3),    # CM by Z[ω], ω = e^(2πi/3)
        (0, -1, -3),   # CM by Z[ω]
        (-1, 0, -4),   # CM by Z[i]
        (1, 0, -4),    # CM by Z[i]
    ]
    
    for a, b, cm_disc in cm_curves:
        E = libadic.EllipticCurve(a, b)
        print(f"\nCurve: {E.to_string()}")
        
        # Check for CM
        has_cm = E.has_cm()
        print(f"  Has CM: {'Yes' if has_cm else 'No'}")
        
        if has_cm:
            disc = E.get_cm_discriminant()
            print(f"  CM discriminant: {disc}")
            print(f"  Expected: {cm_disc}")
            
            # CM curves have special L-function properties
            print(f"  Special property: L-function factors through Hecke characters")

def demo_congruent_numbers():
    """Demonstrate congruent number curves"""
    print("\n" + "="*60)
    print("Congruent Number Problem")
    print("="*60)
    
    print("\nA positive integer n is congruent if it's the area of a")
    print("right triangle with rational sides.")
    print("\nn is congruent ⟺ E_n: y² = x³ - n²x has positive rank")
    
    # Test some numbers
    test_numbers = [5, 6, 7, 13, 14, 15]
    
    for n in test_numbers:
        E = libadic.EllipticCurve.congruent_number_curve(n)
        print(f"\nn = {n}:")
        print(f"  Curve E_{n}: {E.to_string()}")
        
        # Try to compute rank
        rank = E.compute_algebraic_rank()
        
        if rank > 0:
            print(f"  Rank = {rank} > 0")
            print(f"  ✓ {n} is a congruent number!")
        elif rank == 0:
            print(f"  Rank = 0")
            print(f"  ✗ {n} is not a congruent number")
        else:
            # Use analytic rank as fallback
            p = 5
            precision = 20
            analytic_rank = libadic.EllipticLFunctions.compute_analytic_rank(E, p, precision)
            if analytic_rank > 0:
                print(f"  Analytic rank = {analytic_rank} > 0")
                print(f"  ✓ {n} is likely a congruent number")
            else:
                print(f"  Analytic rank = {analytic_rank}")
                print(f"  {n} is likely not congruent")

def main():
    """Run all elliptic curve demonstrations"""
    print("╔" + "="*58 + "╗")
    print("║" + " " * 12 + "Elliptic Curves and p-adic L-functions" + " " * 7 + "║")
    print("║" + " " * 20 + "libadic Demonstration" + " " * 17 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Run demonstrations
        demo_basic_elliptic_curves()
        demo_torsion_subgroup()
        demo_l_series()
        demo_padic_points()
        demo_padic_l_functions()
        demo_rank_computation()
        demo_cm_curves()
        demo_congruent_numbers()
        
        print("\n" + "="*60)
        print("All demonstrations completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
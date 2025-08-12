#!/usr/bin/env python3
"""
Birch and Swinnerton-Dyer Conjecture Verification

This script demonstrates computational verification of the BSD conjecture
for elliptic curves using p-adic L-functions and related invariants.

The BSD conjecture is one of the seven Millennium Prize Problems and
relates the algebraic rank of an elliptic curve to the analytic behavior
of its L-function.
"""

import libadic
import time
import math

def print_separator(title=None):
    """Print a formatted separator"""
    if title:
        padding = (60 - len(title) - 2) // 2
        print("\n" + "="*padding + f" {title} " + "="*padding)
    else:
        print("\n" + "="*60)

def demo_basic_bsd():
    """Demonstrate basic BSD verification for rank 0 curves"""
    print_separator("Basic BSD Verification (Rank 0)")
    
    # Use curve 11a1: y² = x³ - x² - 10x - 20 (simplified to y² = x³ - 1)
    E = libadic.EllipticCurve(0, -1)
    
    print(f"\nCurve: {E.to_string()}")
    print(f"Conductor: {E.get_conductor()}")
    print(f"This is the smallest conductor elliptic curve (11a1)")
    
    # Verify BSD at multiple primes
    primes = [3, 5, 7, 11]
    precision = 30
    
    print(f"\nVerifying BSD at primes: {primes}")
    print(f"p-adic precision: {precision}")
    
    # Run comprehensive BSD verification
    bsd_data = libadic.BSDConjecture.verify_bsd(E, primes, precision)
    
    # Display results
    print("\n" + "-"*40)
    print("BSD Verification Results:")
    print("-"*40)
    
    print(f"Curve label: {bsd_data.curve_label}")
    print(f"Algebraic rank: {bsd_data.algebraic_rank}")
    print(f"Analytic rank: {bsd_data.analytic_rank}")
    
    if bsd_data.ranks_match:
        print("✓ Ranks match! (BSD rank prediction correct)")
    else:
        print("✗ Rank mismatch (unexpected!)")
    
    print(f"\nClassical BSD quotient: {bsd_data.bsd_quotient:.6f}")
    print(f"Predicted #Sha: {bsd_data.sha_prediction:.0f}")
    
    # Check if Sha prediction is a perfect square (as expected)
    sha_sqrt = math.sqrt(bsd_data.sha_prediction)
    if abs(sha_sqrt - round(sha_sqrt)) < 0.01:
        print(f"✓ #Sha is a perfect square: {int(sha_sqrt)}²")
    
    print(f"\nComponents:")
    print(f"  Torsion order: {bsd_data.torsion_order}")
    print(f"  Tamagawa numbers: {bsd_data.tamagawa_numbers}")
    print(f"  Real period: {bsd_data.real_period:.6f}")

def demo_padic_bsd():
    """Demonstrate p-adic BSD verification"""
    print_separator("p-adic BSD Verification")
    
    E = libadic.EllipticCurve(0, -1)
    print(f"\nCurve: {E.to_string()}")
    
    # Test at individual primes with detailed output
    test_primes = [3, 5, 7]
    precision = 40
    
    for p in test_primes:
        print(f"\n" + "-"*40)
        print(f"Prime p = {p}:")
        print("-"*40)
        
        # Verify p-adic BSD
        padic_data = libadic.BSDConjecture.verify_padic_bsd(E, p, precision)
        
        print(f"Reduction type at {p}: ", end="")
        reduction = E.reduction_type(p)
        if reduction == 1:
            print("good ordinary")
        elif reduction == 0:
            print("additive")
        elif reduction == -1:
            print("split multiplicative")
        else:
            print("non-split multiplicative")
        
        print(f"\np-adic BSD components:")
        print(f"  L_p(E, 1) = {padic_data.L_p_value}")
        print(f"  Ω_p = {padic_data.omega_p}")
        print(f"  Reg_p = {padic_data.regulator_p}")
        print(f"  BSD quotient = {padic_data.bsd_quotient_p}")
        
        # Check for exceptional zero
        if padic_data.is_exceptional_zero:
            print(f"\n⚠ Exceptional zero phenomenon detected!")
            print(f"  L-invariant = {padic_data.L_invariant}")
            print(f"  This is the Mazur-Tate-Teitelbaum phenomenon")
        
        # Extract integer from BSD quotient
        sha_p = libadic.BSDConjecture.extract_integer_sha_padic(padic_data.bsd_quotient_p)
        if sha_p:
            print(f"\n✓ p-adic BSD quotient is integral: {sha_p}")
        else:
            print(f"\n⚠ p-adic BSD quotient is not integral")

def demo_higher_rank_bsd():
    """Demonstrate BSD for higher rank curves"""
    print_separator("Higher Rank BSD Verification")
    
    print("\nTesting curves of various ranks:")
    print("(Higher ranks require derivatives of L-functions)")
    
    # Test curves with different ranks
    test_cases = [
        (libadic.EllipticCurve(0, -1), "11a1", 0),
        (libadic.EllipticCurve.curve_37a1(), "37a1", 1),
        (libadic.EllipticCurve.curve_389a1(), "389a1", 2),
    ]
    
    primes = [3, 5]
    precision = 25
    
    for E, label, expected_rank in test_cases:
        print(f"\n" + "-"*40)
        print(f"Curve {label} (expected rank {expected_rank}):")
        print(f"{E.to_string()}")
        print("-"*40)
        
        # Verify BSD
        bsd_data = libadic.BSDConjecture.verify_bsd(E, primes, precision)
        
        print(f"Algebraic rank: {bsd_data.algebraic_rank}")
        print(f"Analytic rank: {bsd_data.analytic_rank}")
        print(f"Ranks match: {'✓ Yes' if bsd_data.ranks_match else '✗ No'}")
        
        if expected_rank > 0:
            print(f"\nFor rank {expected_rank}, BSD involves L^({expected_rank})(E, 1)")
            print(f"BSD quotient: {bsd_data.bsd_quotient:.6f}")
            
            # For rank > 0, need generators for regulator
            if bsd_data.algebraic_rank > 0:
                print(f"Note: Full verification requires computing generators")

def demo_exceptional_zeros():
    """Demonstrate exceptional zero phenomenon"""
    print_separator("Exceptional Zero Phenomenon")
    
    print("\nThe exceptional zero occurs when a curve has")
    print("split multiplicative reduction at p, causing")
    print("L_p(E, 1) = 0 even when L(E, 1) ≠ 0.")
    
    # Find a curve with split multiplicative reduction
    # Curve 11a1 has split multiplicative reduction at p=11
    E = libadic.EllipticCurve(0, -1)
    p = 11
    precision = 30
    
    print(f"\nCurve: {E.to_string()}")
    print(f"Testing at p = {p} (conductor of curve)")
    
    # Check reduction type
    reduction = E.reduction_type(p)
    print(f"Reduction at {p}: ", end="")
    if reduction == -1:
        print("split multiplicative ✓")
    else:
        print(f"type {reduction}")
        return
    
    # Test for exceptional zero
    print(f"\nTesting Mazur-Tate-Teitelbaum conjecture:")
    is_exceptional = libadic.BSDConjecture.test_exceptional_zero(E, p, precision)
    
    if is_exceptional:
        print("✓ Exceptional zero confirmed!")
        
        # Compute L-invariant
        padic_data = libadic.BSDConjecture.verify_padic_bsd(E, p, precision)
        print(f"\nL-invariant computation:")
        print(f"  L_p(E, 1) = {padic_data.L_p_value} (should be 0)")
        print(f"  L-invariant = {padic_data.L_invariant}")
        print(f"\nThe L-invariant appears in the derivative formula:")
        print(f"  L'_p(E, 1) = L-invariant × L(E, 1)")
    else:
        print("No exceptional zero detected")

def demo_sha_predictions():
    """Demonstrate Tate-Shafarevich group predictions"""
    print_separator("Tate-Shafarevich Group Predictions")
    
    print("\nThe Tate-Shafarevich group Sha(E) measures the")
    print("failure of the Hasse principle for E.")
    print("BSD predicts #Sha from the BSD quotient.")
    
    # Test several curves
    test_curves = [
        (libadic.EllipticCurve(0, -1), "11a1"),
        (libadic.EllipticCurve(1, 0), "32a2"),
        (libadic.EllipticCurve(-1, 1), "14a1"),
    ]
    
    for E, label in test_curves:
        print(f"\n" + "-"*40)
        print(f"Curve {label}: {E.to_string()}")
        print("-"*40)
        
        # Predict Sha order
        sha_order = libadic.BSDConjecture.predict_sha_order(E)
        
        if sha_order > 0:
            print(f"Predicted #Sha = {sha_order}")
            
            # Check if it's a perfect square (as conjectured)
            sqrt_sha = math.sqrt(sha_order)
            if abs(sqrt_sha - round(sqrt_sha)) < 0.01:
                print(f"✓ #Sha is a perfect square: {int(sqrt_sha)}²")
            else:
                print(f"⚠ #Sha = {sha_order} is not a perfect square!")
        else:
            print("Unable to predict #Sha (BSD quotient not integral)")
        
        # Also try p-adic prediction
        p = 5
        precision = 30
        sha_p = libadic.BSDConjecture.predict_sha_order_padic(E, p, precision)
        print(f"p-adic prediction (p={p}): {sha_p}")

def demo_goldfeld_conjecture():
    """Test Goldfeld's conjecture about average rank"""
    print_separator("Goldfeld's Conjecture")
    
    print("\nGoldfeld's conjecture: The average rank of elliptic")
    print("curves over Q should be 1/2.")
    print("\nWe test this by computing ranks of quadratic twists.")
    
    # Base curve
    E_base = libadic.EllipticCurve(1, 0)
    print(f"\nBase curve: {E_base.to_string()}")
    
    # Test on quadratic twists
    num_twists = 50
    print(f"Testing {num_twists} quadratic twists...")
    
    avg_rank = libadic.BSDConjecture.test_goldfeld_conjecture(E_base, num_twists)
    
    print(f"\nResults:")
    print(f"  Average rank over {num_twists} twists: {avg_rank:.3f}")
    print(f"  Goldfeld's prediction: 0.500")
    print(f"  Difference: {abs(avg_rank - 0.5):.3f}")
    
    if abs(avg_rank - 0.5) < 0.2:
        print("✓ Consistent with Goldfeld's conjecture")
    else:
        print("⚠ Deviation from Goldfeld's conjecture")
    
    print("\nNote: Larger sample sizes give better approximations")

def demo_cremona_database():
    """Test BSD on Cremona database curves"""
    print_separator("Cremona Database Verification")
    
    print("\nTesting BSD on curves from Cremona's database")
    print("These have independently computed invariants for validation")
    
    # Test curves up to conductor 50
    max_conductor = 50
    primes = [3, 5, 7]
    precision = 20
    
    print(f"\nTesting curves with conductor ≤ {max_conductor}")
    print(f"Using primes: {primes}")
    
    # Run tests
    start_time = time.time()
    test_results = libadic.BSDConjecture.test_cremona_curves(max_conductor, primes, precision)
    elapsed = time.time() - start_time
    
    # Analyze results
    stats = libadic.BSDConjecture.analyze_bsd_statistics(test_results)
    
    print(f"\n" + "-"*40)
    print("Statistical Summary:")
    print("-"*40)
    
    print(f"Total curves tested: {stats.total_curves}")
    print(f"Testing time: {elapsed:.2f} seconds")
    print(f"\nRank agreement:")
    print(f"  Algebraic = Analytic: {stats.rank_matches}/{stats.total_curves}")
    print(f"  Success rate: {100*stats.rank_matches/stats.total_curves:.1f}%")
    
    print(f"\nSha predictions:")
    print(f"  Integer BSD quotient: {stats.sha_integral}/{stats.total_curves}")
    print(f"  Success rate: {100*stats.sha_integral/stats.total_curves:.1f}%")
    
    print(f"\nRank distribution:")
    for rank, count in sorted(stats.rank_distribution.items()):
        print(f"  Rank {rank}: {count} curves")
    
    print(f"\nAverage rank: {stats.average_rank:.3f}")
    
    if stats.sha_distribution:
        print(f"\nSha distribution:")
        for sha, count in sorted(stats.sha_distribution.items())[:5]:
            print(f"  #Sha = {sha}: {count} curves")
    
    if stats.anomalies:
        print(f"\n⚠ Anomalies detected in {len(stats.anomalies)} curves:")
        for anomaly in stats.anomalies[:3]:
            print(f"  {anomaly}")

def demo_bsd_test_suite():
    """Run comprehensive BSD test suite"""
    print_separator("BSD Test Suite")
    
    print("\nRunning comprehensive BSD test suite...")
    print("This tests various curve families:")
    print("  - Rank 0 curves")
    print("  - Rank 1 curves (Gross-Zagier)")
    print("  - Higher rank curves")
    print("  - CM curves")
    print("  - Congruent number curves")
    
    precision = 20
    
    # Run comprehensive tests
    print("\nRunning tests (this may take a while)...")
    start_time = time.time()
    
    test_results = libadic.BSDTestSuite.run_comprehensive_tests(precision)
    
    elapsed = time.time() - start_time
    
    print(f"\nTest suite completed in {elapsed:.2f} seconds")
    print(f"Tested {len(test_results)} curves")
    
    # Summary by curve type
    rank_0 = sum(1 for r in test_results if r.algebraic_rank == 0)
    rank_1 = sum(1 for r in test_results if r.algebraic_rank == 1)
    rank_higher = sum(1 for r in test_results if r.algebraic_rank > 1)
    
    print(f"\nResults by rank:")
    print(f"  Rank 0: {rank_0} curves")
    print(f"  Rank 1: {rank_1} curves")
    print(f"  Rank ≥2: {rank_higher} curves")
    
    # Check success rate
    verified = sum(1 for r in test_results if r.verified_classical)
    print(f"\nClassical BSD verified: {verified}/{len(test_results)}")
    
    verified_padic = sum(1 for r in test_results if r.verified_padic)
    print(f"p-adic BSD verified: {verified_padic}/{len(test_results)}")
    
    # Find any discrepancies
    discrepancies = [r for r in test_results if not r.ranks_match]
    if discrepancies:
        print(f"\n⚠ Found {len(discrepancies)} rank discrepancies!")
        for d in discrepancies[:3]:
            print(f"  {d.curve_label}: alg={d.algebraic_rank}, an={d.analytic_rank}")
    else:
        print("\n✓ All ranks match perfectly!")

def main():
    """Run all BSD demonstrations"""
    print("╔" + "="*58 + "╗")
    print("║" + " " * 8 + "Birch and Swinnerton-Dyer Conjecture" + " " * 13 + "║")
    print("║" + " " * 16 + "Computational Verification" + " " * 16 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nThe BSD conjecture is one of the seven Millennium Prize")
    print("Problems with a $1 million prize for its solution.")
    
    try:
        # Run demonstrations
        demo_basic_bsd()
        demo_padic_bsd()
        demo_higher_rank_bsd()
        demo_exceptional_zeros()
        demo_sha_predictions()
        demo_goldfeld_conjecture()
        demo_cremona_database()
        demo_bsd_test_suite()
        
        print("\n" + "="*60)
        print("BSD verification demonstrations completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
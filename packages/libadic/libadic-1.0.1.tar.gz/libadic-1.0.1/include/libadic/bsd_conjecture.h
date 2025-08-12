#ifndef LIBADIC_BSD_CONJECTURE_H
#define LIBADIC_BSD_CONJECTURE_H

#include "libadic/elliptic_curve.h"
#include "libadic/elliptic_l_functions.h"
#include "libadic/qp.h"
#include <vector>
#include <optional>

namespace libadic {

/**
 * Birch and Swinnerton-Dyer Conjecture verification framework
 * 
 * The BSD conjecture is one of the seven Millennium Prize Problems.
 * It relates the algebraic rank of an elliptic curve to the analytic
 * behavior of its L-function.
 * 
 * Classical BSD: 
 *   ord_{s=1} L(E,s) = rank(E(Q))
 *   
 *   lim_{s→1} L(E,s)/(s-1)^r = Ω·R·∏c_p·#Sha / #E_tors²
 * 
 * p-adic BSD (Mazur-Tate-Teitelbaum):
 *   Similar formula with p-adic L-function L_p(E,s) and p-adic quantities
 * 
 * This class provides tools to computationally verify BSD for specific curves.
 */
class BSDConjecture {
public:
    /**
     * BSD data for a curve
     */
    struct BSDData {
        // Curve identification
        std::string curve_label;
        long conductor;
        
        // Ranks
        long algebraic_rank;      // rank(E(Q))
        long analytic_rank;       // ord_{s=1} L(E,s)
        bool ranks_match;
        
        // Classical BSD quotient
        double bsd_quotient;      // L^(r)(E,1) / (Ω·R·∏c_p) · #E_tors²
        double sha_prediction;    // Predicted #Sha from BSD
        
        // p-adic BSD data
        struct PadicBSDData {
            long p;
            Qp L_p_value;         // L_p(E,1) or derivative
            Qp omega_p;           // p-adic period
            Qp regulator_p;       // p-adic regulator
            Qp bsd_quotient_p;    // p-adic BSD quotient
            long precision;
            bool is_exceptional_zero;  // Split multiplicative case
            Qp L_invariant;           // Teitelbaum's L-invariant if exceptional
        };
        std::vector<PadicBSDData> padic_data;
        
        // Components
        long torsion_order;
        std::vector<long> tamagawa_numbers;
        double real_period;
        
        // Verification status
        bool verified_classical;
        bool verified_padic;
        std::string notes;
    };
    
    /**
     * Verify BSD conjecture for a given curve
     * 
     * Performs comprehensive BSD verification:
     * 1. Computes algebraic and analytic ranks
     * 2. Evaluates L-function (or derivatives)
     * 3. Computes periods, regulators, local factors
     * 4. Checks BSD quotient
     * 
     * @param E The elliptic curve
     * @param primes List of primes for p-adic verification
     * @param precision p-adic precision
     * @return BSD verification data
     */
    static BSDData verify_bsd(const EllipticCurve& E, 
                              const std::vector<long>& primes = {3, 5, 7, 11},
                              long precision = 20);
    
    /**
     * Verify p-adic BSD for a specific prime
     * 
     * Tests the p-adic version of BSD:
     * L_p(E,1) ~ Ω_p · R_p · (local factors) / #E_tors²
     * 
     * Handles:
     * - Ordinary case: standard formula
     * - Supersingular case: uses L_p^± 
     * - Exceptional zero: includes L-invariant
     */
    static BSDData::PadicBSDData verify_padic_bsd(const EllipticCurve& E, 
                                                  long p, 
                                                  long precision);
    
    /**
     * Compute analytic rank via L-function
     * 
     * Determines ord_{s=1} L(E,s) by:
     * 1. Computing L(E,1), L'(E,1), L''(E,1), ...
     * 2. Finding first non-zero derivative
     * 
     * @return Analytic rank, or -1 if cannot determine
     */
    static long compute_analytic_rank(const EllipticCurve& E, long max_rank = 5);
    
    /**
     * Compute p-adic analytic rank
     * 
     * Order of vanishing of L_p(E,s) at s=1
     * May differ from classical rank in exceptional zero case
     */
    static long compute_padic_analytic_rank(const EllipticCurve& E, 
                                           long p, 
                                           long precision,
                                           long max_rank = 5);
    
    /**
     * Predict Tate-Shafarevich group order from BSD
     * 
     * #Sha = BSD quotient (if integral)
     * 
     * @return Predicted #Sha, or 0 if BSD quotient not close to integer
     */
    static long predict_sha_order(const EllipticCurve& E);
    static Qp predict_sha_order_padic(const EllipticCurve& E, long p, long precision);
    
    /**
     * Test BSD for a family of curves
     * 
     * Useful for finding patterns or counterexamples
     */
    static std::vector<BSDData> test_curve_family(
        const std::vector<EllipticCurve>& curves,
        const std::vector<long>& primes = {3, 5, 7},
        long precision = 20
    );
    
    /**
     * Test BSD on standard database curves
     * 
     * Uses Cremona database curves with known invariants
     * Allows verification against published data
     */
    static std::vector<BSDData> test_cremona_curves(
        long max_conductor = 100,
        const std::vector<long>& primes = {3, 5, 7},
        long precision = 20
    );
    
    /**
     * Check if BSD quotient is close to an integer
     * 
     * BSD predicts the quotient should equal #Sha
     * This function checks if quotient ≈ integer
     * 
     * @param quotient The BSD quotient
     * @param tolerance Relative tolerance for integer check
     * @return The integer if close, nullopt otherwise
     */
    static std::optional<long> extract_integer_sha(double quotient, 
                                                   double tolerance = 0.01);
    static std::optional<long> extract_integer_sha_padic(const Qp& quotient);
    
    /**
     * Goldfeld's conjecture test
     * 
     * Average rank should be 1/2
     * Tests this on a family of quadratic twists
     */
    static double test_goldfeld_conjecture(const EllipticCurve& E,
                                          long num_twists = 100);
    
    /**
     * Exceptional zero investigation
     * 
     * For curves with split multiplicative reduction at p,
     * L_p(E,1) may vanish even when L(E,1) ≠ 0
     * This is the "exceptional zero" phenomenon
     * 
     * Tests Mazur-Tate-Teitelbaum conjecture:
     * L'_p(E,1) = L_inv · L(E,1)
     */
    static bool test_exceptional_zero(const EllipticCurve& E, 
                                     long p, 
                                     long precision);
    
    /**
     * Generate BSD verification report
     * 
     * Creates detailed report of BSD verification
     * Including all computed quantities and checks
     */
    static std::string generate_bsd_report(const BSDData& data);
    
    /**
     * Statistical analysis of BSD across many curves
     * 
     * Looks for patterns in:
     * - BSD quotient distribution
     * - Rank distribution
     * - Sha predictions
     * - p-adic phenomena
     */
    struct BSDStatistics {
        long total_curves;
        long rank_matches;      // Curves where algebraic = analytic rank
        long sha_integral;      // Curves where BSD quotient ≈ integer
        double average_rank;
        std::map<long, long> rank_distribution;
        std::map<long, long> sha_distribution;
        std::vector<std::string> anomalies;  // Curves with unexpected behavior
    };
    
    static BSDStatistics analyze_bsd_statistics(const std::vector<BSDData>& data);
    
private:
    // Helper functions
    static std::vector<long> compute_tamagawa_numbers(const EllipticCurve& E);
    static double compute_real_period(const EllipticCurve& E);
    static double compute_real_regulator(const EllipticCurve& E,
                                        const std::vector<EllipticCurve::Point>& generators);
    static bool is_exceptional_prime(const EllipticCurve& E, long p);
};

/**
 * Test suite for BSD conjecture
 * 
 * Automated testing framework similar to Reid-Li tests
 */
class BSDTestSuite {
public:
    /**
     * Run comprehensive BSD tests
     * 
     * Tests BSD on various curve families:
     * - Rank 0 curves (easiest case)
     * - Rank 1 curves (Gross-Zagier)
     * - Higher rank curves
     * - CM curves
     * - Congruent number curves
     * 
     * @return Test results and any discrepancies found
     */
    static std::vector<BSDConjecture::BSDData> run_comprehensive_tests(long precision = 20);
    
    /**
     * Test BSD limits
     * 
     * Similar to Reid-Li limit finding:
     * Tests BSD at increasing precision and conductor
     * Looking for breakdown points
     */
    static void find_bsd_limits();
    
    /**
     * Compare with known results
     * 
     * Verifies computations against published BSD data
     * From Cremona tables, LMFDB, etc.
     */
    static bool verify_against_known_data();
};

} // namespace libadic

#endif // LIBADIC_BSD_CONJECTURE_H
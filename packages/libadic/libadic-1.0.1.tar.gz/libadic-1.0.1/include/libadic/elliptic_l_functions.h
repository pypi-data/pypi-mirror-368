#ifndef LIBADIC_ELLIPTIC_L_FUNCTIONS_H
#define LIBADIC_ELLIPTIC_L_FUNCTIONS_H

#include "libadic/qp.h"
#include "libadic/elliptic_curve.h"
#include "libadic/padic_log.h"
#include <vector>
#include <map>

namespace libadic {

/**
 * p-adic L-functions for elliptic curves
 * 
 * Implements the Mazur-Tate-Teitelbaum construction of p-adic L-functions
 * for elliptic curves, which are essential for testing the p-adic version
 * of the Birch and Swinnerton-Dyer conjecture.
 * 
 * Key features:
 * - Mazur-Tate-Teitelbaum p-adic L-function L_p(E, s)
 * - Special value L_p(E, 1) related to BSD
 * - p-adic regulator computation
 * - Handling of ordinary and supersingular cases
 * - Exceptional zero phenomena
 */
class EllipticLFunctions {
private:
    // Cache for computed values
    struct ELKey {
        std::string curve_id;  // Unique identifier for curve
        long p;
        long s;
        long precision;
        
        bool operator<(const ELKey& other) const {
            if (curve_id != other.curve_id) return curve_id < other.curve_id;
            if (p != other.p) return p < other.p;
            if (s != other.s) return s < other.s;
            return precision < other.precision;
        }
    };
    
    static std::map<ELKey, Qp> lp_cache;
    
    // Helper functions
    static Qp compute_alpha_eigenvalue(const EllipticCurve& E, long p, long precision);
    static Qp compute_modular_symbol(const EllipticCurve& E, long a, long b, long p, long precision);
    static bool is_ordinary(const EllipticCurve& E, long p);
    static bool is_supersingular(const EllipticCurve& E, long p);
    
public:
    /**
     * Mazur-Tate-Teitelbaum p-adic L-function L_p(E, s)
     * 
     * For an elliptic curve E and prime p:
     * - If E has good ordinary reduction at p, uses standard construction
     * - If E has good supersingular reduction, uses ± decomposition
     * - If E has bad reduction, handles exceptional cases
     * 
     * @param E The elliptic curve
     * @param s The p-adic variable (usually s = 1 for BSD)
     * @param p The prime
     * @param precision p-adic precision
     * @return L_p(E, s) as a p-adic number
     */
    static Qp mazur_tate_teitelbaum(const EllipticCurve& E, long s, long p, long precision);
    
    /**
     * Special value L_p(E, 1) for BSD conjecture
     * 
     * The p-adic BSD conjecture relates:
     * L_p(E, 1) / Ω_p ~ #Sha(E) * ∏c_v * #E_tors² / (#E(Q) * Reg_p)
     * 
     * where:
     * - Ω_p is the p-adic period
     * - Sha(E) is the Tate-Shafarevich group
     * - c_v are Tamagawa numbers
     * - E_tors is the torsion subgroup
     * - Reg_p is the p-adic regulator
     */
    static Qp L_p_at_one(const EllipticCurve& E, long p, long precision);
    
    /**
     * p-adic regulator matrix
     * 
     * For generators P_1, ..., P_r of E(Q)/E(Q)_tors:
     * Reg_p = det(<P_i, P_j>_p) where <,>_p is the p-adic height pairing
     * 
     * @param E The elliptic curve
     * @param generators Basis for E(Q) modulo torsion
     * @param p The prime
     * @param precision p-adic precision
     * @return The p-adic regulator
     */
    static Qp p_adic_regulator(const EllipticCurve& E, 
                               const std::vector<EllipticCurve::Point>& generators,
                               long p, long precision);
    
    /**
     * p-adic height pairing
     * 
     * Canonical p-adic height pairing between two points
     * Uses Schneider's formula for computation
     */
    static Qp p_adic_height(const EllipticCurve& E,
                            const EllipticCurve::Point& P,
                            const EllipticCurve::Point& Q,
                            long p, long precision);
    
    /**
     * p-adic period (Néron differential)
     * 
     * ∫_E(Z_p) ω where ω = dx/(2y + a_1x + a_3)
     * For our simplified Weierstrass form: ω = dx/2y
     */
    static Qp p_adic_period(const EllipticCurve& E, long p, long precision);
    
    /**
     * Analytic rank computation
     * 
     * Computes the order of vanishing of L_p(E, s) at s = 1
     * This should equal the algebraic rank by BSD
     */
    static long compute_analytic_rank(const EllipticCurve& E, long p, long precision);
    
    /**
     * L-series derivative at s = 1
     * 
     * For curves of rank ≥ 1, need L'_p(E, 1) or higher derivatives
     */
    static Qp L_p_derivative(const EllipticCurve& E, long k, long p, long precision);
    
    /**
     * Teitelbaum's L-invariant
     * 
     * For curves with split multiplicative reduction at p
     * Appears in exceptional zero formula
     */
    static Qp L_invariant(const EllipticCurve& E, long p, long precision);
    
    /**
     * Plus/minus p-adic L-functions for supersingular primes
     * 
     * When E has supersingular reduction at p, L_p splits as:
     * L_p^± (E, s) with different interpolation properties
     */
    static Qp L_p_plus(const EllipticCurve& E, long s, long p, long precision);
    static Qp L_p_minus(const EllipticCurve& E, long s, long p, long precision);
    
    /**
     * Modular symbols for L-value computation
     * 
     * Computes {r, s}^+ = ∫_r^s f(τ)dτ where f is the modular form for E
     * Essential for computing L_p without computing infinitely many a_n
     */
    static Qp modular_symbol_plus(const EllipticCurve& E, 
                                  const std::pair<long, long>& r,
                                  const std::pair<long, long>& s,
                                  long p, long precision);
    
    /**
     * Complex L-function approximation (for comparison)
     * 
     * Computes L(E, s) = ∏_p (1 - a_p p^{-s} + ε_p p^{1-2s})^{-1}
     * Used to verify p-adic computations match classical values
     */
    static double complex_L_value(const EllipticCurve& E, double s, long num_terms = 1000);
    
    /**
     * Check functional equation
     * 
     * Verifies Λ(E, s) = ±Λ(E, 2-s) where Λ includes Gamma factors
     * Sign is the global root number
     */
    static bool verify_functional_equation(const EllipticCurve& E, long p, long precision);
    
    /**
     * Iwasawa theory invariants
     * 
     * Computes μ and λ invariants from the p-adic L-function
     * Iwasawa Main Conjecture relates these to Selmer groups
     */
    static std::pair<long, long> iwasawa_invariants(const EllipticCurve& E, long p, long precision);
};

/**
 * Helper class for modular form computations
 * Needed for L-function calculations via modular symbols
 */
class ModularFormHelper {
public:
    /**
     * Compute q-expansion coefficients of modular form associated to E
     * f = Σ a_n q^n where q = e^{2πiτ}
     */
    static std::vector<long> compute_q_expansion(const EllipticCurve& E, long num_terms);
    
    /**
     * Atkin-Lehner eigenvalue
     * w_N = ±1 determines functional equation sign
     */
    static int atkin_lehner_eigenvalue(const EllipticCurve& E);
    
    /**
     * Hecke eigenvalue at prime p
     * Should equal a_p for the curve
     */
    static long hecke_eigenvalue(const EllipticCurve& E, long p);
    
    /**
     * Period lattice computation
     * Fundamental periods Ω_+ and Ω_- for BSD
     */
    static std::pair<double, double> compute_periods(const EllipticCurve& E, long precision_bits);
};

} // namespace libadic

#endif // LIBADIC_ELLIPTIC_L_FUNCTIONS_H
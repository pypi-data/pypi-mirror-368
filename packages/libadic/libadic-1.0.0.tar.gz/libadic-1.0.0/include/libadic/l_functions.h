#ifndef LIBADIC_L_FUNCTIONS_H
#define LIBADIC_L_FUNCTIONS_H

#include "libadic/qp.h"
#include "libadic/characters.h"
#include "libadic/bernoulli.h"
#include "libadic/padic_log.h"
#include "libadic/padic_gamma.h"
#include <map>
#include <cmath>
#include <string>

namespace libadic {

/**
 * Kubota-Leopoldt p-adic L-functions
 * Implementation follows Washington's "Introduction to Cyclotomic Fields"
 */
class LFunctions {
private:
    // Cache for computed L-values
    struct LKey {
        long s;
        long p;
        long precision;
        long modulus;
        long conductor;
        std::string char_fingerprint;
        
        bool operator<(const LKey& other) const {
            if (s != other.s) return s < other.s;
            if (p != other.p) return p < other.p;
            if (precision != other.precision) return precision < other.precision;
            if (modulus != other.modulus) return modulus < other.modulus;
            if (conductor != other.conductor) return conductor < other.conductor;
            return char_fingerprint < other.char_fingerprint;
        }
    };
    
    static std::map<LKey, Qp> l_cache;
    static std::map<LKey, Qp> l_derivative_cache;
    static std::map<std::pair<long, long>, std::vector<Qp>> mahler_cache;
    
public:
    /**
     * Compute L_p(s, χ) - the Kubota-Leopoldt p-adic L-function
     * For s = 0: L_p(0, χ) = -(1 - χ(p)p^{-1}) * B_{1,χ}
     * For s = 1-n (n > 0): L_p(1-n, χ) = -(1 - χ(p)p^{n-1}) * B_{n,χ}/n
     */
    static Qp kubota_leopoldt(long s, const DirichletCharacter& chi, long precision);
    
    /**
     * Compute L'_p(s, χ) - derivative of p-adic L-function
     * For s = 0, this uses the Ferrero-Washington formula
     */
    static Qp kubota_leopoldt_derivative(long s, const DirichletCharacter& chi, long precision);
    
public:  // Made public for Python bindings
    /**
     * Compute B_{1,χ} for the character χ
     */
    static Qp compute_B1_chi(const DirichletCharacter& chi, long precision);
    
    /**
     * Compute Euler factor (1 - χ(p)p^{s-1})
     */
    static Qp compute_euler_factor(const DirichletCharacter& chi, long s, long precision);
    
    /**
     * Compute L_p(s, χ) for positive integer s
     * Uses the formula: L_p(s, χ) = (1 - χ(p)p^{-s}) * L(s, χ)
     * where L(s, χ) is computed via partial sums
     */
    static Qp compute_positive_value(long s, const DirichletCharacter& chi, long precision);
    
    /**
     * Compute L'_p(0, χ) for odd characters
     * Uses Ferrero-Washington formula involving log Γ_p
     */
    static Qp compute_derivative_at_zero_odd(const DirichletCharacter& chi, long precision);
    
    /**
     * Compute L'_p(0, χ) for even characters
     */
    static Qp compute_derivative_at_zero_even(const DirichletCharacter& chi, long precision);
    
    /**
     * Compute log Γ_p for fractional arguments
     * Uses distribution relations and functional equations
     */
    static Qp compute_log_gamma_fractional(long numerator, long denominator, 
                                          long p, long precision);
    
    /**
     * Compute p-adic digamma function ψ_p(n)
     */
    static Qp compute_digamma(long n, long p, long precision);
    
    /**
     * Compute p-adic Euler constant
     */
    static Qp compute_padic_euler_constant(long p, long precision);
    
    /**
     * Compute Euler-Maclaurin correction for harmonic series
     */
    static Qp compute_euler_maclaurin_correction(long n, long p, long precision);
    
    /**
     * Compute Mahler coefficients for log Γ_p
     */
    static std::vector<Qp> compute_mahler_coefficients(long p, long precision);
    
public:
    /**
     * Clear all caches
     */
    static void clear_cache();
};

} // namespace libadic

#endif // LIBADIC_L_FUNCTIONS_H

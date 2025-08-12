#ifndef LIBADIC_CHARACTERS_H
#define LIBADIC_CHARACTERS_H

#include "libadic/zp.h"
#include "libadic/cyclotomic.h"
#include <vector>
#include <map>
#include <numeric>
#include <functional>

namespace libadic {

// Forward declaration
class LFunctions;

/**
 * Dirichlet character modulo n
 * A completely multiplicative function χ: (Z/nZ)* → C*
 * For p-adic computations, we use Teichmüller lifts
 */
class DirichletCharacter {
public:  // Made public for Python bindings
    long conductor;
    long modulus;
    long prime;
    std::vector<long> generators;  // Generators of (Z/nZ)*
    std::vector<long> generator_orders;  // Orders of generators
    std::vector<long> character_values;  // Values on generators
    mutable std::map<long, Cyclotomic> value_cache;  // Cache computed values
    
private:
    
    /**
     * Find generators of (Z/nZ)*
     */
    void compute_generators();
    
    static long pow_mod(long base, long exp, long mod);
    
    /**
     * Express a mod modulus in terms of generators
     */
    std::vector<long> express_in_generators(long a) const;
    
public:
    DirichletCharacter(long mod, long p);
    
    /**
     * Create a character from its values on generators
     */
    DirichletCharacter(long mod, long p, const std::vector<long>& gen_values);
    
    /**
     * Compute the conductor (smallest modulus for which χ is primitive)
     */
    void compute_conductor();
    
    long get_conductor() const { return conductor; }
    long get_modulus() const { return modulus; }
    long get_prime() const { return prime; }
    
    /**
     * Evaluate character at n
     * Returns value as element of Z/ord(χ)Z
     */
    long evaluate_at(long n) const;
    
    /**
     * Evaluate character and lift to p-adic number using Teichmüller lift
     */
    Zp evaluate(long n, long precision) const;
    
    /**
     * Evaluate as cyclotomic number
     */
    Cyclotomic evaluate_cyclotomic(long n, long precision) const;
    
    /**
     * Check if character is even: χ(-1) = 1
     */
    bool is_even() const;
    
    /**
     * Check if character is odd: χ(-1) = -1
     */
    bool is_odd() const;
    
    /**
     * Check if character is primitive
     */
    bool is_primitive() const;
    
    /**
     * Check if character is principal (trivial)
     */
    bool is_principal() const;
    
    /**
     * Get the order of the character
     */
    long get_order() const;
    
    /**
     * Enumerate all Dirichlet characters modulo n
     */
    static std::vector<DirichletCharacter> enumerate_characters(long modulus, long prime);
    
    /**
     * Enumerate primitive characters only
     */
    static std::vector<DirichletCharacter> enumerate_primitive_characters(long modulus, long prime);
    
    /**
     * Compute Gauss sum: g(χ) = Σ_{a mod n} χ(a) e^{2πia/n}
     * In p-adic setting, we use Teichmüller characters
     */
    Cyclotomic gauss_sum(long precision) const;
    
    /**
     * L-function value L(s, χ) at integer s
     * For Reid-Li, we need s = 0
     */
    Qp L_value(long s, long precision) const;
};

} // namespace libadic

#endif // LIBADIC_CHARACTERS_H
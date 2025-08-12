#ifndef LIBADIC_MONTGOMERY_CONTEXT_H
#define LIBADIC_MONTGOMERY_CONTEXT_H

#include "libadic/gmp_wrapper.h"
#include <memory>
#include <unordered_map>
#include <vector>

namespace libadic {
namespace crypto {

/**
 * Simplified Montgomery arithmetic context for p-adic operations
 * Provides fast modular arithmetic without expensive divisions
 */
class MontgomeryContext {
private:
    BigInt modulus;      // M = p^precision
    BigInt R;            // Montgomery radix (power of 2)
    BigInt R_inv;        // R^(-1) mod M
    BigInt M_prime;      // -M^(-1) mod R
    int k;               // Number of bits in R (R = 2^k)
    
    void initialize_constants();
    
public:
    MontgomeryContext(const BigInt& prime, long precision);
    
    // Convert to/from Montgomery form
    BigInt to_montgomery(const BigInt& x) const;
    BigInt from_montgomery(const BigInt& x_mont) const;
    
    // Core operations
    BigInt montgomery_reduce(const BigInt& x) const;
    BigInt montgomery_multiply(const BigInt& a_mont, const BigInt& b_mont) const;
    BigInt montgomery_add(const BigInt& a_mont, const BigInt& b_mont) const;
    
    // Getters
    const BigInt& get_modulus() const { return modulus; }
};

/**
 * Cache for Montgomery contexts to avoid recreation
 */
class MontgomeryContextCache {
private:
    struct PairHash {
        size_t operator()(const std::pair<std::string, long>& p) const {
            return std::hash<std::string>()(p.first) ^ (std::hash<long>()(p.second) << 1);
        }
    };
    
    static std::unordered_map<std::pair<std::string, long>, 
                              std::shared_ptr<MontgomeryContext>, 
                              PairHash> cache;
    
public:
    static std::shared_ptr<MontgomeryContext> get_context(const BigInt& prime, long precision);
    static void clear_cache();
};

} // namespace crypto
} // namespace libadic

#endif // LIBADIC_MONTGOMERY_CONTEXT_H
#include "libadic/montgomery_context.h"
#include <stdexcept>

namespace libadic {
namespace crypto {

// Static cache initialization
std::unordered_map<std::pair<std::string, long>, 
                   std::shared_ptr<MontgomeryContext>, 
                   MontgomeryContextCache::PairHash> MontgomeryContextCache::cache;

MontgomeryContext::MontgomeryContext(const BigInt& prime, long precision) {
    // Compute modulus M = p^precision
    modulus = prime.pow(precision);
    
    // Choose R = 2^k where k > log2(M)
    int bits_needed = modulus.bit_length() + 1;
    k = bits_needed;
    R = BigInt(1) << k;  // R = 2^k
    
    initialize_constants();
}

void MontgomeryContext::initialize_constants() {
    // Compute R_inv = R^(-1) mod M using extended GCD
    R_inv = R.mod_inverse(modulus);
    
    // Compute M_prime = -M^(-1) mod R
    BigInt M_inv_mod_R = modulus.mod_inverse(R);
    M_prime = R - M_inv_mod_R;
}

BigInt MontgomeryContext::to_montgomery(const BigInt& x) const {
    // Convert: x -> xR mod M
    return (x * R) % modulus;
}

BigInt MontgomeryContext::from_montgomery(const BigInt& x_mont) const {
    // Convert: x' -> x'R^(-1) mod M
    return montgomery_reduce(x_mont);
}

BigInt MontgomeryContext::montgomery_reduce(const BigInt& x) const {
    // Montgomery reduction algorithm
    // Input: x < R*M
    // Output: xR^(-1) mod M
    
    // Step 1: q = (x mod R) * M_prime mod R
    BigInt mask = (BigInt(1) << k) - BigInt(1);
    BigInt x_mod_R = x & mask;  // Fast mod for power of 2
    BigInt q = (x_mod_R * M_prime) & mask;
    
    // Step 2: a = (x + qM) / R
    BigInt a = (x + q * modulus) >> k;  // Fast division by power of 2
    
    // Step 3: If a >= M, return a - M, else return a
    if (a >= modulus) {
        return a - modulus;
    }
    return a;
}

BigInt MontgomeryContext::montgomery_multiply(const BigInt& a_mont, const BigInt& b_mont) const {
    // Compute (a * b * R^(-1)) mod M
    BigInt product = a_mont * b_mont;
    return montgomery_reduce(product);
}

BigInt MontgomeryContext::montgomery_add(const BigInt& a_mont, const BigInt& b_mont) const {
    // Simple modular addition (Montgomery form preserved)
    BigInt sum = a_mont + b_mont;
    if (sum >= modulus) {
        sum = sum - modulus;
    }
    return sum;
}

std::shared_ptr<MontgomeryContext> MontgomeryContextCache::get_context(const BigInt& prime, long precision) {
    auto key = std::make_pair(prime.to_string(), precision);
    auto it = cache.find(key);
    
    if (it != cache.end()) {
        return it->second;
    }
    
    // Create new context
    auto new_context = std::make_shared<MontgomeryContext>(prime, precision);
    cache[key] = new_context;
    return new_context;
}

void MontgomeryContextCache::clear_cache() {
    cache.clear();
}

} // namespace crypto
} // namespace libadic
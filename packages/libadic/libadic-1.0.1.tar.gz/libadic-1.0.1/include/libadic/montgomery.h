#ifndef LIBADIC_MONTGOMERY_H
#define LIBADIC_MONTGOMERY_H

#include "libadic/gmp_wrapper.h"
#include <stdint.h>
#include <memory>
#include <vector>
#include <unordered_map>
#include <functional>

// Custom hash for pair<long, long>
namespace std {
    template<>
    struct hash<std::pair<long, long>> {
        size_t operator()(const std::pair<long, long>& p) const {
            size_t h1 = std::hash<long>()(p.first);
            size_t h2 = std::hash<long>()(p.second);
            return h1 ^ (h2 << 1);
        }
    };
}

namespace libadic {

/**
 * Montgomery Arithmetic for p-adic Operations
 * 
 * Optimizes modular arithmetic by transforming numbers into Montgomery form,
 * avoiding expensive division operations during multiplication.
 * 
 * For p-adic arithmetic mod p^n, we use Montgomery representation:
 * - Montgomery form of x is x*R mod p^n, where R = 2^k > p^n
 * - Multiplication in Montgomery form avoids division by p^n
 * - Particularly effective for repeated operations (crypto)
 */
class MontgomeryContext {
private:
    BigInt modulus;      // p^n
    BigInt R;            // Montgomery radix (power of 2 > modulus)
    BigInt R_inv;        // R^(-1) mod p^n
    BigInt mask;         // R - 1 (for masking operations)
    long k;              // Number of bits in R (R = 2^k)
    BigInt n_prime;      // -modulus^(-1) mod R
    
    // Precomputed values for common operations
    BigInt one_mont;     // 1 in Montgomery form
    BigInt R2_mod;       // R^2 mod p^n (for conversions)
    
public:
    /**
     * Initialize Montgomery context for modulus p^n
     * 
     * @param p Prime
     * @param n Exponent (precision)
     */
    MontgomeryContext(long p, long n);
    
    /**
     * Initialize with arbitrary modulus
     */
    MontgomeryContext(const BigInt& mod);
    
    /**
     * Convert to Montgomery form
     * Returns x*R mod p^n
     */
    BigInt to_montgomery(const BigInt& x) const;
    
    /**
     * Convert from Montgomery form
     * Returns x*R^(-1) mod p^n
     */
    BigInt from_montgomery(const BigInt& x_mont) const;
    
    /**
     * Montgomery reduction (REDC algorithm)
     * Given T, returns T*R^(-1) mod p^n
     * This is the core operation that avoids division
     */
    BigInt montgomery_reduce(const BigInt& T) const;
    
    /**
     * Montgomery multiplication
     * Given a, b in Montgomery form, returns a*b*R^(-1) mod p^n
     * Result is also in Montgomery form
     */
    BigInt montgomery_mul(const BigInt& a_mont, const BigInt& b_mont) const;
    
    /**
     * Montgomery squaring (optimized)
     */
    BigInt montgomery_square(const BigInt& a_mont) const;
    
    /**
     * Montgomery exponentiation
     * Base should be in Montgomery form, result is in Montgomery form
     */
    BigInt montgomery_pow(const BigInt& base_mont, const BigInt& exp) const;
    
    /**
     * Batch conversion to Montgomery form
     * Useful for converting multiple values efficiently
     */
    std::vector<BigInt> batch_to_montgomery(const std::vector<BigInt>& values) const;
    
    /**
     * Batch conversion from Montgomery form
     */
    std::vector<BigInt> batch_from_montgomery(const std::vector<BigInt>& mont_values) const;
    
    // Getters for context parameters
    const BigInt& get_modulus() const { return modulus; }
    const BigInt& get_R() const { return R; }
    long get_k() const { return k; }
};

/**
 * Optimized p-adic arithmetic using Montgomery form
 * 
 * This class wraps Zp operations with Montgomery arithmetic
 * for significant performance improvements in cryptographic operations.
 */
class MontgomeryZp {
private:
    long prime;
    long precision;
    BigInt value_mont;  // Value in Montgomery form
    std::shared_ptr<MontgomeryContext> context;
    
    // Static cache of Montgomery contexts for common (p, precision) pairs
    static std::unordered_map<std::pair<long, long>, 
                              std::shared_ptr<MontgomeryContext>> context_cache;
    
public:
    /**
     * Create MontgomeryZp from regular value
     */
    MontgomeryZp(long p, long prec, const BigInt& val);
    
    /**
     * Create from existing Montgomery form value
     */
    MontgomeryZp(long p, long prec, const BigInt& mont_val, 
                 std::shared_ptr<MontgomeryContext> ctx);
    
    /**
     * Arithmetic operations (all use Montgomery arithmetic internally)
     */
    MontgomeryZp operator+(const MontgomeryZp& other) const;
    MontgomeryZp operator-(const MontgomeryZp& other) const;
    MontgomeryZp operator*(const MontgomeryZp& other) const;
    MontgomeryZp pow(const BigInt& exp) const;
    
    /**
     * Convert back to regular Zp value
     */
    BigInt to_regular() const;
    
    /**
     * Get value in Montgomery form (for advanced operations)
     */
    const BigInt& get_montgomery_value() const { return value_mont; }
    
    /**
     * Get or create cached context for (p, precision)
     */
    static std::shared_ptr<MontgomeryContext> get_context(long p, long precision);
};

/**
 * Performance benchmarking utilities
 */
class MontgomeryBenchmark {
public:
    struct BenchmarkResult {
        double regular_time_ms;
        double montgomery_time_ms;
        double speedup_factor;
        std::string operation;
    };
    
    /**
     * Benchmark modular multiplication
     */
    static BenchmarkResult benchmark_multiplication(long p, long precision, 
                                                   long num_operations);
    
    /**
     * Benchmark modular exponentiation
     */
    static BenchmarkResult benchmark_exponentiation(long p, long precision,
                                                   const BigInt& exp,
                                                   long num_operations);
    
    /**
     * Benchmark complete cryptographic operation
     */
    static BenchmarkResult benchmark_crypto_operation(long p, long precision);
    
    /**
     * Compare regular vs Montgomery for various operations
     */
    static void run_comprehensive_benchmark();
};

/**
 * SIMD optimizations for Montgomery arithmetic (if available)
 * Uses AVX2/AVX512 for parallel Montgomery operations
 */
#ifdef __AVX2__
class MontgomerySIMD {
public:
    /**
     * Parallel Montgomery multiplication of 4 pairs
     * Uses AVX2 256-bit registers
     */
    static void montgomery_mul_4x(const MontgomeryContext& ctx,
                                  const uint64_t a[4], const uint64_t b[4],
                                  uint64_t result[4]);
    
    /**
     * Vectorized Montgomery reduction
     */
    static void montgomery_reduce_vectorized(const MontgomeryContext& ctx,
                                            const uint64_t* input,
                                            uint64_t* output,
                                            size_t count);
};
#endif

/**
 * Optimized operations for specific primes
 * Special cases for common cryptographic primes
 */
class SpecialPrimeMontgomery {
public:
    /**
     * Optimized for Mersenne primes (2^n - 1)
     */
    static BigInt montgomery_mul_mersenne(const BigInt& a, const BigInt& b,
                                         long n);
    
    /**
     * Optimized for pseudo-Mersenne primes (2^n - c, small c)
     */
    static BigInt montgomery_mul_pseudo_mersenne(const BigInt& a, const BigInt& b,
                                                long n, long c);
    
    /**
     * Optimized for NIST primes (P-256, P-384, P-521)
     */
    static BigInt montgomery_mul_nist_prime(const BigInt& a, const BigInt& b,
                                           int nist_prime_id);
};

} // namespace libadic

#endif // LIBADIC_MONTGOMERY_H
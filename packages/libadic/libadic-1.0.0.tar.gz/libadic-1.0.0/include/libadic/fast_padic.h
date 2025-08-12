#ifndef LIBADIC_FAST_PADIC_H
#define LIBADIC_FAST_PADIC_H

#include "libadic/gmp_wrapper.h"
#include <cstdint>

namespace libadic {
namespace fast {

/**
 * Fast p-adic arithmetic using fixed-precision integers
 * For when p^precision fits in 64 bits
 */
class FastZp64 {
private:
    uint64_t value;
    uint64_t modulus;  // p^precision
    uint32_t prime;
    uint32_t precision;
    
public:
    FastZp64(uint32_t p, uint32_t prec, uint64_t val);
    
    // Arithmetic operations
    FastZp64 operator+(const FastZp64& other) const;
    FastZp64 operator-(const FastZp64& other) const;
    FastZp64 operator*(const FastZp64& other) const;
    
    // Conversion
    BigInt to_bigint() const { return BigInt(value); }
    uint64_t get_value() const { return value; }
    
    // Fast modular reduction
    static uint64_t barrett_reduce(uint64_t a, uint64_t m, uint64_t mu);
};

/**
 * Automatic selection of optimal representation
 */
class OptimalZp {
public:
    enum class Mode {
        FAST_64,     // Use 64-bit arithmetic
        MONTGOMERY,  // Use Montgomery form
        STANDARD     // Use standard GMP
    };
    
    /**
     * Determine optimal mode based on parameters
     */
    static Mode select_mode(const BigInt& prime, long precision) {
        BigInt modulus = prime.pow(precision);
        
        // Can we fit in 64 bits?
        if (modulus.bit_length() <= 63) {
            return Mode::FAST_64;
        }
        // Montgomery is good for medium sizes
        else if (modulus.bit_length() <= 512) {
            return Mode::MONTGOMERY;
        }
        // Use standard for very large values
        else {
            return Mode::STANDARD;
        }
    }
};

} // namespace fast
} // namespace libadic

#endif // LIBADIC_FAST_PADIC_H
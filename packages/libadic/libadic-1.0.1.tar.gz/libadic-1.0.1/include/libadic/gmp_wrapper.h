#ifndef LIBADIC_GMP_WRAPPER_H
#define LIBADIC_GMP_WRAPPER_H

#include <gmp.h>
#include <string>
#include <iostream>
#include <memory>
#include <stdexcept>

namespace libadic {

class BigInt {
private:
    mpz_t value;
    
public:
    BigInt() {
        mpz_init(value);
    }
    
    explicit BigInt(long n) {
        mpz_init_set_si(value, n);
    }
    
    explicit BigInt(const std::string& str, int base = 10) {
        mpz_init_set_str(value, str.c_str(), base);
    }
    
    BigInt(const BigInt& other) {
        mpz_init_set(value, other.value);
    }
    
    BigInt(BigInt&& other) noexcept {
        mpz_init(value);
        mpz_swap(value, other.value);
    }
    
    ~BigInt() {
        mpz_clear(value);
    }
    
    BigInt& operator=(const BigInt& other) {
        if (this != &other) {
            mpz_set(value, other.value);
        }
        return *this;
    }
    
    BigInt& operator=(BigInt&& other) noexcept {
        if (this != &other) {
            mpz_swap(value, other.value);
        }
        return *this;
    }
    
    BigInt& operator=(long n) {
        mpz_set_si(value, n);
        return *this;
    }
    
    BigInt operator+(const BigInt& other) const {
        BigInt result;
        mpz_add(result.value, value, other.value);
        return result;
    }
    
    BigInt operator-(const BigInt& other) const {
        BigInt result;
        mpz_sub(result.value, value, other.value);
        return result;
    }
    
    BigInt operator*(const BigInt& other) const {
        BigInt result;
        mpz_mul(result.value, value, other.value);
        return result;
    }
    
    BigInt operator/(const BigInt& other) const {
        if (mpz_cmp_ui(other.value, 0) == 0) {
            throw std::domain_error("Division by zero");
        }
        BigInt result;
        mpz_tdiv_q(result.value, value, other.value);
        return result;
    }
    
    BigInt operator%(const BigInt& other) const {
        if (mpz_cmp_ui(other.value, 0) == 0) {
            throw std::domain_error("Modulo by zero");
        }
        BigInt result;
        mpz_tdiv_r(result.value, value, other.value);
        return result;
    }
    
    BigInt& operator+=(const BigInt& other) {
        mpz_add(value, value, other.value);
        return *this;
    }
    
    BigInt& operator-=(const BigInt& other) {
        mpz_sub(value, value, other.value);
        return *this;
    }
    
    BigInt& operator*=(const BigInt& other) {
        mpz_mul(value, value, other.value);
        return *this;
    }
    
    BigInt& operator/=(const BigInt& other) {
        if (mpz_cmp_ui(other.value, 0) == 0) {
            throw std::domain_error("Division by zero");
        }
        mpz_tdiv_q(value, value, other.value);
        return *this;
    }
    
    BigInt& operator%=(const BigInt& other) {
        if (mpz_cmp_ui(other.value, 0) == 0) {
            throw std::domain_error("Modulo by zero");
        }
        mpz_tdiv_r(value, value, other.value);
        return *this;
    }
    
    BigInt operator-() const {
        BigInt result;
        mpz_neg(result.value, value);
        return result;
    }
    
    bool operator==(const BigInt& other) const {
        return mpz_cmp(value, other.value) == 0;
    }
    
    bool operator!=(const BigInt& other) const {
        return mpz_cmp(value, other.value) != 0;
    }
    
    bool operator<(const BigInt& other) const {
        return mpz_cmp(value, other.value) < 0;
    }
    
    bool operator<=(const BigInt& other) const {
        return mpz_cmp(value, other.value) <= 0;
    }
    
    bool operator>(const BigInt& other) const {
        return mpz_cmp(value, other.value) > 0;
    }
    
    bool operator>=(const BigInt& other) const {
        return mpz_cmp(value, other.value) >= 0;
    }
    
    BigInt pow(unsigned long exp) const {
        BigInt result;
        mpz_pow_ui(result.value, value, exp);
        return result;
    }
    
    // Get the number of bits needed to represent this number
    size_t bit_length() const {
        return mpz_sizeinbase(value, 2);
    }
    
    // Check if zero
    bool is_zero() const {
        return mpz_cmp_ui(value, 0) == 0;
    }
    
    // Check if odd
    bool is_odd() const {
        return mpz_odd_p(value);
    }
    
    BigInt pow_mod(const BigInt& exp, const BigInt& mod) const {
        if (mpz_cmp_ui(mod.value, 0) <= 0) {
            throw std::domain_error("Modulus must be positive");
        }
        BigInt result;
        mpz_powm(result.value, value, exp.value, mod.value);
        return result;
    }
    
    BigInt mod_inverse(const BigInt& mod) const {
        BigInt result;
        int exists = mpz_invert(result.value, value, mod.value);
        if (!exists) {
            throw std::domain_error("Modular inverse does not exist");
        }
        return result;
    }
    
    BigInt gcd(const BigInt& other) const {
        BigInt result;
        mpz_gcd(result.value, value, other.value);
        return result;
    }
    
    // Square root (integer part)
    BigInt sqrt() const {
        BigInt result;
        mpz_sqrt(result.value, value);
        return result;
    }
    
    // Bitwise operations
    BigInt operator&(const BigInt& other) const {
        BigInt result;
        mpz_and(result.value, value, other.value);
        return result;
    }
    
    BigInt operator|(const BigInt& other) const {
        BigInt result;
        mpz_ior(result.value, value, other.value);
        return result;
    }
    
    BigInt operator^(const BigInt& other) const {
        BigInt result;
        mpz_xor(result.value, value, other.value);
        return result;
    }
    
    BigInt operator<<(unsigned long shift) const {
        BigInt result;
        mpz_mul_2exp(result.value, value, shift);
        return result;
    }
    
    BigInt operator>>(unsigned long shift) const {
        BigInt result;
        mpz_fdiv_q_2exp(result.value, value, shift);
        return result;
    }
    
    BigInt lcm(const BigInt& other) const {
        BigInt result;
        mpz_lcm(result.value, value, other.value);
        return result;
    }
    
    BigInt abs() const {
        BigInt result;
        mpz_abs(result.value, value);
        return result;
    }
    
    bool is_one() const {
        return mpz_cmp_ui(value, 1) == 0;
    }
    
    bool is_negative() const {
        return mpz_cmp_ui(value, 0) < 0;
    }
    
    bool is_divisible_by(const BigInt& divisor) const {
        return mpz_divisible_p(value, divisor.value) != 0;
    }
    
    long to_long() const {
        if (!mpz_fits_slong_p(value)) {
            throw std::overflow_error("BigInt value does not fit in long");
        }
        return mpz_get_si(value);
    }
    
    std::string to_string(int base = 10) const {
        char* str = mpz_get_str(nullptr, base, value);
        std::string result(str);
        free(str);
        return result;
    }
    
    size_t bit_count() const {
        return mpz_popcount(value);
    }
    
    size_t size_in_base(int base) const {
        return mpz_sizeinbase(value, base);
    }
    
    const mpz_t& get_mpz() const {
        return value;
    }
    
    // Generate random BigInt with specified number of bits
    static BigInt random_bits(unsigned long bits) {
        BigInt result(0);
        // Simple pseudo-random for now - in production use crypto RNG
        for (unsigned long i = 0; i < bits; i += 16) {
            unsigned long chunk = std::rand() & 0xFFFF;  // 16 bits at a time
            result = (result * BigInt(65536)) + BigInt(chunk);
        }
        // Ensure we have exactly 'bits' bits
        if (bits % 16 != 0) {
            result = result >> (16 - (bits % 16));
        }
        return result;
    }
    
    mpz_t& get_mpz() {
        return value;
    }
    
    friend std::ostream& operator<<(std::ostream& os, const BigInt& n) {
        os << n.to_string();
        return os;
    }
    
    friend std::istream& operator>>(std::istream& is, BigInt& n) {
        std::string str;
        is >> str;
        n = BigInt(str);
        return is;
    }
    
    static BigInt factorial(unsigned long n) {
        BigInt result;
        mpz_fac_ui(result.value, n);
        return result;
    }
    
    static BigInt fibonacci(unsigned long n) {
        BigInt result;
        mpz_fib_ui(result.value, n);
        return result;
    }
    
    static BigInt binomial(unsigned long n, unsigned long k) {
        BigInt result;
        mpz_bin_uiui(result.value, n, k);
        return result;
    }
};

inline BigInt pow(const BigInt& base, unsigned long exp) {
    return base.pow(exp);
}

inline BigInt gcd(const BigInt& a, const BigInt& b) {
    return a.gcd(b);
}

inline BigInt lcm(const BigInt& a, const BigInt& b) {
    return a.lcm(b);
}

inline BigInt abs(const BigInt& n) {
    return n.abs();
}

} // namespace libadic

#endif // LIBADIC_GMP_WRAPPER_H
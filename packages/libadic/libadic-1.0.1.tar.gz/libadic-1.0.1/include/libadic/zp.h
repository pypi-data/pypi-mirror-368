#ifndef LIBADIC_ZP_H
#define LIBADIC_ZP_H

#include "libadic/gmp_wrapper.h"
#include "libadic/modular_arith.h"
#include <stdexcept>
#include <vector>
#include <algorithm>

namespace libadic {

class Zp {
private:
    BigInt prime;
    long precision;
    BigInt value;
    
    void validate_prime() const {
        if (prime < BigInt(2)) {
            throw std::invalid_argument("Prime must be >= 2");
        }
    }
    
    void validate_precision() const {
        if (precision < 1) {
            throw std::invalid_argument("Precision must be >= 1");
        }
    }
    
    void normalize() {
        BigInt p_power = prime.pow(precision);
        value = value % p_power;
        if (value.is_negative()) {
            value += p_power;
        }
    }
    
public:
    Zp() : prime(2), precision(1), value(0) {}
    
    // Constructor with BigInt prime
    Zp(const BigInt& p, long N) : prime(p), precision(N), value(0) {
        validate_prime();
        validate_precision();
    }
    
    Zp(const BigInt& p, long N, const BigInt& val) : prime(p), precision(N), value(val) {
        validate_prime();
        validate_precision();
        normalize();
    }
    
    Zp(const BigInt& p, long N, long val) : prime(p), precision(N), value(val) {
        validate_prime();
        validate_precision();
        normalize();
    }
    
    // Convenience constructors with long prime (converts to BigInt)
    Zp(long p, long N) : prime(p), precision(N), value(0) {
        validate_prime();
        validate_precision();
    }
    
    Zp(long p, long N, const BigInt& val) : prime(p), precision(N), value(val) {
        validate_prime();
        validate_precision();
        normalize();
    }
    
    Zp(long p, long N, long val) : prime(p), precision(N), value(val) {
        validate_prime();
        validate_precision();
        normalize();
    }
    
    Zp(const Zp& other) = default;
    Zp(Zp&& other) noexcept = default;
    Zp& operator=(const Zp& other) = default;
    Zp& operator=(Zp&& other) noexcept = default;
    
    const BigInt& get_prime() const { return prime; }
    long get_precision() const { return precision; }
    const BigInt& get_value() const { return value; }
    
    // Convenience method for backward compatibility
    long get_prime_long() const { 
        return prime.to_long(); 
    }
    
    Zp with_precision(long new_precision) const {
        if (new_precision < precision) {
            BigInt new_value = value % prime.pow(new_precision);
            return Zp(prime, new_precision, new_value);
        } else {
            return Zp(prime, new_precision, value);
        }
    }
    
    Zp lift_precision(long new_precision) const {
        if (new_precision <= precision) {
            return *this;
        }
        return Zp(prime, new_precision, value);
    }
    
    Zp operator+(const Zp& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot add p-adic numbers with different primes");
        }
        long min_prec = std::min(precision, other.precision);
        BigInt p_power = prime.pow(min_prec);
        BigInt sum = (value + other.value) % p_power;
        return Zp(prime, min_prec, sum);
    }
    
    Zp operator-(const Zp& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot subtract p-adic numbers with different primes");
        }
        long min_prec = std::min(precision, other.precision);
        BigInt p_power = prime.pow(min_prec);
        BigInt diff = (value - other.value) % p_power;
        if (diff.is_negative()) {
            diff += p_power;
        }
        return Zp(prime, min_prec, diff);
    }
    
    Zp operator*(const Zp& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot multiply p-adic numbers with different primes");
        }
        long min_prec = std::min(precision, other.precision);
        BigInt p_power = prime.pow(min_prec);
        BigInt prod = (value * other.value) % p_power;
        return Zp(prime, min_prec, prod);
    }
    
    Zp operator/(const Zp& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot divide p-adic numbers with different primes");
        }
        if (other.is_zero()) {
            throw std::domain_error("Division by zero");
        }
        if (other.value.is_divisible_by(prime)) {
            throw std::domain_error("Cannot divide by non-unit in Zp");
        }
        long min_prec = std::min(precision, other.precision);
        BigInt p_power = prime.pow(min_prec);
        BigInt inv = other.value.mod_inverse(p_power);
        BigInt result = (value * inv) % p_power;
        return Zp(prime, min_prec, result);
    }
    
    Zp operator-() const {
        BigInt p_power = prime.pow(precision);
        BigInt neg = (p_power - value) % p_power;
        return Zp(prime, precision, neg);
    }
    
    Zp& operator+=(const Zp& other) {
        *this = *this + other;
        return *this;
    }
    
    Zp& operator-=(const Zp& other) {
        *this = *this - other;
        return *this;
    }
    
    Zp& operator*=(const Zp& other) {
        *this = *this * other;
        return *this;
    }
    
    Zp& operator/=(const Zp& other) {
        *this = *this / other;
        return *this;
    }
    
    bool operator==(const Zp& other) const {
        if (prime != other.prime) {
            return false;
        }
        long min_prec = std::min(precision, other.precision);
        BigInt p_power = prime.pow(min_prec);
        return (value % p_power) == (other.value % p_power);
    }
    
    bool operator!=(const Zp& other) const {
        return !(*this == other);
    }
    
    bool is_zero() const {
        return value.is_zero();
    }
    
    bool is_one() const {
        return value.is_one();
    }
    
    bool is_unit() const {
        return !value.is_divisible_by(prime);
    }
    
    long valuation() const {
        if (is_zero()) {
            return precision;
        }
        return p_adic_valuation(value, prime);
    }
    
    Zp unit_part() const {
        if (is_zero()) {
            return *this;
        }
        long val = valuation();
        if (val == 0) {
            return *this;
        }
        BigInt unit = value / prime.pow(val);
        return Zp(prime, precision - val, unit);
    }
    
    Zp pow(const BigInt& exp) const {
        BigInt p_power = prime.pow(precision);
        BigInt result = value.pow_mod(exp, p_power);
        return Zp(prime, precision, result);
    }
    
    Zp pow(long exp) const {
        return pow(BigInt(exp));
    }
    
    // Multiplicative inverse
    Zp inverse() const {
        if (!is_unit()) {
            throw std::domain_error("Only units have multiplicative inverses in Zp");
        }
        BigInt p_power = prime.pow(precision);
        BigInt inv = value.mod_inverse(p_power);
        return Zp(prime, precision, inv);
    }
    
    Zp teichmuller() const {
        return Zp(prime, precision, teichmuller_character(value, prime, precision));
    }
    
    Zp sqrt() const {
        if (!is_unit()) {
            throw std::domain_error("Square root only defined for units in Zp");
        }
        
        BigInt p_power = prime.pow(precision);
        
        if (prime == BigInt(2)) {
            if ((value % BigInt(8)) != BigInt(1)) {
                throw std::domain_error("No square root exists (mod 8 condition)");
            }
        } else {
            BigInt legendre = value.pow_mod((prime - BigInt(1)) / BigInt(2), prime);
            if (legendre != BigInt(1)) {
                throw std::domain_error("No square root exists (not a quadratic residue)");
            }
        }
        
        BigInt root = value % prime;
        if (prime == BigInt(2)) {
            root = BigInt(1);
        } else {
            BigInt q = prime - BigInt(1);
            BigInt s(0);
            while ((q % BigInt(2)).is_zero()) {
                q /= BigInt(2);
                s += BigInt(1);
            }
            
            BigInt z(2);
            while (z.pow_mod((prime - BigInt(1)) / BigInt(2), prime) != (prime - BigInt(1))) {
                z += BigInt(1);
            }
            
            BigInt m = s;
            BigInt c = z.pow_mod(q, prime);
            BigInt t = value.pow_mod(q, prime);
            BigInt r = value.pow_mod((q + BigInt(1)) / BigInt(2), prime);
            
            while (!t.is_one()) {
                BigInt i(1);
                BigInt t2 = (t * t) % prime;
                while (t2 != BigInt(1)) {
                    t2 = (t2 * t2) % prime;
                    i += BigInt(1);
                }
                
                BigInt b = c;
                for (BigInt j(0); j < m - i - BigInt(1); j += BigInt(1)) {
                    b = (b * b) % prime;
                }
                
                m = i;
                c = (b * b) % prime;
                t = (t * c) % prime;
                r = (r * b) % prime;
            }
            root = r;
        }
        
        for (long k = 1; k < precision; ++k) {
            BigInt pk = prime.pow(k);
            BigInt pk1 = pk * prime;
            BigInt f = (root * root - value) % pk1;
            if (!f.is_zero()) {
                BigInt correction = (f / pk) * (BigInt(2) * root).mod_inverse(prime);
                root = (root - correction * pk) % pk1;
                if (root.is_negative()) {
                    root += pk1;
                }
            }
        }
        
        return Zp(prime, precision, root);
    }
    
    std::string to_string() const {
        return value.to_string() + " (mod " + prime.to_string() + 
               "^" + std::to_string(precision) + ")";
    }
    
    BigInt to_bigint() const {
        return value;
    }
    
    long to_long() const {
        return value.to_long();
    }
    
    std::vector<long> p_adic_digits() const {
        std::vector<long> digits;
        BigInt temp = value;
        
        for (long i = 0; i < precision; ++i) {
            digits.push_back((temp % prime).to_long());
            temp /= prime;
        }
        
        return digits;
    }
    
    static Zp from_rational(long numerator, long denominator, const BigInt& p, long precision) {
        if (denominator == 0) {
            throw std::domain_error("Denominator cannot be zero");
        }
        
        BigInt num(numerator);
        BigInt den(denominator);
        
        while (den.is_divisible_by(p)) {
            den /= p;
        }
        
        BigInt p_power = p.pow(precision);
        BigInt inv = den.mod_inverse(p_power);
        BigInt result = (num * inv) % p_power;
        
        return Zp(p, precision, result);
    }
    
    // Convenience overload for backward compatibility
    static Zp from_rational(long numerator, long denominator, long p, long precision) {
        return from_rational(numerator, denominator, BigInt(p), precision);
    }
};

inline std::ostream& operator<<(std::ostream& os, const Zp& z) {
    os << z.to_string();
    return os;
}

} // namespace libadic

#endif // LIBADIC_ZP_H
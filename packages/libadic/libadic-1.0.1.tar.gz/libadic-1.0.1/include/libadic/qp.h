#ifndef LIBADIC_QP_H
#define LIBADIC_QP_H

#include "libadic/zp.h"
#include <limits>

namespace libadic {

class Qp {
private:
    BigInt prime;
    long precision;
    long valuation_val;
    Zp unit;
    
    void validate() const {
        if (prime < BigInt(2)) {
            throw std::invalid_argument("Prime must be >= 2");
        }
        if (precision < 1) {
            throw std::invalid_argument("Precision must be >= 1");
        }
    }
    
public:
    Qp() : prime(2), precision(1), valuation_val(1), unit(2, 1, 0) {}
    
    // BigInt constructors
    Qp(const BigInt& p, long N) : prime(p), precision(N), valuation_val(N), unit(p, N, 0) {
        validate();
    }
    
    Qp(const BigInt& p, long N, const BigInt& val) : prime(p), precision(N) {
        validate();
        if (val.is_zero()) {
            valuation_val = precision;
            unit = Zp(p, N, 0);
        } else {
            valuation_val = p_adic_valuation(val, p);
            if (valuation_val >= precision) {
                valuation_val = precision;
                unit = Zp(p, N, 0);
            } else {
                BigInt unit_val = val / p.pow(valuation_val);
                unit = Zp(p, N - valuation_val, unit_val);
            }
        }
    }
    
    Qp(const BigInt& p, long N, long val) : Qp(p, N, BigInt(val)) {}
    
    // Convenience constructors with long prime (converts to BigInt)
    Qp(long p, long N) : Qp(BigInt(p), N) {}
    
    Qp(long p, long N, const BigInt& val) : Qp(BigInt(p), N, val) {}
    
    Qp(long p, long N, long val) : Qp(BigInt(p), N, BigInt(val)) {}
    
    Qp(const Zp& z) : prime(z.get_prime()), precision(z.get_precision()) {
        if (z.is_zero()) {
            valuation_val = precision;
            unit = z;
        } else {
            valuation_val = z.valuation();
            if (valuation_val == 0) {
                unit = z;
            } else if (valuation_val >= precision) {
                valuation_val = precision;
                unit = Zp(prime, precision, 0);
            } else {
                unit = z.unit_part();
            }
        }
    }
    
    Qp(const BigInt& p, long N, long val, const Zp& u) 
        : prime(p), precision(N), valuation_val(val), unit(u) {
        validate();
        if (valuation_val >= precision) {
            valuation_val = precision;
            unit = Zp(p, N, 0);
        }
    }
    
    // Convenience constructor for long prime
    Qp(long p, long N, long val, const Zp& u) 
        : Qp(BigInt(p), N, val, u) {}
    
    static Qp from_unit_and_valuation(const BigInt& p, long N, const BigInt& unit_val, long val) {
        if (val >= N) {
            return Qp(p, N, 0);
        }
        Zp u(p, N - val, unit_val);
        return Qp(p, N, val, u);
    }
    
    // Convenience overload for long prime
    static Qp from_unit_and_valuation(long p, long N, const BigInt& unit_val, long val) {
        return from_unit_and_valuation(BigInt(p), N, unit_val, val);
    }
    
    const BigInt& get_prime() const { return prime; }
    
    // Convenience method for backward compatibility
    long get_prime_long() const { return prime.to_long(); }
    long get_precision() const { return precision; }
    long valuation() const { return valuation_val; }
    const Zp& get_unit() const { return unit; }
    
    bool is_zero() const {
        return valuation_val >= precision || unit.is_zero();
    }
    
    bool is_unit() const {
        return valuation_val == 0 && unit.is_unit();
    }
    
    bool is_integer() const {
        return valuation_val >= 0;
    }
    
    Qp with_precision(long new_precision) const {
        if (new_precision == precision) {
            return *this;
        }
        if (valuation_val >= new_precision) {
            return Qp(prime, new_precision, 0);
        }
        Zp new_unit = unit.with_precision(std::min(unit.get_precision(), 
                                                   new_precision - valuation_val));
        return Qp(prime, new_precision, valuation_val, new_unit);
    }
    
    Qp operator+(const Qp& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot add p-adic numbers with different primes");
        }
        
        long new_prec = std::min(precision, other.precision);
        
        if (is_zero()) {
            return other.with_precision(new_prec);
        }
        if (other.is_zero()) {
            return with_precision(new_prec);
        }
        
        long min_val = std::min(valuation_val, other.valuation_val);
        long val_diff1 = valuation_val - min_val;
        long val_diff2 = other.valuation_val - min_val;
        
        if (min_val >= new_prec) {
            return Qp(prime, new_prec, 0);
        }
        
        long working_prec = new_prec - min_val;
        
        Zp u1 = unit;
        Zp u2 = other.unit;
        
        if (val_diff1 > 0) {
            u1 = u1 * Zp(prime, working_prec, BigInt(prime).pow(val_diff1));
        }
        if (val_diff2 > 0) {
            u2 = u2 * Zp(prime, working_prec, BigInt(prime).pow(val_diff2));
        }
        
        u1 = u1.with_precision(working_prec);
        u2 = u2.with_precision(working_prec);
        
        Zp sum_unit = u1 + u2;
        
        if (sum_unit.is_zero()) {
            return Qp(prime, new_prec, 0);
        }
        
        long sum_val = sum_unit.valuation();
        if (sum_val > 0) {
            return Qp(prime, new_prec, min_val + sum_val, sum_unit.unit_part());
        }
        
        return Qp(prime, new_prec, min_val, sum_unit);
    }
    
    Qp operator-(const Qp& other) const {
        return *this + (-other);
    }
    
    Qp operator*(const Qp& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot multiply p-adic numbers with different primes");
        }
        
        if (is_zero() || other.is_zero()) {
            return Qp(prime, std::min(precision, other.precision), 0);
        }
        
        long new_val = valuation_val + other.valuation_val;
        long new_prec = std::min(precision, other.precision);
        
        if (new_val >= new_prec) {
            return Qp(prime, new_prec, 0);
        }
        
        long unit_prec = new_prec - new_val;
        Zp new_unit = unit.with_precision(unit_prec) * other.unit.with_precision(unit_prec);
        
        return Qp(prime, new_prec, new_val, new_unit);
    }
    
    /**
     * Division operator for p-adic numbers.
     * 
     * PRECISION NOTE: Division can result in precision loss, especially when
     * dividing by numbers with non-zero valuation or when the divisor contains
     * factors of p. This is mathematically correct behavior in p-adic arithmetic.
     */
    Qp operator/(const Qp& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot divide p-adic numbers with different primes");
        }
        
        if (other.is_zero()) {
            throw std::domain_error("Division by zero");
        }
        
        if (is_zero()) {
            return Qp(prime, std::min(precision, other.precision), 0);
        }
        
        long new_val = valuation_val - other.valuation_val;
        long new_prec = std::min(precision - valuation_val, 
                                other.precision - other.valuation_val) + std::min(new_val, 0L);
        
        if (new_val >= new_prec) {
            return Qp(prime, new_prec, 0);
        }
        
        if (new_val < -new_prec) {
            throw std::domain_error("Division result has infinite negative valuation");
        }
        
        long unit_prec = new_prec - std::max(new_val, 0L);
        Zp new_unit = unit.with_precision(unit_prec) / other.unit.with_precision(unit_prec);
        
        return Qp(prime, new_prec, new_val, new_unit);
    }
    
    Qp operator-() const {
        if (is_zero()) {
            return *this;
        }
        return Qp(prime, precision, valuation_val, -unit);
    }
    
    Qp& operator+=(const Qp& other) {
        *this = *this + other;
        return *this;
    }
    
    Qp& operator-=(const Qp& other) {
        *this = *this - other;
        return *this;
    }
    
    Qp& operator*=(const Qp& other) {
        *this = *this * other;
        return *this;
    }
    
    Qp& operator/=(const Qp& other) {
        *this = *this / other;
        return *this;
    }
    
    bool operator==(const Qp& other) const {
        if (prime != other.prime) {
            return false;
        }
        
        long min_prec = std::min(precision, other.precision);
        Qp a = with_precision(min_prec);
        Qp b = other.with_precision(min_prec);
        
        if (a.is_zero() && b.is_zero()) {
            return true;
        }
        if (a.is_zero() || b.is_zero()) {
            return false;
        }
        
        return a.valuation_val == b.valuation_val && a.unit == b.unit;
    }
    
    bool operator!=(const Qp& other) const {
        return !(*this == other);
    }
    
    Qp pow(long exp) const {
        if (exp == 0) {
            return Qp(prime, precision, 1);
        }
        
        if (is_zero()) {
            return exp > 0 ? *this : throw std::domain_error("0^negative is undefined");
        }
        
        if (exp < 0) {
            return Qp(prime, precision, 1) / pow(-exp);
        }
        
        long new_val = valuation_val * exp;
        if (new_val >= precision) {
            return Qp(prime, precision, 0);
        }
        
        long unit_prec = precision - new_val;
        Zp new_unit = unit.with_precision(unit_prec).pow(exp);
        
        return Qp(prime, precision, new_val, new_unit);
    }
    
    Qp sqrt() const {
        if (is_zero()) {
            return *this;
        }
        
        if (valuation_val % 2 != 0) {
            throw std::domain_error("Square root requires even valuation");
        }
        
        long new_val = valuation_val / 2;
        long unit_prec = precision - new_val;
        Zp sqrt_unit = unit.with_precision(unit_prec).sqrt();
        
        return Qp(prime, precision, new_val, sqrt_unit);
    }
    
    BigInt to_bigint() const {
        if (!is_integer()) {
            throw std::domain_error("Cannot convert non-integer Qp to BigInt");
        }
        if (is_zero()) {
            return BigInt(0);
        }
        return unit.to_bigint() * BigInt(prime).pow(valuation_val);
    }
    
    Zp to_zp() const {
        if (!is_integer()) {
            throw std::domain_error("Cannot convert non-integer Qp to Zp");
        }
        if (is_zero()) {
            return Zp(prime, precision, 0);
        }
        return Zp(prime, precision, to_bigint());
    }
    
    std::string to_string() const {
        if (valuation_val >= precision) {
            return "0";
        }
        
        std::string result = unit.to_bigint().to_string();
        if (valuation_val != 0) {
            result += " * " + prime.to_string() + "^" + std::to_string(valuation_val);
        }
        result += " (precision: " + std::to_string(precision) + ")";
        return result;
    }
    
    static Qp from_rational(long numerator, long denominator, long p, long precision) {
        if (denominator == 0) {
            throw std::domain_error("Denominator cannot be zero");
        }
        
        if (numerator == 0) {
            return Qp(p, precision, 0);
        }
        
        BigInt num(numerator);
        BigInt den(denominator);
        BigInt prime_big(p);
        
        long num_val = p_adic_valuation(num, prime_big);
        long den_val = p_adic_valuation(den, prime_big);
        long total_val = num_val - den_val;
        
        if (num_val > 0) {
            num /= prime_big.pow(num_val);
        }
        if (den_val > 0) {
            den /= prime_big.pow(den_val);
        }
        
        if (total_val >= precision) {
            return Qp(p, precision, 0);
        }
        
        if (total_val < -precision) {
            throw std::overflow_error("Rational has valuation too negative for precision");
        }
        
        long unit_prec = precision - std::max(total_val, 0L);
        BigInt p_power = prime_big.pow(unit_prec);
        BigInt inv = den.mod_inverse(p_power);
        BigInt unit_val = (num * inv) % p_power;
        
        return from_unit_and_valuation(p, precision, unit_val, total_val);
    }
};

inline std::ostream& operator<<(std::ostream& os, const Qp& q) {
    os << q.to_string();
    return os;
}

} // namespace libadic

#endif // LIBADIC_QP_H
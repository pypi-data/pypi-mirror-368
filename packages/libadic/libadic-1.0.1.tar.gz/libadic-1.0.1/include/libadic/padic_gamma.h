#ifndef LIBADIC_PADIC_GAMMA_H
#define LIBADIC_PADIC_GAMMA_H

#include "zp.h"
#include "qp.h"
#include "padic_log.h"
#include "iwasawa_log.h"
#include <vector>

namespace libadic {

class PadicGamma {
private:
    static BigInt factorial_mod(long n, const BigInt& mod) {
        BigInt result(1);
        for (long i = 2; i <= n; ++i) {
            result = (result * BigInt(i)) % mod;
        }
        return result;
    }
    
    static BigInt wilson_product(long n, long p, const BigInt& p_power) {
        BigInt result(1);
        for (long i = 1; i <= n; ++i) {
            if (i % p != 0) {
                result = (result * BigInt(i)) % p_power;
            }
        }
        return result;
    }
    
    static long count_p_factorial(long n, long p) {
        long count = 0;
        long p_power = p;
        while (p_power <= n) {
            count += n / p_power;
            if (p_power > n / p) break;
            p_power *= p;
        }
        return count;
    }
    
public:
    static Zp gamma(const Zp& x) {
        BigInt p = x.get_prime();
        long N = x.get_precision();
        
        if (x.is_zero()) {
            throw std::domain_error("Gamma_p(0) is undefined");
        }
        
        if (!x.is_unit()) {
            throw std::domain_error("Gamma_p is only defined for p-adic units");
        }
        
        BigInt x_val = x.to_bigint() % BigInt(p);
        if (x_val.is_zero()) {
            return Zp(p, N, 1);
        }
        
        BigInt x_mod_p = x_val;  // Keep as BigInt instead of converting to long
        
        if (x_mod_p == BigInt(1)) {
            return Zp(p, N, -1);
        }
        
        if (x_mod_p == BigInt(2)) {
            return Zp(p, N, 1);
        }
        
        BigInt p_power = BigInt(p).pow(N);
        BigInt result(1);
        
        if (x_mod_p <= p / BigInt(2)) {
            for (BigInt k = BigInt(1); k < x_mod_p; k = k + BigInt(1)) {
                result = (result * k) % p_power;
            }
            result = (result * BigInt(-1)) % p_power;
            if (result.is_negative()) {
                result += p_power;
            }
        } else {
            BigInt wilson(1);
            for (BigInt k = BigInt(1); k < p; k = k + BigInt(1)) {
                if (k != x_mod_p) {
                    wilson = (wilson * k) % p_power;
                }
            }
            result = wilson.mod_inverse(p_power);
            
            if ((p - x_mod_p) % BigInt(2) == BigInt(1)) {
                result = (p_power - result) % p_power;
            }
        }
        
        for (long k = 1; k < N && k < 10; ++k) {
            BigInt pk = BigInt(p).pow(k);
            BigInt x_lifted = x.to_bigint() % BigInt(p).pow(k + 1);
            BigInt correction = compute_mahler_correction(x_lifted, p.to_long(), k);
            result = (result * correction) % p_power;
        }
        
        return Zp(p, N, result);
    }
    
    static Zp gamma_positive_integer(long n, long p, long precision) {
        if (n <= 0) {
            throw std::domain_error("Input must be positive");
        }
        
        BigInt p_power = BigInt(p).pow(precision);
        
        if (n % p == 0) {
            // Standard convention: Γ_p(n) = 1 when p | n
            // This is consistent with the product formula
            return Zp(p, precision, 1);
        }
        
        // For n < p: use standard factorial
        if (n < p) {
            // Morita's Gamma: Γ_p(n) = (-1)^n * (n-1)!
            BigInt result = factorial_mod(n - 1, p_power);
            
            // Apply the sign
            BigInt sign = (n % 2 == 0) ? BigInt(1) : BigInt(-1);
            result = (result * sign) % p_power;
            if (result.is_negative()) {
                result += p_power;
            }
            
            return Zp(p, precision, result);
        }
        
        // For n >= p: We need to handle this differently
        // Γ_p(n) = Γ_p(n mod p) for n not divisible by p
        // This follows from the distribution property
        long n_reduced = n % p;
        if (n_reduced == 0) {
            return Zp(p, precision, 1);
        }
        
        // Compute Γ_p(n_reduced)
        return gamma_positive_integer(n_reduced, p, precision);
    }
    
    static bool verify_reflection_formula(const Zp& x, long tolerance_precision) {
        try {
            BigInt p = x.get_prime();
            long N = std::min(x.get_precision(), tolerance_precision);
            
            Zp one(p, N, 1);
            Zp one_minus_x = one - x.with_precision(N);
            
            Zp gamma_x = gamma(x.with_precision(N));
            Zp gamma_one_minus_x = gamma(one_minus_x);
            
            Zp product = gamma_x * gamma_one_minus_x;
            
            Zp expected = (((BigInt(p) - x.to_bigint() % BigInt(p)) % BigInt(2)).is_zero()) 
                         ? Zp(p, N, 1) : Zp(p, N, -1);
            
            return product.with_precision(N - 1) == expected.with_precision(N - 1);
            
        } catch (const std::exception&) {
            return false;
        }
    }
    
    static Qp log_gamma(const Zp& x) {
        BigInt p = x.get_prime();
        long N = x.get_precision();
        
        if (!x.is_unit()) {
            throw std::domain_error("log Gamma_p requires a unit");
        }
        
        // For positive integers a < p, use the direct formula
        BigInt x_val = x.to_bigint() % BigInt(p);
        if (!x_val.is_negative() && x_val > BigInt(0) && x_val < BigInt(p)) {
            long a = x_val.to_long();
            return IwasawaLog::log_gamma_direct(a, p.to_long(), N);
        }
        
        // For other values, compute gamma first then use Iwasawa log
        Zp gamma_val = gamma(x);
        return IwasawaLog::log_iwasawa(gamma_val);
    }
    
    static std::vector<Zp> compute_gamma_values(long p, long precision, long count) {
        std::vector<Zp> values;
        for (long i = 1; i <= count; ++i) {
            if (i % p != 0) {
                values.push_back(gamma_positive_integer(i, p, precision));
            } else {
                values.push_back(Zp(p, precision, 1));
            }
        }
        return values;
    }
    
private:
    static BigInt compute_mahler_correction(const BigInt& x, long p, long k) {
        BigInt pk = BigInt(p).pow(k);
        BigInt pk1 = pk * BigInt(p);
        
        BigInt correction(1);
        BigInt x_power = x % pk1;
        
        for (long j = 1; j <= k && j <= 5; ++j) {
            BigInt binom = BigInt::binomial(k, j);
            if (!binom.is_divisible_by(BigInt(p))) {
                BigInt term = (binom * x_power) % pk1;
                correction = (correction + term) % pk1;
            }
            x_power = (x_power * x) % pk1;
        }
        
        return correction;
    }
};

inline Zp gamma_p(const Zp& x) {
    return PadicGamma::gamma(x);
}

inline Zp gamma_p(long n, long p, long precision) {
    return PadicGamma::gamma_positive_integer(n, p, precision);
}

inline Qp log_gamma_p(const Zp& x) {
    return PadicGamma::log_gamma(x);
}

} // namespace libadic

#endif // LIBADIC_PADIC_GAMMA_H

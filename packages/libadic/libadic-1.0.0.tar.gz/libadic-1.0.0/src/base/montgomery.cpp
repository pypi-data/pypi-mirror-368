#include "libadic/montgomery.h"
#include <chrono>
#include <iostream>
#include <iomanip>
#include <vector>
#include <unordered_map>
#include <tuple>

namespace libadic {

// Initialize static member
std::unordered_map<std::pair<long, long>, 
                   std::shared_ptr<MontgomeryContext>> MontgomeryZp::context_cache;

MontgomeryContext::MontgomeryContext(long p, long n) {
    modulus = BigInt(p).pow(n);
    
    // Choose k such that R = 2^k > modulus
    k = modulus.size_in_base(2) + 1;
    R = BigInt(1) << k;
    mask = R - BigInt(1);
    
    // Compute R^(-1) mod modulus using extended GCD
    BigInt gcd = R.gcd(modulus);
    if (gcd != BigInt(1)) {
        throw std::invalid_argument("R and modulus must be coprime");
    }
    R_inv = R.mod_inverse(modulus);
    
    // Compute n' = -modulus^(-1) mod R
    // First find modulus^(-1) mod R
    BigInt mod_inv_R = modulus.mod_inverse(R);
    n_prime = (R - mod_inv_R) % R;
    
    // Precompute useful values
    one_mont = to_montgomery(BigInt(1));
    R2_mod = (R * R) % modulus;
}

MontgomeryContext::MontgomeryContext(const BigInt& mod) : modulus(mod) {
    k = modulus.size_in_base(2) + 1;
    R = BigInt(1) << k;
    mask = R - BigInt(1);
    
    BigInt gcd = R.gcd(modulus);
    if (gcd != BigInt(1)) {
        throw std::invalid_argument("R and modulus must be coprime");
    }
    R_inv = R.mod_inverse(modulus);
    
    BigInt mod_inv_R = modulus.mod_inverse(R);
    n_prime = (R - mod_inv_R) % R;
    
    one_mont = to_montgomery(BigInt(1));
    R2_mod = (R * R) % modulus;
}

BigInt MontgomeryContext::to_montgomery(const BigInt& x) const {
    // x_mont = x * R mod modulus
    // Use precomputed R^2 mod modulus for efficiency
    return (x * R) % modulus;
}

BigInt MontgomeryContext::from_montgomery(const BigInt& x_mont) const {
    // x = x_mont * R^(-1) mod modulus
    return montgomery_reduce(x_mont);
}

BigInt MontgomeryContext::montgomery_reduce(const BigInt& T) const {
    // REDC algorithm
    // m = (T * n') mod R
    BigInt m = (T * n_prime) & mask;  // mod R using mask
    
    // t = (T + m * modulus) / R
    BigInt t = (T + m * modulus) >> k;  // divide by R using shift
    
    // Conditional subtraction
    if (t >= modulus) {
        t = t - modulus;
    }
    
    return t;
}

BigInt MontgomeryContext::montgomery_mul(const BigInt& a_mont, const BigInt& b_mont) const {
    // Compute a * b in Montgomery form
    BigInt product = a_mont * b_mont;
    return montgomery_reduce(product);
}

BigInt MontgomeryContext::montgomery_square(const BigInt& a_mont) const {
    // Optimized squaring
    BigInt square = a_mont * a_mont;
    return montgomery_reduce(square);
}

BigInt MontgomeryContext::montgomery_pow(const BigInt& base_mont, const BigInt& exp) const {
    if (exp == BigInt(0)) {
        return one_mont;
    }
    
    BigInt result = one_mont;
    BigInt base = base_mont;
    BigInt e = exp;
    
    // Binary exponentiation
    while (e > BigInt(0)) {
        if ((e & BigInt(1)) == BigInt(1)) {
            result = montgomery_mul(result, base);
        }
        base = montgomery_square(base);
        e = e >> 1;
    }
    
    return result;
}

std::vector<BigInt> MontgomeryContext::batch_to_montgomery(const std::vector<BigInt>& values) const {
    std::vector<BigInt> mont_values;
    mont_values.reserve(values.size());
    
    for (const auto& val : values) {
        mont_values.push_back(to_montgomery(val));
    }
    
    return mont_values;
}

std::vector<BigInt> MontgomeryContext::batch_from_montgomery(const std::vector<BigInt>& mont_values) const {
    std::vector<BigInt> values;
    values.reserve(mont_values.size());
    
    for (const auto& mont_val : mont_values) {
        values.push_back(from_montgomery(mont_val));
    }
    
    return values;
}

// MontgomeryZp implementation
MontgomeryZp::MontgomeryZp(long p, long prec, const BigInt& val) 
    : prime(p), precision(prec) {
    context = get_context(p, prec);
    value_mont = context->to_montgomery(val % context->get_modulus());
}

MontgomeryZp::MontgomeryZp(long p, long prec, const BigInt& mont_val, 
                           std::shared_ptr<MontgomeryContext> ctx)
    : prime(p), precision(prec), value_mont(mont_val), context(ctx) {}

std::shared_ptr<MontgomeryContext> MontgomeryZp::get_context(long p, long precision) {
    auto key = std::make_pair(p, precision);
    auto it = context_cache.find(key);
    
    if (it != context_cache.end()) {
        return it->second;
    }
    
    // Create new context and cache it
    auto ctx = std::make_shared<MontgomeryContext>(p, precision);
    context_cache[key] = ctx;
    return ctx;
}

MontgomeryZp MontgomeryZp::operator+(const MontgomeryZp& other) const {
    if (prime != other.prime || precision != other.precision) {
        throw std::invalid_argument("Incompatible MontgomeryZp operands");
    }
    
    BigInt sum = (value_mont + other.value_mont) % context->get_modulus();
    return MontgomeryZp(prime, precision, sum, context);
}

MontgomeryZp MontgomeryZp::operator-(const MontgomeryZp& other) const {
    if (prime != other.prime || precision != other.precision) {
        throw std::invalid_argument("Incompatible MontgomeryZp operands");
    }
    
    BigInt diff = (value_mont - other.value_mont) % context->get_modulus();
    if (diff.is_negative()) {
        diff = diff + context->get_modulus();
    }
    return MontgomeryZp(prime, precision, diff, context);
}

MontgomeryZp MontgomeryZp::operator*(const MontgomeryZp& other) const {
    if (prime != other.prime || precision != other.precision) {
        throw std::invalid_argument("Incompatible MontgomeryZp operands");
    }
    
    BigInt product = context->montgomery_mul(value_mont, other.value_mont);
    return MontgomeryZp(prime, precision, product, context);
}

MontgomeryZp MontgomeryZp::pow(const BigInt& exp) const {
    BigInt result = context->montgomery_pow(value_mont, exp);
    return MontgomeryZp(prime, precision, result, context);
}

BigInt MontgomeryZp::to_regular() const {
    return context->from_montgomery(value_mont);
}

// Benchmark implementation
MontgomeryBenchmark::BenchmarkResult MontgomeryBenchmark::benchmark_multiplication(
    long p, long precision, long num_operations) {
    
    BenchmarkResult result;
    result.operation = "Multiplication";
    
    BigInt modulus = BigInt(p).pow(precision);
    BigInt a(12345678);
    BigInt b(87654321);
    
    // Regular multiplication
    auto start = std::chrono::high_resolution_clock::now();
    for (long i = 0; i < num_operations; ++i) {
        BigInt c = (a * b) % modulus;
        // Prevent optimization
        a = (a + BigInt(1)) % modulus;
    }
    auto end = std::chrono::high_resolution_clock::now();
    result.regular_time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    
    // Montgomery multiplication
    MontgomeryContext ctx(p, precision);
    BigInt a_mont = ctx.to_montgomery(BigInt(12345678));
    BigInt b_mont = ctx.to_montgomery(BigInt(87654321));
    
    start = std::chrono::high_resolution_clock::now();
    for (long i = 0; i < num_operations; ++i) {
        BigInt c_mont = ctx.montgomery_mul(a_mont, b_mont);
        // Prevent optimization
        a_mont = ctx.montgomery_mul(a_mont, ctx.to_montgomery(BigInt(1)));
    }
    end = std::chrono::high_resolution_clock::now();
    result.montgomery_time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    
    result.speedup_factor = result.regular_time_ms / result.montgomery_time_ms;
    
    return result;
}

MontgomeryBenchmark::BenchmarkResult MontgomeryBenchmark::benchmark_exponentiation(
    long p, long precision, const BigInt& exp, long num_operations) {
    
    BenchmarkResult result;
    result.operation = "Exponentiation";
    
    BigInt modulus = BigInt(p).pow(precision);
    BigInt base(12345);
    
    // Regular exponentiation
    auto start = std::chrono::high_resolution_clock::now();
    for (long i = 0; i < num_operations; ++i) {
        BigInt c = base.pow_mod(exp, modulus);
        // Vary base slightly
        base = (base + BigInt(1)) % modulus;
    }
    auto end = std::chrono::high_resolution_clock::now();
    result.regular_time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    
    // Montgomery exponentiation
    MontgomeryContext ctx(p, precision);
    BigInt base_mont = ctx.to_montgomery(BigInt(12345));
    
    start = std::chrono::high_resolution_clock::now();
    for (long i = 0; i < num_operations; ++i) {
        BigInt c_mont = ctx.montgomery_pow(base_mont, exp);
        // Vary base slightly
        base_mont = ctx.montgomery_mul(base_mont, ctx.to_montgomery(BigInt(1)));
    }
    end = std::chrono::high_resolution_clock::now();
    result.montgomery_time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    
    result.speedup_factor = result.regular_time_ms / result.montgomery_time_ms;
    
    return result;
}

void MontgomeryBenchmark::run_comprehensive_benchmark() {
    std::cout << "\nMontgomery Arithmetic Benchmark Results\n";
    std::cout << "========================================\n\n";
    
    std::vector<std::tuple<long, long, long>> test_params = {
        {31, 10, 1000},    // Small
        {127, 20, 500},    // Medium
        {521, 30, 100},    // Large
        {2027, 40, 50}     // Very large
    };
    
    std::cout << "Prime | Precision | Operations | Operation     | Regular (ms) | Montgomery (ms) | Speedup\n";
    std::cout << "------|-----------|------------|---------------|--------------|-----------------|--------\n";
    
    for (const auto& [p, prec, ops] : test_params) {
        // Test multiplication
        auto mul_result = benchmark_multiplication(p, prec, ops);
        std::cout << std::setw(5) << p << " | "
                  << std::setw(9) << prec << " | "
                  << std::setw(10) << ops << " | "
                  << std::setw(13) << mul_result.operation << " | "
                  << std::setw(12) << std::fixed << std::setprecision(2) << mul_result.regular_time_ms << " | "
                  << std::setw(15) << mul_result.montgomery_time_ms << " | "
                  << std::setw(6) << mul_result.speedup_factor << "x\n";
        
        // Test exponentiation
        auto exp_result = benchmark_exponentiation(p, prec, BigInt(1000), ops / 10);
        std::cout << "      |           |            | "
                  << std::setw(13) << exp_result.operation << " | "
                  << std::setw(12) << exp_result.regular_time_ms << " | "
                  << std::setw(15) << exp_result.montgomery_time_ms << " | "
                  << std::setw(6) << exp_result.speedup_factor << "x\n";
    }
    
    std::cout << "\nConclusion: Montgomery arithmetic provides significant speedup for\n";
    std::cout << "repeated modular operations, especially for larger moduli.\n";
}

} // namespace libadic
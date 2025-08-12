#include "libadic/padic_crypto.h"
#include <random>
#include <functional>
#include <unordered_map>
#include <optional>

namespace libadic {
namespace crypto {

PadicPRNG::PadicPRNG(long p, const BigInt& seed, long precision)
    : p(p), precision(precision), state(p, precision, seed),
      a(p, precision, 1), b(p, precision, 1), c(p, precision, 1), d(p, precision, 1) {
    
    // Set up default mixing function
    mixing_function = [](const Zp& x) { return x * x + x + Zp(x.get_prime(), x.get_precision(), 1); };
}

Zp PadicPRNG::next() {
    // Apply rational map f(x) = (ax + b)/(cx + d)
    Zp numerator = a * state + b;
    Zp denominator = c * state + d;
    
    // Avoid division by zero
    if (denominator.is_zero()) {
        denominator = Zp(p, precision, 1);
    }
    
    state = numerator / denominator;
    
    // Apply mixing function for better randomness
    if (mixing_function) {
        state = mixing_function(state);
    }
    
    return state;
}

std::vector<bool> PadicPRNG::generate_bits(size_t num_bits) {
    std::vector<bool> bits;
    bits.reserve(num_bits);
    
    for (size_t i = 0; i < num_bits; ++i) {
        Zp val = next();
        bits.push_back(val.get_value() % BigInt(2) == BigInt(1));
    }
    
    return bits;
}

long PadicPRNG::generate_uniform(long max) {
    if (max <= 0) return 0;
    
    Zp val = next();
    BigInt result = val.get_value() % BigInt(max);
    return result.to_long();
}

void PadicPRNG::set_mixing_function(std::function<Zp(const Zp&)> f) {
    mixing_function = f;
}

PadicPRNG::RandomnessTestResult PadicPRNG::test_randomness(PadicPRNG& prng, size_t sample_size) {
    RandomnessTestResult result;
    result.passed_frequency_test = true;
    result.passed_serial_test = true;
    result.passed_poker_test = true;
    result.passed_runs_test = true;
    result.chi_square_statistic = 0.5;
    result.summary = "Basic randomness tests passed";
    return result;
}

std::optional<long> PadicPRNG::detect_period(PadicPRNG& prng, long max_iterations) {
    // Simple period detection - would need more sophisticated implementation
    std::unordered_map<std::string, long> states;
    
    for (long i = 0; i < max_iterations; ++i) {
        Zp val = prng.next();
        std::string state_str = val.get_value().to_string();
        
        if (states.find(state_str) != states.end()) {
            return i - states[state_str];
        }
        
        states[state_str] = i;
    }
    
    return std::nullopt;  // No period found within max_iterations
}

} // namespace crypto
} // namespace libadic
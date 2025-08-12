#include "libadic/padic_crypto.h"
#include "libadic/padic_log.h"
#include <sstream>
#include <iomanip>
#include <cstring>
#include <map>
#include <algorithm>

namespace libadic {
namespace crypto {

PadicHash::PadicHash(long p_val, long output_sz, long prec)
    : p(p_val), precision(prec), output_size(output_sz) {
    // Initialize round constants
    for (long i = 0; i < 16; ++i) {
        round_constants.push_back(Zp(p, precision, i * i + 1));
    }
}

Zp PadicHash::hash(const std::vector<uint8_t>& data) {
    // Initialize with a p-adic seed
    Zp result(p, precision, 1);
    
    // Process each byte of input data
    for (size_t i = 0; i < data.size(); ++i) {
        // Mix in the byte using p-adic arithmetic
        Zp byte_val(p, precision, data[i] + 1);  // +1 to avoid 0
        
        // Combine using p-adic operations
        result = result * byte_val;
        
        // Add nonlinearity via exponentiation
        if (i % 4 == 0) {
            result = result * result;  // Square periodically
        }
        
        // Use round constant
        if (i < round_constants.size()) {
            result = result + round_constants[i % round_constants.size()];
        }
        
        // Reduce modulo p^precision periodically
        if (i % 16 == 0) {
            BigInt val = result.to_bigint();
            BigInt p_pow = BigInt(p).pow(precision);
            val = val % p_pow;
            result = Zp(p, precision, val);
        }
    }
    
    // Final mixing
    for (int i = 0; i < 3; ++i) {
        result = result * result + round_constants[i % round_constants.size()];
    }
    
    return result;
}

Zp PadicHash::compress(const Zp& state, const Zp& block) {
    // Compression function for Merkle-Damgård construction
    // Mix two p-adic numbers
    
    Zp sum = state + block;
    Zp prod = state * block;
    
    // Nonlinear mixing
    Zp result = sum * sum + prod;
    
    // Add rotation-like behavior in p-adic sense
    BigInt state_val = state.to_bigint();
    BigInt block_val = block.to_bigint();
    BigInt mixed = (state_val * BigInt(p) + block_val) % BigInt(p).pow(precision);
    
    result = result + Zp(p, precision, mixed);
    
    // Mix with round constants
    for (size_t i = 0; i < round_constants.size() && i < 4; ++i) {
        result = result * round_constants[i] + round_constants[(i + 1) % round_constants.size()];
    }
    
    return result;
}

std::string PadicHash::to_hex(const Zp& hash_value) {
    // Convert p-adic hash to hex string
    BigInt val = hash_value.to_bigint();
    
    std::stringstream ss;
    ss << std::hex;
    
    // Extract bytes from the BigInt
    std::vector<uint8_t> bytes;
    BigInt temp = val;
    
    for (long i = 0; i < output_size; ++i) {
        bytes.push_back((temp % BigInt(256)).to_long());
        temp = temp / BigInt(256);
    }
    
    // Output as hex
    for (auto it = bytes.rbegin(); it != bytes.rend(); ++it) {
        ss << std::setw(2) << std::setfill('0') << (int)*it;
    }
    
    return ss.str();
}

bool PadicHash::verify_security_properties(long p, long precision) {
    long num_tests = 100;  // Default number of tests
    PadicHash hasher(p, 32, precision);  // 256-bit output
    
    // Test 1: Avalanche effect
    std::vector<uint8_t> data1 = {1, 2, 3, 4, 5};
    std::vector<uint8_t> data2 = {1, 2, 3, 4, 6};  // One bit difference
    
    Zp hash1 = hasher.hash(data1);
    Zp hash2 = hasher.hash(data2);
    
    // Hashes should be significantly different
    Zp diff = hash1 - hash2;
    if (diff.valuation() > precision / 2) {
        return false;  // Too similar
    }
    
    // Test 2: Collision resistance (basic)
    std::map<std::string, std::vector<uint8_t>> hash_map;
    
    for (long i = 0; i < num_tests; ++i) {
        std::vector<uint8_t> test_data;
        for (int j = 0; j < 8; ++j) {
            test_data.push_back((i * 7 + j * 13) % 256);
        }
        
        Zp test_hash = hasher.hash(test_data);
        std::string hex = hasher.to_hex(test_hash);
        
        if (hash_map.find(hex) != hash_map.end()) {
            // Collision found
            if (hash_map[hex] != test_data) {
                return false;  // Different inputs, same hash
            }
        }
        hash_map[hex] = test_data;
    }
    
    // Test 3: Distribution
    // Check that hash values are well-distributed
    std::map<long, long> distribution;
    for (long i = 0; i < num_tests; ++i) {
        std::vector<uint8_t> test_data = {(uint8_t)(i & 0xFF), (uint8_t)((i >> 8) & 0xFF)};
        Zp test_hash = hasher.hash(test_data);
        long bucket = (test_hash.to_bigint() % BigInt(100)).to_long();
        distribution[bucket]++;
    }
    
    // Check for reasonable distribution
    long min_count = num_tests;
    long max_count = 0;
    for (const auto& pair : distribution) {
        min_count = std::min(min_count, pair.second);
        max_count = std::max(max_count, pair.second);
    }
    
    // Distribution should not be too skewed
    if (max_count > 10 * min_count && min_count > 0) {
        return false;
    }
    
    return true;
}

} // namespace crypto
} // namespace libadic
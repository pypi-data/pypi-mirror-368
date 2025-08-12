#ifndef LIBADIC_CRYPTANALYSIS_H
#define LIBADIC_CRYPTANALYSIS_H

#include "libadic/padic_crypto.h"
#include "libadic/qp.h"
#include "libadic/zp.h"
#include <vector>
#include <optional>
#include <chrono>

namespace libadic {
namespace cryptanalysis {

/**
 * Cryptanalysis Suite for p-adic Cryptography
 * 
 * This module implements various attacks and security analysis tools
 * to evaluate the strength of p-adic cryptographic primitives.
 * 
 * Main focus areas:
 * 1. p-adic Shortest Vector Problem (SVP) attacks
 * 2. Lattice reduction algorithms adapted for ultrametric spaces
 * 3. Algebraic attacks on p-adic structures
 * 4. Quantum algorithm simulation
 * 5. Statistical analysis of PRNGs
 */

/**
 * p-adic LLL (Lenstra-Lenstra-Lovász) Algorithm
 * 
 * Adapts the classical LLL lattice reduction algorithm to work
 * with p-adic norms and the ultrametric property.
 * 
 * Key differences from classical LLL:
 * - Uses p-adic inner product
 * - Ultrametric distance instead of Euclidean
 * - Different notion of "reduced" basis
 */
class PadicLLL {
private:
    long p;
    long precision;
    double delta;  // Reduction parameter (typically 0.75)
    
public:
    /**
     * Initialize p-adic LLL with parameters
     * 
     * @param p Prime for p-adic field
     * @param precision p-adic precision
     * @param delta Reduction quality parameter (0.5 < delta < 1)
     */
    PadicLLL(long p, long precision, double delta = 0.75);
    
    /**
     * Reduce a p-adic lattice basis
     * 
     * @param basis Input basis vectors
     * @return Reduced basis
     */
    std::vector<std::vector<Zp>> reduce(const std::vector<std::vector<Zp>>& basis);
    
    /**
     * Check if a basis is LLL-reduced (p-adic version)
     */
    bool is_reduced(const std::vector<std::vector<Zp>>& basis) const;
    
    /**
     * Compute p-adic orthogonal basis using modified Gram-Schmidt
     */
    std::vector<std::vector<Qp>> gram_schmidt_padic(
        const std::vector<std::vector<Zp>>& basis) const;
    
    /**
     * Size reduction step in p-adic metric
     */
    void size_reduce(std::vector<std::vector<Zp>>& basis, long k, long j);
    
    /**
     * Lovász condition for p-adic lattices
     */
    bool lovasz_condition(const std::vector<std::vector<Qp>>& orthogonal, 
                          long k) const;
};

/**
 * Attack on p-adic Lattice Cryptosystem
 * 
 * Attempts to recover private key or decrypt messages
 * without the private key using various lattice attacks.
 */
class LatticeAttack {
private:
    long p;
    long dimension;
    long precision;
    
public:
    LatticeAttack(long p, long dimension, long precision);
    
    /**
     * Try to recover private key from public key
     * 
     * @param public_basis The public "bad" basis
     * @return Private basis if attack succeeds
     */
    std::optional<std::vector<std::vector<Zp>>> recover_private_key(
        const std::vector<std::vector<Zp>>& public_basis);
    
    /**
     * Attempt to decrypt without private key using CVP approximation
     * 
     * @param ciphertext Encrypted message
     * @param public_basis Public key
     * @return Potential plaintext if attack succeeds
     */
    std::optional<std::vector<long>> decrypt_without_key(
        const std::vector<Qp>& ciphertext,
        const std::vector<std::vector<Zp>>& public_basis);
    
    /**
     * Babai's nearest plane algorithm for p-adic CVP
     */
    std::vector<Zp> babai_nearest_plane(
        const std::vector<Qp>& target,
        const std::vector<std::vector<Zp>>& basis);
    
    /**
     * Measure attack success rate
     */
    struct AttackResult {
        bool success;
        double time_ms;
        long iterations;
        std::string method;
    };
    
    AttackResult analyze_security(const crypto::PadicLattice& cryptosystem);
};

/**
 * Baby-step Giant-step Algorithm for p-adic Discrete Logarithm
 * 
 * Solves: Given g, h in Z_p*, find x such that g^x ≡ h (mod p^n)
 * This attacks the p-adic signature scheme.
 */
class PadicDiscreteLog {
private:
    long p;
    long precision;
    
public:
    PadicDiscreteLog(long p, long precision);
    
    /**
     * Solve discrete log using baby-step giant-step
     * 
     * @param base Generator g
     * @param target Target h
     * @param max_exponent Upper bound on x
     * @return x if found
     */
    std::optional<BigInt> solve(const Zp& base, const Zp& target, 
                                const BigInt& max_exponent);
    
    /**
     * Pollard's rho algorithm for p-adic groups
     */
    std::optional<BigInt> pollard_rho(const Zp& base, const Zp& target);
    
    /**
     * Index calculus adaptation for p-adic fields
     * (More complex, requires smooth number theory in Z_p)
     */
    std::optional<BigInt> index_calculus(const Zp& base, const Zp& target);
};

/**
 * Statistical Attacks on p-adic PRNG
 * 
 * Analyzes output to find weaknesses, predict future values,
 * or recover internal state.
 */
class PRNGAttack {
private:
    long p;
    long precision;
    
public:
    PRNGAttack(long p, long precision);
    
    /**
     * Try to recover PRNG internal state from outputs
     * 
     * @param outputs Sequence of PRNG outputs
     * @return Recovered state if successful
     */
    std::optional<Zp> recover_state(const std::vector<Zp>& outputs);
    
    /**
     * Predict next values given past outputs
     * 
     * @param history Past PRNG outputs
     * @param num_predictions How many future values to predict
     * @return Predicted values
     */
    std::vector<Zp> predict_next(const std::vector<Zp>& history, 
                                 long num_predictions);
    
    /**
     * Distinguish from random using statistical tests
     * 
     * @param samples Output samples from PRNG
     * @return Probability that samples are from this PRNG (vs random)
     */
    double distinguish_from_random(const std::vector<Zp>& samples);
    
    /**
     * Find correlations and biases in output
     */
    struct BiasAnalysis {
        double frequency_bias;      // Deviation from uniform
        double serial_correlation;   // Between consecutive outputs
        double long_range_correlation;
        std::vector<long> weak_bits; // Bit positions with bias
    };
    
    BiasAnalysis analyze_bias(const std::vector<Zp>& samples);
};

/**
 * Quantum Algorithm Simulation
 * 
 * Simulates quantum attacks to evaluate post-quantum security.
 * Note: These are classical simulations with exponential slowdown.
 */
class QuantumSimulator {
public:
    /**
     * Simulate Shor's algorithm on p-adic discrete log
     * 
     * @return true if Shor's would work (it shouldn't for p-adic)
     */
    static bool test_shors_applicability(const Zp& base, const Zp& target,
                                         long p, long precision);
    
    /**
     * Simulate Grover's search in p-adic space
     * 
     * @return Speedup factor vs classical (should be less than √N)
     */
    static double grover_speedup_factor(long search_space_size, 
                                        long p, long precision);
    
    /**
     * Test if HHL algorithm applies to p-adic linear systems
     */
    static bool test_hhl_applicability(const std::vector<std::vector<Qp>>& matrix);
    
    /**
     * Estimate quantum circuit depth needed for attack
     */
    static long estimate_quantum_resources(long security_parameter);
};

/**
 * Side-Channel Attack Simulation
 * 
 * Tests resistance to timing, power, and cache attacks.
 */
class SideChannelAnalysis {
public:
    /**
     * Timing attack on p-adic operations
     * 
     * Measures if operation time leaks information about secret values
     */
    struct TimingLeak {
        bool found_correlation;
        double correlation_coefficient;
        std::string vulnerable_operation;
    };
    
    static TimingLeak analyze_timing(const crypto::PadicLattice& system);
    
    /**
     * Simple Power Analysis (SPA) simulation
     */
    static bool simulate_spa_attack(const crypto::PadicLattice& system);
    
    /**
     * Differential Power Analysis (DPA) simulation
     */
    static bool simulate_dpa_attack(const crypto::PadicLattice& system,
                                   long num_traces);
};

/**
 * Comprehensive Security Evaluator
 * 
 * Runs all attacks and provides security assessment.
 */
class SecurityEvaluator {
private:
    long p;
    long dimension;
    long precision;
    
    // Attack modules
    LatticeAttack lattice_attacker;
    PadicDiscreteLog dlog_attacker;
    PRNGAttack prng_attacker;
    
public:
    SecurityEvaluator(long p, long dimension, long precision);
    
    /**
     * Complete security assessment
     */
    struct SecurityReport {
        // Attack results
        bool lattice_attack_success;
        bool discrete_log_broken;
        bool prng_distinguishable;
        bool quantum_vulnerable;
        bool side_channel_vulnerable;
        
        // Security metrics
        long effective_security_bits;
        long quantum_security_bits;
        double attack_time_years;  // With current technology
        
        // Recommendations
        long recommended_key_size;
        long recommended_precision;
        std::string security_level;  // "BROKEN", "WEAK", "MEDIUM", "STRONG", "VERY_STRONG"
        std::vector<std::string> vulnerabilities;
        std::vector<std::string> recommendations;
    };
    
    SecurityReport evaluate_all(const crypto::PadicLattice& lattice_system,
                                const crypto::PadicPRNG& prng,
                                bool verbose = false);
    
    /**
     * Parameter recommendation for target security level
     * 
     * @param target_bits Desired security level in bits (e.g., 128, 256)
     * @return Recommended parameters (p, dimension, precision)
     */
    struct RecommendedParams {
        long prime;
        long dimension;
        long precision;
        size_t key_size_bytes;
        size_t ciphertext_expansion;
    };
    
    static RecommendedParams recommend_parameters(long target_bits);
    
    /**
     * Compare with NIST security levels
     */
    static int get_nist_level(const SecurityReport& report);
};

/**
 * Benchmarking Against Standard Algorithms
 */
class CryptoBenchmark {
public:
    struct BenchmarkResult {
        std::string algorithm;
        double keygen_ms;
        double encrypt_ms;
        double decrypt_ms;
        size_t public_key_bytes;
        size_t private_key_bytes;
        size_t ciphertext_bytes;
        long security_bits;
    };
    
    /**
     * Benchmark our p-adic crypto
     */
    static BenchmarkResult benchmark_padic(long p, long dim, long prec);
    
    /**
     * Compare with other post-quantum algorithms
     * Note: This would need external libraries for real comparison
     */
    static std::vector<BenchmarkResult> compare_with_standards();
    
    /**
     * Generate performance comparison report
     */
    static void generate_comparison_report(const std::string& filename);
};

} // namespace cryptanalysis
} // namespace libadic

#endif // LIBADIC_CRYPTANALYSIS_H
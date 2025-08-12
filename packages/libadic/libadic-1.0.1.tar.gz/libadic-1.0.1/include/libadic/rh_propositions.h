#ifndef LIBADIC_RH_PROPOSITIONS_H
#define LIBADIC_RH_PROPOSITIONS_H

#include "libadic/qp.h"
#include "libadic/zp.h"
#include "libadic/padic_gamma.h"
#include "libadic/iwasawa_log.h"
#include "libadic/l_functions.h"
#include "libadic/characters.h"
#include <vector>
#include <complex>
#include <functional>
#include <map>
#include <optional>

namespace libadic {
namespace rh {

// We use the DirichletCharacter class from characters.h
// No need to duplicate it here

/**
 * Reid transform: R_pm(chi) = sum_{a in G_m} chi(a) * h_m(a)
 * where h_m(a) = log_p(Gamma_p(a/(p-1)))
 */
Qp compute_reid_transform(const libadic::DirichletCharacter& chi, long precision);

/**
 * Even Reid transform: E_pm(chi) = sum_{a in G_m} chi(a) * g_m(a)
 * where g_m is the even kernel from OP3
 */
Qp compute_even_reid_transform(const libadic::DirichletCharacter& chi, long precision);

/**
 * Verification result structure
 */
struct VerificationResult {
    bool passed;
    double confidence;
    std::string op_name;
    std::string details;
    std::map<std::string, Qp> data;  // Numerical data from verification
};

/**
 * OP1: Odd DFT scalarity
 * Verify that R_pm(chi) = u_p,m * (1/p^m) * L'_p(0, chi) for odd chi
 */
VerificationResult verify_op1(const BigInt& p, long m, long precision,
                              const std::vector<libadic::DirichletCharacter>& characters = {});

/**
 * OP2: Conductor stability
 * Verify that u_p,m = u_p for all m >= 1
 */
VerificationResult verify_op2(const BigInt& p, long max_level, long precision);

/**
 * OP3: Even block scalarity
 * Verify that E_pm(chi) = v_p,m * L_p(0, chi) for even chi
 */
VerificationResult verify_op3(const BigInt& p, long m, long precision,
                              const std::vector<DirichletCharacter>& characters = {});

/**
 * OP4: Discrepancy identification
 * Verify the discrepancy between Gauss-sum and cyclotomic regulators
 */
VerificationResult verify_op4(const BigInt& p, long m, long precision);

/**
 * OP8: Mahler/Lipschitz bounds
 * Compute Mahler expansion and verify exponential decay
 */
struct MahlerBounds {
    std::vector<Qp> coefficients;
    double decay_rate;
    double lipschitz_constant;
};

MahlerBounds compute_mahler_bounds(
    std::function<Qp(const Qp&)> f,
    const BigInt& p, 
    long precision,
    long max_degree = 50
);

VerificationResult verify_op8(const BigInt& p, long precision);

/**
 * OP9: Certified numerics pipeline
 * Run interval-verified computation across a grid of parameters
 */
struct CertifiedGrid {
    std::vector<BigInt> primes;
    std::vector<long> levels;
    std::vector<long> precisions;
};

VerificationResult verify_op9(const CertifiedGrid& grid);

/**
 * OP13: p = 2 case
 * Verify odd/even scalarity holds for p = 2
 */
VerificationResult verify_op13(long precision);

/**
 * Generate all primitive Dirichlet characters modulo p^m
 */
std::vector<libadic::DirichletCharacter> generate_primitive_characters(const BigInt& p, long m);

/**
 * Generate test grid for verification
 */
CertifiedGrid generate_test_grid(
    const std::vector<BigInt>& primes = {BigInt(2), BigInt(3), BigInt(5), BigInt(7), BigInt(11)},
    const std::vector<long>& levels = {1, 2, 3},
    const std::vector<long>& precisions = {20, 50, 100}
);

/**
 * Master verification function - runs all implementable OPs
 */
std::vector<VerificationResult> verify_all_ops(
    const CertifiedGrid& grid = generate_test_grid(),
    bool verbose = true
);

/**
 * Helper: Compute discrete Fourier transform over (Z/p^mZ)^*
 */
template<typename T>
T compute_dft(
    const DirichletCharacter& chi,
    std::function<T(long)> kernel,
    const BigInt& p,
    long m
);

/**
 * Helper: Check if a p-adic number is a unit
 */
bool is_padic_unit(const Qp& x);

/**
 * Helper: Extract the unit part from a ratio of p-adic numbers
 */
std::optional<Qp> extract_unit_ratio(const Qp& numerator, const Qp& denominator);

} // namespace rh
} // namespace libadic

#endif // LIBADIC_RH_PROPOSITIONS_H
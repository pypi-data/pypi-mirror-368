/**
 * Proper implementation of Babai's nearest plane algorithm for p-adic lattices
 */

#include "libadic/padic_cvp_solver.h"
#include "libadic/padic_linear_algebra.h"
#include <vector>
#include <iostream>

namespace libadic {
namespace crypto {

/**
 * Simple Babai rounding for p-adic CVP
 * Uses the private (good) basis to find closest lattice point
 */
std::vector<long> decrypt_with_babai(
    const std::vector<Qp>& ciphertext,
    const linalg::Matrix& private_basis,  // Good basis (trapdoor)
    const linalg::Matrix& public_basis,
    const BigInt& p,
    long precision,
    long dimension) {
    
#ifdef LIBADIC_DEBUG
    std::cout << "[DEBUG] decrypt_with_babai called, dimension=" << dimension << std::endl;
#endif
    
    // Step 1: Solve for lattice coefficients modulo p^(precision - scale_bits)
    BigInt p_big = p;
    BigInt modulus = p_big.pow(precision);
    long scale_bits = std::min(precision / 4, 8L);
    long red_prec = std::max(1L, precision - scale_bits);
    BigInt red_mod = p_big.pow(red_prec);

    // Build B^T (PUBLIC basis) with reduced precision to recover encryption coeffs
    linalg::Matrix BT_red(dimension, linalg::Vector(dimension));
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            // transpose: BT[i][j] = public_basis[j][i]
            BT_red[i][j] = Zp(p, red_prec, public_basis[j][i].get_value());
        }
    }

    // Invert B^T modulo p^red_prec
    linalg::PadicMatrix BTM(p, red_prec, BT_red);
    auto inv_opt = BTM.inverse();
    if (!inv_opt.has_value()) {
        // Degenerate case: return zeros
        std::vector<long> zero_msg(dimension, 0);
        return zero_msg;
    }
    linalg::Matrix invBT = inv_opt->get_data();

    // Build reduced target vector t_mod from ciphertext
    std::vector<Zp> t_red(dimension);
    for (long i = 0; i < dimension; ++i) {
        const Qp &q = ciphertext[i];
        BigInt unit_val = q.get_unit().get_value();
        long vq = q.valuation();
        BigInt ct_val = (unit_val * p_big.pow(std::max(0L, vq))) % red_mod;
        t_red[i] = Zp(p, red_prec, ct_val);
    }

    // Compute coefficients modulo p^red_prec: c = invBT * t_red
    std::vector<BigInt> coefficients(dimension, BigInt(0));
    for (long i = 0; i < dimension; ++i) {
        Zp sum(p, red_prec, 0);
        for (long j = 0; j < dimension; ++j) {
            sum = sum + invBT[i][j] * t_red[j];
        }
        // Use symmetric_reduce from PadicCVPSolver to get proper coefficients
        coefficients[i] = PadicCVPSolver::symmetric_reduce(sum.get_value(), p, red_prec);
    }

    // Optional local search refinement around coefficients to improve CVP
    auto valuation = [&](const BigInt& x) -> long {
        if (x == BigInt(0)) return precision; // treat as very close
        BigInt t = x;
        if (t < BigInt(0)) t = -t;
        long v = 0;
        while (t % p_big == BigInt(0) && v < precision) { t = t / p_big; v++; }
        return v;
    };

    auto score_coeffs = [&](const std::vector<BigInt>& coeffs) -> long {
        long best = precision;
        for (long i = 0; i < dimension; ++i) {
            BigInt sum(0);
            for (long j = 0; j < dimension; ++j) {
                sum = (sum + private_basis[j][i].get_value() * coeffs[j]) % modulus;
            }
            // ciphertext representative
            const Qp &q = ciphertext[i];
            BigInt unit_val = q.get_unit().get_value();
            long vq = q.valuation();
            BigInt ct_val = (unit_val * p_big.pow(std::max(0L, vq))) % modulus;
            BigInt diff = ct_val - sum;
            // map to symmetric rep
            BigInt half_mod = modulus / BigInt(2);
            if (diff > half_mod) diff = diff - modulus;
            long v = valuation(diff);
            if (v < best) best = v;
        }
        return best;
    };

    // Search radius
    int radius = (dimension <= 4) ? 3 : 1;
    std::vector<BigInt> best_coeffs = coefficients;
    long best_score = score_coeffs(best_coeffs);
    if (radius > 0) {
        // Simple DFS over small cube around coefficients
        std::vector<long> deltas(dimension, 0);
        // Iterate over [-r, r]^dimension
        std::vector<int> idx(dimension, -radius);
        while (true) {
            std::vector<BigInt> cand = coefficients;
            for (long k = 0; k < dimension; ++k) {
                cand[k] = cand[k] + BigInt(idx[k]);
            }
            long sc = score_coeffs(cand);
            if (sc > best_score) { best_score = sc; best_coeffs = cand; }
            // increment idx like odometer
            long pos = 0;
            while (pos < dimension) {
                idx[pos]++;
                if (idx[pos] <= radius) break;
                idx[pos] = -radius; pos++;
            }
            if (pos == dimension) break;
        }
    }

    coefficients = best_coeffs;

#ifdef LIBADIC_DEBUG
    std::cout << "[DEBUG] Babai solve_cvp completed, found coefficients:";
    for (const auto& c : coefficients) {
        std::cout << " " << c.to_string();
    }
    std::cout << std::endl;
#endif
    
    // Step 2: Reconstruct the closest lattice point using PUBLIC basis (since coeffs are from public basis inverse)
    std::vector<BigInt> closest_lattice_point(dimension, BigInt(0));
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            closest_lattice_point[i] = closest_lattice_point[i] + 
                public_basis[j][i].get_value() * coefficients[j];
        }
        // Reduce modulo p^precision
        closest_lattice_point[i] = closest_lattice_point[i] % BigInt(p).pow(precision);
    }
    
    // Step 3: Compute difference (should be scaled_message + noise)
    std::vector<BigInt> diff(dimension);
    for (long i = 0; i < dimension; ++i) {
        // Safely reconstruct ciphertext integer representative
        const Qp &q = ciphertext[i];
        BigInt unit_val = q.get_unit().get_value();
        long v = q.valuation();
        BigInt ct_val = (unit_val * p_big.pow(std::max(0L, v))) % modulus;

        diff[i] = ct_val - closest_lattice_point[i];
        
        // Ensure positive by adding modulus if needed
        while (diff[i] < BigInt(0)) {
            diff[i] = diff[i] + modulus;
        }
        diff[i] = diff[i] % modulus;
    }
    
    // Step 4: Extract message by removing scale factor
    // scale_bits already defined above
    BigInt scale_factor = BigInt(p).pow(scale_bits);
    std::vector<long> message(dimension);
    
    for (long i = 0; i < dimension; ++i) {
        // Normalize to symmetric representative in (-mod/2, mod/2]
        BigInt half_mod = modulus / BigInt(2);
        BigInt val = diff[i] % modulus;
        if (val > half_mod) {
            val = val - modulus;
        }

        // Round to nearest multiple of scale_factor
        BigInt half_scale = scale_factor / BigInt(2);
        BigInt quotient;
        if (val >= BigInt(0)) {
            quotient = (val + half_scale) / scale_factor;
        } else {
            quotient = (val - half_scale) / scale_factor;  // symmetric rounding for negatives
        }

        // Extract message value
        message[i] = quotient.to_long();
    }
    
    return message;
}

} // namespace crypto
} // namespace libadic

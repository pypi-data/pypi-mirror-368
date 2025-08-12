#ifndef LIBADIC_PADIC_CVP_SOLVER_H
#define LIBADIC_PADIC_CVP_SOLVER_H

#include "libadic/qp.h"
#include "libadic/zp.h"
#include "libadic/padic_linear_algebra.h"
#include <vector>
#include <optional>

namespace libadic {
namespace crypto {

/**
 * p-adic Closest Vector Problem (CVP) Solver
 * 
 * Solves the fundamental problem in p-adic lattice cryptography:
 * Given a lattice L and target vector t, find the lattice point
 * closest to t under the p-adic metric.
 * 
 * The p-adic metric fundamentally changes the geometry:
 * - Ultrametric property: d(x,z) ≤ max(d(x,y), d(y,z))
 * - All triangles are isosceles
 * - Balls are both open and closed
 * - No unique shortest path between points
 */
class PadicCVPSolver {
public:  // Made public for access by CryptoCVP helper functions
    BigInt p;
    long precision;
private:
    linalg::Matrix basis;
    long dimension;
    
    // Precomputed data for efficiency
    linalg::QMatrix gram_schmidt_basis;
    std::vector<std::vector<Qp>> mu_coefficients;
    bool is_preprocessed;
    
public:
    /**
     * Initialize CVP solver with lattice basis
     */
    PadicCVPSolver(const BigInt& p, long precision, const linalg::Matrix& lattice_basis);
    
    // Convenience constructor for backward compatibility  
    PadicCVPSolver(long p, long precision, const linalg::Matrix& lattice_basis);
    
    /**
     * Preprocess basis for faster CVP solving
     * Computes Gram-Schmidt orthogonalization and mu coefficients
     */
    void preprocess();
    
    /**
     * Solve CVP using Babai's nearest plane algorithm
     * Adapted for p-adic metric
     * 
     * @param target Target vector
     * @return Closest lattice point
     */
    linalg::Vector solve_cvp(const linalg::QVector& target);
    
    /**
     * Solve CVP with bounded distance
     * Returns nullopt if no solution within bound
     * 
     * @param target Target vector
     * @param bound Maximum p-adic distance
     * @return Closest point if within bound
     */
    std::optional<linalg::Vector> solve_bounded_cvp(
        const linalg::QVector& target,
        long bound_valuation
    );
    
    /**
     * Babai's rounding algorithm
     * Simpler but less accurate than nearest plane
     */
    linalg::Vector babai_round(const linalg::QVector& target);
    
    /**
     * Enumeration-based exact CVP
     * Exponential time but finds optimal solution
     * 
     * @param target Target vector
     * @param max_coefficients Maximum coefficient bound for enumeration
     * @return Exact closest vector
     */
    linalg::Vector exact_cvp(const linalg::QVector& target, long max_coefficients);
    
    /**
     * Find all lattice points within p-adic ball
     * 
     * @param center Center of ball
     * @param radius_valuation Valuation defining radius (higher = smaller ball)
     * @return All lattice points in ball
     */
    std::vector<linalg::Vector> enumerate_ball(
        const linalg::QVector& center,
        long radius_valuation
    );
    
    /**
     * Compute p-adic distance between vectors
     */
    static long padic_distance(const linalg::QVector& u, const linalg::QVector& v);
    
    /**
     * Check if point is in lattice
     */
    bool is_lattice_point(const linalg::QVector& point) const;
    
    /**
     * Project vector onto lattice using p-adic metric
     */
    linalg::QVector project_onto_lattice(const linalg::QVector& v);
    
    /**
     * Solve approximate CVP with quality guarantee
     * 
     * @param target Target vector
     * @param approximation_factor Approximation quality (1 = exact)
     * @return Approximate solution
     */
    linalg::Vector approximate_cvp(const linalg::QVector& target, double approximation_factor);
    
    /**
     * Helper: p-adic rounding to nearest integer
     * Different from real rounding due to ultrametric
     */
    static Zp padic_round(const Qp& x, long p, long precision);

    /**
     * Helper: symmetric reduction to (-mod/2, mod/2].
     * Returns representative of a modulo p^precision centered at 0.
     */
    static BigInt symmetric_reduce(const BigInt& a, const BigInt& p, long precision);

    /**
     * Helper: round a value to nearest multiple of scale (p^s) with symmetric rounding.
     * Operates on representatives modulo p^precision.
     */
    static BigInt round_to_multiple(const BigInt& a, const BigInt& scale, const BigInt& modulus);
    
    /**
     * Helper: Compute lattice coordinates from point
     */
    linalg::QVector get_lattice_coordinates(const linalg::QVector& point) const;
    
    /**
     * Helper: Reconstruct point from lattice coordinates
     */
    linalg::QVector from_lattice_coordinates(const linalg::QVector& coords) const;
    
    // Public getters for Python bindings
    const linalg::Matrix& get_basis() const { return basis; }
    long get_dimension() const { return dimension; }
    bool is_basis_preprocessed() const { return is_preprocessed; }
};

/**
 * Advanced CVP algorithms for cryptography
 */
class CryptoCVP {
public:
    /**
     * CVP with side information (for decryption)
     * Uses hint about plaintext structure
     */
    static linalg::Vector solve_cvp_with_hint(
        PadicCVPSolver& solver,
        const linalg::QVector& target,
        const std::vector<long>& plaintext_bounds
    );
    
    /**
     * Parallel CVP for multiple targets
     * Optimized batch processing
     */
    static std::vector<linalg::Vector> batch_cvp(
        PadicCVPSolver& solver,
        const std::vector<linalg::QVector>& targets
    );
    
    /**
     * CVP with noise tolerance
     * For noisy ciphertext decryption
     */
    static linalg::Vector noisy_cvp(
        PadicCVPSolver& solver,
        const linalg::QVector& noisy_target,
        long noise_valuation
    );
    
    /**
     * Verify CVP solution correctness
     */
    static bool verify_cvp_solution(
        const linalg::Matrix& basis,
        const linalg::QVector& target,
        const linalg::Vector& solution,
        long p,
        long precision
    );
    
    /**
     * Quality metrics for CVP solution
     */
    struct CVPQuality {
        long distance_valuation;
        double approximation_ratio;
        bool is_unique;
        long computation_time_us;
    };
    
    static CVPQuality analyze_solution(
        const linalg::Matrix& basis,
        const linalg::QVector& target,
        const linalg::Vector& solution,
        long p,
        long precision
    );
};

/**
 * Specialized Babai algorithms for p-adic lattices
 */
class BabaiAlgorithms {
public:
    /**
     * Classic Babai nearest plane for p-adic metric
     */
    static linalg::Vector nearest_plane(
        const linalg::QMatrix& gram_schmidt_basis,
        const linalg::QVector& target,
        const linalg::Matrix& original_basis,
        long p,
        long precision
    );
    
    /**
     * Iterative refinement of Babai's solution
     * Improves accuracy through p-adic lifting
     */
    static linalg::Vector refined_babai(
        const linalg::Matrix& basis,
        const linalg::QVector& target,
        long p,
        long precision,
        long iterations
    );
    
    /**
     * Babai with enumeration in small radius
     * Combines speed of Babai with exactness of enumeration
     */
    static linalg::Vector hybrid_babai(
        const linalg::Matrix& basis,
        const linalg::QVector& target,
        long p,
        long precision,
        long enum_radius
    );
};

} // namespace crypto
} // namespace libadic

#endif // LIBADIC_PADIC_CVP_SOLVER_H

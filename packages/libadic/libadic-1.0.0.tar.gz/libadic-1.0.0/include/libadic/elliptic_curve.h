#ifndef LIBADIC_ELLIPTIC_CURVE_H
#define LIBADIC_ELLIPTIC_CURVE_H

#include "libadic/qp.h"
#include "libadic/zp.h"
#include "libadic/gmp_wrapper.h"
#include <vector>
#include <optional>

namespace libadic {

/**
 * Elliptic curve over Q in Weierstrass form: y² = x³ + ax + b
 * 
 * This class provides the foundation for computing p-adic L-functions
 * and testing the Birch and Swinnerton-Dyer conjecture.
 * 
 * Supported operations:
 * - Point arithmetic (addition, doubling)
 * - Reduction modulo p
 * - Torsion point computation
 * - j-invariant and discriminant
 * - Conductor computation
 * - L-series coefficients (a_p)
 */
class EllipticCurve {
public:
    /**
     * Point on the elliptic curve
     * Uses projective coordinates [X:Y:Z] where x = X/Z², y = Y/Z³
     * Point at infinity is [0:1:0]
     */
    struct Point {
        BigInt X, Y, Z;
        
        Point() : X(0), Y(1), Z(0) {}  // Point at infinity
        Point(const BigInt& x, const BigInt& y) : X(x), Y(y), Z(1) {}
        Point(const BigInt& x, const BigInt& y, const BigInt& z) : X(x), Y(y), Z(z) {}
        
        bool is_infinity() const { return Z == BigInt(0); }
        bool operator==(const Point& other) const;
        bool operator!=(const Point& other) const { return !(*this == other); }
    };
    
    /**
     * p-adic point on the elliptic curve
     */
    struct PadicPoint {
        Qp x, y;
        bool is_infinity;
        
        PadicPoint() : is_infinity(true) {}
        PadicPoint(const Qp& x_, const Qp& y_) : x(x_), y(y_), is_infinity(false) {}
    };

private:
    BigInt a_coeff;    // Coefficient a in y² = x³ + ax + b
    BigInt b_coeff;    // Coefficient b in y² = x³ + ax + b
    BigInt discriminant;
    BigInt j_invariant_num;
    BigInt j_invariant_den;
    long conductor;
    
    // Cache for L-series coefficients
    mutable std::vector<long> a_p_cache;
    mutable std::vector<long> cached_primes;
    
    void compute_invariants();
    void compute_conductor();
    
public:
    /**
     * Construct elliptic curve y² = x³ + ax + b
     */
    EllipticCurve(const BigInt& a, const BigInt& b);
    EllipticCurve(long a, long b);
    
    /**
     * Construct from Cremona label (e.g., "11a1", "37b2")
     * Returns nullopt if label not recognized
     */
    static std::optional<EllipticCurve> from_cremona_label(const std::string& label);
    
    // Accessors
    const BigInt& get_a() const { return a_coeff; }
    const BigInt& get_b() const { return b_coeff; }
    const BigInt& get_discriminant() const { return discriminant; }
    long get_conductor() const { return conductor; }
    
    /**
     * Get j-invariant as a rational number
     */
    std::pair<BigInt, BigInt> get_j_invariant() const {
        return {j_invariant_num, j_invariant_den};
    }
    
    /**
     * Check if point (x, y) is on the curve
     */
    bool contains_point(const BigInt& x, const BigInt& y) const;
    bool contains_point(const Point& P) const;
    
    /**
     * Point arithmetic
     */
    Point add_points(const Point& P, const Point& Q) const;
    Point double_point(const Point& P) const;
    Point negate_point(const Point& P) const;
    Point scalar_multiply(const Point& P, const BigInt& n) const;
    
    /**
     * p-adic point arithmetic
     */
    PadicPoint add_points_padic(const PadicPoint& P, const PadicPoint& Q, long p, long precision) const;
    PadicPoint double_point_padic(const PadicPoint& P, long p, long precision) const;
    PadicPoint scalar_multiply_padic(const PadicPoint& P, const BigInt& n, long p, long precision) const;
    
    /**
     * Reduction type at prime p
     * Returns: 1 for good reduction, 0 for additive, -1 for split multiplicative, -2 for non-split
     */
    int reduction_type(long p) const;
    
    /**
     * Number of points modulo p (for good reduction)
     * Uses Schoof's algorithm for large p
     */
    long count_points_mod_p(long p) const;
    
    /**
     * L-series coefficient a_p = p + 1 - #E(F_p)
     * For bad reduction, uses special formulas
     */
    long get_ap(long p) const;
    
    /**
     * Compute L-series up to X
     * L(E, s) = Σ a_n/n^s
     */
    std::vector<long> compute_an_coefficients(long max_n) const;
    
    /**
     * Algebraic rank (computed via descent if possible)
     * Returns -1 if cannot determine
     */
    long compute_algebraic_rank() const;
    
    /**
     * Find torsion subgroup
     */
    std::vector<Point> compute_torsion_points() const;
    long get_torsion_order() const;
    
    /**
     * Period computations (needed for BSD)
     */
    BigInt compute_real_period_approx(long precision_bits) const;
    Qp compute_padic_period(long p, long precision) const;
    
    /**
     * Check if curve has complex multiplication
     */
    bool has_cm() const;
    long get_cm_discriminant() const;
    
    /**
     * String representation
     */
    std::string to_string() const;
    std::string to_latex() const;
    
    /**
     * Famous curves for testing
     */
    static EllipticCurve curve_11a1() { return EllipticCurve(0, -1); }     // Rank 0, conductor 11
    static EllipticCurve curve_37a1() { return EllipticCurve(0, -1); }     // Rank 1, conductor 37
    static EllipticCurve curve_389a1() { return EllipticCurve(1, -2); }    // Rank 2, conductor 389
    static EllipticCurve congruent_number_curve(long n) {                 // y² = x³ - n²x
        return EllipticCurve(-BigInt(n) * BigInt(n), BigInt(0));
    }
};

/**
 * Database of elliptic curves from standard tables
 */
class EllipticCurveDatabase {
public:
    struct CurveData {
        std::string cremona_label;
        long conductor;
        long a, b;
        long rank;
        long torsion_order;
        std::vector<long> generators;  // x-coordinates of generators
    };
    
    static std::vector<CurveData> get_curves_with_conductor(long N);
    static std::vector<CurveData> get_curves_with_rank(long r);
    static std::optional<CurveData> get_curve_by_label(const std::string& label);
    
    // Get first few curves for testing
    static std::vector<CurveData> get_test_curves();
};

} // namespace libadic

#endif // LIBADIC_ELLIPTIC_CURVE_H
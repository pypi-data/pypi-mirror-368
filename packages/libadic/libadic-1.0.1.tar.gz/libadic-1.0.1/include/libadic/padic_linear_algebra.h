#ifndef LIBADIC_PADIC_LINEAR_ALGEBRA_H
#define LIBADIC_PADIC_LINEAR_ALGEBRA_H

#include "libadic/qp.h"
#include "libadic/zp.h"
#include <vector>
#include <optional>

namespace libadic {
namespace linalg {

/**
 * p-adic Linear Algebra Operations
 * 
 * Provides complete matrix operations over p-adic fields with
 * proper handling of the ultrametric norm and valuations.
 */

using Matrix = std::vector<std::vector<Zp>>;
using QMatrix = std::vector<std::vector<Qp>>;
using Vector = std::vector<Zp>;
using QVector = std::vector<Qp>;

/**
 * p-adic Matrix Operations
 */
class PadicMatrix {
private:
    BigInt p;
    long precision;
    Matrix data;
    long rows;
    long cols;
    
public:
    /**
     * Constructors
     */
    PadicMatrix(const BigInt& p, long precision, long rows, long cols);
    PadicMatrix(const BigInt& p, long precision, const Matrix& data);
    
    // Convenience constructors for backward compatibility
    PadicMatrix(long p, long precision, long rows, long cols);
    PadicMatrix(long p, long precision, const Matrix& data);
    
    /**
     * Matrix multiplication with proper modular reduction
     */
    PadicMatrix operator*(const PadicMatrix& other) const;
    
    /**
     * Matrix addition/subtraction
     */
    PadicMatrix operator+(const PadicMatrix& other) const;
    PadicMatrix operator-(const PadicMatrix& other) const;
    
    /**
     * Scalar multiplication
     */
    PadicMatrix operator*(const Zp& scalar) const;
    
    /**
     * Matrix-vector multiplication
     */
    Vector operator*(const Vector& v) const;
    
    /**
     * Transpose
     */
    PadicMatrix transpose() const;
    
    /**
     * p-adic determinant using Gaussian elimination
     */
    Zp determinant() const;
    
    /**
     * Matrix inversion using Hensel lifting
     * Returns nullopt if matrix is not invertible
     */
    std::optional<PadicMatrix> inverse() const;
    
    /**
     * Check if matrix is invertible (unit determinant)
     */
    bool is_invertible() const;
    
    /**
     * Hermite Normal Form
     * Returns HNF and transformation matrix U such that U*A = H
     */
    std::pair<PadicMatrix, PadicMatrix> hermite_normal_form() const;
    
    /**
     * Smith Normal Form
     * Returns (U, S, V) such that U*A*V = S (diagonal)
     */
    std::tuple<PadicMatrix, PadicMatrix, PadicMatrix> smith_normal_form() const;
    
    /**
     * LU decomposition with p-adic pivoting
     */
    std::pair<PadicMatrix, PadicMatrix> lu_decomposition() const;
    
    /**
     * QR decomposition using p-adic Gram-Schmidt
     */
    std::pair<QMatrix, PadicMatrix> qr_decomposition() const;
    
    /**
     * Solve linear system Ax = b
     */
    std::optional<Vector> solve(const Vector& b) const;
    
    /**
     * Compute kernel (null space)
     */
    std::vector<Vector> kernel() const;
    
    /**
     * Compute image (column space)
     */
    std::vector<Vector> image() const;
    
    /**
     * Rank computation
     */
    long rank() const;
    
    /**
     * Check if matrix is unimodular (det = ±1)
     */
    bool is_unimodular() const;
    
    /**
     * Generate random unimodular matrix
     */
    static PadicMatrix random_unimodular(const BigInt& p, long precision, long n);
    static PadicMatrix random_unimodular(long p, long precision, long n);  // Backward compatibility
    
    /**
     * Generate identity matrix
     */
    static PadicMatrix identity(const BigInt& p, long precision, long n);
    static PadicMatrix identity(long p, long precision, long n);  // Backward compatibility
    
    /**
     * Generate random matrix with specified valuation bounds
     */
    static PadicMatrix random_matrix(const BigInt& p, long precision, long rows, long cols,
                                     long min_val, long max_val);
    static PadicMatrix random_matrix(long p, long precision, long rows, long cols,
                                     long min_val, long max_val);  // Backward compatibility
    
    // Accessors
    long get_rows() const { return rows; }
    long get_cols() const { return cols; }
    const Matrix& get_data() const { return data; }
    Zp& at(long i, long j) { return data[i][j]; }
    const Zp& at(long i, long j) const { return data[i][j]; }
};

/**
 * p-adic Vector Operations
 */
class PadicVector {
public:
    /**
     * p-adic inner product
     */
    static Zp inner_product(const Vector& u, const Vector& v);
    
    /**
     * p-adic norm (minimum valuation)
     */
    static long padic_norm(const Vector& v);
    
    /**
     * Check if vectors are p-adically orthogonal
     */
    static bool are_orthogonal(const Vector& u, const Vector& v);
    
    /**
     * Project vector onto subspace
     */
    static QVector project(const QVector& v, const std::vector<QVector>& basis);
    
    /**
     * Gram-Schmidt orthogonalization (p-adic version)
     */
    static std::vector<QVector> gram_schmidt(const std::vector<Vector>& vectors,
                                             const BigInt& p, long precision);
    
    // Convenience overload for backward compatibility
    static std::vector<QVector> gram_schmidt(const std::vector<Vector>& vectors,
                                             long p, long precision);
    
    /**
     * Find p-adically short vectors in lattice
     */
    static std::vector<Vector> find_short_vectors(const Matrix& basis,
                                                  const BigInt& p, long precision,
                                                  long max_norm);
    static std::vector<Vector> find_short_vectors(const Matrix& basis,
                                                  long p, long precision,
                                                  long max_norm);  // Backward compatibility
};

/**
 * Hensel Lifting for Matrix Operations
 */
class HenselLifting {
public:
    /**
     * Lift matrix inverse from mod p to mod p^n
     */
    static PadicMatrix lift_inverse(const PadicMatrix& A, long target_precision);
    
    /**
     * Lift solution of Ax = b from mod p to mod p^n
     */
    static Vector lift_solution(const PadicMatrix& A, const Vector& b,
                                const Vector& x0, long target_precision);
    
    /**
     * Lift eigenvalues and eigenvectors
     */
    static std::pair<std::vector<Zp>, std::vector<Vector>>
    lift_eigenpairs(const PadicMatrix& A, long target_precision);
};

/**
 * Special Matrix Generators for Cryptography
 */
class CryptoMatrixGen {
public:
    /**
     * Generate "good" basis with controlled p-adic norms
     * Short vectors in p-adic metric (high valuation)
     */
    static Matrix generate_good_basis(const BigInt& p, long precision, long dimension,
                                      long min_valuation);
    static Matrix generate_good_basis(long p, long precision, long dimension,
                                      long min_valuation);  // Backward compatibility
    
    /**
     * Generate "bad" basis from good basis
     * Long vectors in p-adic metric (low valuation)
     */
    static Matrix generate_bad_basis(const Matrix& good_basis,
                                     const BigInt& p, long precision);
    static Matrix generate_bad_basis(const Matrix& good_basis,
                                     long p, long precision);  // Backward compatibility
    
    /**
     * Generate basis with specific orthogonality properties
     */
    static Matrix generate_orthogonal_basis(const BigInt& p, long precision, long dimension);
    static Matrix generate_orthogonal_basis(long p, long precision, long dimension);  // Backward compatibility
    
    /**
     * Generate basis for specific lattice types
     */
    static Matrix generate_ideal_lattice(const BigInt& p, long precision, long dimension);
    static Matrix generate_ideal_lattice(long p, long precision, long dimension);  // Backward compatibility
    
    /**
     * Quality metrics for basis
     */
    static double basis_quality(const Matrix& basis, const BigInt& p, long precision);
    static double basis_quality(const Matrix& basis, long p, long precision);  // Backward compatibility
    
    /**
     * Orthogonality defect
     */
    static double orthogonality_defect(const Matrix& basis, const BigInt& p, long precision);
    static double orthogonality_defect(const Matrix& basis, long p, long precision);  // Backward compatibility
};

} // namespace linalg
} // namespace libadic

#endif // LIBADIC_PADIC_LINEAR_ALGEBRA_H
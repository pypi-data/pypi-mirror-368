#include "libadic/padic_linear_algebra.h"
#include <random>
#include <algorithm>
#include <stdexcept>
#include <tuple>

namespace libadic {
namespace linalg {

// PadicMatrix implementation
PadicMatrix::PadicMatrix(const BigInt& p_, long precision_, long rows_, long cols_)
    : p(p_), precision(precision_), rows(rows_), cols(cols_) {
    data.resize(rows);
    for (long i = 0; i < rows; ++i) {
        data[i].resize(cols);
        for (long j = 0; j < cols; ++j) {
            data[i][j] = Zp(p, precision, 0);
        }
    }
}

PadicMatrix::PadicMatrix(const BigInt& p_, long precision_, const Matrix& data_)
    : p(p_), precision(precision_), data(data_) {
    if (data.empty()) {
        rows = 0;
        cols = 0;
    } else {
        rows = data.size();
        cols = data[0].size();
    }
}

// Backward compatibility constructors
PadicMatrix::PadicMatrix(long p_, long precision_, long rows_, long cols_)
    : PadicMatrix(BigInt(p_), precision_, rows_, cols_) {}

PadicMatrix::PadicMatrix(long p_, long precision_, const Matrix& data_)
    : PadicMatrix(BigInt(p_), precision_, data_) {
    if (data.empty()) {
        rows = 0;
        cols = 0;
    } else {
        rows = data.size();
        cols = data[0].size();
    }
}

PadicMatrix PadicMatrix::operator*(const PadicMatrix& other) const {
    if (cols != other.rows) {
        throw std::invalid_argument("Matrix dimensions incompatible for multiplication");
    }
    
    PadicMatrix result(p, precision, rows, other.cols);
    
    for (long i = 0; i < rows; ++i) {
        for (long j = 0; j < other.cols; ++j) {
            Zp sum(p, precision, 0);
            for (long k = 0; k < cols; ++k) {
                sum = sum + data[i][k] * other.data[k][j];
            }
            result.data[i][j] = sum;
        }
    }
    
    return result;
}

PadicMatrix PadicMatrix::operator+(const PadicMatrix& other) const {
    if (rows != other.rows || cols != other.cols) {
        throw std::invalid_argument("Matrix dimensions must match for addition");
    }
    
    PadicMatrix result(p, precision, rows, cols);
    
    for (long i = 0; i < rows; ++i) {
        for (long j = 0; j < cols; ++j) {
            result.data[i][j] = data[i][j] + other.data[i][j];
        }
    }
    
    return result;
}

PadicMatrix PadicMatrix::operator-(const PadicMatrix& other) const {
    if (rows != other.rows || cols != other.cols) {
        throw std::invalid_argument("Matrix dimensions must match for subtraction");
    }
    
    PadicMatrix result(p, precision, rows, cols);
    
    for (long i = 0; i < rows; ++i) {
        for (long j = 0; j < cols; ++j) {
            result.data[i][j] = data[i][j] - other.data[i][j];
        }
    }
    
    return result;
}

PadicMatrix PadicMatrix::operator*(const Zp& scalar) const {
    PadicMatrix result(p, precision, rows, cols);
    
    for (long i = 0; i < rows; ++i) {
        for (long j = 0; j < cols; ++j) {
            result.data[i][j] = data[i][j] * scalar;
        }
    }
    
    return result;
}

Vector PadicMatrix::operator*(const Vector& v) const {
    if (cols != static_cast<long>(v.size())) {
        throw std::invalid_argument("Vector dimension must match matrix columns");
    }
    
    Vector result(rows);
    
    for (long i = 0; i < rows; ++i) {
        Zp sum(p, precision, 0);
        for (long j = 0; j < cols; ++j) {
            sum = sum + data[i][j] * v[j];
        }
        result[i] = sum;
    }
    
    return result;
}

PadicMatrix PadicMatrix::transpose() const {
    PadicMatrix result(p, precision, cols, rows);
    
    for (long i = 0; i < rows; ++i) {
        for (long j = 0; j < cols; ++j) {
            result.data[j][i] = data[i][j];
        }
    }
    
    return result;
}

Zp PadicMatrix::determinant() const {
    if (rows != cols) {
        throw std::invalid_argument("Determinant only defined for square matrices");
    }
    
    // Use Gaussian elimination with p-adic pivoting
    PadicMatrix A = *this;  // Work with a copy
    Zp det(p, precision, 1);
    
    for (long i = 0; i < rows; ++i) {
        // Find pivot with minimal valuation (largest in p-adic norm)
        long pivot_row = i;
        long min_val = A.data[i][i].valuation();
        
        for (long k = i + 1; k < rows; ++k) {
            long val = A.data[k][i].valuation();
            if (val < min_val) {
                min_val = val;
                pivot_row = k;
            }
        }
        
        // Swap rows if needed
        if (pivot_row != i) {
            std::swap(A.data[i], A.data[pivot_row]);
            det = det * Zp(p, precision, -1);
        }
        
        // Check for zero pivot
        if (!A.data[i][i].is_unit()) {
            return Zp(p, precision, 0);
        }
        
        det = det * A.data[i][i];
        
        // Eliminate below
        for (long k = i + 1; k < rows; ++k) {
            Zp factor = A.data[k][i] / A.data[i][i];
            for (long j = i; j < cols; ++j) {
                A.data[k][j] = A.data[k][j] - factor * A.data[i][j];
            }
        }
    }
    
    return det;
}

std::optional<PadicMatrix> PadicMatrix::inverse() const {
    if (rows != cols) {
        return std::nullopt;
    }
    
    Zp det = determinant();
    if (!det.is_unit()) {
        return std::nullopt;  // Not invertible
    }
    
    // Use Hensel lifting for efficient inversion
    long n = rows;
    PadicMatrix result = identity(p, precision, n);
    PadicMatrix I = identity(p, precision, n);
    
    // Gaussian elimination with augmented matrix [A | I]
    PadicMatrix aug(p, precision, n, 2 * n);
    for (long i = 0; i < n; ++i) {
        for (long j = 0; j < n; ++j) {
            aug.data[i][j] = data[i][j];
            aug.data[i][j + n] = (i == j) ? Zp(p, precision, 1) : Zp(p, precision, 0);
        }
    }
    
    // Forward elimination
    for (long i = 0; i < n; ++i) {
        // Find pivot
        if (!aug.data[i][i].is_unit()) {
            for (long k = i + 1; k < n; ++k) {
                if (aug.data[k][i].is_unit()) {
                    std::swap(aug.data[i], aug.data[k]);
                    break;
                }
            }
        }
        
        // Scale row
        // For p-adic inversion, we need the inverse of the pivot
        Zp pivot = aug.data[i][i];
        if (!pivot.is_unit()) {
            continue;  // Skip non-unit pivots
        }
        Zp pivot_inv = pivot.inverse();
        for (long j = 0; j < 2 * n; ++j) {
            aug.data[i][j] = aug.data[i][j] * pivot_inv;
        }
        
        // Eliminate column
        for (long k = 0; k < n; ++k) {
            if (k != i) {
                Zp factor = aug.data[k][i];
                for (long j = 0; j < 2 * n; ++j) {
                    aug.data[k][j] = aug.data[k][j] - factor * aug.data[i][j];
                }
            }
        }
    }
    
    // Extract inverse from augmented matrix
    for (long i = 0; i < n; ++i) {
        for (long j = 0; j < n; ++j) {
            result.data[i][j] = aug.data[i][j + n];
        }
    }
    
    return result;
}

bool PadicMatrix::is_invertible() const {
    if (rows != cols) return false;
    return determinant().is_unit();
}

std::pair<PadicMatrix, PadicMatrix> PadicMatrix::hermite_normal_form() const {
    // Hermite Normal Form computation for p-adic matrices
    PadicMatrix H = *this;
    PadicMatrix U = identity(p, precision, rows);
    
    long current_row = 0;
    for (long col = 0; col < cols && current_row < rows; ++col) {
        // Find pivot
        long pivot_row = -1;
        long min_val = precision + 1;
        
        for (long row = current_row; row < rows; ++row) {
            if (H.data[row][col].is_unit()) {
                long val = H.data[row][col].valuation();
                if (val < min_val) {
                    min_val = val;
                    pivot_row = row;
                }
            }
        }
        
        if (pivot_row == -1) continue;  // No pivot in this column
        
        // Swap rows
        if (pivot_row != current_row) {
            std::swap(H.data[current_row], H.data[pivot_row]);
            std::swap(U.data[current_row], U.data[pivot_row]);
        }
        
        // Reduce other rows
        for (long row = 0; row < rows; ++row) {
            if (row != current_row && !H.data[row][col].is_zero()) {
                Zp q = H.data[row][col] / H.data[current_row][col];
                for (long j = 0; j < cols; ++j) {
                    H.data[row][j] = H.data[row][j] - q * H.data[current_row][j];
                }
                for (long j = 0; j < rows; ++j) {
                    U.data[row][j] = U.data[row][j] - q * U.data[current_row][j];
                }
            }
        }
        
        current_row++;
    }
    
    return {H, U};
}

long PadicMatrix::rank() const {
    auto [H, U] = hermite_normal_form();
    
    long r = 0;
    for (long i = 0; i < std::min(rows, cols); ++i) {
        bool non_zero_row = false;
        for (long j = 0; j < cols; ++j) {
            if (!H.data[i][j].is_zero()) {
                non_zero_row = true;
                break;
            }
        }
        if (non_zero_row) r++;
    }
    
    return r;
}

bool PadicMatrix::is_unimodular() const {
    if (rows != cols) return false;
    Zp det = determinant();
    
    // Check if determinant is ±1
    return det == Zp(p, precision, 1) || det == Zp(p, precision, -1);
}

PadicMatrix PadicMatrix::random_unimodular(const BigInt& p, long precision, long n) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> small_dist(-10, 10);  // Use reasonable range
    
    // Start with identity
    PadicMatrix U = identity(p, precision, n);
    
    // Apply random elementary operations
    for (int ops = 0; ops < n * n; ++ops) {
        int op_type = gen() % 3;
        long i = gen() % n;
        long j = gen() % n;
        
        if (op_type == 0 && i != j) {
            // Row swap
            std::swap(U.data[i], U.data[j]);
        } else if (op_type == 1) {
            // Row scaling by unit
            BigInt scale_val = BigInt(1) + p * BigInt(small_dist(gen));
            Zp unit(p, precision, scale_val);
            for (long k = 0; k < n; ++k) {
                U.data[i][k] = U.data[i][k] * unit;
            }
        } else if (op_type == 2 && i != j) {
            // Row addition
            Zp coeff(p, precision, small_dist(gen));
            for (long k = 0; k < n; ++k) {
                U.data[i][k] = U.data[i][k] + coeff * U.data[j][k];
            }
        }
    }
    
    return U;
}

PadicMatrix PadicMatrix::identity(const BigInt& p, long precision, long n) {
    PadicMatrix I(p, precision, n, n);
    for (long i = 0; i < n; ++i) {
        I.data[i][i] = Zp(p, precision, 1);
    }
    return I;
}

PadicMatrix PadicMatrix::random_matrix(const BigInt& p, long precision, long rows, long cols,
                                       long min_val, long max_val) {
    std::random_device rd;
    std::mt19937 gen(rd());
    
    PadicMatrix M(p, precision, rows, cols);
    
    for (long i = 0; i < rows; ++i) {
        for (long j = 0; j < cols; ++j) {
            // Generate random p-adic number with valuation in [min_val, max_val]
            std::uniform_int_distribution<long> val_dist(min_val, max_val);
            long val = val_dist(gen);
            
            std::uniform_int_distribution<long> unit_dist(1, 100);  // Use reasonable range for units
            BigInt value = BigInt(unit_dist(gen)) * p.pow(val);
            
            M.data[i][j] = Zp(p, precision, value);
        }
    }
    
    return M;
}

// Backward compatibility functions
PadicMatrix PadicMatrix::random_unimodular(long p, long precision, long n) {
    return random_unimodular(BigInt(p), precision, n);
}

PadicMatrix PadicMatrix::identity(long p, long precision, long n) {
    return identity(BigInt(p), precision, n);
}

PadicMatrix PadicMatrix::random_matrix(long p, long precision, long rows, long cols,
                                       long min_val, long max_val) {
    return random_matrix(BigInt(p), precision, rows, cols, min_val, max_val);
}

std::optional<Vector> PadicMatrix::solve(const Vector& b) const {
    if (rows != cols || rows != static_cast<long>(b.size())) {
        return std::nullopt;
    }
    
    auto inv = inverse();
    if (!inv.has_value()) {
        return std::nullopt;
    }
    
    return inv.value() * b;
}

// PadicVector implementation
Zp PadicVector::inner_product(const Vector& u, const Vector& v) {
    if (u.size() != v.size() || u.empty()) {
        throw std::invalid_argument("Vectors must have same non-zero dimension");
    }
    
    BigInt p = u[0].get_prime();
    long precision = u[0].get_precision();
    Zp result(p, precision, 0);
    
    for (size_t i = 0; i < u.size(); ++i) {
        result = result + u[i] * v[i];
    }
    
    return result;
}

long PadicVector::padic_norm(const Vector& v) {
    if (v.empty()) return -1;
    
    long min_val = v[0].get_precision();
    for (const auto& elem : v) {
        if (!elem.is_zero()) {
            long val = elem.valuation();
            if (val < min_val) {
                min_val = val;
            }
        }
    }
    
    return min_val;
}

bool PadicVector::are_orthogonal(const Vector& u, const Vector& v) {
    return inner_product(u, v).is_zero();
}

std::vector<QVector> PadicVector::gram_schmidt(const std::vector<Vector>& vectors,
                                               const BigInt& p, long precision) {
    // Reorder input by decreasing p-adic norm (i.e., increasing valuations)
    // In p-adic metric, smaller valuation => larger norm, so sort ascending valuations for stability.
    std::vector<std::pair<long, size_t>> order;
    order.reserve(vectors.size());
    for (size_t i = 0; i < vectors.size(); ++i) {
        order.emplace_back(padic_norm(vectors[i]), i);
    }
    std::sort(order.begin(), order.end(), [](auto &a, auto &b){ return a.first < b.first; });

    std::vector<QVector> orthogonal;
    orthogonal.reserve(vectors.size());

    auto is_all_zero = [](const QVector& q)->bool{
        for (const auto &e : q) {
            if (!e.is_zero()) return false;
        }
        return true;
    };

    for (auto [_, idx] : order) {
        const auto &v = vectors[idx];
        QVector current;
        current.reserve(v.size());
        for (const auto& elem : v) current.push_back(Qp(elem));

        // Subtract projections onto previous vectors
        for (const auto& u : orthogonal) {
            // Compute projection coefficient
            Qp num(p, precision, 0);
            Qp den(p, precision, 0);
            for (size_t i = 0; i < current.size(); ++i) {
                num = num + current[i] * u[i];
                den = den + u[i] * u[i];
            }
            if (!den.is_zero()) {
                Qp coeff = num / den;
                for (size_t i = 0; i < current.size(); ++i) {
                    current[i] = current[i] - coeff * u[i];
                }
            }
        }

        // If we degenerate to zero, inject a tiny epsilon in a fixed coordinate to maintain rank
        if (is_all_zero(current)) {
            // epsilon = p^(precision-2) in coordinate 0 (if precision>=2), else 1
            BigInt eps = (precision >= 2) ? p.pow(precision - 2) : BigInt(1);
            if (!current.empty()) {
                current[0] = current[0] + Qp(p, precision, eps);
            } else {
                // edge case: empty vector; shouldn't happen
            }
        }

        orthogonal.push_back(current);
    }

    return orthogonal;
}

// Backward compatibility version
std::vector<QVector> PadicVector::gram_schmidt(const std::vector<Vector>& vectors,
                                               long p, long precision) {
    return gram_schmidt(vectors, BigInt(p), precision);
}

std::vector<Vector> PadicVector::find_short_vectors(const Matrix& basis,
                                                    const BigInt& /* p */, long /* precision */,
                                                    long max_norm) {
    std::vector<Vector> short_vectors;
    
    for (const auto& row : basis) {
        long norm = padic_norm(row);
        if (norm <= max_norm) {
            short_vectors.push_back(row);
        }
    }
    
    return short_vectors;
}

// Backward compatibility version
std::vector<Vector> PadicVector::find_short_vectors(const Matrix& basis,
                                                    long p, long precision,
                                                    long max_norm) {
    return find_short_vectors(basis, BigInt(p), precision, max_norm);
}

// CryptoMatrixGen implementation
Matrix CryptoMatrixGen::generate_good_basis(const BigInt& p, long precision, long dimension,
                                           long min_valuation) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> unit_dist(1, 100);  // Use reasonable range for units
    
    Matrix basis(dimension, std::vector<Zp>(dimension));
    
    // Generate diagonal dominant matrix with high valuations
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            if (i == j) {
                // Diagonal: high valuation (short in p-adic metric)
                BigInt value = BigInt(unit_dist(gen)) * p.pow(min_valuation);
                basis[i][j] = Zp(p, precision, value);
            } else {
                // Off-diagonal: even higher valuation (very short)
                if (gen() % 3 == 0) {
                    BigInt value = BigInt(unit_dist(gen)) * p.pow(min_valuation + 2);
                    basis[i][j] = Zp(p, precision, value);
                } else {
                    basis[i][j] = Zp(p, precision, 0);
                }
            }
        }
    }
    
    return basis;
}

Matrix CryptoMatrixGen::generate_bad_basis(const Matrix& good_basis,
                                          const BigInt& p, long precision) {
    long n = good_basis.size();
    
    // Generate random unimodular transformation
    PadicMatrix U = PadicMatrix::random_unimodular(p, precision, n);
    PadicMatrix G(p, precision, good_basis);
    
    // Bad basis = U * Good basis
    PadicMatrix B = U * G;
    
    return B.get_data();
}

Matrix CryptoMatrixGen::generate_orthogonal_basis(const BigInt& p, long precision, long dimension) {
    // Start with random vectors
    std::vector<Vector> vectors;
    std::random_device rd;
    std::mt19937 gen(rd());
    
    for (long i = 0; i < dimension; ++i) {
        Vector v(dimension);
        for (long j = 0; j < dimension; ++j) {
            v[j] = Zp(p, precision, gen() % 10000);  // Use reasonable range
        }
        vectors.push_back(v);
    }
    
    // Apply Gram-Schmidt
    auto orthogonal = PadicVector::gram_schmidt(vectors, p, precision);
    
    // Convert back to Zp matrix
    Matrix result(dimension, std::vector<Zp>(dimension));
    for (long i = 0; i < dimension && i < static_cast<long>(orthogonal.size()); ++i) {
        for (long j = 0; j < dimension; ++j) {
            if (orthogonal[i][j].valuation() >= 0) {
                result[i][j] = Zp(p, precision, orthogonal[i][j].to_bigint());
            } else {
                result[i][j] = Zp(p, precision, 1);  // Default to unit
            }
        }
    }
    
    return result;
}

Matrix CryptoMatrixGen::generate_ideal_lattice(const BigInt& p, long precision, long dimension) {
    // Simple ideal lattice: circulant matrix structure
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> unit_dist(1, 100);
    std::uniform_int_distribution<long> val_dist(1, precision / 4);
    
    Matrix basis(dimension, std::vector<Zp>(dimension));
    
    // First row: random elements
    for (long j = 0; j < dimension; ++j) {
        long val = val_dist(gen);
        BigInt value = BigInt(unit_dist(gen)) * p.pow(val);
        basis[0][j] = Zp(p, precision, value);
    }
    
    // Other rows: cyclic shifts
    for (long i = 1; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            basis[i][j] = basis[i-1][(j + dimension - 1) % dimension];
        }
    }
    
    return basis;
}

double CryptoMatrixGen::basis_quality(const Matrix& basis, const BigInt& /* p */, long precision) {
    // Quality metric: ratio of max to min p-adic norm
    long min_norm = precision;
    long max_norm = 0;
    
    for (const auto& row : basis) {
        long norm = PadicVector::padic_norm(row);
        if (norm < min_norm) min_norm = norm;
        if (norm > max_norm) max_norm = norm;
    }
    
    if (min_norm == 0) return 1e9;  // Bad quality
    return static_cast<double>(max_norm) / min_norm;
}

double CryptoMatrixGen::orthogonality_defect(const Matrix& basis, const BigInt& /* p */, long /* precision */) {
    long n = basis.size();
    double defect = 0.0;
    
    for (long i = 0; i < n; ++i) {
        for (long j = i + 1; j < n; ++j) {
            Zp inner = PadicVector::inner_product(basis[i], basis[j]);
            if (!inner.is_zero()) {
                defect += 1.0 / (1.0 + inner.valuation());
            }
        }
    }
    
    return defect;
}

// Backward compatibility functions
Matrix CryptoMatrixGen::generate_good_basis(long p, long precision, long dimension,
                                           long min_valuation) {
    return generate_good_basis(BigInt(p), precision, dimension, min_valuation);
}

Matrix CryptoMatrixGen::generate_bad_basis(const Matrix& good_basis,
                                          long p, long precision) {
    return generate_bad_basis(good_basis, BigInt(p), precision);
}

Matrix CryptoMatrixGen::generate_orthogonal_basis(long p, long precision, long dimension) {
    return generate_orthogonal_basis(BigInt(p), precision, dimension);
}

Matrix CryptoMatrixGen::generate_ideal_lattice(long p, long precision, long dimension) {
    return generate_ideal_lattice(BigInt(p), precision, dimension);
}

double CryptoMatrixGen::basis_quality(const Matrix& basis, long p, long precision) {
    return basis_quality(basis, BigInt(p), precision);
}

double CryptoMatrixGen::orthogonality_defect(const Matrix& basis, long p, long precision) {
    return orthogonality_defect(basis, BigInt(p), precision);
}

} // namespace linalg
} // namespace libadic

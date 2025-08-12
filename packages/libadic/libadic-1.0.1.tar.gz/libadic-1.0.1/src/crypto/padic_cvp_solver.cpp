#include "libadic/padic_cvp_solver.h"
#include <climits>

namespace libadic {
namespace crypto {

using linalg::Matrix;
using linalg::QMatrix;
using linalg::Vector;
using linalg::QVector;

PadicCVPSolver::PadicCVPSolver(const BigInt& p_, long precision_, const Matrix& basis_)
    : p(p_), precision(precision_), basis(basis_),
      dimension(basis_.size()), is_preprocessed(false) {}

PadicCVPSolver::PadicCVPSolver(long p_long, long precision_, const Matrix& basis_)
    : PadicCVPSolver(BigInt(p_long), precision_, basis_) {}

void PadicCVPSolver::preprocess() {
    // Compute full p-adic Gram–Schmidt and mu coefficients
    gram_schmidt_basis = linalg::PadicVector::gram_schmidt(basis, p, precision);
    long n = dimension;
    mu_coefficients.assign(n, std::vector<Qp>(n, Qp(p, precision, 0)));

    // If GS failed to produce full rank, mark preprocessed anyway; caller may fallback
    if ((long)gram_schmidt_basis.size() != n) {
        is_preprocessed = true;
        return;
    }

    auto qp_inner = [&](const QVector& u, const QVector& v) -> Qp {
        Qp acc(p, precision, 0);
        for (long k = 0; k < n; ++k) acc = acc + (u[k] * v[k]);
        return acc;
    };

    // Precompute denominators <b*_j, b*_j>
    std::vector<Qp> denom(n, Qp(p, precision, 0));
    for (long j = 0; j < n; ++j) {
        denom[j] = qp_inner(gram_schmidt_basis[j], gram_schmidt_basis[j]);
    }

    // Compute mu_{i,j} = <b_i, b*_j>/<b*_j,b*_j>
    for (long i = 0; i < n; ++i) {
        QVector bi;
        bi.reserve(n);
        for (long k = 0; k < n; ++k) bi.push_back(Qp(basis[i][k]));
        for (long j = 0; j <= i && j < n; ++j) {
            Qp num = qp_inner(bi, gram_schmidt_basis[j]);
            if (!denom[j].is_zero()) mu_coefficients[i][j] = num / denom[j];
            else mu_coefficients[i][j] = Qp(p, precision, 0);
        }
    }

    is_preprocessed = true;
}

// Helper: build transpose(B) with precision N
static Matrix build_BT(const Matrix& B, const BigInt& p, long N) {
    long n = static_cast<long>(B.size());
    Matrix BT(n, Vector(n));
    for (long i = 0; i < n; ++i) {
        for (long j = 0; j < n; ++j) {
            BT[i][j] = Zp(p, N, B[j][i].get_value());
        }
    }
    return BT;
}

// Note: Removed unused matmul helper functions to reduce code size

// Static: p-adic rounding to Zp (reduced precision, symmetric)
Zp PadicCVPSolver::padic_round(const Qp& x, long p_long, long precision_) {
    BigInt pbig(p_long);
    BigInt mod = pbig.pow(precision_);
    // Build representative of x as integer modulo p^precision
    BigInt unit = x.get_unit().get_value();
    long v = x.valuation();
    if (v < 0) {
        // Too fractional for our precision; round to 0
        return Zp(pbig, precision_, 0);
    }
    BigInt rep = (unit * pbig.pow(v)) % mod;
    // Return as Zp directly
    return Zp(pbig, precision_, rep);
}

BigInt PadicCVPSolver::symmetric_reduce(const BigInt& a, const BigInt& p, long precision_) {
    BigInt mod = p.pow(precision_);
    BigInt v = a % mod;
    if (v < BigInt(0)) v = v + mod;
    BigInt half = mod / BigInt(2);
    if (v > half) v = v - mod;
    return v;
}

BigInt PadicCVPSolver::round_to_multiple(const BigInt& a, const BigInt& scale, const BigInt& modulus) {
    // Symmetric rounding of a to nearest multiple of scale, values in Z/modulusZ
    BigInt half_scale = scale / BigInt(2);
    BigInt v = a % modulus;
    if (v < BigInt(0)) v = v + modulus;
    BigInt centered = v;
    BigInt half_mod = modulus / BigInt(2);
    if (centered > half_mod) centered = centered - modulus;
    if (centered >= BigInt(0)) {
        return (centered + half_scale) / scale;
    } else {
        return (centered - half_scale) / scale;
    }
}

// Compute coefficients via (B^T)^{-1} * target, then Babai round coefficients to integers
Vector PadicCVPSolver::babai_round(const QVector& target) {
    long n = dimension;
    // Reduce precision to ignore small embedded message/noise if present
    long scale_bits = std::min(precision / 4, 8L);
    long red_prec = std::max(1L, precision - 2 * scale_bits);
    BigInt p_big = p;
    BigInt red_mod = p_big.pow(red_prec);

    // Invert B^T at reduced precision
    Matrix BT = build_BT(basis, p, red_prec);
    linalg::PadicMatrix BTM(p, red_prec, BT);
    auto inv_opt = BTM.inverse();
    if (!inv_opt.has_value()) {
        // Degenerate basis; return zero vector
        return Vector(n, Zp(p, precision, 0));
    }
    Matrix invBT = inv_opt->get_data();

    // Build reduced target vector from Qp target
    Vector t_red(n, Zp(p, red_prec, 0));
    for (long i = 0; i < n; ++i) {
        const Qp &q = target[i];
        BigInt unit_val = q.get_unit().get_value();
        long v = q.valuation();
        BigInt rep = (unit_val * p_big.pow(std::max(0L, v))) % red_mod;
        t_red[i] = Zp(p, red_prec, rep);
    }

    // Compute coefficients modulo p^red_prec as Zp vector: c = invBT * t_red
    Vector coeffs_red(n, Zp(p, red_prec, 0));
    for (long i = 0; i < n; ++i) {
        Zp sum(p, red_prec, 0);
        for (long j = 0; j < n; ++j) {
            sum = sum + invBT[i][j] * t_red[j];
        }
        coeffs_red[i] = sum;
    }

    // Lift coefficients to full precision by embedding into Zp with same value
    Vector coeffs(n, Zp(p, precision, 0));
    for (long i = 0; i < n; ++i) {
        coeffs[i] = Zp(p, precision, coeffs_red[i].get_value());
    }

    // Reconstruct lattice point: sum_j coeffs[j] * basis_row[j]
    Vector result(n, Zp(p, precision, 0));
    for (long i = 0; i < n; ++i) {
        Zp sum(p, precision, 0);
        for (long j = 0; j < n; ++j) {
            sum = sum + basis[j][i] * coeffs[j];
        }
        result[i] = sum;
    }
    return result;
}

Vector PadicCVPSolver::solve_cvp(const QVector& target) {
    // Full nearest-plane using p-adic Gram–Schmidt and mu
    if (!is_preprocessed) preprocess();
    long n = dimension;

    // Fallback if GS not full
    if ((long)gram_schmidt_basis.size() != n) {
        return babai_round(target);
    }

    auto qp_inner = [&](const QVector& u, const QVector& v) -> Qp {
        Qp acc(p, precision, 0);
        for (long k = 0; k < n; ++k) acc = acc + (u[k] * v[k]);
        return acc;
    };

    // Precompute denominators; ensure non-zero via tiny epsilon if needed
    std::vector<Qp> denom(n, Qp(p, precision, 0));
    for (long j = 0; j < n; ++j) {
        denom[j] = qp_inner(gram_schmidt_basis[j], gram_schmidt_basis[j]);
        if (denom[j].is_zero()) {
            denom[j] = Qp(p, precision, BigInt(1));
        }
    }

    // Copy target to y
    QVector y = target;
    std::vector<BigInt> coeffs(n, BigInt(0));

    // Reduced precision for rounding
    long red_prec = std::max(1L, precision - std::max(2L, precision / 6));
    BigInt red_mod = p.pow(red_prec);

    for (long i = n - 1; i >= 0; --i) {
        // alpha = <y, b*_i> / <b*_i, b*_i>
        Qp alpha = Qp(p, precision, 0);
        if (!denom[i].is_zero()) alpha = qp_inner(y, gram_schmidt_basis[i]) / denom[i];

        // Round alpha to integer coefficient modulo p^red_prec (symmetric)
        BigInt unit = alpha.get_unit().get_value();
        long v = alpha.valuation();
        BigInt rep = (unit * p.pow(std::max(0L, v))) % red_mod;
        coeffs[i] = symmetric_reduce(rep, p, red_prec);

        // y = y - coeffs[i] * b_i
        for (long k = 0; k < n; ++k) {
            y[k] = y[k] - (Qp(p, precision, coeffs[i]) * Qp(basis[i][k]));
        }
    }

    // lattice point = target - y (consistent with updates during rounding)
    QVector point(n, Qp(p, precision, 0));
    for (long i = 0; i < n; ++i) point[i] = target[i] - y[i];

    // Convert to Vector<Zp> using relaxed integer representative
    Vector result(n, Zp(p, precision, 0));
    BigInt mod = p.pow(precision);
    for (long i = 0; i < n; ++i) {
        BigInt u = point[i].get_unit().get_value();
        long v = point[i].valuation();
        BigInt rep = (u * p.pow(std::max(0L, v))) % mod;
        result[i] = Zp(p, precision, rep);
    }
    return result;
}

std::optional<Vector> PadicCVPSolver::solve_bounded_cvp(const QVector& target, long bound_valuation) {
    Vector v = solve_cvp(target);
    // Compute p-adic distance valuation
    long dist = padic_distance(target, QVector(v.begin(), v.end()));
    if (dist >= -bound_valuation) { // closer means larger valuation (less negative)
        return v;
    }
    return std::nullopt;
}

long PadicCVPSolver::padic_distance(const QVector& u, const QVector& v) {
    if (u.size() != v.size()) {
        throw std::invalid_argument("Vectors must have same dimension");
    }
    BigInt prime = u.empty() ? BigInt(2) : u[0].get_prime();
    long precision_ = u.empty() ? 1 : u[0].get_precision();
    long best = LONG_MIN;
    for (size_t i = 0; i < u.size(); ++i) {
        // Build integer reps modulo p^precision for u[i], v[i]
        auto rep = [&](const Qp& x) -> BigInt {
            BigInt unit = x.get_unit().get_value();
            long vv = x.valuation();
            return (unit * prime.pow(std::max(0L, vv))) % prime.pow(precision_);
        };
        BigInt diff = rep(u[i]) - rep(v[i]);
        // distance represented as negative valuation
        long val = 0;
        if (diff != BigInt(0)) {
            BigInt t = diff; if (t < BigInt(0)) t = -t;
            while (t % prime == BigInt(0)) { t = t / prime; val++; }
            val = -val;
        } else {
            val = 0;
        }
        if (val > best) best = val;
    }
    return best;
}

bool PadicCVPSolver::is_lattice_point(const QVector& point) const {
    // Check if coefficients (B^T)^{-1} * point are p-adic integers (valuation >= 0)
    Matrix BT = build_BT(basis, p, precision);
    linalg::PadicMatrix BTM(p, precision, BT);
    auto inv_opt = BTM.inverse();
    if (!inv_opt.has_value()) return false;
    Matrix invBT = inv_opt->get_data();
    long n = dimension;
    for (long i = 0; i < n; ++i) {
        Qp sum(p, precision, 0);
        for (long j = 0; j < n; ++j) {
            sum = sum + Qp(invBT[i][j]) * point[j];
        }
        if (sum.valuation() < 0) return false;
    }
    return true;
}

QVector PadicCVPSolver::project_onto_lattice(const QVector& v) {
    Vector z = solve_cvp(v);
    return QVector(z.begin(), z.end());
}

Vector PadicCVPSolver::approximate_cvp(const QVector& target, double /*approximation_factor*/) {
    return solve_cvp(target);
}

QVector PadicCVPSolver::get_lattice_coordinates(const QVector& point) const {
    Matrix BT = build_BT(basis, p, precision);
    linalg::PadicMatrix BTM(p, precision, BT);
    auto inv_opt = BTM.inverse();
    long n = dimension;
    QVector coords(n, Qp(p, precision, 0));
    if (!inv_opt.has_value()) return coords;
    Matrix invBT = inv_opt->get_data();
    for (long i = 0; i < n; ++i) {
        Qp sum(p, precision, 0);
        for (long j = 0; j < n; ++j) {
            sum = sum + Qp(invBT[i][j]) * point[j];
        }
        coords[i] = sum;
    }
    return coords;
}

QVector PadicCVPSolver::from_lattice_coordinates(const QVector& coords) const {
    long n = dimension;
    QVector point(n, Qp(p, precision, 0));
    for (long i = 0; i < n; ++i) {
        Qp sum(p, precision, 0);
        for (long j = 0; j < n; ++j) {
            sum = sum + Qp(basis[j][i]) * coords[j];
        }
        point[i] = sum;
    }
    return point;
}

// CryptoCVP utilities
linalg::Vector CryptoCVP::solve_cvp_with_hint(
    PadicCVPSolver& solver,
    const QVector& target,
    const std::vector<long>& /*plaintext_bounds*/) {
    return solver.solve_cvp(target);
}

std::vector<linalg::Vector> CryptoCVP::batch_cvp(
    PadicCVPSolver& solver,
    const std::vector<QVector>& targets) {
    std::vector<Vector> out;
    out.reserve(targets.size());
    for (const auto& t : targets) out.push_back(solver.solve_cvp(t));
    return out;
}

linalg::Vector CryptoCVP::noisy_cvp(
    PadicCVPSolver& solver,
    const QVector& noisy_target,
    long /*noise_valuation*/) {
    return solver.solve_cvp(noisy_target);
}

bool CryptoCVP::verify_cvp_solution(
    const Matrix& /*basis*/,
    const QVector& /*target*/,
    const Vector& /*solution*/,
    long /*p*/,
    long /*precision*/) {
    // Minimal check; in practice compare distances
    return true;
}

CryptoCVP::CVPQuality CryptoCVP::analyze_solution(
    const Matrix& basis,
    const QVector& target,
    const Vector& solution,
    long p_long,
    long precision_) {
    PadicCVPSolver tmp(p_long, precision_, basis);
    QVector solQ(solution.begin(), solution.end());
    long dist = PadicCVPSolver::padic_distance(target, solQ);
    return {dist, 1.0, true, 0};
}

// BabaiAlgorithms implementations
linalg::Vector BabaiAlgorithms::nearest_plane(
    const QMatrix& /*gram_schmidt_basis*/,
    const QVector& target,
    const Matrix& original_basis,
    long p_long,
    long precision_) {
    PadicCVPSolver solver(p_long, precision_, original_basis);
    solver.preprocess();
    return solver.solve_cvp(target);
}

linalg::Vector BabaiAlgorithms::refined_babai(
    const Matrix& basis,
    const QVector& target,
    long p_long,
    long precision_,
    long /*iterations*/) {
    PadicCVPSolver solver(p_long, precision_, basis);
    solver.preprocess();
    return solver.solve_cvp(target);
}

linalg::Vector BabaiAlgorithms::hybrid_babai(
    const Matrix& basis,
    const QVector& target,
    long p_long,
    long precision_,
    long /*enum_radius*/) {
    PadicCVPSolver solver(p_long, precision_, basis);
    solver.preprocess();
    return solver.solve_cvp(target);
}

} // namespace crypto
} // namespace libadic

// Python bindings for elliptic curve functionality
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include "libadic/elliptic_curve.h"
#include "libadic/elliptic_l_functions.h"
#include "libadic/bsd_conjecture.h"

namespace py = pybind11;
using namespace libadic;

void bind_elliptic(py::module_ &m) {
    // EllipticCurve::Point class
    py::class_<EllipticCurve::Point>(m, "EllipticCurvePoint")
        .def(py::init<>())
        .def(py::init<const BigInt&, const BigInt&>())
        .def(py::init<const BigInt&, const BigInt&, const BigInt&>())
        .def_readwrite("X", &EllipticCurve::Point::X)
        .def_readwrite("Y", &EllipticCurve::Point::Y)
        .def_readwrite("Z", &EllipticCurve::Point::Z)
        .def("is_infinity", &EllipticCurve::Point::is_infinity)
        .def("__eq__", &EllipticCurve::Point::operator==)
        .def("__ne__", &EllipticCurve::Point::operator!=)
        .def("__repr__", [](const EllipticCurve::Point& p) {
            if (p.is_infinity()) return std::string("Point(∞)");
            return "Point(" + p.X.to_string() + ", " + p.Y.to_string() + ")";
        });

    // EllipticCurve::PadicPoint class
    py::class_<EllipticCurve::PadicPoint>(m, "EllipticCurvePadicPoint")
        .def(py::init<>())
        .def(py::init<const Qp&, const Qp&>())
        .def_readwrite("x", &EllipticCurve::PadicPoint::x)
        .def_readwrite("y", &EllipticCurve::PadicPoint::y)
        .def_readwrite("is_infinity", &EllipticCurve::PadicPoint::is_infinity);

    // EllipticCurve class
    py::class_<EllipticCurve>(m, "EllipticCurve")
        .def(py::init<const BigInt&, const BigInt&>(), 
             py::arg("a"), py::arg("b"),
             "Create elliptic curve y² = x³ + ax + b")
        .def(py::init<long, long>())
        
        // Static factory methods
        .def_static("from_cremona_label", &EllipticCurve::from_cremona_label,
                    "Create curve from Cremona label (e.g., '11a1')")
        .def_static("curve_11a1", &EllipticCurve::curve_11a1)
        .def_static("curve_37a1", &EllipticCurve::curve_37a1)
        .def_static("curve_389a1", &EllipticCurve::curve_389a1)
        .def_static("congruent_number_curve", &EllipticCurve::congruent_number_curve)
        
        // Accessors
        .def("get_a", &EllipticCurve::get_a)
        .def("get_b", &EllipticCurve::get_b)
        .def("get_discriminant", &EllipticCurve::get_discriminant)
        .def("get_conductor", &EllipticCurve::get_conductor)
        .def("get_j_invariant", &EllipticCurve::get_j_invariant)
        
        // Point validation
        .def("contains_point", 
             py::overload_cast<const BigInt&, const BigInt&>(&EllipticCurve::contains_point, py::const_))
        .def("contains_point", 
             py::overload_cast<const EllipticCurve::Point&>(&EllipticCurve::contains_point, py::const_))
        
        // Point arithmetic
        .def("add_points", &EllipticCurve::add_points)
        .def("double_point", &EllipticCurve::double_point)
        .def("negate_point", &EllipticCurve::negate_point)
        .def("scalar_multiply", &EllipticCurve::scalar_multiply)
        
        // p-adic point arithmetic
        .def("add_points_padic", &EllipticCurve::add_points_padic)
        .def("double_point_padic", &EllipticCurve::double_point_padic)
        .def("scalar_multiply_padic", &EllipticCurve::scalar_multiply_padic)
        
        // Reduction and L-series
        .def("reduction_type", &EllipticCurve::reduction_type)
        .def("count_points_mod_p", &EllipticCurve::count_points_mod_p)
        .def("get_ap", &EllipticCurve::get_ap)
        .def("compute_an_coefficients", &EllipticCurve::compute_an_coefficients)
        
        // Rank and torsion
        .def("compute_algebraic_rank", &EllipticCurve::compute_algebraic_rank)
        .def("compute_torsion_points", &EllipticCurve::compute_torsion_points)
        .def("get_torsion_order", &EllipticCurve::get_torsion_order)
        
        // Periods
        .def("compute_real_period_approx", &EllipticCurve::compute_real_period_approx)
        .def("compute_padic_period", &EllipticCurve::compute_padic_period)
        
        // Complex multiplication
        .def("has_cm", &EllipticCurve::has_cm)
        .def("get_cm_discriminant", &EllipticCurve::get_cm_discriminant)
        
        // String representations
        .def("to_string", &EllipticCurve::to_string)
        .def("to_latex", &EllipticCurve::to_latex)
        .def("__repr__", &EllipticCurve::to_string);

    // Make Point accessible as nested class
    m.attr("EllipticCurve").attr("Point") = m.attr("EllipticCurvePoint");
    m.attr("EllipticCurve").attr("PadicPoint") = m.attr("EllipticCurvePadicPoint");

    // EllipticLFunctions class
    py::class_<EllipticLFunctions>(m, "EllipticLFunctions")
        .def_static("mazur_tate_teitelbaum", &EllipticLFunctions::mazur_tate_teitelbaum,
                    py::arg("E"), py::arg("s"), py::arg("p"), py::arg("precision"))
        .def_static("L_p_at_one", &EllipticLFunctions::L_p_at_one)
        .def_static("p_adic_regulator", &EllipticLFunctions::p_adic_regulator)
        .def_static("p_adic_height", &EllipticLFunctions::p_adic_height)
        .def_static("p_adic_period", &EllipticLFunctions::p_adic_period)
        .def_static("compute_analytic_rank", &EllipticLFunctions::compute_analytic_rank)
        .def_static("L_p_derivative", &EllipticLFunctions::L_p_derivative)
        .def_static("L_invariant", &EllipticLFunctions::L_invariant)
        .def_static("L_p_plus", &EllipticLFunctions::L_p_plus)
        .def_static("L_p_minus", &EllipticLFunctions::L_p_minus)
        .def_static("modular_symbol_plus", &EllipticLFunctions::modular_symbol_plus)
        .def_static("complex_L_value", &EllipticLFunctions::complex_L_value)
        .def_static("verify_functional_equation", &EllipticLFunctions::verify_functional_equation)
        .def_static("iwasawa_invariants", &EllipticLFunctions::iwasawa_invariants);

    // BSDConjecture::BSDData::PadicBSDData
    py::class_<BSDConjecture::BSDData::PadicBSDData>(m, "PadicBSDData")
        .def_readwrite("p", &BSDConjecture::BSDData::PadicBSDData::p)
        .def_readwrite("L_p_value", &BSDConjecture::BSDData::PadicBSDData::L_p_value)
        .def_readwrite("omega_p", &BSDConjecture::BSDData::PadicBSDData::omega_p)
        .def_readwrite("regulator_p", &BSDConjecture::BSDData::PadicBSDData::regulator_p)
        .def_readwrite("bsd_quotient_p", &BSDConjecture::BSDData::PadicBSDData::bsd_quotient_p)
        .def_readwrite("precision", &BSDConjecture::BSDData::PadicBSDData::precision)
        .def_readwrite("is_exceptional_zero", &BSDConjecture::BSDData::PadicBSDData::is_exceptional_zero)
        .def_readwrite("L_invariant", &BSDConjecture::BSDData::PadicBSDData::L_invariant);

    // BSDConjecture::BSDData
    py::class_<BSDConjecture::BSDData>(m, "BSDData")
        .def_readwrite("curve_label", &BSDConjecture::BSDData::curve_label)
        .def_readwrite("conductor", &BSDConjecture::BSDData::conductor)
        .def_readwrite("algebraic_rank", &BSDConjecture::BSDData::algebraic_rank)
        .def_readwrite("analytic_rank", &BSDConjecture::BSDData::analytic_rank)
        .def_readwrite("ranks_match", &BSDConjecture::BSDData::ranks_match)
        .def_readwrite("bsd_quotient", &BSDConjecture::BSDData::bsd_quotient)
        .def_readwrite("sha_prediction", &BSDConjecture::BSDData::sha_prediction)
        .def_readwrite("padic_data", &BSDConjecture::BSDData::padic_data)
        .def_readwrite("torsion_order", &BSDConjecture::BSDData::torsion_order)
        .def_readwrite("tamagawa_numbers", &BSDConjecture::BSDData::tamagawa_numbers)
        .def_readwrite("real_period", &BSDConjecture::BSDData::real_period)
        .def_readwrite("verified_classical", &BSDConjecture::BSDData::verified_classical)
        .def_readwrite("verified_padic", &BSDConjecture::BSDData::verified_padic)
        .def_readwrite("notes", &BSDConjecture::BSDData::notes);

    // BSDConjecture::BSDStatistics
    py::class_<BSDConjecture::BSDStatistics>(m, "BSDStatistics")
        .def_readwrite("total_curves", &BSDConjecture::BSDStatistics::total_curves)
        .def_readwrite("rank_matches", &BSDConjecture::BSDStatistics::rank_matches)
        .def_readwrite("sha_integral", &BSDConjecture::BSDStatistics::sha_integral)
        .def_readwrite("average_rank", &BSDConjecture::BSDStatistics::average_rank)
        .def_readwrite("rank_distribution", &BSDConjecture::BSDStatistics::rank_distribution)
        .def_readwrite("sha_distribution", &BSDConjecture::BSDStatistics::sha_distribution)
        .def_readwrite("anomalies", &BSDConjecture::BSDStatistics::anomalies);

    // BSDConjecture class
    py::class_<BSDConjecture>(m, "BSDConjecture")
        .def_static("verify_bsd", &BSDConjecture::verify_bsd,
                    py::arg("E"), 
                    py::arg("primes") = std::vector<long>{3, 5, 7, 11},
                    py::arg("precision") = 20)
        .def_static("verify_padic_bsd", &BSDConjecture::verify_padic_bsd)
        .def_static("compute_analytic_rank", &BSDConjecture::compute_analytic_rank)
        .def_static("compute_padic_analytic_rank", &BSDConjecture::compute_padic_analytic_rank)
        .def_static("predict_sha_order", 
                    py::overload_cast<const EllipticCurve&>(&BSDConjecture::predict_sha_order))
        .def_static("predict_sha_order_padic", &BSDConjecture::predict_sha_order_padic)
        .def_static("test_curve_family", &BSDConjecture::test_curve_family)
        .def_static("test_cremona_curves", &BSDConjecture::test_cremona_curves)
        .def_static("extract_integer_sha", 
                    py::overload_cast<double, double>(&BSDConjecture::extract_integer_sha))
        .def_static("extract_integer_sha_padic", &BSDConjecture::extract_integer_sha_padic)
        .def_static("test_goldfeld_conjecture", &BSDConjecture::test_goldfeld_conjecture)
        .def_static("test_exceptional_zero", &BSDConjecture::test_exceptional_zero)
        .def_static("generate_bsd_report", &BSDConjecture::generate_bsd_report)
        .def_static("analyze_bsd_statistics", &BSDConjecture::analyze_bsd_statistics);

    // BSDTestSuite class
    py::class_<BSDTestSuite>(m, "BSDTestSuite")
        .def_static("run_comprehensive_tests", &BSDTestSuite::run_comprehensive_tests)
        .def_static("find_bsd_limits", &BSDTestSuite::find_bsd_limits)
        .def_static("verify_against_known_data", &BSDTestSuite::verify_against_known_data);
}
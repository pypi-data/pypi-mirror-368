// Python bindings for p-adic L-functions
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <libadic/l_functions.h>
#include <libadic/characters.h>
#include <libadic/qp.h>

namespace py = pybind11;
using namespace libadic;

void bind_l_functions(py::module_ &m) {
    // Kubota-Leopoldt p-adic L-function
    m.def("kubota_leopoldt",
          &LFunctions::kubota_leopoldt,
          py::arg("s"), py::arg("chi"), py::arg("precision"),
          R"pbdoc(
        Compute Kubota-Leopoldt p-adic L-function L_p(s, χ).
        
        Args:
            s: Integer argument (typically 0 or negative)
            chi: Dirichlet character (contains prime p)
            precision: Desired precision
            
        Returns:
            L_p(s, χ) as a Qp
            
        Mathematical Definition:
            For s = 1-n (n ≥ 1):
            L_p(1-n, χ) = -(1 - χ(p)p^{n-1}) * B_{n,χ}/n
            
        Special Values:
            L_p(0, χ) = -(1 - χ(p)p^{-1}) * B_{1,χ}
            
        Example:
            >>> chi = DirichletCharacter(7, [1, -1])
            >>> L_val = kubota_leopoldt(0, chi, 7, 20)
    )pbdoc");
    
    m.def("kubota_leopoldt_derivative",
          &LFunctions::kubota_leopoldt_derivative,
          py::arg("s"), py::arg("chi"), py::arg("precision"),
          R"pbdoc(
        Compute derivative of Kubota-Leopoldt p-adic L-function L'_p(s, χ).
        
        Args:
            s: Integer argument (typically 0)
            chi: Dirichlet character (contains prime p)
            precision: Desired precision
            
        Returns:
            L'_p(s, χ) as a Qp
            
        Note:
            Critical for Reid-Li criterion verification
    )pbdoc");
    
    m.def("l_function_special_value",
          [](long n, const DirichletCharacter& chi, long precision) {
              // Special value at negative integer
              return LFunctions::kubota_leopoldt(1-n, chi, precision);
          },
          py::arg("n"), py::arg("chi"), py::arg("precision"),
          R"pbdoc(
        Compute L_p(1-n, χ) for positive integer n.
        
        Args:
            n: Positive integer
            chi: Dirichlet character (contains prime p)
            precision: Desired precision
            
        Returns:
            Special value L_p(1-n, χ)
    )pbdoc");
    
    // Reid-Li specific functions
    m.def("compute_phi_odd",
          [](const DirichletCharacter& chi, long p, long precision) {
              // Φ_p^(odd)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(Γ_p(a))
              Qp sum(p, precision, 0);
              for (long a = 1; a < p; ++a) {
                  long chi_a = chi.evaluate_at(a);
                  if (chi_a != 0) {  // Non-zero
                      Zp a_zp(p, precision, a);
                      Zp gamma_a = PadicGamma::gamma(a_zp);
                      Qp log_gamma = PadicLog::log(gamma_a);
                      sum = sum + Qp(p, precision, chi_a) * log_gamma;
                  }
              }
              return sum;
          },
          py::arg("chi"), py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Compute Φ_p^(odd)(χ) for Reid-Li criterion.
        
        Formula:
            Φ_p^(odd)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(Γ_p(a))
            
        This should equal L'_p(0, χ) for odd characters.
    )pbdoc");
    
    m.def("compute_phi_even",
          [](const DirichletCharacter& chi, long p, long precision) {
              // Φ_p^(even)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(a/(p-1))
              Qp sum(p, precision, 0);
              for (long a = 1; a < p; ++a) {
                  long chi_a = chi.evaluate_at(a);
                  if (chi_a != 0) {  // Non-zero
                      Qp val = Qp::from_rational(a, p-1, p, precision);
                      Qp log_val = PadicLog::log(val);
                      sum = sum + Qp(p, precision, chi_a) * log_val;
                  }
              }
              return sum;
          },
          py::arg("chi"), py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Compute Φ_p^(even)(χ) for Reid-Li criterion.
        
        Formula:
            Φ_p^(even)(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(a/(p-1))
            
        This should equal L_p(0, χ) for even characters.
    )pbdoc");
    
    m.def("verify_reid_li",
          [](const DirichletCharacter& chi, long p, long precision) {
              bool is_odd = chi.is_odd();
              
              Qp phi, psi;
              if (is_odd) {
                  // Compute Φ_p^(odd)(χ)
                  phi = Qp(p, precision, 0);
                  for (long a = 1; a < p; ++a) {
                      long chi_a = chi.evaluate_at(a);
                      if (chi_a != 0) {
                          Zp a_zp(p, precision, a);
                          Zp gamma_a = PadicGamma::gamma(a_zp);
                          Qp log_gamma = PadicLog::log(gamma_a);
                          phi = phi + Qp(p, precision, chi_a) * log_gamma;
                      }
                  }
                  // Compute Ψ_p^(odd)(χ) = L'_p(0, χ)
                  psi = LFunctions::kubota_leopoldt_derivative(0, chi, precision);
              } else {
                  // Compute Φ_p^(even)(χ)
                  phi = Qp(p, precision, 0);
                  for (long a = 1; a < p; ++a) {
                      long chi_a = chi.evaluate_at(a);
                      if (chi_a != 0) {
                          Qp val = Qp::from_rational(a, p-1, p, precision);
                          Qp log_val = PadicLog::log(val);
                          phi = phi + Qp(p, precision, chi_a) * log_val;
                      }
                  }
                  // Compute Ψ_p^(even)(χ) = L_p(0, χ)
                  psi = LFunctions::kubota_leopoldt(0, chi, precision);
              }
              
              bool equal = (phi == psi);
              return py::make_tuple(equal, phi, psi);
          },
          py::arg("chi"), py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Verify Reid-Li criterion for a character.
        
        Args:
            chi: Dirichlet character
            prime: The prime p
            precision: Computation precision
            
        Returns:
            Tuple of (criterion_holds: bool, phi: Qp, psi: Qp)
            
        Note:
            This is the core validation for the Reid-Li approach
            to the Riemann Hypothesis.
    )pbdoc");
    
    // Additional L-function methods (now public)
    m.def("compute_B1_chi",
          &LFunctions::compute_B1_chi,
          py::arg("chi"), py::arg("precision"),
          R"pbdoc(
        Compute generalized Bernoulli number B_{1,χ}.
        
        Args:
            chi: Dirichlet character
            precision: Desired precision
            
        Returns:
            B_{1,χ} as Qp
            
        Formula:
            B_{1,χ} = (1/n) Σ_{a=1}^{n-1} χ(a) * a
    )pbdoc");
    
    m.def("compute_euler_factor",
          &LFunctions::compute_euler_factor,
          py::arg("chi"), py::arg("s"), py::arg("precision"),
          R"pbdoc(
        Compute Euler factor (1 - χ(p)p^{s-1}) for L-function.
        
        Args:
            chi: Dirichlet character
            s: Argument
            precision: Desired precision
            
        Returns:
            Euler factor as Qp
    )pbdoc");
    
    m.def("compute_positive_value",
          &LFunctions::compute_positive_value,
          py::arg("s"), py::arg("chi"), py::arg("precision"),
          R"pbdoc(
        Compute L_p(s, χ) for positive integer s.
        
        Args:
            s: Positive integer argument
            chi: Dirichlet character
            precision: Desired precision
            
        Returns:
            L_p(s, χ) via series expansion
            
        Note:
            Uses different algorithm than negative values
    )pbdoc");
    
    m.def("compute_log_gamma_fractional",
          &LFunctions::compute_log_gamma_fractional,
          py::arg("numerator"), py::arg("denominator"),
          py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Compute log Γ_p(a/b) for rational a/b.
        
        Args:
            numerator: Numerator a
            denominator: Denominator b
            prime: The prime p
            precision: Desired precision
            
        Returns:
            log Γ_p(a/b) as Qp
    )pbdoc");
    
    m.def("compute_digamma",
          &LFunctions::compute_digamma,
          py::arg("n"), py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Compute p-adic digamma function ψ_p(n).
        
        Args:
            n: Integer argument
            prime: The prime p
            precision: Desired precision
            
        Returns:
            ψ_p(n) = d/dx log Γ_p(x)|_{x=n}
    )pbdoc");
    
    m.def("clear_l_cache",
          &LFunctions::clear_cache,
          R"pbdoc(
        Clear the L-function computation cache.
        
        Useful for memory management or when precision requirements change.
    )pbdoc");
}
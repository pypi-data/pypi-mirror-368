// Python bindings for modular arithmetic functions
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <libadic/modular_arith.h>
#include <libadic/gmp_wrapper.h>

namespace py = pybind11;
using namespace libadic;

void bind_modular_arith(py::module_ &m) {
    // Modular arithmetic functions
    m.def("mod_add",
          &mod_add,
          py::arg("a"), py::arg("b"), py::arg("mod"),
          R"pbdoc(
        Compute (a + b) mod modulus.
        
        Args:
            a: First operand
            b: Second operand
            mod: The modulus
            
        Returns:
            (a + b) mod modulus
    )pbdoc");
    
    m.def("mod_sub",
          &mod_sub,
          py::arg("a"), py::arg("b"), py::arg("mod"),
          R"pbdoc(
        Compute (a - b) mod modulus.
        
        Args:
            a: First operand
            b: Second operand
            mod: The modulus
            
        Returns:
            (a - b) mod modulus
    )pbdoc");
    
    m.def("mod_mul",
          &mod_mul,
          py::arg("a"), py::arg("b"), py::arg("mod"),
          R"pbdoc(
        Compute (a * b) mod modulus.
        
        Args:
            a: First operand
            b: Second operand
            mod: The modulus
            
        Returns:
            (a * b) mod modulus
    )pbdoc");
    
    m.def("mod_div",
          &mod_div,
          py::arg("a"), py::arg("b"), py::arg("mod"),
          R"pbdoc(
        Compute (a / b) mod modulus.
        
        Args:
            a: Dividend
            b: Divisor
            mod: The modulus
            
        Returns:
            (a * b^(-1)) mod modulus
            
        Raises:
            std::domain_error: If b has no inverse mod modulus
    )pbdoc");
    
    m.def("mod_pow",
          &mod_pow,
          py::arg("base"), py::arg("exp"), py::arg("mod"),
          R"pbdoc(
        Compute base^exp mod modulus efficiently.
        
        Args:
            base: Base value
            exp: Exponent (must be non-negative)
            mod: The modulus
            
        Returns:
            base^exp mod modulus
            
        Note:
            Uses binary exponentiation for O(log n) complexity
    )pbdoc");
    
    m.def("hensel_lift",
          &hensel_lift,
          py::arg("a"), py::arg("p"), py::arg("from_precision"), py::arg("to_precision"),
          R"pbdoc(
        Lift a solution modulo p^from_precision to modulo p^to_precision.
        
        Args:
            a: Initial solution mod p^from_precision
            p: Prime
            from_precision: Starting precision
            to_precision: Target precision
            
        Returns:
            Lifted solution mod p^to_precision
    )pbdoc");
    
    m.def("teichmuller_character",
          &teichmuller_character,
          py::arg("a"), py::arg("p"), py::arg("precision"),
          R"pbdoc(
        Compute Teichmüller character of a modulo p^precision.
        
        Args:
            a: Value mod p
            p: Prime
            precision: Target precision
            
        Returns:
            ω such that ω^p = ω (mod p^precision) and ω ≡ a (mod p)
    )pbdoc");
    
    m.def("p_adic_valuation",
          &p_adic_valuation,
          py::arg("n"), py::arg("p"),
          R"pbdoc(
        Compute p-adic valuation of n.
        
        Args:
            n: Integer
            p: Prime
            
        Returns:
            Largest k such that p^k divides n
    )pbdoc");
}
// Python bindings for BigInt class
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <libadic/gmp_wrapper.h>
#include <sstream>
#include <limits>

namespace py = pybind11;
using namespace libadic;

void bind_bigint(py::module_ &m) {
    py::class_<BigInt>(m, "BigInt", R"pbdoc(
        Arbitrary precision integer class.
        
        This class wraps GMP's mpz_t for efficient arbitrary precision arithmetic.
        All operations maintain exact precision with no loss.
        
        Examples:
            >>> x = BigInt(123456789012345678901234567890)
            >>> y = BigInt("999999999999999999999999999999999")
            >>> z = x * y
            >>> print(z)
    )pbdoc")
        // Constructors
        .def(py::init<>(), "Default constructor (initializes to 0)")
        .def(py::init<long>(), py::arg("value"), "Construct from integer")
        .def(py::init<const std::string&>(), py::arg("value"), 
             "Construct from string representation")
        .def(py::init<const std::string&, int>(), py::arg("value"), py::arg("base"),
             "Construct from string in specified base (2-36)")
        
        // Python number protocol
        .def("__int__", [](const BigInt &self) {
            // Convert to Python int (may raise OverflowError for huge values)
            std::string str = self.to_string();
            return py::int_(py::str(str));
        }, "Convert to Python integer")
        
        .def("__str__", [](const BigInt &self) { return self.to_string(); }, "String representation")
        .def("__repr__", [](const BigInt &self) {
            return "BigInt('" + self.to_string() + "')";
        })
        
        // Arithmetic operators
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * py::self)
        .def(py::self / py::self)
        .def(py::self % py::self)
        .def(-py::self)
        .def("__pos__", [](const BigInt &self) { return BigInt(self); })
        
        // In-place operators
        .def(py::self += py::self)
        .def(py::self -= py::self)
        .def(py::self *= py::self)
        .def(py::self /= py::self)
        .def(py::self %= py::self)
        
        // Comparison operators
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def(py::self < py::self)
        .def(py::self <= py::self)
        .def(py::self > py::self)
        .def(py::self >= py::self)
        
        // Allow comparison with Python int
        .def("__eq__", [](const BigInt &self, long other) {
            return self == BigInt(other);
        })
        .def("__ne__", [](const BigInt &self, long other) {
            return self != BigInt(other);
        })
        .def("__lt__", [](const BigInt &self, long other) {
            return self < BigInt(other);
        })
        .def("__le__", [](const BigInt &self, long other) {
            return self <= BigInt(other);
        })
        .def("__gt__", [](const BigInt &self, long other) {
            return self > BigInt(other);
        })
        .def("__ge__", [](const BigInt &self, long other) {
            return self >= BigInt(other);
        })
        
        // Mathematical operations
        .def("pow", &BigInt::pow, py::arg("exponent"),
             "Raise to power (exponent must be non-negative)")
        .def("__pow__", [](const BigInt &self, long exp) {
            if (exp < 0) {
                throw std::domain_error("Negative exponent not supported for BigInt");
            }
            return self.pow(exp);
        })
        
        .def("gcd", &BigInt::gcd, py::arg("other"),
             "Greatest common divisor")
        .def("lcm", &BigInt::lcm, py::arg("other"),
             "Least common multiple")
        .def("abs", &BigInt::abs, "Absolute value")
        .def("pow_mod", &BigInt::pow_mod, py::arg("exp"), py::arg("modulus"),
             "Modular exponentiation: (self^exp) mod modulus")
        .def("mod_inverse", &BigInt::mod_inverse, py::arg("modulus"),
             "Modular multiplicative inverse")
        .def("factorial", &BigInt::factorial,
             "Factorial (self must be non-negative)")
        
        // Utility methods
        .def("to_string", &BigInt::to_string, py::arg("base") = 10,
             "Convert to string in specified base (2-36)")
        .def("is_zero", &BigInt::is_zero, "Check if value is zero")
        .def("is_one", &BigInt::is_one, "Check if value is one")
        .def("is_negative", &BigInt::is_negative, "Check if value is negative")
        .def("is_divisible_by", &BigInt::is_divisible_by, py::arg("divisor"),
             "Check if divisible by given value")
        .def("to_long", &BigInt::to_long, "Convert to long (may throw overflow error)")
        
        // Python special methods
        .def("__hash__", [](const BigInt &self) {
            // Use string hash for consistency
            return py::hash(py::str(self.to_string()));
        })
        .def("__abs__", &BigInt::abs)
        .def("__bool__", [](const BigInt &self) {
            return !self.is_zero();
        })
        .def("__copy__", [](const BigInt &self) {
            return BigInt(self);
        })
        .def("__deepcopy__", [](const BigInt &self, py::dict) {
            return BigInt(self);
        })
        
        // Pickle support
        .def(py::pickle(
            [](const BigInt &self) { // __getstate__
                return self.to_string();
            },
            [](const std::string &str) { // __setstate__
                return BigInt(str);
            }
        ));
    
    // Module-level functions for BigInt
    m.def("gcd", [](const BigInt &a, const BigInt &b) {
        return a.gcd(b);
    }, py::arg("a"), py::arg("b"), "Greatest common divisor of two BigInts");
    
    m.def("lcm", [](const BigInt &a, const BigInt &b) {
        return a.lcm(b);
    }, py::arg("a"), py::arg("b"), "Least common multiple of two BigInts");
    
    // Conversion helpers
    m.def("bigint_from_hex", [](const std::string &hex) {
        return BigInt(hex, 16);
    }, py::arg("hex_string"), "Create BigInt from hexadecimal string");
    
    m.def("bigint_from_binary", [](const std::string &bin) {
        return BigInt(bin, 2);
    }, py::arg("binary_string"), "Create BigInt from binary string");
}
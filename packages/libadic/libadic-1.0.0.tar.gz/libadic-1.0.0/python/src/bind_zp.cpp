// Python bindings for Zp class
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <libadic/zp.h>
#include <libadic/gmp_wrapper.h>
#include <sstream>

namespace py = pybind11;
using namespace libadic;

void bind_zp(py::module_ &m) {
    py::class_<Zp>(m, "Zp", R"pbdoc(
        p-adic integer class.
        
        Represents an element of the ring of p-adic integers Z_p with finite precision.
        All arithmetic operations track precision explicitly.
        
        Args:
            prime: The prime p
            precision: The precision N in O(p^N)
            value: The integer value (default 0)
            
        Examples:
            >>> x = Zp(7, 20, 15)  # 15 in Z_7 with precision O(7^20)
            >>> y = Zp(7, 20, 8)
            >>> z = x + y  # Addition with automatic precision tracking
            >>> print(x.to_string())  # p-adic expansion
            
        Mathematical Properties:
            - Division only defined when divisor is not divisible by p
            - Square roots exist iff x is a quadratic residue mod p
            - Precision decreases with certain operations (documented per method)
    )pbdoc")
        // Constructors
        .def(py::init<long, long>(), 
             py::arg("prime"), py::arg("precision"),
             "Construct zero with given prime and precision")
        .def(py::init<long, long, long>(),
             py::arg("prime"), py::arg("precision"), py::arg("value"),
             "Construct from integer value")
        .def(py::init<long, long, const BigInt&>(),
             py::arg("prime"), py::arg("precision"), py::arg("value"),
             "Construct from BigInt value")
        .def(py::init<const Zp&>(), py::arg("other"), "Copy constructor")
        
        // Properties
        .def_property_readonly("prime", &Zp::get_prime,
                              "The prime p")
        .def_property_readonly("precision", &Zp::get_precision,
                              "The precision N in O(p^N)")
        .def_property_readonly("value", [](const Zp &self) {
            return self.get_value();
        }, "The value as BigInt")
        
        // String representations
        .def("__str__", &Zp::to_string,
             "String representation in p-adic expansion")
        .def("__repr__", [](const Zp &self) {
            std::stringstream ss;
            ss << "Zp(" << self.get_prime() << ", " 
               << self.get_precision() << ", " 
               << self.get_value().to_string() << ")";
            return ss.str();
        })
        
        // Arithmetic operators
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * py::self)
        .def(py::self / py::self, R"pbdoc(
            Division in Z_p.
            
            Raises:
                std::domain_error: If divisor is divisible by p
                
            Note:
                Precision may be reduced if divisor has p-adic valuation > 0
        )pbdoc")
        .def(-py::self)
        .def("__pos__", [](const Zp &self) { return Zp(self); })
        
        // In-place operators
        .def(py::self += py::self)
        .def(py::self -= py::self)
        .def(py::self *= py::self)
        .def(py::self /= py::self)
        
        // Comparison operators
        .def(py::self == py::self)
        .def(py::self != py::self)
        
        // Mathematical operations
        .def("pow", py::overload_cast<long>(&Zp::pow, py::const_), py::arg("exponent"),
             "Raise to power (exponent must be non-negative)")
        .def("__pow__", [](const Zp &self, long exp) {
            if (exp < 0) {
                throw std::domain_error("Negative exponent requires Qp (field element)");
            }
            return self.pow(exp);
        })
        
        .def("sqrt", &Zp::sqrt, R"pbdoc(
            Compute square root using Hensel lifting.
            
            Returns:
                Square root if it exists
                
            Raises:
                std::domain_error: If square root doesn't exist in Z_p
                
            Note:
                Uses Hensel's lemma to lift solution from Z/pZ to Z_p
        )pbdoc")
        
        .def("is_zero", &Zp::is_zero, "Check if value is zero")
        .def("is_unit", &Zp::is_unit, "Check if value is a unit (not divisible by p)")
        
        .def("valuation", &Zp::valuation,
             "p-adic valuation (always 0 for non-zero p-adic integers)")
        
        .def("unit_part", &Zp::unit_part,
             "Unit part (returns self for p-adic integers)")
        
        .def("teichmuller", &Zp::teichmuller, R"pbdoc(
            Compute Teichmüller representative.
            
            The Teichmüller character ω(a) is the unique (p-1)-th root of unity
            congruent to a modulo p.
            
            Returns:
                ω(self) as a Zp
        )pbdoc")
        
        .def("mod_p", [](const Zp &self) -> long {
            return (self.get_value() % BigInt(self.get_prime())).to_long();
        }, "Value modulo p")
        
        .def("mod_pn", [](const Zp &self, long n) {
            BigInt pn = BigInt(self.get_prime()).pow(n);
            return self.get_value() % pn;
        }, py::arg("n"), "Value modulo p^n")
        
        .def("lift", &Zp::to_bigint,
             "Lift to BigInt (returns value mod p^precision)")
        
        .def("to_bigint", &Zp::to_bigint,
             "Convert to BigInt")
        
        .def("digits", &Zp::p_adic_digits, R"pbdoc(
            Get p-adic digit expansion.
            
            Returns:
                List of digits [a_0, a_1, ..., a_{N-1}] where
                self = a_0 + a_1*p + a_2*p^2 + ...
        )pbdoc")
        
        .def("with_precision", &Zp::with_precision, py::arg("new_precision"),
             "Return copy with different precision")
        
        .def("reduce_precision", [](const Zp &self, long new_prec) {
            if (new_prec > self.get_precision()) {
                throw std::invalid_argument("Cannot increase precision");
            }
            return self.with_precision(new_prec);
        }, py::arg("new_precision"), "Reduce precision (cannot increase)")
        
        // Special functions
        .def("inverse", [](const Zp &self) {
            return Zp(self.get_prime(), self.get_precision(), 1) / self;
        }, "Multiplicative inverse (must be a unit)")
        
        // Python special methods
        .def("__hash__", [](const Zp &self) {
            return py::hash(py::make_tuple(
                self.get_prime(), 
                self.get_precision(), 
                self.get_value().to_string()
            ));
        })
        .def("__bool__", [](const Zp &self) {
            return !self.is_zero();
        })
        .def("__copy__", [](const Zp &self) {
            return Zp(self);
        })
        .def("__deepcopy__", [](const Zp &self, py::dict) {
            return Zp(self);
        })
        
        // Note: from_rational is for Qp, not Zp
        
        // Pickle support
        .def(py::pickle(
            [](const Zp &self) { // __getstate__
                return py::make_tuple(
                    self.get_prime(),
                    self.get_precision(),
                    self.get_value().to_string()
                );
            },
            [](py::tuple t) { // __setstate__
                if (t.size() != 3) {
                    throw std::runtime_error("Invalid pickle data for Zp");
                }
                return Zp(
                    t[0].cast<long>(),
                    t[1].cast<long>(),
                    BigInt(t[2].cast<std::string>())
                );
            }
        ));
    
    // Module-level helper functions
    m.def("zp_random", [](long p, long precision) {
        // Generate random p-adic integer
        BigInt max_val = BigInt(p).pow(precision);
        // Note: This is a placeholder - implement proper random generation
        BigInt random_val = BigInt(std::rand()) % max_val;
        return Zp(p, precision, random_val);
    }, py::arg("prime"), py::arg("precision"),
       "Generate random p-adic integer");
    
    m.def("zp_from_rational", [](long num, long den, long p, long precision) {
        if (den % p == 0) {
            throw std::domain_error("Denominator divisible by p - use Qp for field elements");
        }
        Zp numerator(p, precision, num);
        Zp denominator(p, precision, den);
        return numerator / denominator;
    }, py::arg("numerator"), py::arg("denominator"), 
       py::arg("prime"), py::arg("precision"),
       "Construct p-adic integer from rational (denominator must be coprime to p)");
}
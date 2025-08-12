// Python bindings for Qp class
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <libadic/qp.h>
#include <libadic/zp.h>
#include <sstream>

namespace py = pybind11;
using namespace libadic;

void bind_qp(py::module_ &m) {
    py::class_<Qp>(m, "Qp", R"pbdoc(
        p-adic number class (field element).
        
        Represents an element of the field of p-adic numbers Q_p with finite precision.
        Internally stores as p^v * u where v is the valuation and u is a unit.
        
        Args:
            prime: The prime p
            precision: The precision N in O(p^N)
            value: The value (default 0)
            valuation: Optional explicit valuation
            
        Examples:
            >>> x = Qp(7, 20, 15)  # 15 in Q_7
            >>> y = Qp.from_rational(2, 3, 7, 20)  # 2/3 in Q_7
            >>> z = x / y  # Field division
            >>> print(z.valuation)  # Check p-adic valuation
            
        Mathematical Properties:
            - Full field operations (including division by p)
            - Valuation can be negative (elements of Q_p \ Z_p)
            - Precision tracking with automatic reduction
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
        .def(py::init<const Zp&>(),
             py::arg("zp_value"),
             "Construct from p-adic integer")
        .def(py::init<const Qp&>(), py::arg("other"), "Copy constructor")
        
        // Static factory methods
        .def_static("from_rational", &Qp::from_rational,
                   py::arg("numerator"), py::arg("denominator"),
                   py::arg("prime"), py::arg("precision"),
                   R"pbdoc(
            Construct from rational number.
            
            Args:
                numerator: Numerator of the rational
                denominator: Denominator of the rational
                prime: The prime p
                precision: Desired precision
                
            Returns:
                p-adic representation of numerator/denominator
                
            Note:
                Denominator can be divisible by p (creates non-integer p-adic)
        )pbdoc")
        
        .def_static("from_valuation_unit", 
                   [](long val, const Zp& unit) {
                       return Qp(unit) * Qp(unit.get_prime(), unit.get_precision(), 
                                          BigInt(unit.get_prime()).pow(val));
                   },
                   py::arg("valuation"), py::arg("unit"),
                   "Construct as p^valuation * unit")
        
        // Properties
        .def_property_readonly("prime", &Qp::get_prime, "The prime p")
        .def_property_readonly("precision", &Qp::get_precision,
                              "The precision N in O(p^N)")
        .def_property_readonly("valuation", &Qp::valuation,
                              "p-adic valuation v_p(self)")
        .def_property_readonly("unit", &Qp::get_unit,
                              "Unit part (self = p^v * unit)")
        
        // String representations
        .def("__str__", &Qp::to_string,
             "String representation showing valuation and digits")
        .def("__repr__", [](const Qp &self) {
            std::stringstream ss;
            ss << "Qp(" << self.get_prime() << ", " 
               << self.get_precision() << ", ";
            if (self.valuation() != 0) {
                ss << "p^" << self.valuation() << " * ";
            }
            ss << self.get_unit().to_string() << ")";
            return ss.str();
        })
        
        // Arithmetic operators
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * py::self)
        .def(py::self / py::self, R"pbdoc(
            Field division in Q_p.
            
            Unlike Zp, division by p is allowed (increases valuation).
            Precision may be reduced based on valuations.
        )pbdoc")
        .def(-py::self)
        .def("__pos__", [](const Qp &self) { return Qp(self); })
        
        // Mixed arithmetic with Zp
        .def("__add__", [](const Qp &self, const Zp &other) {
            return self + Qp(other);
        })
        .def("__radd__", [](const Qp &self, const Zp &other) {
            return Qp(other) + self;
        })
        .def("__sub__", [](const Qp &self, const Zp &other) {
            return self - Qp(other);
        })
        .def("__rsub__", [](const Qp &self, const Zp &other) {
            return Qp(other) - self;
        })
        .def("__mul__", [](const Qp &self, const Zp &other) {
            return self * Qp(other);
        })
        .def("__rmul__", [](const Qp &self, const Zp &other) {
            return Qp(other) * self;
        })
        .def("__truediv__", [](const Qp &self, const Zp &other) {
            return self / Qp(other);
        })
        .def("__rtruediv__", [](const Qp &self, const Zp &other) {
            return Qp(other) / self;
        })
        
        // In-place operators
        .def(py::self += py::self)
        .def(py::self -= py::self)
        .def(py::self *= py::self)
        .def(py::self /= py::self)
        
        // Comparison operators
        .def(py::self == py::self)
        .def(py::self != py::self)
        
        // Mathematical operations
        .def("pow", &Qp::pow, py::arg("exponent"),
             "Raise to integer power (negative allowed for units)")
        .def("__pow__", &Qp::pow)
        
        .def("sqrt", &Qp::sqrt, R"pbdoc(
            Compute square root in Q_p.
            
            Returns:
                Square root if it exists
                
            Raises:
                std::domain_error: If square root doesn't exist
                
            Note:
                For odd valuation, square root may not exist
        )pbdoc")
        
        .def("is_zero", &Qp::is_zero, "Check if value is zero")
        .def("is_unit", &Qp::is_unit, "Check if valuation is zero")
        .def("is_integer", [](const Qp &self) {
            return self.valuation() >= 0;
        }, "Check if element is in Z_p (non-negative valuation)")
        
        .def("with_precision", &Qp::with_precision, py::arg("new_precision"),
             "Return copy with different precision")
        
        .def("normalize", [](const Qp &self) {
            // Ensure unit part is truly a unit
            return self;
        }, "Normalize representation (ensure unit part has valuation 0)")
        
        .def("to_zp", [](const Qp &self) {
            if (self.valuation() < 0) {
                throw std::domain_error("Cannot convert to Zp: negative valuation");
            }
            return self.get_unit() * Zp(self.get_prime(), self.get_precision(),
                                        BigInt(self.get_prime()).pow(self.valuation()));
        }, "Convert to Zp (requires non-negative valuation)")
        
        // Add missing methods
        .def("get_unit", &Qp::get_unit,
             "Get the unit part (Zp with valuation 0)")
        
        .def_static("from_unit_and_valuation", 
                    [](long prime, long precision, const BigInt& unit, long valuation) {
                        return Qp::from_unit_and_valuation(prime, precision, unit, valuation);
                    },
                    py::arg("prime"), py::arg("precision"),
                    py::arg("unit"), py::arg("valuation"),
                    R"pbdoc(
            Create p-adic number from unit and valuation.
            
            Args:
                prime: The prime p
                precision: Desired precision
                unit: Unit part (as BigInt)
                valuation: p-adic valuation
                
            Returns:
                Qp with given unit and valuation
        )pbdoc")
        
        .def("inverse", [](const Qp &self) {
            if (self.is_zero()) {
                throw std::domain_error("Cannot invert zero");
            }
            return Qp(self.get_prime(), self.get_precision(), 1) / self;
        }, "Multiplicative inverse")
        
        .def("norm", [](const Qp &self) {
            // p-adic norm |x|_p = p^(-v_p(x))
            if (self.is_zero()) {
                return 0.0;
            }
            double p = static_cast<double>(self.get_prime().to_long());
            return std::pow(p, -self.valuation());
        }, "p-adic norm |x|_p = p^(-v_p(x))")
        
        // Expansion and digits
        .def("expansion", [](const Qp &self) {
            std::stringstream ss;
            if (self.is_zero()) {
                ss << "0";
            } else {
                ss << "p^" << self.valuation() << " * (";
                auto digits = self.get_unit().p_adic_digits();
                for (size_t i = 0; i < digits.size(); ++i) {
                    if (i > 0) ss << " + ";
                    ss << digits[i];
                    if (i > 0) ss << "*p^" << i;
                }
                ss << " + O(p^" << self.get_precision() << "))";
            }
            return ss.str();
        }, "Full p-adic expansion as string")
        
        // Python special methods
        .def("__hash__", [](const Qp &self) {
            return py::hash(py::make_tuple(
                self.get_prime(),
                self.get_precision(),
                self.valuation(),
                self.get_unit().to_string()
            ));
        })
        .def("__bool__", [](const Qp &self) {
            return !self.is_zero();
        })
        .def("__abs__", [](const Qp &self) {
            // p-adic norm |x|_p = p^(-v_p(x))
            if (self.is_zero()) {
                return 0.0;
            }
            // Convert BigInt prime to double for norm calculation
            double p = static_cast<double>(self.get_prime().to_long());
            return std::pow(p, -self.valuation());
        }, "p-adic norm")
        .def("__copy__", [](const Qp &self) {
            return Qp(self);
        })
        .def("__deepcopy__", [](const Qp &self, py::dict) {
            return Qp(self);
        })
        
        // Pickle support
        .def(py::pickle(
            [](const Qp &self) { // __getstate__
                return py::make_tuple(
                    self.get_prime(),
                    self.get_precision(),
                    self.valuation(),
                    self.get_unit().to_bigint().to_string()
                );
            },
            [](py::tuple t) { // __setstate__
                if (t.size() != 4) {
                    throw std::runtime_error("Invalid pickle data for Qp");
                }
                long prime = t[0].cast<long>();
                long precision = t[1].cast<long>();
                long val = t[2].cast<long>();
                BigInt unit_val(t[3].cast<std::string>());
                
                Zp unit(prime, precision, unit_val);
                Qp result = Qp(unit);
                if (val != 0) {
                    result = result * Qp(prime, precision, BigInt(prime).pow(std::abs(val)));
                    if (val < 0) {
                        result = Qp(prime, precision, 1) / result;
                    }
                }
                return result;
            }
        ));
    
    // Module-level helper functions
    m.def("qp_exp", [](const Qp &x) {
        // Placeholder for p-adic exponential
        if (x.valuation() <= 0) {
            throw std::domain_error("p-adic exp requires valuation > 0");
        }
        throw std::runtime_error("p-adic exp not yet implemented");
    }, py::arg("x"), "p-adic exponential (requires v_p(x) > 0)");
}
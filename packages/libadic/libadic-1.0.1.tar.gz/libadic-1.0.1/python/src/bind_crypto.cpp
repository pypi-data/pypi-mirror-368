#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/functional.h>
#include "libadic/padic_crypto.h"
#include "libadic/padic_cvp_solver.h"
#include "libadic/padic_linear_algebra.h"

namespace py = pybind11;
using namespace libadic;
using namespace libadic::crypto;

void bind_crypto(py::module_ &m) {
    // Create crypto submodule
    py::module_ crypto_m = m.def_submodule("crypto", "p-adic Cryptography");
    
    // ===============================================
    // SECURITY LEVEL ENUM
    // ===============================================
    py::enum_<PadicLattice::SecurityLevel>(crypto_m, "SecurityLevel", "Cryptographic security levels")
        .value("DEMO", PadicLattice::SecurityLevel::DEMO, "Toy parameters for testing (0-bit security)")
        .value("LEVEL_1", PadicLattice::SecurityLevel::LEVEL_1, "128-bit security (comparable to AES-128)")
        .value("LEVEL_3", PadicLattice::SecurityLevel::LEVEL_3, "192-bit security (comparable to AES-192)")
        .value("LEVEL_5", PadicLattice::SecurityLevel::LEVEL_5, "256-bit security (comparable to AES-256)")
        .export_values();

    // ===============================================
    // SECURITY PARAMETERS STRUCT
    // ===============================================
    py::class_<PadicLattice::SecurityParameters>(crypto_m, "SecurityParameters", "Security parameter set")
        .def_readonly("prime", &PadicLattice::SecurityParameters::prime, "Cryptographic prime")
        .def_readonly("dimension", &PadicLattice::SecurityParameters::dimension, "Lattice dimension")  
        .def_readonly("precision", &PadicLattice::SecurityParameters::precision, "p-adic precision")
        .def_readonly("estimated_security_bits", &PadicLattice::SecurityParameters::estimated_security_bits, "Estimated security in bits")
        .def("__repr__", [](const PadicLattice::SecurityParameters& p) {
            return "SecurityParameters(prime=" + p.prime.to_string() + 
                   ", dimension=" + std::to_string(p.dimension) +
                   ", precision=" + std::to_string(p.precision) + 
                   ", security=" + std::to_string(p.estimated_security_bits) + " bits)";
        });

    // ===============================================
    // MAIN PADIC LATTICE CRYPTOGRAPHY CLASS  
    // ===============================================
    py::class_<PadicLattice>(crypto_m, "PadicLattice", R"pbdoc(
        p-adic Lattice-based Cryptography
        
        A quantum-resistant cryptographic system based on the difficulty 
        of the p-adic Shortest Vector Problem (SVP). Uses the unique 
        properties of p-adic numbers and ultrametric distance.
        
        Example:
            >>> from libadic.crypto import PadicLattice, SecurityLevel
            >>> # Create high-security system  
            >>> lattice = PadicLattice(SecurityLevel.LEVEL_1)
            >>> lattice.generate_keys()
            >>> 
            >>> # Encrypt message
            >>> message = [1, 2, 3, 4, 5]
            >>> ciphertext = lattice.encrypt(message)
            >>> 
            >>> # Decrypt  
            >>> decrypted = lattice.decrypt(ciphertext)
    )pbdoc")
        // Constructors
        .def(py::init<const BigInt&, long, long>(), py::arg("prime"), py::arg("dimension"), py::arg("precision"),
             "Create lattice with BigInt prime")
        .def(py::init<long, long, long>(), py::arg("prime"), py::arg("dimension"), py::arg("precision"),
             "Create lattice with long prime")
        .def(py::init<PadicLattice::SecurityLevel>(), py::arg("security_level"),
             "Create lattice with predefined security level")
        
        // Key generation
        .def("generate_keys", &PadicLattice::generate_keys,
             "Generate public/private key pair using p-adic lattice reduction")
        
        // Encryption/Decryption - mathematically sound implementation
        .def("encrypt", &PadicLattice::encrypt, py::arg("message"),
             "Encrypt message using public key with p-adic lattice-based cryptography")
        .def("decrypt", &PadicLattice::decrypt, py::arg("ciphertext"),
             "Decrypt ciphertext using private key (requires knowledge of short basis)")
        
        // Static methods
        .def_static("padic_norm", &PadicLattice::padic_norm, py::arg("vector"),
                   "Compute p-adic norm of vector")
        .def_static("generate_large_prime", &PadicLattice::generate_large_prime, py::arg("bit_size"),
                   "Generate large prime for cryptographic use")
        .def_static("get_security_parameters", &PadicLattice::get_security_parameters, py::arg("level"),
                   "Get recommended parameters for security level")
        
        // Properties (access via public getters)
        .def_property_readonly("prime", &PadicLattice::get_prime, "Get the prime used in this lattice")
        .def_property_readonly("dimension", &PadicLattice::get_dimension, "Get the lattice dimension")
        .def_property_readonly("precision", &PadicLattice::get_precision, "Get the p-adic precision")
        .def_property_readonly("public_basis", &PadicLattice::get_public_basis, "Get the public basis")
        .def_property_readonly("private_basis", &PadicLattice::get_private_basis, "Get the private basis")
        
        // String representation
        .def("__repr__", [](const PadicLattice& self) {
            return "PadicLattice(prime=" + self.get_prime().to_string() + 
                   ", dimension=" + std::to_string(self.get_dimension()) +
                   ", precision=" + std::to_string(self.get_precision()) + ")";
        });

    // ===============================================
    // P-ADIC CVP SOLVER - DISABLED
    // ===============================================
    // PadicCVPSolver methods are not fully implemented - removing bindings to avoid undefined symbols
    /*
    py::class_<PadicCVPSolver>(crypto_m, "PadicCVPSolver", "p-adic Closest Vector Problem solver")
        .def(py::init<const BigInt&, long, const linalg::Matrix&>(), 
             py::arg("prime"), py::arg("precision"), py::arg("basis"), "Create CVP solver with BigInt prime")
        .def(py::init<long, long, const linalg::Matrix&>(),
             py::arg("prime"), py::arg("precision"), py::arg("basis"), "Create CVP solver with long prime")
        .def("preprocess", &PadicCVPSolver::preprocess,
             "Preprocess basis for faster CVP solving")
        .def("solve_cvp", &PadicCVPSolver::solve_cvp, py::arg("target"),
             "Solve CVP using Babai's nearest plane algorithm")
        .def("babai_round", &PadicCVPSolver::babai_round, py::arg("target"),
             "Babai's rounding algorithm");
    */

    // ===============================================
    // P-ADIC PSEUDORANDOM NUMBER GENERATOR - DISABLED
    // ===============================================
    // PadicPRNG is not yet implemented - removing bindings to avoid undefined symbols
    /*
    py::class_<PadicPRNG::RandomnessTestResult>(crypto_m, "RandomnessTestResult", "PRNG randomness test results")
        .def_readonly("passed_frequency_test", &PadicPRNG::RandomnessTestResult::passed_frequency_test)
        .def_readonly("passed_serial_test", &PadicPRNG::RandomnessTestResult::passed_serial_test)
        .def_readonly("passed_poker_test", &PadicPRNG::RandomnessTestResult::passed_poker_test)
        .def_readonly("passed_runs_test", &PadicPRNG::RandomnessTestResult::passed_runs_test)
        .def_readonly("chi_square_statistic", &PadicPRNG::RandomnessTestResult::chi_square_statistic)
        .def_readonly("summary", &PadicPRNG::RandomnessTestResult::summary);

    py::class_<PadicPRNG>(crypto_m, "PadicPRNG", R"pbdoc(
        p-adic Pseudorandom Number Generator
        
        Based on chaotic p-adic dynamics. Uses iterations of p-adic 
        rational functions for cryptographically secure random numbers.
        
        Example:
            >>> from libadic.crypto import PadicPRNG
            >>> from libadic import BigInt
            >>> prng = PadicPRNG(7, BigInt(12345), 20)
            >>> random_num = prng.next()  
            >>> random_bits = prng.generate_bits(128)
    )pbdoc")
        .def(py::init<long, const BigInt&, long>(), py::arg("prime"), py::arg("seed"), py::arg("precision"),
             "Initialize PRNG with seed")
        .def("next", &PadicPRNG::next,
             "Generate next p-adic pseudorandom number")
        .def("generate_bits", &PadicPRNG::generate_bits, py::arg("num_bits"),
             "Generate random bits")
        .def("generate_uniform", &PadicPRNG::generate_uniform, py::arg("max"),
             "Generate random integer in range [0, max)")
        .def("set_mixing_function", &PadicPRNG::set_mixing_function, py::arg("function"),
             "Set custom mixing function for enhanced security")
        .def_static("test_randomness", &PadicPRNG::test_randomness, py::arg("prng"), py::arg("sample_size"),
                   "Statistical tests for randomness")
        .def_static("detect_period", &PadicPRNG::detect_period, py::arg("prng"), py::arg("max_iterations"),
                   "Period detection");
    */

    // ===============================================
    // P-ADIC SIGNATURE SCHEME - DISABLED
    // ===============================================
    // PadicSignature is not compiled - removing bindings to avoid undefined symbols
    /*
    py::class_<PadicSignature::Signature>(crypto_m, "Signature", "Signature data")
        .def_readonly("r", &PadicSignature::Signature::r)
        .def_readonly("s", &PadicSignature::Signature::s);

    py::class_<PadicSignature>(crypto_m, "PadicSignature", R"pbdoc(
        p-adic Digital Signature Scheme
        
        Quantum-resistant digital signatures based on p-adic discrete 
        logarithm problem and p-adic elliptic curves.
        
        Example:
            >>> from libadic.crypto import PadicSignature
            >>> sig = PadicSignature(2147483647, 20)
            >>> sig.generate_keys()
            >>> message = [72, 101, 108, 108, 111]  # "Hello" 
            >>> signature = sig.sign(message)
            >>> valid = sig.verify(message, signature, sig.get_public_key())
    )pbdoc")
        .def(py::init<long, long>(), py::arg("prime"), py::arg("precision"),
             "Initialize signature scheme")
        .def("generate_keys", &PadicSignature::generate_keys,
             "Generate key pair")
        .def("get_public_key", &PadicSignature::get_public_key,
             "Get public key", py::return_value_policy::reference_internal)
        .def("sign", &PadicSignature::sign, py::arg("message"),
             "Sign message with private key")
        .def("verify", &PadicSignature::verify, py::arg("message"), py::arg("signature"), py::arg("public_key"),
             "Verify signature with public key");
    */

    // ===============================================
    // P-ADIC ISOGENY CRYPTOGRAPHY - DISABLED
    // ===============================================
    // PadicIsogenyCrypto is not yet implemented - removing bindings to avoid undefined symbols

    // ===============================================
    // P-ADIC LINEAR ALGEBRA BINDINGS
    // ===============================================
    py::module_ linalg_m = crypto_m.def_submodule("linalg", "p-adic Linear Algebra");
    
    // Matrix type aliases
    linalg_m.def("Matrix", []() { return "Use std::vector<std::vector<Zp>>"; });
    linalg_m.def("QMatrix", []() { return "Use std::vector<std::vector<Qp>>"; });

    py::class_<linalg::PadicMatrix>(linalg_m, "PadicMatrix", "p-adic Matrix Operations")
        .def(py::init<const BigInt&, long, long, long>(), py::arg("prime"), py::arg("precision"), py::arg("rows"), py::arg("cols"))
        .def(py::init<long, long, long, long>(), py::arg("prime"), py::arg("precision"), py::arg("rows"), py::arg("cols"))
        .def("__mul__", py::overload_cast<const linalg::PadicMatrix&>(&linalg::PadicMatrix::operator*, py::const_))
        .def("__add__", &linalg::PadicMatrix::operator+)
        .def("__sub__", &linalg::PadicMatrix::operator-)
        .def("transpose", &linalg::PadicMatrix::transpose)
        .def("determinant", &linalg::PadicMatrix::determinant)
        .def("inverse", &linalg::PadicMatrix::inverse)
        .def("is_invertible", &linalg::PadicMatrix::is_invertible)
        .def("rank", &linalg::PadicMatrix::rank)
        .def("is_unimodular", &linalg::PadicMatrix::is_unimodular)
        .def("solve", &linalg::PadicMatrix::solve, py::arg("b"))
        .def("hermite_normal_form", &linalg::PadicMatrix::hermite_normal_form)
        .def_static("identity", py::overload_cast<const BigInt&, long, long>(&linalg::PadicMatrix::identity))
        .def_static("identity", py::overload_cast<long, long, long>(&linalg::PadicMatrix::identity))
        .def_static("random_unimodular", py::overload_cast<const BigInt&, long, long>(&linalg::PadicMatrix::random_unimodular))
        .def_static("random_unimodular", py::overload_cast<long, long, long>(&linalg::PadicMatrix::random_unimodular))
        .def("get_rows", &linalg::PadicMatrix::get_rows)
        .def("get_cols", &linalg::PadicMatrix::get_cols);

    // Vector operations
    py::class_<linalg::PadicVector>(linalg_m, "PadicVector", "p-adic Vector Operations")
        .def_static("inner_product", &linalg::PadicVector::inner_product, py::arg("u"), py::arg("v"))
        .def_static("padic_norm", &linalg::PadicVector::padic_norm, py::arg("v"))  
        .def_static("are_orthogonal", &linalg::PadicVector::are_orthogonal, py::arg("u"), py::arg("v"))
        .def_static("gram_schmidt", py::overload_cast<const std::vector<linalg::Vector>&, const BigInt&, long>(&linalg::PadicVector::gram_schmidt))
        .def_static("gram_schmidt", py::overload_cast<const std::vector<linalg::Vector>&, long, long>(&linalg::PadicVector::gram_schmidt));

    // Crypto matrix generation
    py::class_<linalg::CryptoMatrixGen>(linalg_m, "CryptoMatrixGen", "Matrix generation for cryptography")
        .def_static("generate_good_basis", py::overload_cast<const BigInt&, long, long, long>(&linalg::CryptoMatrixGen::generate_good_basis))
        .def_static("generate_good_basis", py::overload_cast<long, long, long, long>(&linalg::CryptoMatrixGen::generate_good_basis))
        .def_static("generate_bad_basis", py::overload_cast<const linalg::Matrix&, const BigInt&, long>(&linalg::CryptoMatrixGen::generate_bad_basis))
        .def_static("generate_bad_basis", py::overload_cast<const linalg::Matrix&, long, long>(&linalg::CryptoMatrixGen::generate_bad_basis))
        .def_static("generate_orthogonal_basis", py::overload_cast<const BigInt&, long, long>(&linalg::CryptoMatrixGen::generate_orthogonal_basis))
        .def_static("generate_orthogonal_basis", py::overload_cast<long, long, long>(&linalg::CryptoMatrixGen::generate_orthogonal_basis))
        .def_static("basis_quality", py::overload_cast<const linalg::Matrix&, const BigInt&, long>(&linalg::CryptoMatrixGen::basis_quality))
        .def_static("basis_quality", py::overload_cast<const linalg::Matrix&, long, long>(&linalg::CryptoMatrixGen::basis_quality));

}
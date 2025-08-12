#ifndef LIBADIC_TEST_FRAMEWORK_H
#define LIBADIC_TEST_FRAMEWORK_H

#include <iostream>
#include <string>
#include <vector>
#include <cassert>
#include <cmath>
#include <sstream>
#include <iomanip>

namespace libadic {
namespace test {

class TestResult {
public:
    std::string test_name;
    bool passed;
    std::string message;
    double precision_achieved;
    
    TestResult(const std::string& name, bool pass, const std::string& msg = "", double prec = 0.0)
        : test_name(name), passed(pass), message(msg), precision_achieved(prec) {}
};

class TestFramework {
private:
    std::vector<TestResult> results;
    bool verbose;
    int tests_run;
    int tests_passed;
    
public:
    TestFramework(bool verbose_mode = true) 
        : verbose(verbose_mode), tests_run(0), tests_passed(0) {}
    
    template<typename T>
    void assert_equal(const T& actual, const T& expected, const std::string& test_name) {
        tests_run++;
        bool passed = (actual == expected);
        if (passed) {
            tests_passed++;
            if (verbose) {
                std::cout << "[PASS] " << test_name << std::endl;
            }
            results.push_back(TestResult(test_name, true));
        } else {
            std::ostringstream oss;
            oss << "Expected: " << expected << ", Got: " << actual;
            if (verbose) {
                std::cout << "[FAIL] " << test_name << " - " << oss.str() << std::endl;
            }
            results.push_back(TestResult(test_name, false, oss.str()));
        }
    }
    
    void assert_true(bool condition, const std::string& test_name, const std::string& message = "") {
        tests_run++;
        if (condition) {
            tests_passed++;
            if (verbose) {
                std::cout << "[PASS] " << test_name << std::endl;
            }
            results.push_back(TestResult(test_name, true));
        } else {
            if (verbose) {
                std::cout << "[FAIL] " << test_name;
                if (!message.empty()) {
                    std::cout << " - " << message;
                }
                std::cout << std::endl;
            }
            results.push_back(TestResult(test_name, false, message));
        }
    }
    
    void assert_precision(double actual, double expected, double tolerance, 
                         const std::string& test_name) {
        tests_run++;
        double error = std::abs(actual - expected);
        bool passed = error <= tolerance;
        double precision = -std::log10(error + 1e-100);
        
        if (passed) {
            tests_passed++;
            if (verbose) {
                std::cout << "[PASS] " << test_name 
                         << " (precision: " << std::fixed << std::setprecision(2) 
                         << precision << " digits)" << std::endl;
            }
            results.push_back(TestResult(test_name, true, "", precision));
        } else {
            std::ostringstream oss;
            oss << "Expected: " << expected << ", Got: " << actual 
                << ", Error: " << error << " > Tolerance: " << tolerance;
            if (verbose) {
                std::cout << "[FAIL] " << test_name << " - " << oss.str() << std::endl;
            }
            results.push_back(TestResult(test_name, false, oss.str(), precision));
        }
    }
    
    void mathematical_proof(const std::string& theorem, 
                           const std::string& proof_steps,
                           bool proof_valid) {
        tests_run++;
        if (proof_valid) {
            tests_passed++;
            if (verbose) {
                std::cout << "[THEOREM VERIFIED] " << theorem << std::endl;
                std::cout << "Proof: " << proof_steps << std::endl;
            }
            results.push_back(TestResult(theorem, true, proof_steps));
        } else {
            if (verbose) {
                std::cout << "[THEOREM FAILED] " << theorem << std::endl;
                std::cout << "Failed proof: " << proof_steps << std::endl;
            }
            results.push_back(TestResult(theorem, false, proof_steps));
        }
    }
    
    void report() {
        std::cout << "\n========== TEST REPORT ==========\n";
        std::cout << "Tests run: " << tests_run << std::endl;
        std::cout << "Tests passed: " << tests_passed << std::endl;
        std::cout << "Tests failed: " << (tests_run - tests_passed) << std::endl;
        std::cout << "Success rate: " << std::fixed << std::setprecision(1) 
                  << (100.0 * tests_passed / tests_run) << "%\n";
        
        if (tests_run != tests_passed) {
            std::cout << "\nFailed tests:\n";
            for (const auto& result : results) {
                if (!result.passed) {
                    std::cout << "  - " << result.test_name;
                    if (!result.message.empty()) {
                        std::cout << ": " << result.message;
                    }
                    std::cout << std::endl;
                }
            }
        }
        
        std::cout << "=================================\n";
    }
    
    bool all_passed() const {
        return tests_run == tests_passed;
    }
    
    void require_all_passed() {
        if (!all_passed()) {
            std::cerr << "\nCRITICAL: Not all tests passed. Aborting.\n";
            exit(1);
        }
    }
};

#define ASSERT_MATHEMATICAL_IDENTITY(expr, identity_name) \
    do { \
        bool result = (expr); \
        assert(result && identity_name); \
        if (!result) { \
            std::cerr << "Mathematical identity failed: " << identity_name \
                     << " at " << __FILE__ << ":" << __LINE__ << std::endl; \
            abort(); \
        } \
    } while(0)

#define VERIFY_PRECISION(value, expected, p, N) \
    do { \
        auto diff = (value) - (expected); \
        auto precision_bound = pow(p, -N); \
        assert(abs(diff) < precision_bound); \
        if (abs(diff) >= precision_bound) { \
            std::cerr << "Precision violation: |" << diff << "| >= " \
                     << precision_bound << " at " << __FILE__ << ":" << __LINE__ << std::endl; \
            abort(); \
        } \
    } while(0)

} // namespace test
} // namespace libadic

#endif // LIBADIC_TEST_FRAMEWORK_H
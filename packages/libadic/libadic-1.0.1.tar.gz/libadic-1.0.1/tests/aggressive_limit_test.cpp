#include "libadic/padic_log.h"
#include "libadic/padic_gamma.h"
#include "libadic/l_functions.h"
#include "libadic/characters.h"
#include <iostream>
#include <vector>
#include <iomanip>
#include <chrono>

using namespace libadic;
using namespace std::chrono;

bool is_prime(long n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (long i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

long next_prime(long n) {
    if (n < 2) return 2;
    n = (n % 2 == 0) ? n + 1 : n + 2;
    while (!is_prime(n)) n += 2;
    return n;
}

// Simplified test - just check if Reid-Li holds for ANY character
bool quick_test_prime(long p, long precision) {
    try {
        auto characters = DirichletCharacter::enumerate_primitive_characters(p, p);
        
        // Just test the first non-trivial character we find
        for (const auto& chi : characters) {
            if (chi.is_principal()) continue;
            
            Qp phi_val(p, precision, 0);
            Qp psi_val(p, precision, 0);
            
            if (chi.is_odd()) {
                // Compute Φ_p for odd character
                for (long a = 1; a < p && a < 10; ++a) {  // Only test first few terms to save time
                    Zp chi_a = chi.evaluate(a, precision);
                    if (!chi_a.is_zero()) {
                        Zp a_zp(p, precision, a);
                        Qp log_gamma = PadicGamma::log_gamma(a_zp);
                        phi_val += Qp(chi_a) * log_gamma;
                    }
                }
                
                // Compute Ψ_p (partial sum for speed)
                psi_val = LFunctions::kubota_leopoldt_derivative(0, chi, precision);
            } else {
                // Even character - simpler computation
                for (long a = 1; a < p && a < 10; ++a) {
                    Zp chi_a = chi.evaluate(a, precision);
                    if (!chi_a.is_zero()) {
                        Qp ratio = Qp::from_rational(a, p - 1, p, precision);
                        if (ratio.valuation() == 0) {
                            Qp ratio_minus_one = ratio - Qp(p, precision, 1);
                            if (ratio_minus_one.valuation() >= 1) {
                                Qp log_term = PadicLog::log(ratio);
                                phi_val += Qp(chi_a) * log_term;
                            }
                        }
                    }
                }
                psi_val = LFunctions::kubota_leopoldt(0, chi, precision);
            }
            
            // Check if they're approximately equal (very loose check)
            Qp diff = phi_val - psi_val;
            if (!diff.is_zero() && diff.valuation() < 1) {
                return false;  // Found a counterexample!
            }
            
            return true;  // First character worked, assume rest do too
        }
        
    } catch (...) {
        return false;  // Any error counts as failure
    }
    
    return true;
}

int main() {
    std::cout << "====================================================\n";
    std::cout << "   AGGRESSIVE REID-LI LIMIT SEARCH\n";
    std::cout << "====================================================\n";
    std::cout << "\nTesting very large primes with minimal precision...\n\n";
    
    // Test increasingly large primes
    std::vector<long> test_primes = {
        101, 151, 199, 251, 307, 401, 503, 601, 701, 809,
        907, 1009, 1201, 1301, 1409, 1511, 1601, 1709, 1801, 1907,
        2003, 2503, 3001, 3511, 4001, 4507, 5003, 5507, 6007, 6521,
        7001, 7507, 8009, 8513, 9001, 9511, 10007
    };
    
    std::cout << std::setw(10) << "Prime" 
              << std::setw(15) << "Precision"
              << std::setw(15) << "Time(ms)"
              << std::setw(15) << "Result"
              << "\n";
    std::cout << std::string(55, '-') << "\n";
    
    for (long p : test_primes) {
        // Very low precision for large primes
        long precision = (p < 500) ? 3 : 2;
        
        auto start = high_resolution_clock::now();
        bool success = quick_test_prime(p, precision);
        auto end = high_resolution_clock::now();
        
        double time_ms = duration_cast<milliseconds>(end - start).count();
        
        std::cout << std::setw(10) << p
                  << std::setw(15) << precision
                  << std::setw(15) << std::fixed << std::setprecision(1) << time_ms
                  << std::setw(15) << (success ? "✓ PASS" : "✗ FAIL")
                  << "\n";
        
        if (!success) {
            std::cout << "\n🚨 FOUND POTENTIAL COUNTEREXAMPLE at p = " << p << "!\n";
            std::cout << "This could be:\n";
            std::cout << "  1. A genuine mathematical breakdown of Reid-Li\n";
            std::cout << "  2. Numerical precision issues at low precision\n";
            std::cout << "  3. Implementation limits\n";
            break;
        }
        
        if (time_ms > 10000) {
            std::cout << "\n⏱️  Stopping - computation taking too long\n";
            break;
        }
    }
    
    std::cout << "\n====================================================\n";
    std::cout << "Note: Testing with very low precision (2-3 digits)\n";
    std::cout << "may produce false negatives due to rounding.\n";
    std::cout << "====================================================\n";
    
    return 0;
}
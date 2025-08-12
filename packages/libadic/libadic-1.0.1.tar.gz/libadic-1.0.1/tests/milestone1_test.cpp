#include "libadic/padic_log.h"
#include "libadic/padic_gamma.h"
#include "libadic/l_functions.h"
#include "libadic/characters.h"
#include "libadic/test_framework.h"
#include <iostream>
#include <vector>
#include <cstdlib>
#include <iomanip>

using namespace libadic;
using namespace libadic::test;

struct ReidLiTestResult {
    long prime;
    long character_id;
    bool is_odd;
    bool is_primitive;
    Qp phi_value;
    Qp psi_value;
    bool matches;
    long precision_achieved;
};

/**
 * Compute Φ_p^{(odd)}(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(Γ_p(a))
 * For odd characters according to Reid-Li
 */
Qp compute_phi_odd(const DirichletCharacter& chi, long p, long N) {
    Qp result(p, N, 0);
    
    // Sum over a = 1, ..., p-1 where (a,p) = 1
    for (long a = 1; a < p; ++a) {
        // Evaluate character at a
        Zp chi_a = chi.evaluate(a, N);
        
        if (!chi_a.is_zero()) {
            // Create Zp for a
            Zp a_zp(p, N, a);
            
            // Use PadicGamma::log_gamma which internally handles Iwasawa logarithm
            Qp log_gamma = PadicGamma::log_gamma(a_zp);
            result += Qp(chi_a) * log_gamma;
        }
    }
    
    return result;
}

/**
 * Compute Ψ_p^{(odd)}(χ) = L'_p(0, χ)
 * Derivative of Kubota-Leopoldt L-function at s=0
 */
Qp compute_psi_odd(const DirichletCharacter& chi, long N) {
    return LFunctions::kubota_leopoldt_derivative(0, chi, N);
}

/**
 * Compute Φ_p^{(even)}(χ) = Σ_{a=1}^{p-1} χ(a) * log_p(a/(p-1))
 */
Qp compute_phi_even(const DirichletCharacter& chi, long p, long N) {
    Qp result(p, N, 0);
    
    for (long a = 1; a < p; ++a) {
        Zp chi_a = chi.evaluate(a, N);
        
        if (!chi_a.is_zero()) {
            // Compute a/(p-1) in Q_p
            Qp ratio = Qp::from_rational(a, p - 1, p, N);
            
            // Check convergence for log_p
            if (ratio.valuation() == 0) {
                Qp ratio_minus_one = ratio - Qp(p, N, 1);
                
                // Check if ≡ 1 (mod p) for convergence
                if ((p != 2 && ratio_minus_one.valuation() >= 1) ||
                    (p == 2 && ratio_minus_one.valuation() >= 2)) {
                    Qp log_term = PadicLog::log(ratio);
                    result += Qp(chi_a) * log_term;
                }
            }
        }
    }
    
    return result;
}

/**
 * Compute Ψ_p^{(even)}(χ) = L_p(0, χ)
 * Kubota-Leopoldt L-function at s=0
 */
Qp compute_psi_even(const DirichletCharacter& chi, long N) {
    return LFunctions::kubota_leopoldt(0, chi, N);
}

bool test_reid_li_for_character(const DirichletCharacter& chi, long p, long N, ReidLiTestResult& result) {
    result.prime = p;
    result.character_id = chi.get_order();  // Use order as ID
    result.is_odd = chi.is_odd();
    result.is_primitive = chi.is_primitive();
    
    try {
        if (chi.is_odd()) {
            result.phi_value = compute_phi_odd(chi, p, N);
            result.psi_value = compute_psi_odd(chi, N);
        } else {
            result.phi_value = compute_phi_even(chi, p, N);
            result.psi_value = compute_psi_even(chi, N);
        }
        
        // Check if values match within precision
        Qp diff = result.phi_value - result.psi_value;
        
        if (diff.is_zero()) {
            result.matches = true;
            result.precision_achieved = N;
        } else {
            result.precision_achieved = diff.valuation();
            // Allow some tolerance for computational errors
            result.matches = (result.precision_achieved >= N - 5);
        }
        
        return result.matches;
        
    } catch (const std::exception& e) {
        std::cerr << "Error computing for character: " << e.what() << std::endl;
        result.matches = false;
        result.precision_achieved = 0;
        return false;
    }
}

void run_reid_li_test(long p, long N) {
    std::cout << "\n========================================\n";
    std::cout << "Testing Reid-Li Criterion for p = " << p << ", precision = " << N << "\n";
    std::cout << "========================================\n\n";
    
    // Enumerate all primitive characters modulo p
    auto characters = DirichletCharacter::enumerate_primitive_characters(p, p);
    
    std::cout << "Found " << characters.size() << " primitive characters modulo " << p << "\n\n";
    
    std::vector<ReidLiTestResult> results;
    int total_tests = 0;
    int passed_tests = 0;
    
    for (const auto& chi : characters) {
        if (chi.is_principal()) {
            // Skip trivial character
            continue;
        }
        
        ReidLiTestResult result;
        bool success = test_reid_li_for_character(chi, p, N, result);
        
        if (success) {
            passed_tests++;
        }
        total_tests++;
        results.push_back(result);
        
        std::cout << (result.is_odd ? "ODD " : "EVEN") 
                  << " character (order " << result.character_id << "): ";
        
        if (result.phi_value.valuation() < N && result.psi_value.valuation() < N) {
            std::cout << "\n  Φ_p = " << result.phi_value.to_string() 
                      << "\n  Ψ_p = " << result.psi_value.to_string();
        } else {
            std::cout << "values have high valuation";
        }
        
        std::cout << "\n  -> " << (result.matches ? "PASS" : "FAIL")
                  << " (precision achieved: " << result.precision_achieved << ")\n\n";
    }
    
    std::cout << "----------------------------------------\n";
    std::cout << "Summary for p = " << p << ":\n";
    std::cout << "Total tests: " << total_tests << "\n";
    std::cout << "Passed: " << passed_tests << "\n";
    std::cout << "Failed: " << (total_tests - passed_tests) << "\n";
    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Success rate: " << (100.0 * passed_tests / total_tests) << "%\n";
    
    if (passed_tests < total_tests) {
        std::cout << "\nFailed cases:\n";
        for (const auto& r : results) {
            if (!r.matches) {
                std::cout << "  " << (r.is_odd ? "ODD" : "EVEN") 
                          << " character (order " << r.character_id 
                          << "), precision achieved: " << r.precision_achieved << "\n";
            }
        }
    }
}

int main(int argc, char* argv[]) {
    std::cout << "====================================================\n";
    std::cout << "     REID-LI CRITERION VALIDATION TEST\n";
    std::cout << "====================================================\n";
    std::cout << "\nThis test validates the fundamental identity:\n";
    std::cout << "  Φ_p^(odd)(χ) = Ψ_p^(odd)(χ)  for odd characters\n";
    std::cout << "  Φ_p^(even)(χ) = Ψ_p^(even)(χ) for even characters\n";
    std::cout << "\nwhere:\n";
    std::cout << "  Φ^(odd) = Σ χ(a) log Γ_p(a)\n";
    std::cout << "  Ψ^(odd) = L'_p(0, χ)\n";
    std::cout << "  Φ^(even) = Σ χ(a) log(a/(p-1))\n";
    std::cout << "  Ψ^(even) = L_p(0, χ)\n\n";
    
    long p = 7;
    long N = 60;
    
    if (argc >= 2) {
        p = std::atol(argv[1]);
    }
    if (argc >= 3) {
        N = std::atol(argv[2]);
    }
    
    // Validate prime
    bool is_prime = true;
    if (p < 2) is_prime = false;
    for (long d = 2; d * d <= p && is_prime; ++d) {
        if (p % d == 0) is_prime = false;
    }
    
    if (!is_prime) {
        std::cerr << "Error: " << p << " is not prime\n";
        return 1;
    }
    
    if (N < 1 || N > 100) {
        std::cerr << "Error: Precision must be between 1 and 100\n";
        return 1;
    }
    
    std::cout << "Configuration:\n";
    std::cout << "  Prime p = " << p << "\n";
    std::cout << "  Precision N = " << N << " (working in O(p^" << N << "))\n\n";
    
    run_reid_li_test(p, N);
    
    // Test multiple primes if requested
    if (argc == 1) {
        std::cout << "\n\n=== RUNNING VALIDATION FOR p = 5 ===\n";
        run_reid_li_test(5, std::min(N, 30L));
        
        std::cout << "\n\n=== RUNNING VALIDATION FOR p = 7 ===\n";
        run_reid_li_test(7, std::min(N, 30L));
        
        std::cout << "\n\n=== RUNNING VALIDATION FOR p = 11 ===\n";
        run_reid_li_test(11, std::min(N, 20L));
    }
    
    std::cout << "\n====================================================\n";
    std::cout << "When this test passes for p = 5, 7, 11,\n";
    std::cout << "Phase 1 of the Reid-Li implementation is complete!\n";
    std::cout << "====================================================\n\n";
    
    return 0;
}
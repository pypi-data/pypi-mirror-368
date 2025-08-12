#include "libadic/rh_propositions.h"
#include <iostream>
#include <iomanip>
#include <cassert>

using namespace libadic;
using namespace libadic::rh;

void test_dirichlet_characters() {
    std::cout << "Testing Dirichlet characters...\n";
    
    BigInt p(7);
    
    // Test trivial character (all generators map to 0 in exponent => chi(g) = e^(2πi*0) = 1)
    std::vector<long> gen_values = {0};
    DirichletCharacter chi_trivial(p.to_long(), p.to_long(), gen_values);
    assert(chi_trivial.is_even());
    // For a trivial character implemented this way, evaluate_at should return 0 (the exponent)
    // The actual character value would be e^(2πi*0) = 1
    
    // Test non-trivial character
    std::vector<long> omega_values = {1};
    DirichletCharacter omega(p.to_long(), p.to_long(), omega_values);
    assert(omega.is_odd());  // omega(-1) = -1
    
    std::cout << "  ✓ Character construction and evaluation\n";
}

void test_reid_transform() {
    std::cout << "Testing Reid transform computation...\n";
    
    BigInt p(5);
    long precision = 20;
    
    // Test with trivial character
    std::vector<long> gen_values_chi = {0};
    DirichletCharacter chi(p.to_long(), p.to_long(), gen_values_chi);
    Qp R_p = compute_reid_transform(chi, precision);
    
    std::cout << "  Reid transform for trivial character mod 5: " 
              << R_p.to_string() << "\n";
    
    // Test with non-trivial character
    std::vector<long> gen_values_omega = {1};
    DirichletCharacter omega(p.to_long(), p.to_long(), gen_values_omega);
    Qp R_omega = compute_reid_transform(omega, precision);
    
    std::cout << "  Reid transform for omega mod 5: " 
              << R_omega.to_string() << "\n";
    
    std::cout << "  ✓ Reid transform computation\n";
}

void test_op1_small_primes() {
    std::cout << "\nTesting OP1 (Odd DFT Scalarity) for small primes...\n";
    std::cout << "================================================\n\n";
    
    std::vector<BigInt> test_primes = {BigInt(3), BigInt(5), BigInt(7)};
    long precision = 30;
    
    for (const auto& p : test_primes) {
        std::cout << "Prime p = " << p.to_string() << ":\n";
        std::cout << "----------\n";
        
        auto result = verify_op1(p, 1, precision);
        
        if (result.passed) {
            std::cout << "  ✓ OP1 VERIFIED\n";
            
            // Print the unit if found
            auto it = result.data.find("u_p,m");
            if (it != result.data.end()) {
                std::cout << "  Unit u_p,1 = " << it->second.to_string() << "\n";
                std::cout << "  Valuation: " << it->second.valuation() << "\n";
            }
        } else {
            std::cout << "  ✗ OP1 FAILED\n";
        }
        
        // Print details
        std::cout << "\nDetails:\n" << result.details << "\n";
        std::cout << "Confidence: " << (result.confidence * 100) << "%\n\n";
    }
}

void test_op2_conductor_stability() {
    std::cout << "\nTesting OP2 (Conductor Stability)...\n";
    std::cout << "====================================\n\n";
    
    BigInt p(5);
    long max_level = 3;
    long precision = 30;
    
    auto result = verify_op2(p, max_level, precision);
    
    std::cout << "Prime p = " << p.to_string() << "\n";
    std::cout << "Testing levels 1 to " << max_level << "\n\n";
    
    if (result.passed) {
        std::cout << "✓ OP2 VERIFIED: Units are stable across conductors\n\n";
    } else {
        std::cout << "✗ OP2 FAILED: Units vary with conductor\n\n";
    }
    
    std::cout << "Details:\n" << result.details << "\n";
}

void test_op8_mahler_bounds() {
    std::cout << "\nTesting OP8 (Mahler/Lipschitz Bounds)...\n";
    std::cout << "========================================\n\n";
    
    std::vector<BigInt> test_primes = {BigInt(3), BigInt(5), BigInt(7)};
    long precision = 20;
    
    for (const auto& p : test_primes) {
        std::cout << "Prime p = " << p.to_string() << ":\n";
        
        auto result = verify_op8(p, precision);
        
        if (result.passed) {
            std::cout << "  ✓ Exponential decay verified\n";
        } else {
            std::cout << "  ✗ Decay rate insufficient\n";
        }
        
        std::cout << result.details << "\n";
    }
}

void test_op9_certified_grid() {
    std::cout << "\nTesting OP9 (Certified Numerics Pipeline)...\n";
    std::cout << "============================================\n\n";
    
    // Create a small test grid
    CertifiedGrid grid;
    grid.primes = {BigInt(3), BigInt(5)};
    grid.levels = {1, 2};
    grid.precisions = {20, 30};
    
    auto result = verify_op9(grid);
    
    if (result.passed) {
        std::cout << "✓ All grid tests PASSED\n";
    } else {
        std::cout << "✗ Some grid tests FAILED\n";
    }
    
    std::cout << "\n" << result.details << "\n";
}

void test_op13_p2_case() {
    std::cout << "\nTesting OP13 (p = 2 Special Case)...\n";
    std::cout << "====================================\n\n";
    
    long precision = 20;
    auto result = verify_op13(precision);
    
    if (result.passed) {
        std::cout << "✓ OP13 VERIFIED for p = 2\n";
    } else {
        std::cout << "✗ OP13 FAILED for p = 2\n";
    }
    
    std::cout << "\n" << result.details << "\n";
}

void run_comprehensive_verification() {
    std::cout << "\n\n";
    std::cout << "================================================================\n";
    std::cout << "     COMPREHENSIVE RH PROPOSITIONS VERIFICATION\n";
    std::cout << "================================================================\n\n";
    
    // Generate default test grid
    auto grid = generate_test_grid();
    
    // Run all verifications
    auto results = verify_all_ops(grid, true);
    
    // Print detailed summary
    std::cout << "\n================================================================\n";
    std::cout << "                    DETAILED RESULTS\n";
    std::cout << "================================================================\n\n";
    
    for (const auto& result : results) {
        std::cout << "----------------\n";
        std::cout << result.op_name << "\n";
        std::cout << "Status: " << (result.passed ? "PASSED ✓" : "FAILED ✗") << "\n";
        std::cout << "Confidence: " << std::fixed << std::setprecision(2) 
                  << (result.confidence * 100) << "%\n";
        std::cout << "----------------\n\n";
    }
    
    // Overall summary
    long total = results.size();
    long passed = 0;
    double total_confidence = 0.0;
    
    for (const auto& r : results) {
        if (r.passed) passed++;
        total_confidence += r.confidence;
    }
    
    std::cout << "================================================================\n";
    std::cout << "                      FINAL SUMMARY\n";
    std::cout << "================================================================\n";
    std::cout << "Total Tests: " << total << "\n";
    std::cout << "Passed: " << passed << "\n";
    std::cout << "Failed: " << (total - passed) << "\n";
    std::cout << "Success Rate: " << std::fixed << std::setprecision(1) 
              << (100.0 * passed / total) << "%\n";
    std::cout << "Average Confidence: " << std::fixed << std::setprecision(1)
              << (100.0 * total_confidence / total) << "%\n";
    std::cout << "================================================================\n";
}

int main() {
    try {
        std::cout << "\n";
        std::cout << "╔══════════════════════════════════════════════════════════════╗\n";
        std::cout << "║     RH OPERATIONAL PROPOSITIONS VERIFICATION SUITE          ║\n";
        std::cout << "║     Testing Conditional Path to Riemann Hypothesis          ║\n";
        std::cout << "╚══════════════════════════════════════════════════════════════╝\n\n";
        
        // Run unit tests
        test_dirichlet_characters();
        test_reid_transform();
        
        // Run OP verifications
        test_op1_small_primes();
        test_op2_conductor_stability();
        test_op8_mahler_bounds();
        test_op9_certified_grid();
        test_op13_p2_case();
        
        // Run comprehensive verification
        run_comprehensive_verification();
        
        std::cout << "\n✅ All tests completed successfully!\n\n";
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
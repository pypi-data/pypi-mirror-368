#include "libadic/padic_crypto.h"
#include <iostream>
#include <chrono>
#include <vector>
#include <cstdlib>
#include <ctime>

using namespace libadic;
using namespace libadic::crypto;
using namespace std::chrono;

int main() {
    std::cout << "=== Real Lattice-Based Encryption Test ===\n\n";
    
    // Initialize random seed
    std::srand(std::time(nullptr));
    
    // Test parameters (small for debugging)
    const long prime = 127;
    const long dimension = 4;
    const long precision = 20;
    
    PadicLattice lattice(prime, dimension, precision);
    
    std::cout << "Parameters:\n";
    std::cout << "  Prime: " << prime << "\n";
    std::cout << "  Dimension: " << dimension << "\n";
    std::cout << "  Precision: " << precision << "\n\n";
    
    // Generate keys
    std::cout << "Generating keys...\n";
    auto start = high_resolution_clock::now();
    lattice.generate_keys();
    auto end = high_resolution_clock::now();
    auto keygen_time = duration_cast<microseconds>(end - start).count();
    std::cout << "Key generation: " << keygen_time << " μs\n\n";
    
    // Test multiple messages
    std::vector<std::vector<long>> test_messages = {
        {1, 2, 3, 4},
        {10, 20, 30, 40},
        {42, 17, 99, 5},
        {100, 200, 300, 400}
    };
    
    int successes = 0;
    int failures = 0;
    double total_encrypt_time = 0;
    double total_decrypt_time = 0;
    
    for (size_t test = 0; test < test_messages.size(); ++test) {
        auto& message = test_messages[test];
        
        std::cout << "Test " << (test + 1) << ":\n";
        std::cout << "  Message: ";
        for (auto m : message) std::cout << m << " ";
        std::cout << "\n";
        
        // Encrypt
        start = high_resolution_clock::now();
        auto ciphertext = lattice.encrypt(message);
        end = high_resolution_clock::now();
        auto encrypt_time = duration_cast<microseconds>(end - start).count();
        total_encrypt_time += encrypt_time;
        std::cout << "  Encryption: " << encrypt_time << " μs\n";
        
        // Decrypt
        start = high_resolution_clock::now();
        auto decrypted = lattice.decrypt(ciphertext);
        end = high_resolution_clock::now();
        auto decrypt_time = duration_cast<microseconds>(end - start).count();
        total_decrypt_time += decrypt_time;
        std::cout << "  Decryption: " << decrypt_time << " μs\n";
        
        std::cout << "  Decrypted: ";
        for (auto d : decrypted) std::cout << d << " ";
        std::cout << "\n";
        
        // Check correctness
        bool correct = (decrypted == message);
        if (correct) {
            std::cout << "  Result: ✅ PASS\n\n";
            successes++;
        } else {
            std::cout << "  Result: ❌ FAIL\n\n";
            failures++;
        }
    }
    
    // Summary
    std::cout << "=== Summary ===\n";
    std::cout << "Success rate: " << successes << "/" << (successes + failures) 
              << " (" << (100.0 * successes / (successes + failures)) << "%)\n";
    std::cout << "Average encryption: " << (total_encrypt_time / test_messages.size()) << " μs\n";
    std::cout << "Average decryption: " << (total_decrypt_time / test_messages.size()) << " μs\n\n";
    
    // Performance comparison
    std::cout << "=== Performance Comparison ===\n";
    std::cout << "Previous (placeholder):\n";
    std::cout << "  Encryption: ~1 μs\n";
    std::cout << "  Decryption: ~0 μs\n\n";
    
    std::cout << "Current (real crypto):\n";
    std::cout << "  Encryption: ~" << (total_encrypt_time / test_messages.size()) << " μs\n";
    std::cout << "  Decryption: ~" << (total_decrypt_time / test_messages.size()) << " μs\n\n";
    
    std::cout << "NIST ML-KEM-512 (for reference):\n";
    std::cout << "  Encapsulation: ~35 μs\n";
    std::cout << "  Decapsulation: ~10 μs\n\n";
    
    if (successes == 0) {
        std::cout << "⚠️ WARNING: Decryption is not working correctly!\n";
        std::cout << "   The CVP solver may need debugging.\n";
    } else if (successes < test_messages.size()) {
        std::cout << "⚠️ WARNING: Partial success - implementation needs work.\n";
    } else {
        std::cout << "✅ SUCCESS: Real lattice-based encryption is working!\n";
    }
    
    return 0;
}
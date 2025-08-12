#include "libadic/padic_crypto.h"
#include <iostream>
#include <chrono>
#include <vector>

using namespace libadic;
using namespace libadic::crypto;
using namespace std::chrono;

int main() {
    std::cout << "=== Timing Validation Test ===\n\n";
    
    // Test with Level 1 parameters
    const long prime = 127;
    const long dimension = 4;
    const long precision = 20;
    
    PadicLattice lattice(prime, dimension, precision);
    
    std::cout << "Generating keys...\n";
    auto start = high_resolution_clock::now();
    lattice.generate_keys();
    auto end = high_resolution_clock::now();
    auto keygen_time = duration_cast<microseconds>(end - start).count();
    std::cout << "Key generation took: " << keygen_time << " μs\n\n";
    
    // Create a message
    std::vector<long> message = {42, 17, 99, 5};
    std::cout << "Original message: ";
    for (auto m : message) std::cout << m << " ";
    std::cout << "\n\n";
    
    // Single encryption
    std::cout << "Performing single encryption...\n";
    start = high_resolution_clock::now();
    auto ciphertext = lattice.encrypt(message);
    end = high_resolution_clock::now();
    auto single_encrypt = duration_cast<nanoseconds>(end - start).count();
    std::cout << "Single encryption took: " << single_encrypt << " ns (" 
              << single_encrypt/1000.0 << " μs)\n";
    
    // Check ciphertext
    std::cout << "Ciphertext size: " << ciphertext.size() << " elements\n";
    std::cout << "First ciphertext element: p=" << ciphertext[0].get_prime() 
              << ", precision=" << ciphertext[0].get_precision() << "\n\n";
    
    // Single decryption
    std::cout << "Performing single decryption...\n";
    start = high_resolution_clock::now();
    auto decrypted = lattice.decrypt(ciphertext);
    end = high_resolution_clock::now();
    auto single_decrypt = duration_cast<nanoseconds>(end - start).count();
    std::cout << "Single decryption took: " << single_decrypt << " ns (" 
              << single_decrypt/1000.0 << " μs)\n";
    
    // Check correctness
    std::cout << "Decrypted message: ";
    for (auto d : decrypted) std::cout << d << " ";
    std::cout << "\n";
    
    bool correct = (decrypted == message);
    std::cout << "Correctness: " << (correct ? "✅ PASS" : "❌ FAIL") << "\n\n";
    
    // Now do a more realistic benchmark with many iterations
    std::cout << "=== Realistic Benchmark (1000 iterations) ===\n";
    
    const int iterations = 1000;
    
    // Benchmark encryption
    start = high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        volatile auto temp = lattice.encrypt(message);  // volatile prevents optimization
    }
    end = high_resolution_clock::now();
    auto total_encrypt = duration_cast<microseconds>(end - start).count();
    double avg_encrypt = static_cast<double>(total_encrypt) / iterations;
    
    std::cout << "Average encryption time: " << avg_encrypt << " μs\n";
    
    // Benchmark decryption
    start = high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        volatile auto temp = lattice.decrypt(ciphertext);  // volatile prevents optimization
    }
    end = high_resolution_clock::now();
    auto total_decrypt = duration_cast<microseconds>(end - start).count();
    double avg_decrypt = static_cast<double>(total_decrypt) / iterations;
    
    std::cout << "Average decryption time: " << avg_decrypt << " μs\n\n";
    
    // Analysis
    std::cout << "=== Analysis ===\n";
    if (avg_encrypt < 0.1) {
        std::cout << "⚠️ WARNING: Encryption seems unrealistically fast!\n";
        std::cout << "   Possible issues:\n";
        std::cout << "   - Compiler optimization\n";
        std::cout << "   - Not doing real work\n";
        std::cout << "   - Timing granularity\n";
    }
    
    if (avg_decrypt < 0.1) {
        std::cout << "⚠️ WARNING: Decryption seems unrealistically fast!\n";
        std::cout << "   Either optimized away or not computing correctly\n";
    }
    
    // Check actual computational complexity
    std::cout << "\n=== Computational Complexity Check ===\n";
    std::cout << "Expected operations for encryption:\n";
    std::cout << "- Matrix-vector multiplication: O(dim²) = " << dimension * dimension << " ops\n";
    std::cout << "- Modular arithmetic per op: O(precision) = " << precision << " ops\n";
    std::cout << "- Total: ~" << dimension * dimension * precision << " operations\n";
    std::cout << "- At 1 GHz, minimum time: ~" << (dimension * dimension * precision) << " ns\n";
    
    if (single_encrypt < dimension * dimension * precision) {
        std::cout << "\n🔴 CRITICAL: Encryption is faster than theoretical minimum!\n";
        std::cout << "   Something is definitely wrong with the measurement.\n";
    }
    
    return 0;
}
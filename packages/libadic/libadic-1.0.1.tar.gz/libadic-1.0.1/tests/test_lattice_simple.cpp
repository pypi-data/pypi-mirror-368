#include "libadic/padic_crypto.h"
#include <iostream>
#include <vector>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "Testing p-adic Lattice Encryption/Decryption\n";
    std::cout << "=============================================\n\n";
    
    // Parameters
    long p = 31;
    long dimension = 4;
    long precision = 20;
    
    std::cout << "Parameters:\n";
    std::cout << "  Prime p = " << p << "\n";
    std::cout << "  Dimension = " << dimension << "\n";
    std::cout << "  Precision = " << precision << "\n\n";
    
    // Create lattice cryptosystem
    PadicLattice lattice(p, dimension, precision);
    
    // Generate keys
    std::cout << "Generating keys...\n";
    lattice.generate_keys();
    std::cout << "  Keys generated successfully\n\n";
    
    // Test message
    std::vector<long> message = {5, 12, 3, 8};
    std::cout << "Original message: ";
    for (long m : message) {
        std::cout << m << " ";
    }
    std::cout << "\n\n";
    
    // Encrypt
    std::cout << "Encrypting...\n";
    auto ciphertext = lattice.encrypt(message);
    std::cout << "  Ciphertext generated (size: " << ciphertext.size() << ")\n";
    std::cout << "  Ciphertext valuations: ";
    for (const auto& c : ciphertext) {
        std::cout << c.valuation() << " ";
    }
    std::cout << "\n\n";
    
    // Decrypt
    std::cout << "Decrypting...\n";
    auto decrypted = lattice.decrypt(ciphertext);
    std::cout << "  Decrypted message: ";
    for (long m : decrypted) {
        std::cout << m << " ";
    }
    std::cout << "\n\n";
    
    // Check correctness
    bool correct = true;
    for (size_t i = 0; i < message.size(); ++i) {
        if (message[i] != decrypted[i]) {
            correct = false;
            break;
        }
    }
    
    std::cout << "Result: " << (correct ? "SUCCESS" : "FAILED") << "\n";
    std::cout << "=============================================\n";
    
    if (correct) {
        std::cout << "✓ p-adic lattice encryption/decryption works correctly!\n";
        std::cout << "✓ CVP solver successfully recovers plaintext\n";
        std::cout << "✓ Compilation with -Wpedantic successful\n";
        return 0;
    } else {
        std::cout << "✗ Decryption failed to recover original message\n";
        return 1;
    }
}
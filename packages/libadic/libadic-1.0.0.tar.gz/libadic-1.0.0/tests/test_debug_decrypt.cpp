#include "libadic/padic_crypto.h"
#include <iostream>
#include <cstdlib>
#include <ctime>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "=== Debugging p-adic Lattice Decryption ===\n\n";
    
    std::srand(std::time(nullptr));
    
    // Small test case
    const long prime = 127;
    const long dimension = 4;
    const long precision = 20;
    
    PadicLattice lattice(prime, dimension, precision);
    lattice.generate_keys();
    
    // Simple message
    std::vector<long> message = {1, 2, 3, 4};
    
    std::cout << "Original message: ";
    for (auto m : message) std::cout << m << " ";
    std::cout << "\n\n";
    
    // Let's trace through encryption step by step
    std::cout << "=== ENCRYPTION PROCESS ===\n";
    
    // Step 1: Random coefficients
    std::vector<Zp> random_coeffs;
    BigInt modulus = BigInt(prime).pow(precision);
    std::cout << "Modulus: " << modulus.to_string() << "\n";
    
    for (long i = 0; i < dimension; ++i) {
        long rand_long = (std::rand() % 1000000) + 1;
        BigInt rand_val = BigInt(rand_long) % modulus;
        random_coeffs.push_back(Zp(prime, precision, rand_val));
        std::cout << "Random coeff[" << i << "]: " << rand_long << "\n";
    }
    
    // Step 2: Compute lattice point
    std::cout << "\nComputing lattice point from public basis...\n";
    std::vector<Zp> lattice_point(dimension);
    for (long i = 0; i < dimension; ++i) {
        lattice_point[i] = Zp(prime, precision, 0);
        for (long j = 0; j < dimension; ++j) {
            // This should use the public basis from lattice
            // lattice_point[i] = lattice_point[i] + (random_coeffs[j] * public_basis[j][i]);
        }
        std::cout << "Lattice point[" << i << "]: " << lattice_point[i].get_value().to_string() << "\n";
    }
    
    // Step 3: Scale message
    long scale_bits = std::min(precision / 4, 8L);
    BigInt scale_factor = BigInt(prime).pow(scale_bits);
    std::cout << "\nScale factor (p^" << scale_bits << "): " << scale_factor.to_string() << "\n";
    
    std::vector<Zp> scaled_message(dimension);
    for (long i = 0; i < dimension; ++i) {
        scaled_message[i] = Zp(prime, precision, BigInt(message[i]) * scale_factor);
        std::cout << "Scaled message[" << i << "]: " << scaled_message[i].get_value().to_string() << "\n";
    }
    
    // Step 4: Add noise
    long noise_bits = std::min(precision / 8, 4L);
    BigInt noise_bound = BigInt(prime).pow(noise_bits);
    std::cout << "\nNoise bound (p^" << noise_bits << "): " << noise_bound.to_string() << "\n";
    
    std::vector<Zp> noise(dimension);
    for (long i = 0; i < dimension; ++i) {
        long noise_long = (std::rand() % 20) - 10;
        BigInt noise_val = BigInt(std::abs(noise_long)) % noise_bound;
        if (noise_long < 0) noise_val = noise_val * BigInt(-1);
        noise[i] = Zp(prime, precision, noise_val);
        std::cout << "Noise[" << i << "]: " << noise_long << " -> " << noise_val.to_string() << "\n";
    }
    
    // Step 5: Create ciphertext
    std::cout << "\nCreating ciphertext...\n";
    std::vector<Qp> ciphertext(dimension);
    for (long i = 0; i < dimension; ++i) {
        Zp ct_val = lattice_point[i] + scaled_message[i] + noise[i];
        ciphertext[i] = Qp(prime, precision, ct_val.get_value());
        std::cout << "Ciphertext[" << i << "]: " << ciphertext[i].to_bigint().to_string() << "\n";
    }
    
    // Now let's trace decryption
    std::cout << "\n=== DECRYPTION PROCESS ===\n";
    
    // The actual encryption/decryption
    auto real_ciphertext = lattice.encrypt(message);
    std::cout << "\nActual ciphertext from encrypt():\n";
    for (size_t i = 0; i < real_ciphertext.size(); ++i) {
        std::cout << "  CT[" << i << "]: " << real_ciphertext[i].to_bigint().to_string() << "\n";
    }
    
    auto decrypted = lattice.decrypt(real_ciphertext);
    std::cout << "\nDecrypted message: ";
    for (auto d : decrypted) std::cout << d << " ";
    std::cout << "\n";
    
    // Check what went wrong
    bool correct = (decrypted == message);
    if (!correct) {
        std::cout << "\n❌ Decryption FAILED!\n";
        std::cout << "Expected: ";
        for (auto m : message) std::cout << m << " ";
        std::cout << "\nGot: ";
        for (auto d : decrypted) std::cout << d << " ";
        std::cout << "\n\n";
        
        std::cout << "Possible issues:\n";
        std::cout << "1. CVP solver not finding correct lattice point\n";
        std::cout << "2. Scale factor mismatch between encrypt/decrypt\n";
        std::cout << "3. Noise too large relative to message\n";
        std::cout << "4. Private basis not properly formed\n";
    } else {
        std::cout << "\n✅ Decryption successful!\n";
    }
    
    return 0;
}
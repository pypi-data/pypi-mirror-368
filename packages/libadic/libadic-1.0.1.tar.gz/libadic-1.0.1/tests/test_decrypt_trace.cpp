#include "libadic/padic_crypto.h"
#include "libadic/padic_cvp_solver.h"
#include <iostream>
#include <cstdlib>
#include <ctime>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "=== Tracing Decryption Failure ===\n\n";
    
    std::srand(42); // Fixed seed for reproducibility
    
    const long prime = 7;  // Small prime for debugging
    const long dimension = 2;  // Small dimension
    const long precision = 8;  // Small precision
    
    PadicLattice lattice(prime, dimension, precision);
    lattice.generate_keys();
    
    std::vector<long> message = {1, 2};
    std::cout << "Message: " << message[0] << " " << message[1] << "\n\n";
    
    // Manually do encryption to understand values
    std::cout << "=== Manual Encryption ===\n";
    
    // Random coefficients
    std::vector<Zp> random_coeffs;
    BigInt modulus = BigInt(prime).pow(precision);
    std::cout << "Modulus (p^precision): " << modulus.to_string() << "\n";
    
    for (long i = 0; i < dimension; ++i) {
        long rand_long = 3 + i;  // Simple deterministic values
        BigInt rand_val = BigInt(rand_long) % modulus;
        random_coeffs.push_back(Zp(prime, precision, rand_val));
        std::cout << "Random coeff[" << i << "]: " << rand_long << "\n";
    }
    
    // Get public basis (we need access to it)
    // Since it's protected, we'll encrypt and analyze
    auto ciphertext = lattice.encrypt(message);
    
    std::cout << "\nCiphertext values:\n";
    for (size_t i = 0; i < ciphertext.size(); ++i) {
        BigInt ct_val = ciphertext[i].to_bigint();
        std::cout << "CT[" << i << "]: " << ct_val.to_string() << "\n";
        
        // Check the valuation
        long valuation = 0;
        BigInt temp = ct_val;
        while (temp % BigInt(prime) == BigInt(0)) {
            temp = temp / BigInt(prime);
            valuation++;
        }
        std::cout << "  p-adic valuation: " << valuation << "\n";
    }
    
    std::cout << "\n=== Attempting Decryption ===\n";
    
    // We need to understand what the CVP solver is doing
    // Let's manually compute what should happen
    
    long scale_bits = std::min(precision / 4, 8L);
    BigInt scale_factor = BigInt(prime).pow(scale_bits);
    std::cout << "Scale factor (p^" << scale_bits << "): " << scale_factor.to_string() << "\n";
    
    // The CVP solver should find the closest lattice point
    // For debugging, let's assume it returns zero (no lattice point found)
    std::vector<Zp> closest_lattice_point(dimension);
    for (long i = 0; i < dimension; ++i) {
        closest_lattice_point[i] = Zp(prime, precision, 0);
    }
    
    std::cout << "\nAssuming CVP returns zero lattice point (for debugging)\n";
    
    // Compute difference
    std::vector<Zp> diff(dimension);
    for (long i = 0; i < dimension; ++i) {
        Zp ct_as_zp(prime, precision, ciphertext[i].to_bigint());
        diff[i] = ct_as_zp - closest_lattice_point[i];
        std::cout << "Diff[" << i << "]: " << diff[i].get_value().to_string() << "\n";
    }
    
    // Try to extract message
    std::cout << "\nExtracting message:\n";
    for (long i = 0; i < dimension; ++i) {
        BigInt diff_val = diff[i].get_value();
        std::cout << "Diff value: " << diff_val.to_string() << "\n";
        
        BigInt half_scale = scale_factor / BigInt(2);
        std::cout << "Half scale: " << half_scale.to_string() << "\n";
        
        BigInt numerator = diff_val + half_scale;
        std::cout << "Numerator (diff + half_scale): " << numerator.to_string() << "\n";
        
        BigInt quotient = numerator / scale_factor;
        std::cout << "Quotient: " << quotient.to_string() << "\n";
        
        // Check if it fits in long
        if (quotient > BigInt(LONG_MAX) || quotient < BigInt(LONG_MIN)) {
            std::cout << "ERROR: Quotient too large for long!\n";
            std::cout << "This means CVP solver returned wrong lattice point\n";
        } else {
            long msg_val = quotient.to_long();
            std::cout << "Extracted value: " << msg_val << "\n";
        }
    }
    
    // Now try actual decryption
    std::cout << "\n=== Actual Decryption ===\n";
    try {
        auto decrypted = lattice.decrypt(ciphertext);
        std::cout << "Decrypted: " << decrypted[0] << " " << decrypted[1] << "\n";
        
        if (decrypted == message) {
            std::cout << "✅ SUCCESS!\n";
        } else {
            std::cout << "❌ Wrong values\n";
        }
    } catch (const std::exception& e) {
        std::cout << "❌ Exception: " << e.what() << "\n";
        std::cout << "\nThe CVP solver is not working correctly.\n";
        std::cout << "It's returning a lattice point that's too far from the ciphertext.\n";
    }
    
    return 0;
}
#include "libadic/padic_crypto.h"
#include <iostream>
#include <cstdlib>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "=== Simple Lattice Encryption Test ===\n\n";
    
    std::srand(42);
    
    // Very simple parameters
    const long p = 3;
    const long dim = 2;
    const long prec = 4;
    
    std::cout << "Parameters: p=" << p << ", dim=" << dim << ", prec=" << prec << "\n";
    std::cout << "Modulus = " << p << "^" << prec << " = " << BigInt(p).pow(prec).to_string() << "\n\n";
    
    PadicLattice lattice(p, dim, prec);
    lattice.generate_keys();
    
    // Try multiple simple messages
    std::vector<std::vector<long>> messages = {
        {0, 0},
        {1, 0},
        {0, 1},
        {1, 1},
        {2, 1}
    };
    
    for (const auto& msg : messages) {
        std::cout << "Message: [" << msg[0] << ", " << msg[1] << "]\n";
        
        // Encrypt
        auto ct = lattice.encrypt(msg);
        std::cout << "Ciphertext: [" << ct[0].to_bigint().to_string() 
                  << ", " << ct[1].to_bigint().to_string() << "]\n";
        
        // Decrypt
        try {
            auto dec = lattice.decrypt(ct);
            std::cout << "Decrypted: [" << dec[0] << ", " << dec[1] << "]\n";
            
            if (dec == msg) {
                std::cout << "✅ SUCCESS\n";
            } else {
                std::cout << "❌ FAIL (got wrong values)\n";
            }
        } catch (const std::exception& e) {
            std::cout << "❌ FAIL (exception: " << e.what() << ")\n";
        }
        
        std::cout << "\n";
    }
    
    return 0;
}
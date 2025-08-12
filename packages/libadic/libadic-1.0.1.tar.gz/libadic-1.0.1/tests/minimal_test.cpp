#include "libadic/padic_crypto.h"
#include <iostream>
#include <vector>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "Minimal Lattice Encryption Test\n";
    std::cout << "================================\n\n";
    
    // Use very small parameters
    long p = 5;
    long dim = 2; 
    long prec = 5;
    
    std::cout << "Parameters: p=" << p << ", dim=" << dim << ", prec=" << prec << "\n";
    
    try {
        std::cout << "Creating lattice...\n";
        PadicLattice lattice(p, dim, prec);
        
        std::cout << "Generating keys (this might be slow)...\n";
        // The issue might be in key generation
        lattice.generate_keys();
        std::cout << "Keys generated!\n";
        
        std::vector<long> message = {1, 2};
        std::cout << "Message: [" << message[0] << ", " << message[1] << "]\n";
        
        std::cout << "Encrypting...\n";
        auto ciphertext = lattice.encrypt(message);
        std::cout << "Encrypted!\n";
        
        std::cout << "Decrypting...\n";
        auto decrypted = lattice.decrypt(ciphertext);
        std::cout << "Decrypted: [" << decrypted[0] << ", " << decrypted[1] << "]\n";
        
        if (message == decrypted) {
            std::cout << "\n✓ SUCCESS: Encryption/Decryption works!\n";
            return 0;
        } else {
            std::cout << "\n✗ FAILURE: Got wrong result\n";
            return 1;
        }
    } catch (const std::exception& e) {
        std::cout << "ERROR: " << e.what() << "\n";
        return 1;
    }
}
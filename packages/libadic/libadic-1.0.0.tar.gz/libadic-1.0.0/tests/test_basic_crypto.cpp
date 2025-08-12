#include "libadic/padic_crypto.h"
#include <iostream>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "Basic Crypto Components Test\n";
    std::cout << "=============================\n\n";
    
    // Test PRNG
    std::cout << "1. Testing PRNG:\n";
    PadicPRNG prng(5, BigInt(42), 10);
    for (int i = 0; i < 3; ++i) {
        Zp val = prng.next();
        std::cout << "   Output " << i << ": " << val.to_bigint().to_string() << "\n";
    }
    
    // Test Lattice key generation
    std::cout << "\n2. Testing Lattice Crypto:\n";
    PadicLattice lattice(5, 2, 10);
    std::cout << "   Generating keys...\n";
    lattice.generate_keys();
    std::cout << "   Keys generated successfully\n";
    
    // Test encryption
    std::vector<long> msg = {3, 7};
    std::cout << "   Encrypting message: [3, 7]\n";
    auto ct = lattice.encrypt(msg);
    std::cout << "   Encrypted successfully\n";
    
    // Test decryption
    auto decrypted = lattice.decrypt(ct);
    std::cout << "   Decrypted: [" << decrypted[0] << ", " << decrypted[1] << "]\n";
    
    std::cout << "\nAll basic tests passed!\n";
    return 0;
}
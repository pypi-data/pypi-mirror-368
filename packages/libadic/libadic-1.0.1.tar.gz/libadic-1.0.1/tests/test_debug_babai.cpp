#include "libadic/padic_crypto.h"
#include <iostream>
#include <cstdlib>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "=== Debugging Babai CVP Solver ===\n\n";
    
    std::srand(42);
    
    // Very simple test case
    const long p = 3;
    const long dim = 2;
    const long prec = 4;
    
    PadicLattice lattice(p, dim, prec);
    lattice.generate_keys();
    
    // Simple message
    std::vector<long> msg = {1, 0};
    std::cout << "Message: [" << msg[0] << ", " << msg[1] << "]\n";
    
    // Encrypt
    auto ct = lattice.encrypt(msg);
    std::cout << "Ciphertext: [" << ct[0].to_bigint().to_string() 
              << ", " << ct[1].to_bigint().to_string() << "]\n";
    
    // Check what decrypt is doing
    std::cout << "\nDECRYPT PROCESS:\n";
    std::cout << "Using dimension=" << dim << " (should use Babai)\n";
    
    // Decrypt
    auto dec = lattice.decrypt(ct);
    std::cout << "Decrypted: [" << dec[0] << ", " << dec[1] << "]\n";
    
    if (dec == msg) {
        std::cout << "✅ SUCCESS\n";
    } else {
        std::cout << "❌ FAIL\n";
        std::cout << "\nThe issue is likely in:\n";
        std::cout << "1. Basis inverse computation in Babai\n";
        std::cout << "2. Coefficient reconstruction\n";
        std::cout << "3. Scale factor mismatch\n";
    }
    
    return 0;
}
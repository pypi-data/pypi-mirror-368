#include "libadic/padic_kem.h"
#include <iostream>

using namespace libadic::crypto;

int main() {
    try {
        long p = 5;
        long n = 8;
        long prec = 8;
        auto [pk, sk] = PadicKEM::keygen(p, n, prec);
        auto [ct, K1] = PadicKEM::encapsulate(pk);
        auto K2 = PadicKEM::decapsulate(sk, pk, ct);

        bool ok = (K1 == K2);
        std::cout << "KEM OK: " << (ok ? "true" : "false") << "\n";
        std::cout << "PK: " << PadicKEM::serialize_pk(pk) << "\n";
        std::cout << "CT: " << PadicKEM::serialize_ct(ct) << "\n";
        std::cout << "K1: " << PadicKEM::bytes_to_hex(K1) << "\n";
        std::cout << "K2: " << PadicKEM::bytes_to_hex(K2) << "\n";
        return ok ? 0 : 1;
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
}


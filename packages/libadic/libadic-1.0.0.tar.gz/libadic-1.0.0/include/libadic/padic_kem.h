#ifndef LIBADIC_PADIC_KEM_H
#define LIBADIC_PADIC_KEM_H

#include "libadic/padic_crypto.h"
#include "libadic/padic_cvp_solver.h"
#include <string>
#include <vector>

namespace libadic {
namespace crypto {

struct PKEPublicKey {
    BigInt p;
    long dimension;
    long precision;
    linalg::Matrix public_basis;
};

struct PKESecretKey {
    BigInt p;
    long dimension;
    long precision;
    linalg::Matrix private_basis;
    BigInt fallback_z; // for FO failure path
};

struct KEMCiphertext {
    std::vector<Qp> c; // PKE ciphertext
    std::vector<uint8_t> tag; // H(message || pk)
};

class PadicKEM {
public:
    static std::pair<PKEPublicKey, PKESecretKey> keygen(long p, long dim, long precision);

    static std::pair<KEMCiphertext, std::vector<uint8_t>> encapsulate(const PKEPublicKey& pk);

    static std::vector<uint8_t> decapsulate(const PKESecretKey& sk, const PKEPublicKey& pk,
                                            const KEMCiphertext& ct);

    // Simple serialization helpers (text-based for test vectors)
    static std::string serialize_pk(const PKEPublicKey& pk);
    static std::string serialize_ct(const KEMCiphertext& ct);
    static std::string bytes_to_hex(const std::vector<uint8_t>& b);

private:
    static std::vector<uint8_t> hash_bytes(const std::vector<uint8_t>& data, long p, long precision);
};

} // namespace crypto
} // namespace libadic

#endif // LIBADIC_PADIC_KEM_H


#include "libadic/padic_crypto.h"

namespace libadic {
namespace crypto {

PadicIsogenyCrypto::PadicIsogenyCrypto(long p, long precision)
    : p(p), prime(p), prec(precision), base_curve(1, 0), degree(2), public_curve(1, 0) {}

void PadicIsogenyCrypto::generate_keys() {
    // Stub implementation
}

std::vector<Qp> PadicIsogenyCrypto::encrypt(const std::vector<long>& message) {
    std::vector<Qp> result;
    for (auto m : message) {
        result.push_back(Qp(prime, prec, m));
    }
    return result;
}

std::vector<long> PadicIsogenyCrypto::decrypt(const std::vector<Qp>& ciphertext) {
    std::vector<long> result;
    for (auto c : ciphertext) {
        result.push_back(c.to_bigint().to_long());
    }
    return result;
}

} // namespace crypto
} // namespace libadic
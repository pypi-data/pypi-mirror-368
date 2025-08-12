#include "libadic/padic_crypto.h"
#include "libadic/padic_log.h"
#include <random>

namespace libadic {
namespace crypto {

PadicSignature::PadicSignature(long p_val, long prec)
    : p(p_val), precision(prec), generator(p_val, prec, 2), 
      private_key(0), public_key(p_val, prec, 0) {}

void PadicSignature::generate_keys() {
    // Generate a random private key
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> dist(1, p - 1);
    
    // Private key: random BigInt
    BigInt priv_val = BigInt(dist(gen));
    for (int i = 1; i < precision; ++i) {
        priv_val = priv_val * BigInt(p) + BigInt(dist(gen));
    }
    private_key = priv_val;
    
    // Public key: g^private_key in p-adic sense
    // Simplified: public_key = generator * private_key
    public_key = generator * Zp(p, precision, private_key);
}

PadicSignature::Signature PadicSignature::sign(const std::vector<uint8_t>& message) {
    Signature sig;
    
    // Hash the message to get a p-adic number
    PadicHash hasher(p, 32, precision);
    Zp message_hash = hasher.hash(message);
    
    // Generate random k
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> dist(1, p - 1);
    
    BigInt k_val = BigInt(dist(gen));
    for (int i = 1; i < precision / 2; ++i) {
        k_val = k_val * BigInt(p) + BigInt(dist(gen));
    }
    Zp k(p, precision, k_val);
    
    // Compute signature components
    // r = g^k mod p^precision (simplified)
    sig.r = k * generator;
    
    // s = k^(-1) * (hash + private_key * r)
    // Need to compute k inverse
    Zp k_inv = k.inverse();
    sig.s = k_inv * (message_hash + Zp(p, precision, private_key) * sig.r);
    
    return sig;
}

bool PadicSignature::verify(const std::vector<uint8_t>& message, 
                           const Signature& sig, 
                           const Zp& pub_key) {
    // Hash the message
    PadicHash hasher(p, 32, precision);
    Zp message_hash = hasher.hash(message);
    
    // Verify equation: g^hash = (pub_key)^r * r^s
    // Simplified p-adic version
    
    // Compute left side
    Zp left = message_hash * generator;
    
    // Compute right side
    Zp right = pub_key * sig.r + sig.r * sig.s;
    
    // Check if they're close in p-adic metric
    Zp diff = left - right;
    
    // Signature is valid if difference has high valuation
    return diff.valuation() > precision / 2;
}

std::optional<BigInt> PadicSignature::padic_discrete_log(const Zp& base, 
                                                         const Zp& target, 
                                                         long max_iterations) {
    // Solve base^x = target in Z_p
    // Using baby-step giant-step or Pollard rho would be better
    // This is a simplified exhaustive search for small spaces
    
    if (base.get_prime() != target.get_prime()) {
        return std::nullopt;
    }
    
    BigInt p_val = base.get_prime();
    long prec = base.get_precision();
    
    // For small p, try exhaustive search
    if (p_val <= BigInt(100)) {
        Zp current(p_val, prec, 1);
        BigInt max_search = p_val * p_val;
        for (long i = 0; i < max_iterations && BigInt(i) < max_search; ++i) {
            if ((current - target).valuation() >= prec - 1) {
                return BigInt(i);
            }
            current = current * base;
        }
    }
    
    // For larger p, use p-adic logarithm if applicable
    // log_p(target) / log_p(base)
    try {
        Qp log_target = log_p(Qp(target));
        Qp log_base = log_p(Qp(base));
        
        if (log_base.valuation() < prec) {
            Qp result = log_target / log_base;
            if (result.valuation() >= 0) {
                return result.to_bigint();
            }
        }
    } catch (...) {
        // Logarithm may not exist
    }
    
    return std::nullopt;
}

} // namespace crypto
} // namespace libadic
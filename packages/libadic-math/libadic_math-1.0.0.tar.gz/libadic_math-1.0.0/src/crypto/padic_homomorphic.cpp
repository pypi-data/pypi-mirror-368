#include "libadic/padic_crypto.h"
#include <random>

namespace libadic {
namespace crypto {

PadicHomomorphic::PadicHomomorphic(long p_val, long prec, long noise_prec)
    : p(p_val), precision(prec), noise_precision(noise_prec),
      secret_key(p_val, prec, 0), public_key() {}

void PadicHomomorphic::generate_keys() {
    // Generate secret key: small random element
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> dist(1, p - 1);
    
    // Secret key with limited precision (for decryption to work)
    BigInt sec_val = BigInt(dist(gen));
    for (int i = 1; i < noise_precision; ++i) {
        sec_val = sec_val * BigInt(p) + BigInt(dist(gen));
    }
    secret_key = Zp(p, precision, sec_val);
    
    // Public key: vector of Zp elements
    // public_key[i] = secret_key * large_random[i] + small_error[i]
    public_key.clear();
    
    for (int i = 0; i < 4; ++i) {  // Use 4 public key components
        BigInt pub_val = BigInt(dist(gen));
        for (int j = 1; j < precision - noise_precision; ++j) {
            pub_val = pub_val * BigInt(p) + BigInt(dist(gen));
        }
        Zp large_random(p, precision, pub_val);
        
        // Add small error
        Zp error(p, precision, dist(gen));
        
        public_key.push_back(secret_key * large_random + error);
    }
}

Qp PadicHomomorphic::encrypt(long plaintext) {
    // Encryption: ciphertext = plaintext + sum(public_key[i] * random[i]) + error
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> dist(0, p - 1);
    
    // Start with plaintext as Qp
    Qp ciphertext(p, precision, plaintext);
    
    // Add randomized public key components
    for (const auto& pk : public_key) {
        // Generate random element
        BigInt rand_val = BigInt(dist(gen));
        for (int i = 1; i < noise_precision; ++i) {
            rand_val = rand_val * BigInt(p) + BigInt(dist(gen));
        }
        Zp random_elem(p, precision, rand_val);
        
        // Convert to Qp and add
        ciphertext = ciphertext + Qp(pk * random_elem);
    }
    
    // Add small error
    Qp error(p, precision, dist(gen));
    ciphertext = ciphertext + error;
    
    return ciphertext;
}

long PadicHomomorphic::decrypt(const Qp& ciphertext) {
    // Decryption: extract plaintext mod secret_key
    // Simplified: use secret key to remove the masking
    
    // Convert to Zp by taking unit part
    Zp cipher_z(p, precision, ciphertext.to_bigint());
    
    // Compute ciphertext * secret_key^(-1) to extract message + noise
    Zp sec_inv = secret_key.inverse();
    Zp temp = cipher_z * sec_inv;
    
    // Round to remove noise (in p-adic sense)
    // Extract the low-order bits as the plaintext
    BigInt val = temp.to_bigint();
    
    // Reduce modulo a reasonable message space
    long message_space = 1000000;  // Messages up to 1 million
    long plaintext = (val % BigInt(message_space)).to_long();
    
    return plaintext;
}

Qp PadicHomomorphic::add(const Qp& c1, const Qp& c2) {
    // Homomorphic addition is just p-adic addition
    return c1 + c2;
}

Qp PadicHomomorphic::multiply(const Qp& c1, const Qp& c2) {
    // Homomorphic multiplication
    // Note: noise grows with multiplication
    return c1 * c2;
}

long PadicHomomorphic::estimate_noise(const Qp& ciphertext) {
    // Estimate noise level based on valuation
    // Lower valuation means more noise
    return ciphertext.valuation();
}

Qp PadicHomomorphic::bootstrap(const Qp& ciphertext) {
    // Bootstrapping to reduce noise
    // This is a simplified version - real bootstrapping is complex
    
    // Decrypt and re-encrypt
    long plaintext = decrypt(ciphertext);
    
    // Re-encrypt with fresh randomness
    return encrypt(plaintext);
}

} // namespace crypto
} // namespace libadic
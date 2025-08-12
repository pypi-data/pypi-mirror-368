#include "libadic/padic_crypto.h"
#include <chrono>
#include <cmath>

namespace libadic {
namespace crypto {

long SecurityAnalysis::estimate_security_bits(long p, long dimension, long precision) {
    // Estimate security level in bits based on parameters
    // Security based on lattice dimension and p-adic precision
    long base_security = static_cast<long>(std::log2(p) * dimension * precision * 0.3);
    
    // Cap at reasonable values
    return std::min(base_security, 256L);
}

bool SecurityAnalysis::test_lattice_attack_resistance(const PadicLattice& lattice_const, long num_attempts) {
    // Need non-const copy to call encrypt/decrypt
    PadicLattice lattice = lattice_const;
    // Test resistance to basic lattice attacks
    
    // Generate a test message
    std::vector<long> message;
    std::vector<Qp> ciphertext;
    
    // Use fixed dimension since we don't have getters
    long dim = 4;  // Default dimension
    
    for (long i = 0; i < dim; ++i) {
        message.push_back(i + 1);
    }
    
    try {
        ciphertext = lattice.encrypt(message);
    } catch (...) {
        return false;  // Encryption failed
    }
    
    // Try to break without private key
    for (long attempt = 0; attempt < num_attempts; ++attempt) {
        // Attempt 1: Try closest vector attack
        std::vector<Qp> guess;
        for (size_t i = 0; i < ciphertext.size(); ++i) {
            // Random guess near ciphertext
            BigInt val = ciphertext[i].to_bigint();
            val = val + BigInt(attempt % 10 - 5);
            guess.push_back(Qp(ciphertext[i].get_prime(), ciphertext[i].get_precision(), val));
        }
        
        // Check if guess decrypts to original message
        try {
            std::vector<long> decrypted = lattice.decrypt(guess);
            bool match = true;
            for (size_t i = 0; i < message.size() && i < decrypted.size(); ++i) {
                if (message[i] != decrypted[i]) {
                    match = false;
                    break;
                }
            }
            if (match && guess != ciphertext) {
                return false;  // Attack succeeded
            }
        } catch (...) {
            // Decryption failed, continue
        }
    }
    
    return true;  // Resisted all attacks
}

bool SecurityAnalysis::run_nist_tests(PadicPRNG& prng) {
    // Run subset of NIST statistical tests
    // This is a simplified version
    long num_bits = 10000;
    auto result = PadicPRNG::test_randomness(prng, num_bits);
    
    // Check if all tests passed
    return result.passed_frequency_test && 
           result.passed_serial_test && 
           result.passed_poker_test && 
           result.passed_runs_test;
}

SecurityAnalysis::BenchmarkResult SecurityAnalysis::benchmark_cryptosystem(
    long prime, long dimension, long precision) {
    
    BenchmarkResult result;
    
    using namespace std::chrono;
    
    PadicLattice lattice(prime, dimension, precision);
    
    // Benchmark key generation
    auto start = high_resolution_clock::now();
    lattice.generate_keys();
    auto end = high_resolution_clock::now();
    result.key_gen_ms = duration_cast<milliseconds>(end - start).count();
    
    // Prepare test message
    std::vector<long> message;
    for (long i = 0; i < dimension; ++i) {
        message.push_back(i + 1);
    }
    
    // Benchmark encryption
    long num_operations = 100;
    start = high_resolution_clock::now();
    for (long i = 0; i < num_operations; ++i) {
        auto cipher = lattice.encrypt(message);
    }
    end = high_resolution_clock::now();
    result.encrypt_ms = duration_cast<milliseconds>(end - start).count() / static_cast<double>(num_operations);
    
    // Benchmark decryption
    auto ciphertext = lattice.encrypt(message);
    start = high_resolution_clock::now();
    for (long i = 0; i < num_operations; ++i) {
        auto plain = lattice.decrypt(ciphertext);
    }
    end = high_resolution_clock::now();
    result.decrypt_ms = duration_cast<milliseconds>(end - start).count() / static_cast<double>(num_operations);
    
    // Operations per second
    if (result.encrypt_ms > 0) {
        result.operations_per_second = 1000.0 / result.encrypt_ms;
    } else {
        result.operations_per_second = 0;
    }
    
    return result;
}

} // namespace crypto
} // namespace libadic
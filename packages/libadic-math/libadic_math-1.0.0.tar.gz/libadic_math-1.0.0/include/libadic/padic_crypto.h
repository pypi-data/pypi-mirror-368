#ifndef LIBADIC_PADIC_CRYPTO_H
#define LIBADIC_PADIC_CRYPTO_H

#include "libadic/qp.h"
#include "libadic/zp.h"
#include "libadic/elliptic_curve.h"
#include "libadic/padic_log.h"
#include "libadic/montgomery_context.h"
#include <vector>
#include <random>
#include <optional>
#include <functional>
#include <memory>

namespace libadic {

// Forward declaration for linalg namespace types
namespace linalg {
    using Matrix = std::vector<std::vector<Zp>>;
    using Vector = std::vector<Zp>;
}

namespace crypto {

/**
 * p-adic Cryptography Framework
 * 
 * Leverages unique properties of p-adic numbers for cryptographic applications:
 * 1. Non-Archimedean metric (ultrametric property)
 * 2. Different notion of "closeness" than real numbers
 * 3. Hensel lifting for efficient computations
 * 4. p-adic logarithm with different algebraic properties
 * 
 * Security relies on:
 * - Difficulty of p-adic discrete logarithm
 * - Complexity of finding close p-adic lattice points
 * - Non-linear p-adic dynamics
 */

/**
 * p-adic Lattice-based Cryptography
 * 
 * Uses p-adic lattices where the security is based on the
 * difficulty of the p-adic Shortest Vector Problem (SVP)
 */
class PadicLattice {
protected:  // Changed from private to protected for derived classes
    BigInt p;                            // Prime (now supports cryptographic sizes)
    long dimension;                      // Lattice dimension
    long precision;                      // p-adic precision
    std::vector<std::vector<Zp>> basis;  // Lattice basis
    
    // Private key: short basis
    std::vector<std::vector<Zp>> private_basis;
    
    // Public key: "bad" basis (long vectors)
    std::vector<std::vector<Zp>> public_basis;
    
private:
    // Helper methods for encryption/decryption
    long computeScaleBits(bool small_params) const;
    linalg::Matrix buildTranspose(const linalg::Matrix& basis) const;
    
    // Montgomery arithmetic optimization
    mutable std::shared_ptr<MontgomeryContext> mont_context;
    mutable std::vector<std::vector<BigInt>> public_basis_mont;  // Public basis in Montgomery form
    mutable std::vector<std::vector<BigInt>> private_basis_mont; // Private basis in Montgomery form
    mutable bool montgomery_initialized = false;
    
    void initialize_montgomery() const;
    std::vector<Zp> montgomery_matrix_vector_multiply(
        const std::vector<std::vector<BigInt>>& matrix_mont,
        const std::vector<Zp>& vector) const;
    
public:
    /**
     * Security levels for p-adic lattice cryptography
     */
    enum class SecurityLevel {
        DEMO,     // Toy parameters for testing (0-bit security)
        LEVEL_1,  // 128-bit security (comparable to AES-128)
        LEVEL_3,  // 192-bit security (comparable to AES-192)  
        LEVEL_5   // 256-bit security (comparable to AES-256)
    };
    
    /**
     * Generate a p-adic lattice cryptosystem with custom parameters
     * 
     * @param p Prime for p-adic field (BigInt for large primes)
     * @param dim Lattice dimension (security parameter)
     * @param precision p-adic precision
     */
    PadicLattice(const BigInt& p, long dim, long precision);
    
    /**
     * Generate a p-adic lattice cryptosystem with custom parameters
     * 
     * @param p Prime for p-adic field (convenience long version)
     * @param dim Lattice dimension (security parameter)
     * @param precision p-adic precision
     */
    PadicLattice(long p, long dim, long precision);
    
    /**
     * Generate a p-adic lattice cryptosystem with security level
     * Automatically selects secure parameters for the given security level
     * 
     * @param level Target security level
     */
    PadicLattice(SecurityLevel level);
    
    /**
     * Key generation using p-adic lattice reduction
     * Creates a "good" private basis and "bad" public basis
     */
    virtual void generate_keys();
    
    /**
     * Encrypt a message using public key
     * Adds p-adically small noise that's hard to remove without private key
     */
    virtual std::vector<Qp> encrypt(const std::vector<long>& message);
    
    /**
     * Decrypt using private key (short basis)
     * Uses p-adic closest vector algorithm
     */
    virtual std::vector<long> decrypt(const std::vector<Qp>& ciphertext);
    
    /**
     * p-adic norm of a vector
     * Uses ultrametric: |x+y|_p ≤ max(|x|_p, |y|_p)
     */
    static long padic_norm(const std::vector<Zp>& vec);
    
    /**
     * p-adic Gram-Schmidt orthogonalization
     * Different from real version due to ultrametric
     */
    static std::vector<std::vector<Qp>> padic_gram_schmidt(
        const std::vector<std::vector<Zp>>& basis,
        long p, long precision
    );
    
    /**
     * Find closest lattice point (p-adic metric)
     * Core of decryption algorithm
     */
    std::vector<Zp> closest_vector(const std::vector<Qp>& target) const;
    
    /**
     * Generate cryptographically secure large prime for given security level
     */
    static BigInt generate_secure_prime(SecurityLevel level);
    
    /**
     * Generate large prime near 2^bit_size for cryptographic use
     */
    static BigInt generate_large_prime(long bit_size);
    
    /**
     * Get recommended parameters for security level
     */
    struct SecurityParameters {
        BigInt prime;
        long dimension;
        long precision;
        long estimated_security_bits;
    };
    
    static SecurityParameters get_security_parameters(SecurityLevel level);
    
    // Public getters for Python bindings
    BigInt get_prime() const { return p; }
    long get_dimension() const { return dimension; }
    long get_precision() const { return precision; }
    const std::vector<std::vector<Zp>>& get_public_basis() const { return public_basis; }
    const std::vector<std::vector<Zp>>& get_private_basis() const { return private_basis; }
};

/**
 * Isogeny-based Cryptography with p-adic methods
 * 
 * Uses isogenies between supersingular elliptic curves
 * Enhanced with p-adic computations for efficiency
 */
class PadicIsogenyCrypto {
private:
    long p;                    // Prime (typically p ≡ 3 mod 4)
    long prime;               // Prime for p-adic arithmetic  
    long prec;                // Precision for computations
    EllipticCurve base_curve;  // Supersingular curve
    long degree;               // Isogeny degree
    
    // Private key: secret isogeny path
    std::vector<long> secret_path;
    
    // Public key: image curve under secret isogeny
    EllipticCurve public_curve;
    
public:
    /**
     * Initialize with supersingular curve over F_p²
     * 
     * @param p Prime for base field
     * @param precision p-adic precision for computations
     */
    PadicIsogenyCrypto(long p, long precision);
    
    /**
     * Generate keys using secret isogeny walks
     * 
     * Private key: random walk in isogeny graph
     * Public key: endpoint curve
     */
    void generate_keys();
    
    /**
     * SIDH-style key exchange
     * Alice and Bob compute shared secret via parallel isogenies
     */
    struct KeyExchangeData {
        EllipticCurve curve;
        std::vector<EllipticCurve::Point> kernel_generators;
    };
    
    KeyExchangeData generate_exchange_data() const;
    
    /**
     * Compute shared secret from exchange data
     * Uses p-adic methods for efficient isogeny computation
     */
    BigInt compute_shared_secret(const KeyExchangeData& other_data) const;
    
    /**
     * p-adic Vélu's formula for isogeny computation
     * More efficient than standard methods for certain primes
     */
    static EllipticCurve compute_isogeny_padic(
        const EllipticCurve& E,
        const std::vector<EllipticCurve::Point>& kernel,
        long p, long precision
    );
    
    /**
     * Check if curve is supersingular using p-adic methods
     * Counts points mod p^n for efficiency
     */
    static bool is_supersingular_padic(const EllipticCurve& E, long p);
    
    /**
     * Find j-invariant of isogenous curve
     * Uses modular polynomials and p-adic lifting
     */
    static Qp isogenous_j_invariant(const EllipticCurve& E, long ell, long p, long precision);
    
    /**
     * Encrypt message using isogeny-based scheme
     */
    std::vector<Qp> encrypt(const std::vector<long>& message);
    
    /**
     * Decrypt ciphertext using private isogeny
     */
    std::vector<long> decrypt(const std::vector<Qp>& ciphertext);
};

/**
 * p-adic Pseudorandom Number Generator
 * 
 * Based on chaotic p-adic dynamics
 * Uses iterations of p-adic rational functions
 */
class PadicPRNG {
private:
    long p;                // Prime
    long precision;        // Working precision
    Zp state;             // Current state
    
    // Parameters for the rational map
    Zp a, b, c, d;        // f(x) = (ax + b)/(cx + d)
    
    // Non-linear map for better mixing
    std::function<Zp(const Zp&)> mixing_function;
    
public:
    /**
     * Initialize PRNG with seed
     * 
     * @param p Prime for p-adic field
     * @param seed Initial seed value
     * @param precision Working precision
     */
    PadicPRNG(long p, const BigInt& seed, long precision);
    
    /**
     * Generate next p-adic pseudorandom number
     * Uses chaotic dynamics of rational map
     */
    Zp next();
    
    /**
     * Generate random bits
     * Extracts bits from p-adic digits
     */
    std::vector<bool> generate_bits(size_t num_bits);
    
    /**
     * Generate random integer in range [0, max)
     */
    long generate_uniform(long max);
    
    /**
     * Set custom mixing function for enhanced security
     * Default uses f(x) = x^p + ax + b (mod p^n)
     */
    void set_mixing_function(std::function<Zp(const Zp&)> f);
    
    /**
     * Statistical tests for randomness
     */
    struct RandomnessTestResult {
        bool passed_frequency_test;
        bool passed_serial_test;
        bool passed_poker_test;
        bool passed_runs_test;
        double chi_square_statistic;
        std::string summary;
    };
    
    static RandomnessTestResult test_randomness(PadicPRNG& prng, size_t sample_size);
    
    /**
     * Period detection (should be large for cryptographic use)
     */
    static std::optional<long> detect_period(PadicPRNG& prng, long max_iterations);
};

/**
 * p-adic Hash Function
 * 
 * Cryptographic hash using p-adic arithmetic
 * Provides avalanche effect through p-adic chaos
 */
class PadicHash {
private:
    long p;
    long precision;
    long output_size;  // in p-adic digits
    
    // Compression function parameters
    std::vector<Zp> round_constants;
    
public:
    PadicHash(long p, long output_size, long precision);
    
    /**
     * Hash arbitrary data to p-adic number
     * 
     * @param data Input data
     * @return Hash value as p-adic number
     */
    Zp hash(const std::vector<uint8_t>& data);
    
    /**
     * Merkle-Damgård construction with p-adic compression
     */
    Zp compress(const Zp& state, const Zp& block);
    
    /**
     * Convert hash to hex string for standard representation
     */
    std::string to_hex(const Zp& hash_value);
    
    /**
     * Verify hash properties (avalanche, collision resistance)
     */
    static bool verify_security_properties(long p, long precision);
};

/**
 * p-adic Digital Signature
 * 
 * Signature scheme based on p-adic discrete logarithm
 */
class PadicSignature {
private:
    long p;
    long precision;
    
    // Generator of multiplicative group
    Zp generator;
    
    // Private key: random exponent
    BigInt private_key;
    
    // Public key: g^private_key (p-adically)
    Zp public_key;
    
public:
    PadicSignature(long p, long precision);
    
    /**
     * Generate signing/verification keys
     */
    void generate_keys();
    
    /**
     * Sign a message
     * Uses p-adic variant of DSA/Schnorr
     */
    struct Signature {
        Zp r;  // Commitment
        Zp s;  // Response
    };
    
    Signature sign(const std::vector<uint8_t>& message);
    
    /**
     * Verify signature
     */
    bool verify(const std::vector<uint8_t>& message, const Signature& sig, const Zp& public_key);
    
    /**
     * Get public key
     */
    const Zp& get_public_key() const { return public_key; }
    
    /**
     * p-adic discrete logarithm problem (hard problem)
     * Given g, h in Z_p*, find x such that g^x ≡ h (mod p^n)
     */
    static std::optional<BigInt> padic_discrete_log(const Zp& base, const Zp& target, long max_iterations);
};

/**
 * Homomorphic Encryption using p-adic numbers
 * 
 * Allows computation on encrypted data
 * Uses p-adic structure for noise management
 */
class PadicHomomorphic {
private:
    long p;
    long precision;
    long noise_precision;  // Precision for noise terms
    
    // Secret key
    Zp secret_key;
    
    // Public key components
    std::vector<Zp> public_key;
    
public:
    PadicHomomorphic(long p, long precision, long noise_precision);
    
    void generate_keys();
    
    /**
     * Encrypt with controlled noise
     * Noise is p-adically small but hard to remove
     */
    Qp encrypt(long plaintext);
    
    /**
     * Decrypt by removing noise with secret key
     */
    long decrypt(const Qp& ciphertext);
    
    /**
     * Homomorphic addition
     * c1 + c2 encrypts m1 + m2
     */
    static Qp add(const Qp& c1, const Qp& c2);
    
    /**
     * Homomorphic multiplication (increases noise)
     * c1 * c2 encrypts m1 * m2
     */
    static Qp multiply(const Qp& c1, const Qp& c2);
    
    /**
     * Noise estimation
     * Track noise growth through operations
     */
    static long estimate_noise(const Qp& ciphertext);
    
    /**
     * Bootstrapping (refresh ciphertext to reduce noise)
     * Complex operation using p-adic properties
     */
    Qp bootstrap(const Qp& ciphertext);
};

/**
 * Security Analysis Tools
 */
class SecurityAnalysis {
public:
    /**
     * Estimate security level in bits
     * Based on best known attacks
     */
    static long estimate_security_bits(long p, long dimension, long precision);
    
    /**
     * Test resistance to lattice attacks
     */
    static bool test_lattice_attack_resistance(const PadicLattice& lattice, long attack_iterations);
    
    /**
     * Test PRNG quality with NIST test suite adaptation
     */
    static bool run_nist_tests(PadicPRNG& prng);
    
    /**
     * Benchmark encryption/decryption speed
     */
    struct BenchmarkResult {
        double key_gen_ms;
        double encrypt_ms;
        double decrypt_ms;
        double operations_per_second;
    };
    
    static BenchmarkResult benchmark_cryptosystem(long p, long dimension, long precision);
};

} // namespace crypto
} // namespace libadic

#endif // LIBADIC_PADIC_CRYPTO_H
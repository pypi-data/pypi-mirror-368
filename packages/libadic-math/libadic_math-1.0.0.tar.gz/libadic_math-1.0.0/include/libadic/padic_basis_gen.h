#ifndef LIBADIC_PADIC_BASIS_GEN_H
#define LIBADIC_PADIC_BASIS_GEN_H

#include "libadic/qp.h"
#include "libadic/zp.h"
#include "libadic/padic_linear_algebra.h"
#include <vector>
#include <random>
#include <functional>

namespace libadic {
namespace crypto {

/**
 * p-adic Basis Generation for Cryptographic Lattices
 * 
 * Generates bases with specific properties for cryptographic security:
 * - Controlled p-adic norms (valuation distribution)
 * - Hidden structure (trapdoors)
 * - Resistance to reduction attacks
 */
class PadicBasisGenerator {
public:
    /**
     * Distribution types for basis generation
     */
    enum class Distribution {
        UNIFORM,           // Uniform over Z_p
        GAUSSIAN_PADIC,    // p-adic Gaussian (concentrated at high valuations)
        DISCRETE_GAUSSIAN, // Discrete Gaussian mod p^n
        BINARY,           // Binary {0,1} coefficients
        TERNARY,          // Ternary {-1,0,1} coefficients
        SPARSE            // Sparse with controlled density
    };
    
    /**
     * Security levels (NIST-like)
     */
    enum class SecurityLevel {
        LEVEL_1,  // 128-bit security
        LEVEL_3,  // 192-bit security
        LEVEL_5   // 256-bit security
    };
    
    /**
     * Generate cryptographically secure basis
     * 
     * @param p Prime
     * @param dimension Lattice dimension
     * @param precision p-adic precision
     * @param level Security level
     * @return Generated basis with security guarantees
     */
    static linalg::Matrix generate_secure_basis(
        long p,
        long dimension,
        long precision,
        SecurityLevel level
    );
    
    /**
     * Generate basis with specific distribution
     * 
     * @param p Prime
     * @param dimension Lattice dimension
     * @param precision p-adic precision
     * @param dist Distribution type
     * @param params Distribution parameters
     * @return Generated basis
     */
    static linalg::Matrix generate_with_distribution(
        long p,
        long dimension,
        long precision,
        Distribution dist,
        const std::vector<double>& params = {}
    );
    
    /**
     * Generate trapdoor basis pair
     * 
     * @param p Prime
     * @param dimension Lattice dimension
     * @param precision p-adic precision
     * @return Pair of (public_basis, private_basis)
     */
    static std::pair<linalg::Matrix, linalg::Matrix> generate_trapdoor_basis(
        const BigInt& p,
        long dimension,
        long precision
    );
    
    // Convenience overload for backward compatibility
    static std::pair<linalg::Matrix, linalg::Matrix> generate_trapdoor_basis(
        long p,
        long dimension,
        long precision
    );
    
    /**
     * Generate basis for specific cryptographic schemes
     */
    
    // For NTRU-like schemes
    static linalg::Matrix generate_ntru_basis(
        long p,
        long dimension,
        long precision,
        long df,  // Number of +1s in f
        long dg   // Number of +1s in g
    );
    
    // For LWE-like schemes
    static linalg::Matrix generate_lwe_basis(
        long p,
        long dimension,
        long precision,
        double noise_rate
    );
    
    // For GGH-like schemes
    static linalg::Matrix generate_ggh_basis(
        long p,
        long dimension,
        long precision,
        double orthogonality_defect
    );
    
    /**
     * Generate basis with controlled singular values
     * Important for security against SVP attacks
     */
    static linalg::Matrix generate_with_singular_values(
        long p,
        long dimension,
        long precision,
        const std::vector<long>& singular_valuations
    );
    
    /**
     * Generate ideal lattice basis
     * Structured lattices for efficiency
     */
    static linalg::Matrix generate_ideal_basis(
        long p,
        long dimension,
        long precision,
        const std::vector<Zp>& ideal_generator
    );
    
    /**
     * Generate cyclic/circulant basis
     * First row defines entire matrix
     */
    static linalg::Matrix generate_cyclic_basis(
        long p,
        long dimension,
        long precision,
        const linalg::Vector& first_row
    );
    
    /**
     * Quality metrics for generated bases
     */
    struct BasisQuality {
        double hermite_factor;
        double orthogonality_defect;
        long shortest_vector_valuation;
        double condition_number;
        bool is_reduced;
        bool meets_security_requirements;
    };
    
    static BasisQuality analyze_basis(
        const linalg::Matrix& basis,
        long p,
        long precision,
        SecurityLevel level
    );
    
    /**
     * Randomness extraction from p-adic sources
     */
    static linalg::Matrix extract_random_basis(
        long p,
        long dimension,
        long precision,
        std::function<Zp()> random_source
    );
    
    /**
     * Helper: Generate p-adic Gaussian samples
     */
    static Zp sample_padic_gaussian(
        long p,
        long precision,
        long center_valuation,
        double sigma,
        std::mt19937& gen
    );
    
    /**
     * Helper: Generate discrete Gaussian samples
     */
    static Zp sample_discrete_gaussian(
        long p,
        long precision,
        double sigma,
        std::mt19937& gen
    );
    
    /**
     * Helper: Apply random unimodular transformation
     */
    static linalg::Matrix apply_unimodular_transform(
        const linalg::Matrix& basis,
        long p,
        long precision,
        std::mt19937& gen
    );
    
private:
    
    /**
     * Helper: Ensure basis has full rank
     */
    static bool ensure_full_rank(
        linalg::Matrix& basis,
        long p,
        long precision
    );
    
    /**
     * Helper: Balance basis for security
     */
    static void balance_basis(
        linalg::Matrix& basis,
        long p,
        long precision
    );
};

/**
 * Advanced basis generation for specific attacks/defenses
 */
class AdvancedBasisGen {
public:
    /**
     * Generate basis resistant to LLL reduction
     */
    static linalg::Matrix generate_lll_resistant(
        long p,
        long dimension,
        long precision,
        double gap_factor
    );
    
    /**
     * Generate basis resistant to BKZ reduction
     */
    static linalg::Matrix generate_bkz_resistant(
        long p,
        long dimension,
        long precision,
        long block_size
    );
    
    /**
     * Generate basis with planted shortest vector
     * For cryptanalysis testing
     */
    static std::pair<linalg::Matrix, linalg::Vector> generate_with_planted_vector(
        long p,
        long dimension,
        long precision,
        long planted_valuation
    );
    
    /**
     * Generate basis from error-correcting code
     * Provides additional structure
     */
    static linalg::Matrix generate_from_code(
        long p,
        long dimension,
        long precision,
        const std::vector<std::vector<Zp>>& generator_matrix
    );
    
    /**
     * Generate basis with hidden sublattice
     * For hierarchical schemes
     */
    static linalg::Matrix generate_with_sublattice(
        long p,
        long dimension,
        long precision,
        long sublattice_dimension,
        long sublattice_index
    );
};

/**
 * Noise generation for lattice cryptography
 */
class NoiseGenerator {
public:
    /**
     * Generate p-adically small noise
     * High valuation = small in p-adic metric
     */
    static linalg::Vector generate_small_noise(
        long p,
        long dimension,
        long precision,
        long min_valuation
    );
    
    /**
     * Generate noise with specific distribution
     */
    static linalg::Vector generate_noise(
        long p,
        long dimension,
        long precision,
        PadicBasisGenerator::Distribution dist,
        const std::vector<double>& params = {}
    );
    
    /**
     * Generate flooding noise
     * Overwhelms existing noise for security
     */
    static linalg::Vector generate_flooding_noise(
        long p,
        long dimension,
        long precision,
        long flooding_valuation
    );
    
    /**
     * Generate noise for specific security level
     */
    static linalg::Vector generate_secure_noise(
        long p,
        long dimension,
        long precision,
        PadicBasisGenerator::SecurityLevel level
    );
    
    /**
     * Verify noise meets security requirements
     */
    static bool verify_noise_security(
        const linalg::Vector& noise,
        long p,
        long precision,
        PadicBasisGenerator::SecurityLevel level
    );
};

} // namespace crypto
} // namespace libadic

#endif // LIBADIC_PADIC_BASIS_GEN_H
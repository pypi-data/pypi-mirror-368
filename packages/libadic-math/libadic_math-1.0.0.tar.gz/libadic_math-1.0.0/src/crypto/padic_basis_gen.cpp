#include "libadic/padic_basis_gen.h"
#include <cmath>
#include <algorithm>
#include <numeric>
#include <stdexcept>

namespace libadic {
namespace crypto {

// PadicBasisGenerator implementation
linalg::Matrix PadicBasisGenerator::generate_secure_basis(
    long p,
    long dimension,
    long precision,
    SecurityLevel level) {
    
    // Determine parameters based on security level
    long min_valuation = 2;
    long max_valuation = precision / 3;
    Distribution dist = Distribution::DISCRETE_GAUSSIAN;
    
    switch (level) {
        case SecurityLevel::LEVEL_1:
            min_valuation = 2;
            max_valuation = precision / 3;
            dist = Distribution::DISCRETE_GAUSSIAN;
            break;
        case SecurityLevel::LEVEL_3:
            min_valuation = 3;
            max_valuation = precision / 2;
            dist = Distribution::GAUSSIAN_PADIC;
            break;
        case SecurityLevel::LEVEL_5:
            min_valuation = 4;
            max_valuation = 2 * precision / 3;
            dist = Distribution::GAUSSIAN_PADIC;
            break;
    }
    
    // Generate basis with appropriate distribution
    std::vector<double> params = {
        static_cast<double>(min_valuation),
        static_cast<double>(max_valuation),
        std::sqrt(static_cast<double>(dimension))  // sigma
    };
    
    auto basis = generate_with_distribution(p, dimension, precision, dist, params);
    
    // Apply security transformations
    std::random_device rd;
    std::mt19937 gen(rd());
    
    // Add controlled structure for security
    basis = apply_unimodular_transform(basis, p, precision, gen);
    
    // Ensure full rank
    if (!ensure_full_rank(basis, p, precision)) {
        // Regenerate if rank deficient
        return generate_secure_basis(p, dimension, precision, level);
    }
    
    // Balance for security
    balance_basis(basis, p, precision);
    
    return basis;
}

linalg::Matrix PadicBasisGenerator::generate_with_distribution(
    long p,
    long dimension,
    long precision,
    Distribution dist,
    const std::vector<double>& params) {
    
    std::random_device rd;
    std::mt19937 gen(rd());
    
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    switch (dist) {
        case Distribution::UNIFORM: {
            std::uniform_int_distribution<long> uniform(0, p * p);
            for (long i = 0; i < dimension; ++i) {
                for (long j = 0; j < dimension; ++j) {
                    basis[i][j] = Zp(p, precision, uniform(gen));
                }
            }
            break;
        }
        
        case Distribution::GAUSSIAN_PADIC: {
            long center_val = params.empty() ? precision / 2 : static_cast<long>(params[0]);
            double sigma = params.size() < 2 ? 1.0 : params[1];
            
            for (long i = 0; i < dimension; ++i) {
                for (long j = 0; j < dimension; ++j) {
                    basis[i][j] = sample_padic_gaussian(p, precision, center_val, sigma, gen);
                }
            }
            break;
        }
        
        case Distribution::DISCRETE_GAUSSIAN: {
            double sigma = params.empty() ? std::sqrt(dimension) : params[0];
            
            for (long i = 0; i < dimension; ++i) {
                for (long j = 0; j < dimension; ++j) {
                    basis[i][j] = sample_discrete_gaussian(p, precision, sigma, gen);
                }
            }
            break;
        }
        
        case Distribution::BINARY: {
            std::bernoulli_distribution binary(0.5);
            for (long i = 0; i < dimension; ++i) {
                for (long j = 0; j < dimension; ++j) {
                    basis[i][j] = Zp(p, precision, binary(gen) ? 1 : 0);
                }
            }
            break;
        }
        
        case Distribution::TERNARY: {
            std::uniform_int_distribution<> ternary(-1, 1);
            for (long i = 0; i < dimension; ++i) {
                for (long j = 0; j < dimension; ++j) {
                    basis[i][j] = Zp(p, precision, ternary(gen));
                }
            }
            break;
        }
        
        case Distribution::SPARSE: {
            double density = params.empty() ? 0.3 : params[0];
            std::bernoulli_distribution is_nonzero(density);
            std::uniform_int_distribution<long> value_dist(1, p);
            
            for (long i = 0; i < dimension; ++i) {
                for (long j = 0; j < dimension; ++j) {
                    if (is_nonzero(gen)) {
                        basis[i][j] = Zp(p, precision, value_dist(gen));
                    } else {
                        basis[i][j] = Zp(p, precision, 0);
                    }
                }
            }
            break;
        }
    }
    
    return basis;
}

std::pair<linalg::Matrix, linalg::Matrix> PadicBasisGenerator::generate_trapdoor_basis(
    const BigInt& p,
    long dimension,
    long precision) {
    
    std::random_device rd;
    std::mt19937 gen(rd());
    
    // STEP 1: Generate a "good" private basis (short, nearly orthogonal)
    linalg::Matrix private_basis(dimension, linalg::Vector(dimension));
    
    // Create private basis with controlled short vectors
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            if (i == j) {
                // Diagonal: small unit values (avoid multiples of p)
                long small_val = 2 + (gen() % 6); // 2-7
                long p_long = p.to_long();
                if (p_long != 0 && (small_val % p_long) == 0) {
                    small_val += 1; // ensure unit
                }
                private_basis[i][j] = Zp(p, precision, small_val);
            } else if (std::abs(i - j) == 1) {
                // Near-diagonal: very small values for mild non-orthogonality
                long tiny_val = (gen() % 3); // 0,1,2 - mostly zeros
                private_basis[i][j] = Zp(p, precision, tiny_val);
            } else {
                // Off-diagonal: mostly zeros (nearly orthogonal)
                private_basis[i][j] = Zp(p, precision, 0);
            }
        }
    }
    
    // STEP 2: Generate "bad" public basis via unimodular transformation
    // This creates the trapdoor: same lattice, but harder for CVP
    linalg::Matrix public_basis(dimension, linalg::Vector(dimension));
    
    // Initialize with private basis
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            public_basis[i][j] = private_basis[i][j];
        }
    }
    
    // Apply aggressive unimodular transformations to make public basis "bad"
    // These preserve the lattice but make CVP much harder
    long rounds = std::max(1L, dimension * 2);
    for (long round = 0; round < rounds; ++round) {
        long i = gen() % dimension;
        long j = gen() % dimension;
        if (i != j) {
            // Row operation: add random multiple of row i to row j
            // This preserves determinant and lattice span
            // Use small unit multipliers to improve numerical stability in Z_p
            static const long choices[] = {-3, -2, -1, 1, 2, 3};
            long multiplier = choices[gen() % 6];
            if (multiplier != 0) {
                for (long col = 0; col < dimension; ++col) {
                    BigInt new_val = public_basis[j][col].get_value() + 
                                   BigInt(multiplier) * public_basis[i][col].get_value();
                    public_basis[j][col] = Zp(p, precision, new_val);
                }
            }
        }
    }
    
    return {public_basis, private_basis};
}

std::pair<linalg::Matrix, linalg::Matrix> PadicBasisGenerator::generate_trapdoor_basis(
    long p,
    long dimension,
    long precision) {
    return generate_trapdoor_basis(BigInt(p), dimension, precision);
}

linalg::Matrix PadicBasisGenerator::generate_ntru_basis(
    long p,
    long dimension,
    long precision,
    long df,
    long dg) {
    
    std::random_device rd;
    std::mt19937 gen(rd());
    
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    // Generate NTRU-like structure
    // f and g are sparse ternary polynomials
    std::vector<long> f_indices, g_indices;
    
    // Random positions for non-zero coefficients
    std::vector<long> positions(dimension);
    std::iota(positions.begin(), positions.end(), 0);
    
    std::shuffle(positions.begin(), positions.end(), gen);
    
    for (long i = 0; i < df && i < dimension; ++i) {
        f_indices.push_back(positions[i]);
    }
    
    std::shuffle(positions.begin(), positions.end(), gen);
    
    for (long i = 0; i < dg && i < dimension; ++i) {
        g_indices.push_back(positions[i]);
    }
    
    // Construct basis matrix
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            if (i == j) {
                // Identity part
                basis[i][j] = Zp(p, precision, 1);
            } else {
                // NTRU structure
                long idx_diff = (j - i + dimension) % dimension;
                
                bool in_f = std::find(f_indices.begin(), f_indices.end(), idx_diff) != f_indices.end();
                bool in_g = std::find(g_indices.begin(), g_indices.end(), idx_diff) != g_indices.end();
                
                if (in_f) {
                    basis[i][j] = Zp(p, precision, gen() % 2 ? 1 : -1);
                } else if (in_g) {
                    basis[i][j] = Zp(p, precision, gen() % 2 ? 1 : -1);
                } else {
                    basis[i][j] = Zp(p, precision, 0);
                }
            }
        }
    }
    
    return basis;
}

linalg::Matrix PadicBasisGenerator::generate_lwe_basis(
    long p,
    long dimension,
    long precision,
    double noise_rate) {
    
    std::random_device rd;
    std::mt19937 gen(rd());
    
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    // LWE structure: A is random, s is secret, e is small noise
    std::uniform_int_distribution<long> uniform(0, p - 1);
    std::normal_distribution<double> gaussian(0, noise_rate * p);
    
    // Generate random matrix A
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            if (i < dimension / 2) {
                // Upper part: random matrix A
                basis[i][j] = Zp(p, precision, uniform(gen));
            } else {
                // Lower part: identity + noise
                if (i - dimension/2 == j) {
                    basis[i][j] = Zp(p, precision, p);  // Scaled identity
                } else {
                    // Small noise
                    long noise = static_cast<long>(std::abs(gaussian(gen))) % p;
                    basis[i][j] = Zp(p, precision, noise);
                }
            }
        }
    }
    
    return basis;
}

linalg::Matrix PadicBasisGenerator::generate_ggh_basis(
    long p,
    long dimension,
    long precision,
    double orthogonality_defect) {
    
    // Start with nearly orthogonal basis
    auto basis = linalg::CryptoMatrixGen::generate_orthogonal_basis(p, precision, dimension);
    
    // Add controlled non-orthogonality
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<double> uniform(0, 1);
    
    for (long i = 0; i < dimension; ++i) {
        for (long j = i + 1; j < dimension; ++j) {
            if (uniform(gen) < orthogonality_defect) {
                // Add small perturbation to destroy orthogonality
                long perturb_val = gen() % p;
                basis[i][j] = basis[i][j] + Zp(p, precision, perturb_val);
            }
        }
    }
    
    return basis;
}

linalg::Matrix PadicBasisGenerator::generate_with_singular_values(
    long p,
    long dimension,
    long precision,
    const std::vector<long>& singular_valuations) {
    
    if (singular_valuations.size() != static_cast<size_t>(dimension)) {
        throw std::invalid_argument("Number of singular values must match dimension");
    }
    
    // Create diagonal matrix with specified singular values
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            if (i == j) {
                // Diagonal: singular value
                BigInt value = BigInt(p).pow(singular_valuations[i]);
                basis[i][j] = Zp(p, precision, value);
            } else {
                basis[i][j] = Zp(p, precision, 0);
            }
        }
    }
    
    // Apply random orthogonal transformations
    std::random_device rd;
    std::mt19937 gen(rd());
    
    basis = apply_unimodular_transform(basis, p, precision, gen);
    
    return basis;
}

linalg::Matrix PadicBasisGenerator::generate_ideal_basis(
    long /* p */,
    long dimension,
    long /* precision */,
    const std::vector<Zp>& ideal_generator) {
    
    if (ideal_generator.size() != static_cast<size_t>(dimension)) {
        throw std::invalid_argument("Ideal generator must have dimension elements");
    }
    
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    // Each row is a rotation of the ideal generator
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            basis[i][j] = ideal_generator[(j - i + dimension) % dimension];
        }
    }
    
    return basis;
}

linalg::Matrix PadicBasisGenerator::generate_cyclic_basis(
    long /* p */,
    long dimension,
    long /* precision */,
    const linalg::Vector& first_row) {
    
    if (first_row.size() != static_cast<size_t>(dimension)) {
        throw std::invalid_argument("First row must have dimension elements");
    }
    
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    // Circulant matrix: each row is cyclic shift of previous
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            basis[i][j] = first_row[(j - i + dimension) % dimension];
        }
    }
    
    return basis;
}

PadicBasisGenerator::BasisQuality PadicBasisGenerator::analyze_basis(
    const linalg::Matrix& basis,
    long p,
    long precision,
    SecurityLevel level) {
    
    BasisQuality quality;
    
    long dim = basis.size();
    
    // Compute Hermite factor (simplified)
    // HF = ||b1|| / (det(L)^(1/n))
    linalg::PadicMatrix mat(p, precision, basis);
    Zp det = mat.determinant();
    
    long b1_norm = linalg::PadicVector::padic_norm(basis[0]);
    // Use valuation for quality metrics instead of trying to convert large BigInt
    // The determinant's p-adic valuation gives us the quality information we need
    long det_val = det.valuation();
    double quality_metric = std::abs(det_val - b1_norm * dim);
    
    // Lower is better for this metric
    quality.hermite_factor = std::exp(-quality_metric / dim);
    
    // Compute orthogonality defect
    quality.orthogonality_defect = linalg::CryptoMatrixGen::orthogonality_defect(basis, p, precision);
    
    // Find shortest vector valuation (approximation)
    quality.shortest_vector_valuation = precision;
    for (const auto& row : basis) {
        long norm = linalg::PadicVector::padic_norm(row);
        if (norm < quality.shortest_vector_valuation) {
            quality.shortest_vector_valuation = norm;
        }
    }
    
    // Condition number (ratio of largest to smallest singular value)
    // Simplified: use ratio of norms
    long max_norm = 0;
    long min_norm = precision;
    for (const auto& row : basis) {
        long norm = linalg::PadicVector::padic_norm(row);
        if (norm > max_norm) max_norm = norm;
        if (norm < min_norm) min_norm = norm;
    }
    quality.condition_number = (min_norm == 0) ? 1e9 : static_cast<double>(max_norm) / min_norm;
    
    // Check if reduced (simplified check)
    // With our new metric, values close to 1 are good
    quality.is_reduced = quality.hermite_factor > 0.3;  // exp(-quality) > 0.3 means good quality
    
    // Check security requirements based on level
    switch (level) {
        case SecurityLevel::LEVEL_1:
            quality.meets_security_requirements = 
                quality.shortest_vector_valuation >= 2 &&
                quality.orthogonality_defect > 0.5;
            break;
        case SecurityLevel::LEVEL_3:
            quality.meets_security_requirements = 
                quality.shortest_vector_valuation >= 3 &&
                quality.orthogonality_defect > 0.7;
            break;
        case SecurityLevel::LEVEL_5:
            quality.meets_security_requirements = 
                quality.shortest_vector_valuation >= 4 &&
                quality.orthogonality_defect > 0.9;
            break;
    }
    
    return quality;
}

linalg::Matrix PadicBasisGenerator::extract_random_basis(
    long p,
    long dimension,
    long precision,
    std::function<Zp()> random_source) {
    
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    for (long i = 0; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            basis[i][j] = random_source();
        }
    }
    
    // Ensure full rank
    if (!ensure_full_rank(basis, p, precision)) {
        // Add identity to ensure invertibility
        for (long i = 0; i < dimension; ++i) {
            basis[i][i] = basis[i][i] + Zp(p, precision, 1);
        }
    }
    
    return basis;
}

// Private helper methods
Zp PadicBasisGenerator::sample_padic_gaussian(
    long p,
    long precision,
    long center_valuation,
    double sigma,
    std::mt19937& gen) {
    
    // Sample valuation from discrete Gaussian centered at center_valuation
    std::normal_distribution<double> gaussian(center_valuation, sigma);
    long valuation = static_cast<long>(std::round(gaussian(gen)));
    
    // Clamp to valid range
    valuation = std::max(0L, std::min(valuation, precision - 1));
    
    // Sample unit part uniformly
    std::uniform_int_distribution<long> unit_dist(1, p - 1);
    long unit = unit_dist(gen);
    
    // Construct p-adic number
    BigInt value = BigInt(unit) * BigInt(p).pow(valuation);
    
    return Zp(p, precision, value);
}

// Constant-time discrete Gaussian sampler over Z, reduced modulo p^precision
// Implementation uses a bounded support CDT with constant-time selection.
Zp PadicBasisGenerator::sample_discrete_gaussian(
    long p,
    long precision,
    double sigma,
    std::mt19937& gen) {
    using u64 = unsigned long long;

    // Choose symmetric support width t ≈ ceil(6*sigma) (captures > 99.7%)
    long t = static_cast<long>(std::ceil(6.0 * std::max(0.5, sigma)));
    t = std::max(3L, std::min(64L, t)); // clamp for stability

    // Precompute weights w[k] ∝ exp(-k^2/(2*sigma^2)) for k = 0..t
    // Accumulate into 64-bit scaled CDF for constant-time sampling
    std::vector<double> w(t + 1, 0.0);
    const double two_sigma2 = 2.0 * sigma * sigma;
    w[0] = 1.0;
    double sumw = w[0];
    for (long k = 1; k <= t; ++k) {
        w[k] = std::exp(-(static_cast<double>(k) * static_cast<double>(k)) / two_sigma2);
        sumw += (k == 0 ? 1.0 : 2.0) * w[k]; // account for symmetry
    }

    // Build CDF over nonnegative k with symmetric duplication
    // We map a uniform 64-bit r into signed sample using constant-time selection
    std::vector<u64> cdf_nonneg(t + 1, 0);
    const long scale_bits = 62; // keep headroom
    const u64 scale = (scale_bits >= 63) ? (std::numeric_limits<u64>::max() >> 1) : (1ULL << scale_bits);

    double accum = 0.0;
    for (long k = 0; k <= t; ++k) {
        double mass = (k == 0 ? w[k] : 2.0 * w[k]);
        accum += mass / sumw;
        long double scaled = static_cast<long double>(accum) * static_cast<long double>(scale);
        u64 val = static_cast<u64>(scaled);
        // Ensure non-decreasing CDF
        if (k > 0 && val < cdf_nonneg[k - 1]) val = cdf_nonneg[k - 1];
        cdf_nonneg[k] = val;
    }
    cdf_nonneg[t] = scale; // ensure full coverage

    // Draw 64-bit randomness and map via constant-time search
    auto rng32 = [&]() -> u64 { return static_cast<u64>(gen()); };
    u64 r = (rng32() << 32) ^ rng32();
    r &= (scale - 1ULL); // confine to [0, scale)

    // Constant-time select index k such that r < cdf_nonneg[k]
    u64 select_mask = 0ULL;
    long sel_k = 0;
    for (long k = 0; k <= t; ++k) {
        // mask = 1 if r < cdf[k] and we haven't selected yet
        u64 lt = (r < cdf_nonneg[k]) ? 1ULL : 0ULL;
        u64 take = lt & (~select_mask & 1ULL);
        sel_k = static_cast<long>(take ? k : sel_k);
        select_mask |= take;
    }

    // For k=0, sign is 0. For k>0, choose random sign bit in constant pattern
    u64 signbit = (rng32() & 1ULL);
    long sample = (sel_k == 0) ? 0 : static_cast<long>((signbit ? -sel_k : sel_k));

    // Reduce modulo p^precision to Zp
    BigInt modulus = BigInt(p).pow(precision);
    BigInt value = BigInt(sample) % modulus;
    if (value < BigInt(0)) value = value + modulus;
    return Zp(p, precision, value);
}

linalg::Matrix PadicBasisGenerator::apply_unimodular_transform(
    const linalg::Matrix& basis,
    long p,
    long precision,
    std::mt19937& /* gen */) {
    
    long dim = basis.size();
    
    // Generate random unimodular matrix
    auto U = linalg::PadicMatrix::random_unimodular(p, precision, dim);
    
    // Apply transformation
    linalg::PadicMatrix basis_mat(p, precision, basis);
    linalg::PadicMatrix transformed = U * basis_mat;
    
    return transformed.get_data();
}

bool PadicBasisGenerator::ensure_full_rank(
    linalg::Matrix& basis,
    long p,
    long precision) {
    
    linalg::PadicMatrix mat(p, precision, basis);
    long rank = mat.rank();
    
    if (rank < static_cast<long>(basis.size())) {
        // Try to fix by adding small perturbations
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<long> small_dist(1, p);
        
        for (long i = 0; i < static_cast<long>(basis.size()); ++i) {
            if (i < rank) continue;
            
            // Add small random values to make linearly independent
            for (long j = 0; j < static_cast<long>(basis[i].size()); ++j) {
                basis[i][j] = basis[i][j] + Zp(p, precision, small_dist(gen));
            }
        }
        
        // Re-check rank
        linalg::PadicMatrix fixed_mat(p, precision, basis);
        return fixed_mat.rank() == static_cast<long>(basis.size());
    }
    
    return true;
}

void PadicBasisGenerator::balance_basis(
    linalg::Matrix& basis,
    long p,
    long precision) {
    
    // Balance norms of basis vectors
    std::vector<long> norms;
    for (const auto& row : basis) {
        norms.push_back(linalg::PadicVector::padic_norm(row));
    }
    
    // Find median norm
    std::sort(norms.begin(), norms.end());
    long median_norm = norms[norms.size() / 2];
    
    // Scale vectors to balance around median
    for (size_t i = 0; i < basis.size(); ++i) {
        long current_norm = linalg::PadicVector::padic_norm(basis[i]);
        long diff = median_norm - current_norm;
        
        if (std::abs(diff) > precision / 4) {
            // Scale vector
            BigInt scale_factor = BigInt(p).pow(diff / 2);
            for (auto& elem : basis[i]) {
                elem = elem * Zp(p, precision, scale_factor);
            }
        }
    }
}

// AdvancedBasisGen implementation
linalg::Matrix AdvancedBasisGen::generate_lll_resistant(
    long p,
    long dimension,
    long precision,
    double gap_factor) {
    
    // Generate basis with controlled gap between successive minima
    std::vector<long> singular_vals;
    
    for (long i = 0; i < dimension; ++i) {
        // Exponentially decreasing singular values with controlled gap
        long val = static_cast<long>(precision * (1.0 - i * gap_factor / dimension));
        val = std::max(1L, val);
        singular_vals.push_back(val);
    }
    
    return PadicBasisGenerator::generate_with_singular_values(
        p, dimension, precision, singular_vals);
}

linalg::Matrix AdvancedBasisGen::generate_bkz_resistant(
    long p,
    long dimension,
    long precision,
    long block_size) {
    
    // Generate basis resistant to BKZ with given block size
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    std::random_device rd;
    std::mt19937 gen(rd());
    
    // Create blocks with different properties
    for (long block = 0; block < dimension; block += block_size) {
        long block_end = std::min(block + block_size, dimension);
        
        // Each block has similar norm vectors
        long block_valuation = precision / 2 + (gen() % (precision / 4));
        
        for (long i = block; i < block_end; ++i) {
            for (long j = block; j < block_end; ++j) {
                if (i == j) {
                    basis[i][j] = Zp(p, precision, BigInt(p).pow(block_valuation));
                } else {
                    // Small off-diagonal in block
                    basis[i][j] = Zp(p, precision, gen() % p);
                }
            }
        }
    }
    
    return basis;
}

std::pair<linalg::Matrix, linalg::Vector> AdvancedBasisGen::generate_with_planted_vector(
    long p,
    long dimension,
    long precision,
    long planted_valuation) {
    
    // Generate random basis
    auto basis = PadicBasisGenerator::generate_with_distribution(
        p, dimension, precision, 
        PadicBasisGenerator::Distribution::UNIFORM);
    
    // Create short planted vector
    linalg::Vector planted(dimension);
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> unit_dist(1, p - 1);
    
    for (long i = 0; i < dimension; ++i) {
        if (i == 0) {
            // Make sure it's non-zero
            planted[i] = Zp(p, precision, 
                BigInt(unit_dist(gen)) * BigInt(p).pow(planted_valuation));
        } else if (gen() % 3 == 0) {
            // Sparse short vector
            planted[i] = Zp(p, precision, 
                BigInt(unit_dist(gen)) * BigInt(p).pow(planted_valuation + 1));
        } else {
            planted[i] = Zp(p, precision, 0);
        }
    }
    
    // Ensure planted vector is in lattice
    basis[0] = planted;
    
    // Apply unimodular transformation to hide it
    basis = PadicBasisGenerator::apply_unimodular_transform(basis, p, precision, gen);
    
    return {basis, planted};
}

linalg::Matrix AdvancedBasisGen::generate_from_code(
    long p,
    long dimension,
    long precision,
    const std::vector<std::vector<Zp>>& generator_matrix) {
    
    // Use error-correcting code generator matrix as basis
    linalg::Matrix basis = generator_matrix;
    
    // Ensure correct dimensions
    if (basis.size() != static_cast<size_t>(dimension)) {
        basis.resize(dimension);
    }
    
    for (auto& row : basis) {
        if (row.size() != static_cast<size_t>(dimension)) {
            row.resize(dimension, Zp(p, precision, 0));
        }
    }
    
    // Add p-adic structure
    for (long i = 0; i < dimension; ++i) {
        basis[i][i] = basis[i][i] + Zp(p, precision, BigInt(p).pow(precision / 3));
    }
    
    return basis;
}

linalg::Matrix AdvancedBasisGen::generate_with_sublattice(
    long p,
    long dimension,
    long precision,
    long sublattice_dimension,
    long sublattice_index) {
    
    if (sublattice_dimension > dimension) {
        throw std::invalid_argument("Sublattice dimension cannot exceed lattice dimension");
    }
    
    linalg::Matrix basis(dimension, linalg::Vector(dimension));
    
    // Generate sublattice basis
    for (long i = 0; i < sublattice_dimension; ++i) {
        for (long j = 0; j < sublattice_dimension; ++j) {
            if (i == j) {
                // Sublattice has index p^sublattice_index
                basis[i][j] = Zp(p, precision, BigInt(p).pow(sublattice_index));
            } else {
                basis[i][j] = Zp(p, precision, 0);
            }
        }
    }
    
    // Complete to full lattice
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> dist(0, p - 1);
    
    for (long i = sublattice_dimension; i < dimension; ++i) {
        for (long j = 0; j < dimension; ++j) {
            if (i == j) {
                basis[i][j] = Zp(p, precision, 1);
            } else {
                basis[i][j] = Zp(p, precision, dist(gen));
            }
        }
    }
    
    // Mix to hide sublattice structure
    return PadicBasisGenerator::apply_unimodular_transform(basis, p, precision, gen);
}

// NoiseGenerator implementation
linalg::Vector NoiseGenerator::generate_small_noise(
    long p,
    long dimension,
    long precision,
    long min_valuation) {
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> unit_dist(1, p - 1);
    std::uniform_int_distribution<long> val_dist(min_valuation, precision - 1);
    
    linalg::Vector noise(dimension);
    
    for (long i = 0; i < dimension; ++i) {
        long valuation = val_dist(gen);
        long unit = unit_dist(gen);
        
        noise[i] = Zp(p, precision, BigInt(unit) * BigInt(p).pow(valuation));
    }
    
    return noise;
}

linalg::Vector NoiseGenerator::generate_noise(
    long p,
    long dimension,
    long precision,
    PadicBasisGenerator::Distribution dist,
    const std::vector<double>& params) {
    
    // Generate noise vector with specified distribution
    auto noise_matrix = PadicBasisGenerator::generate_with_distribution(
        p, 1, precision, dist, params);
    
    // Extract as vector
    linalg::Vector noise(dimension);
    for (long i = 0; i < dimension; ++i) {
        if (i < static_cast<long>(noise_matrix[0].size())) {
            noise[i] = noise_matrix[0][i];
        } else {
            // Generate additional elements if needed
            std::random_device rd;
            std::mt19937 gen(rd());
            noise[i] = PadicBasisGenerator::sample_discrete_gaussian(
                p, precision, params.empty() ? 1.0 : params[0], gen);
        }
    }
    
    return noise;
}

linalg::Vector NoiseGenerator::generate_flooding_noise(
    long p,
    long dimension,
    long precision,
    long flooding_valuation) {
    
    // Generate large noise to flood existing noise
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long> unit_dist(1, p - 1);
    
    linalg::Vector noise(dimension);
    
    for (long i = 0; i < dimension; ++i) {
        // All noise at same (low) valuation for flooding
        long unit = unit_dist(gen);
        noise[i] = Zp(p, precision, BigInt(unit) * BigInt(p).pow(flooding_valuation));
    }
    
    return noise;
}

linalg::Vector NoiseGenerator::generate_secure_noise(
    long p,
    long dimension,
    long precision,
    PadicBasisGenerator::SecurityLevel level) {
    
    long min_valuation = precision / 3;
    
    switch (level) {
        case PadicBasisGenerator::SecurityLevel::LEVEL_1:
            min_valuation = precision / 3;
            break;
        case PadicBasisGenerator::SecurityLevel::LEVEL_3:
            min_valuation = precision / 2;
            break;
        case PadicBasisGenerator::SecurityLevel::LEVEL_5:
            min_valuation = 2 * precision / 3;
            break;
    }
    
    return generate_small_noise(p, dimension, precision, min_valuation);
}

bool NoiseGenerator::verify_noise_security(
    const linalg::Vector& noise,
    long /* p */,
    long precision,
    PadicBasisGenerator::SecurityLevel level) {
    
    // Check that noise meets security requirements
    long min_required_valuation = precision / 3;
    
    switch (level) {
        case PadicBasisGenerator::SecurityLevel::LEVEL_1:
            min_required_valuation = precision / 3;
            break;
        case PadicBasisGenerator::SecurityLevel::LEVEL_3:
            min_required_valuation = precision / 2;
            break;
        case PadicBasisGenerator::SecurityLevel::LEVEL_5:
            min_required_valuation = 2 * precision / 3;
            break;
    }
    
    // Check all noise components
    for (const auto& component : noise) {
        if (!component.is_zero() && component.valuation() < min_required_valuation) {
            return false;
        }
    }
    
    // Check that noise is not too structured
    // (simplified check: not all components identical)
    if (noise.size() > 1) {
        bool all_same = true;
        for (size_t i = 1; i < noise.size(); ++i) {
            if (!(noise[i] == noise[0])) {
                all_same = false;
                break;
            }
        }
        if (all_same) {
            return false;  // Too structured
        }
    }
    
    return true;
}

} // namespace crypto
} // namespace libadic

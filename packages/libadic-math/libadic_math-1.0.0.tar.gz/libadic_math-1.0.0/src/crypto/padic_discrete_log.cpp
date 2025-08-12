#include "libadic/cryptanalysis.h"
#include <unordered_map>
#include <cmath>
#include <random>

namespace libadic {
namespace cryptanalysis {

PadicDiscreteLog::PadicDiscreteLog(long p_, long precision_)
    : p(p_), precision(precision_) {}

std::optional<BigInt> PadicDiscreteLog::solve(const Zp& base, const Zp& target, 
                                              const BigInt& max_exponent) {
    // Baby-step Giant-step algorithm for p-adic discrete logarithm
    // Solve: base^x ≡ target (mod p^precision)
    
    if (!base.is_unit()) {
        return std::nullopt; // Base must be invertible
    }
    
    // Choose m = ceil(sqrt(max_exponent))
    BigInt m = max_exponent.sqrt() + BigInt(1);
    
    // Baby steps: compute base^j for j = 0, 1, ..., m-1
    std::unordered_map<std::string, BigInt> baby_steps;
    Zp current(p, precision, 1);
    
    for (BigInt j(0); j < m; j = j + BigInt(1)) {
        // Use string representation as key for hash map
        std::string key = current.to_bigint().to_string();
        baby_steps[key] = j;
        current = current * base;
    }
    
    // Giant steps: compute target * base^(-m*i) for i = 0, 1, ..., m-1
    Zp base_inv = base.inverse();
    Zp giant_step_multiplier = base_inv.pow(m.to_long()); // base^(-m)
    
    current = target;
    for (BigInt i(0); i < m; i = i + BigInt(1)) {
        std::string key = current.to_bigint().to_string();
        
        // Check if we have a collision
        auto it = baby_steps.find(key);
        if (it != baby_steps.end()) {
            // Found: base^j = target * base^(-m*i)
            // Therefore: base^(j + m*i) = target
            BigInt x = it->second + m * i;
            
            // Verify the solution
            Zp check = base.pow(x.to_long());
            if (check == target) {
                return x;
            }
        }
        
        current = current * giant_step_multiplier;
    }
    
    return std::nullopt; // No solution found
}

std::optional<BigInt> PadicDiscreteLog::pollard_rho(const Zp& base, const Zp& target) {
    // Pollard's rho algorithm adapted for p-adic groups
    // Uses Floyd's cycle detection
    
    if (!base.is_unit() || !target.is_unit()) {
        return std::nullopt;
    }
    
    // Define a pseudo-random walk function
    auto f = [&](const Zp& x, BigInt& a, BigInt& b) -> Zp {
        // Partition function based on last digit mod 3
        int partition = (x.to_bigint() % BigInt(3)).to_long();
        
        switch (partition) {
            case 0:
                // Multiply by base
                a = a + BigInt(1);
                return x * base;
            case 1:
                // Square
                a = a * BigInt(2);
                b = b * BigInt(2);
                return x * x;
            case 2:
                // Multiply by target
                b = b + BigInt(1);
                return x * target;
            default:
                return x;
        }
    };
    
    // Initialize tortoise and hare
    Zp x_tortoise = base;
    Zp x_hare = base;
    BigInt a_tortoise(1), b_tortoise(0);
    BigInt a_hare(1), b_hare(0);
    
    // Maximum iterations to prevent infinite loop
    const long max_iters = 1000000;
    
    for (long iter = 0; iter < max_iters; ++iter) {
        // Tortoise takes one step
        x_tortoise = f(x_tortoise, a_tortoise, b_tortoise);
        
        // Hare takes two steps
        x_hare = f(x_hare, a_hare, b_hare);
        x_hare = f(x_hare, a_hare, b_hare);
        
        // Check for collision
        if (x_tortoise == x_hare) {
            // We have base^a_tortoise * target^b_tortoise = base^a_hare * target^b_hare
            // Therefore: base^(a_tortoise - a_hare) = target^(b_hare - b_tortoise)
            
            BigInt a_diff = a_tortoise - a_hare;
            BigInt b_diff = b_hare - b_tortoise;
            
            if (b_diff == BigInt(0)) {
                continue; // Useless collision
            }
            
            // Need to solve: base^a_diff = target^b_diff
            // If b_diff is invertible mod p^n, we can solve for the discrete log
            
            // For simplicity, check if b_diff is coprime to p^precision
            BigInt p_power = BigInt(p).pow(precision);
            BigInt gcd = b_diff.gcd(p_power);
            
            if (gcd == BigInt(1)) {
                // b_diff is invertible
                BigInt b_inv = b_diff.mod_inverse(p_power);
                BigInt x = (a_diff * b_inv) % p_power;
                
                // Verify
                Zp check = base.pow(x.to_long());
                if (check == target) {
                    return x;
                }
            }
        }
    }
    
    return std::nullopt;
}

std::optional<BigInt> PadicDiscreteLog::index_calculus(const Zp& base, const Zp& target) {
    // Simplified index calculus for p-adic fields
    // This is a complex algorithm that would require:
    // 1. Factor base of small primes
    // 2. Smooth number detection in Z_p
    // 3. Linear algebra over Z/p^nZ
    
    // For now, return a placeholder indicating the method is not fully implemented
    // In a real implementation, this would be the most powerful attack
    
    // Try simple cases where the logarithm is small
    Zp current(p, precision, 1);
    for (long x = 0; x < 1000; ++x) {
        if (current == target) {
            return BigInt(x);
        }
        current = current * base;
    }
    
    return std::nullopt;
}

// PRNGAttack implementation
PRNGAttack::PRNGAttack(long p_, long precision_)
    : p(p_), precision(precision_) {}

std::optional<Zp> PRNGAttack::recover_state(const std::vector<Zp>& outputs) {
    if (outputs.size() < 3) {
        return std::nullopt; // Need enough outputs
    }
    
    // Try to recover the state by analyzing the rational map structure
    // f(x) = (ax + b)/(cx + d)
    
    // If we have consecutive outputs y0, y1, y2, we can set up equations:
    // y1 = f(y0), y2 = f(y1)
    
    // This gives us a system of equations to solve for the parameters
    // For now, use a simple heuristic approach
    
    // Check if there's a simple linear relationship
    for (size_t i = 1; i < outputs.size() - 1; ++i) {
        // Check if outputs[i+1] = f(outputs[i]) for some simple f
        
        // Try linear: y_{i+1} = a*y_i + b
        if (i > 0) {
            // Set up linear system from two consecutive relations
            // This is simplified; real attack would be more sophisticated
            
            Zp y0 = outputs[i-1];
            Zp y1 = outputs[i];
            Zp y2 = outputs[i+1];
            
            // If the PRNG got stuck in a cycle
            if (y1 == y2) {
                return y1; // Found a fixed point, which is the state
            }
        }
    }
    
    // More sophisticated state recovery would involve:
    // 1. Analyzing the full algebraic structure
    // 2. Using lattice reduction
    // 3. Differential cryptanalysis
    
    return std::nullopt;
}

std::vector<Zp> PRNGAttack::predict_next(const std::vector<Zp>& history, 
                                         long num_predictions) {
    std::vector<Zp> predictions;
    
    if (history.size() < 10) {
        // Not enough history for prediction
        return predictions;
    }
    
    // Look for patterns in the history
    // Simple approach: detect short cycles
    for (size_t period = 1; period < history.size() / 2; ++period) {
        bool found_cycle = true;
        
        // Check if last 'period' values repeat
        for (size_t i = 0; i < period && found_cycle; ++i) {
            if (history[history.size() - 1 - i] != 
                history[history.size() - 1 - period - i]) {
                found_cycle = false;
            }
        }
        
        if (found_cycle) {
            // Predict based on the cycle
            for (long i = 0; i < num_predictions; ++i) {
                predictions.push_back(history[history.size() - period + (i % period)]);
            }
            return predictions;
        }
    }
    
    // If no cycle found, try to fit a simple model
    // For now, just repeat the last value (weak prediction)
    Zp last = history.back();
    for (long i = 0; i < num_predictions; ++i) {
        predictions.push_back(last);
    }
    
    return predictions;
}

double PRNGAttack::distinguish_from_random(const std::vector<Zp>& samples) {
    if (samples.size() < 100) {
        return 0.5; // Not enough samples to distinguish
    }
    
    // Statistical tests to distinguish from random
    double score = 0.0;
    
    // Test 1: Frequency test
    std::unordered_map<std::string, int> frequency;
    for (const auto& sample : samples) {
        frequency[sample.to_bigint().to_string()]++;
    }
    
    // Check for unusual frequency distribution
    double expected = static_cast<double>(samples.size()) / frequency.size();
    double chi_square = 0.0;
    
    for (const auto& [value, count] : frequency) {
        double diff = count - expected;
        chi_square += (diff * diff) / expected;
    }
    
    // High chi-square indicates non-random
    if (chi_square > samples.size()) {
        score += 0.3;
    }
    
    // Test 2: Look for arithmetic progressions
    bool found_progression = false;
    for (size_t i = 2; i < samples.size() && !found_progression; ++i) {
        Zp diff1 = samples[i] - samples[i-1];
        Zp diff2 = samples[i-1] - samples[i-2];
        if (diff1 == diff2 && !diff1.is_zero()) {
            found_progression = true;
            score += 0.3;
        }
    }
    
    // Test 3: Check for small cycles
    for (size_t period = 2; period < 20 && period < samples.size() / 2; ++period) {
        int matches = 0;
        for (size_t i = period; i < samples.size(); ++i) {
            if (samples[i] == samples[i - period]) {
                matches++;
            }
        }
        
        if (matches > static_cast<int>(samples.size() / (2 * period))) {
            score += 0.4;
            break;
        }
    }
    
    return std::min(1.0, std::max(0.0, score));
}

PRNGAttack::BiasAnalysis PRNGAttack::analyze_bias(const std::vector<Zp>& samples) {
    BiasAnalysis analysis;
    
    if (samples.empty()) {
        return analysis;
    }
    
    // Frequency bias
    std::unordered_map<int, int> bit_counts;
    for (const auto& sample : samples) {
        BigInt value = sample.to_bigint();
        for (int bit = 0; bit < 64; ++bit) {
            if ((value & (BigInt(1).operator<<(bit))) != BigInt(0)) {
                bit_counts[bit]++;
            }
        }
    }
    
    // Check which bits deviate from 50%
    for (const auto& [bit, count] : bit_counts) {
        double ratio = static_cast<double>(count) / samples.size();
        if (std::abs(ratio - 0.5) > 0.1) {
            analysis.weak_bits.push_back(bit);
        }
    }
    
    analysis.frequency_bias = 0.0;
    for (const auto& [bit, count] : bit_counts) {
        double ratio = static_cast<double>(count) / samples.size();
        analysis.frequency_bias += std::abs(ratio - 0.5);
    }
    analysis.frequency_bias /= bit_counts.size();
    
    // Serial correlation
    if (samples.size() > 1) {
        double correlation = 0.0;
        for (size_t i = 1; i < samples.size(); ++i) {
            // Simplified correlation based on Hamming distance
            BigInt xor_val = samples[i].to_bigint() ^ samples[i-1].to_bigint();
            int hamming_weight = 0;
            BigInt temp = xor_val;
            while (temp > BigInt(0)) {
                if ((temp & BigInt(1)) == BigInt(1)) {
                    hamming_weight++;
                }
                temp = temp.operator>>(1);
            }
            correlation += hamming_weight;
        }
        analysis.serial_correlation = correlation / (samples.size() - 1) / 32.0;
    }
    
    // Long-range correlation (simplified)
    if (samples.size() > 10) {
        double long_correlation = 0.0;
        for (size_t lag = 2; lag < 10 && lag < samples.size(); ++lag) {
            for (size_t i = lag; i < samples.size(); ++i) {
                if (samples[i] == samples[i - lag]) {
                    long_correlation += 1.0;
                }
            }
        }
        analysis.long_range_correlation = long_correlation / (samples.size() * 8);
    }
    
    return analysis;
}

} // namespace cryptanalysis
} // namespace libadic
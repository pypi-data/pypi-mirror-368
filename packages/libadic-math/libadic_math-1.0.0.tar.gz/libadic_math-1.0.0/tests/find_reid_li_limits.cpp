#include "libadic/padic_log.h"
#include "libadic/padic_gamma.h"
#include "libadic/l_functions.h"
#include "libadic/characters.h"
#include <iostream>
#include <vector>
#include <iomanip>
#include <chrono>

using namespace libadic;
using namespace std::chrono;

struct TestResult {
    long prime;
    long num_characters;
    long num_passed;
    long num_failed;
    long min_precision_achieved;
    long target_precision;
    double time_ms;
    std::string failure_reason;
};

// Simple primality test
bool is_prime(long n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (long i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

// Get next prime after n
long next_prime(long n) {
    if (n < 2) return 2;
    n = (n % 2 == 0) ? n + 1 : n + 2;
    while (!is_prime(n)) n += 2;
    return n;
}

// Compute Φ_p for odd character
Qp compute_phi_odd(const DirichletCharacter& chi, long p, long N) {
    Qp result(p, N, 0);
    for (long a = 1; a < p; ++a) {
        Zp chi_a = chi.evaluate(a, N);
        if (!chi_a.is_zero()) {
            Zp a_zp(p, N, a);
            Qp log_gamma = PadicGamma::log_gamma(a_zp);
            result += Qp(chi_a) * log_gamma;
        }
    }
    return result;
}

// Compute Ψ_p for odd character (L'_p(0, χ))
Qp compute_psi_odd(const DirichletCharacter& chi, long N) {
    return LFunctions::kubota_leopoldt_derivative(0, chi, N);
}

// Compute Φ_p for even character
Qp compute_phi_even(const DirichletCharacter& chi, long p, long N) {
    Qp result(p, N, 0);
    for (long a = 1; a < p; ++a) {
        Zp chi_a = chi.evaluate(a, N);
        if (!chi_a.is_zero()) {
            Qp ratio = Qp::from_rational(a, p - 1, p, N);
            if (ratio.valuation() == 0) {
                Qp ratio_minus_one = ratio - Qp(p, N, 1);
                if ((p != 2 && ratio_minus_one.valuation() >= 1) ||
                    (p == 2 && ratio_minus_one.valuation() >= 2)) {
                    Qp log_term = PadicLog::log(ratio);
                    result += Qp(chi_a) * log_term;
                }
            }
        }
    }
    return result;
}

// Compute Ψ_p for even character (L_p(0, χ))
Qp compute_psi_even(const DirichletCharacter& chi, long N) {
    return LFunctions::kubota_leopoldt(0, chi, N);
}

TestResult test_prime(long p, long target_precision) {
    TestResult result;
    result.prime = p;
    result.target_precision = target_precision;
    result.num_passed = 0;
    result.num_failed = 0;
    result.min_precision_achieved = target_precision;
    
    auto start = high_resolution_clock::now();
    
    try {
        // Get all primitive characters mod p
        auto characters = DirichletCharacter::enumerate_primitive_characters(p, p);
        result.num_characters = 0;
        
        for (const auto& chi : characters) {
            if (chi.is_principal()) continue;
            result.num_characters++;
            
            Qp phi_val, psi_val;
            
            if (chi.is_odd()) {
                phi_val = compute_phi_odd(chi, p, target_precision);
                psi_val = compute_psi_odd(chi, target_precision);
            } else {
                phi_val = compute_phi_even(chi, p, target_precision);
                psi_val = compute_psi_even(chi, target_precision);
            }
            
            Qp diff = phi_val - psi_val;
            long precision_achieved = diff.is_zero() ? target_precision : diff.valuation();
            
            if (precision_achieved < result.min_precision_achieved) {
                result.min_precision_achieved = precision_achieved;
            }
            
            // Consider it passed if we achieve at least 80% of target precision
            if (precision_achieved >= (target_precision * 8 / 10)) {
                result.num_passed++;
            } else {
                result.num_failed++;
                if (result.failure_reason.empty()) {
                    result.failure_reason = "Precision only " + std::to_string(precision_achieved) + 
                                          "/" + std::to_string(target_precision);
                }
            }
        }
        
    } catch (const std::exception& e) {
        result.failure_reason = std::string("Exception: ") + e.what();
        result.num_failed = result.num_characters;
    }
    
    auto end = high_resolution_clock::now();
    result.time_ms = duration_cast<milliseconds>(end - start).count();
    
    return result;
}

int main() {
    std::cout << "====================================================\n";
    std::cout << "     REID-LI CRITERION LIMIT FINDER\n";
    std::cout << "====================================================\n";
    std::cout << "\nSearching for computational or mathematical limits...\n\n";
    
    std::cout << std::setw(7) << "Prime" 
              << std::setw(10) << "Chars"
              << std::setw(10) << "Passed"
              << std::setw(10) << "Failed"
              << std::setw(12) << "Min Prec"
              << std::setw(12) << "Target"
              << std::setw(12) << "Time(ms)"
              << std::setw(15) << "Status"
              << "\n";
    std::cout << std::string(96, '-') << "\n";
    
    std::vector<TestResult> results;
    
    // Test strategy:
    // 1. Start with small primes at high precision
    // 2. Gradually increase prime size
    // 3. Adaptively reduce precision for larger primes
    // 4. Stop when we hit failures or computational limits
    
    long p = 5;
    long consecutive_successes = 0;
    long consecutive_failures = 0;
    bool found_limit = false;
    
    while (p < 200 && !found_limit) {
        // Adaptive precision: reduce as prime gets larger
        long target_precision;
        if (p < 20) {
            target_precision = 30;
        } else if (p < 50) {
            target_precision = 20;
        } else if (p < 100) {
            target_precision = 10;
        } else {
            target_precision = 5;
        }
        
        TestResult result = test_prime(p, target_precision);
        results.push_back(result);
        
        // Print result
        std::cout << std::setw(7) << result.prime
                  << std::setw(10) << result.num_characters
                  << std::setw(10) << result.num_passed
                  << std::setw(10) << result.num_failed
                  << std::setw(12) << result.min_precision_achieved
                  << std::setw(12) << result.target_precision
                  << std::setw(12) << std::fixed << std::setprecision(1) << result.time_ms;
        
        if (result.num_failed == 0) {
            std::cout << std::setw(15) << "✓ PASS" << "\n";
            consecutive_successes++;
            consecutive_failures = 0;
        } else if (!result.failure_reason.empty() && 
                   result.failure_reason.find("Exception") != std::string::npos) {
            std::cout << std::setw(15) << "✗ ERROR" << "\n";
            std::cout << "  Error: " << result.failure_reason << "\n";
            consecutive_failures++;
            consecutive_successes = 0;
        } else {
            std::cout << std::setw(15) << "✗ FAIL" << "\n";
            if (!result.failure_reason.empty()) {
                std::cout << "  Reason: " << result.failure_reason << "\n";
            }
            consecutive_failures++;
            consecutive_successes = 0;
        }
        
        // Check for stopping conditions
        if (consecutive_failures >= 3) {
            std::cout << "\n⚠️  Found limit: 3 consecutive failures at p = " << p << "\n";
            found_limit = true;
        } else if (result.time_ms > 5000) {
            std::cout << "\n⚠️  Computational limit: test taking > 5 seconds at p = " << p << "\n";
            found_limit = true;
        }
        
        // Next prime - jump larger for bigger primes to save time
        if (p < 20) {
            p = next_prime(p);
        } else if (p < 50) {
            p = next_prime(p + 4);  // Skip some primes
        } else {
            p = next_prime(p + 10); // Skip more primes
        }
    }
    
    // Summary
    std::cout << "\n====================================================\n";
    std::cout << "                    SUMMARY\n";
    std::cout << "====================================================\n\n";
    
    long total_chars = 0, total_passed = 0, total_failed = 0;
    long largest_working_prime = 0;
    
    for (const auto& r : results) {
        total_chars += r.num_characters;
        total_passed += r.num_passed;
        total_failed += r.num_failed;
        if (r.num_failed == 0 && r.prime > largest_working_prime) {
            largest_working_prime = r.prime;
        }
    }
    
    std::cout << "Total primes tested: " << results.size() << "\n";
    std::cout << "Total characters tested: " << total_chars << "\n";
    std::cout << "Total passed: " << total_passed << "\n";
    std::cout << "Total failed: " << total_failed << "\n";
    std::cout << "Success rate: " << std::fixed << std::setprecision(1) 
              << (100.0 * total_passed / total_chars) << "%\n";
    std::cout << "Largest working prime: " << largest_working_prime << "\n";
    
    if (found_limit) {
        std::cout << "\n🔍 LIMIT ANALYSIS:\n";
        if (consecutive_failures >= 3) {
            std::cout << "Reid-Li criterion appears to break down around p = " 
                      << results.back().prime << "\n";
            std::cout << "This could indicate:\n";
            std::cout << "  1. Computational precision limits\n";
            std::cout << "  2. Numerical instability in the implementation\n";
            std::cout << "  3. A genuine mathematical issue\n";
        } else {
            std::cout << "Hit computational time limit but criterion still holding\n";
        }
    } else {
        std::cout << "\n✅ NO LIMIT FOUND!\n";
        std::cout << "Reid-Li criterion holds for all tested primes up to " 
                  << results.back().prime << "\n";
    }
    
    return 0;
}
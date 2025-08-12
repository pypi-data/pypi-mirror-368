#ifndef LIBADIC_BERNOULLI_H
#define LIBADIC_BERNOULLI_H

#include "libadic/qp.h"
#include "libadic/cyclotomic.h"
#include <map>
#include <vector>
#include <numeric>
#include <functional>
#include <algorithm>

namespace libadic {

/**
 * Computation of Bernoulli numbers and generalized Bernoulli numbers
 * B_n and B_{n,χ} for Dirichlet characters χ
 */
class BernoulliNumbers {
private:
    // Cache for regular Bernoulli numbers
    inline static std::map<long, Qp> bernoulli_cache;
    
    // Cache for generalized Bernoulli numbers
    struct CharKey {
        long n;
        long conductor;
        long a; // character value determinant
        long p;
        long precision;
        
        bool operator<(const CharKey& other) const {
            if (n != other.n) return n < other.n;
            if (conductor != other.conductor) return conductor < other.conductor;
            if (a != other.a) return a < other.a;
            if (p != other.p) return p < other.p;
            return precision < other.precision;
        }
    };
    inline static std::map<CharKey, Qp> generalized_cache;
    
public:
    /**
     * Compute the n-th Bernoulli number B_n
     * B_0 = 1, B_1 = -1/2, B_{2k+1} = 0 for k >= 1
     * Uses the recursive formula:
     * Σ_{k=0}^{n} C(n+1,k) B_k = 0
     */
    static Qp bernoulli(long n, long p, long precision) {
        if (n < 0) {
            throw std::invalid_argument("Bernoulli index must be non-negative");
        }
        
        // Check cache
        auto key = n * 1000000L + p * 1000L + precision;
        if (bernoulli_cache.find(key) != bernoulli_cache.end()) {
            return bernoulli_cache[key];
        }
        
        Qp result(p, precision, 0);
        
        // Special cases
        if (n == 0) {
            result = Qp(p, precision, 1);
        } else if (n == 1) {
            result = Qp::from_rational(-1, 2, p, precision);
        } else if (n > 1 && n % 2 == 1) {
            result = Qp(p, precision, 0);
        } else {
            // Even n >= 2: Use recursive formula
            // B_n = -1/(n+1) * Σ_{k=0}^{n-1} C(n+1,k) * B_k
            
            Qp sum(p, precision, 0);
            for (long k = 0; k < n; ++k) {
                BigInt binom = BigInt::binomial(static_cast<unsigned long>(n + 1), 
                                               static_cast<unsigned long>(k));
                Qp b_k = bernoulli(k, p, precision);
                sum += Qp(p, precision, binom) * b_k;
            }
            
            result = -sum / Qp(p, precision, n + 1);
        }
        
        // Apply von Staudt-Clausen theorem for p-adic normalization
        // B_{2n} ≡ Σ_{p-1|2n} 1/p (mod Z)
        if (n > 0 && n % 2 == 0) {
            if ((n % (p - 1)) == 0) {
                // Add p-adic correction
                // Check if p divides n
                if (n % p != 0) {
                    Qp correction = Qp::from_rational(1, p, p, precision);
                    result = result + correction;
                }
            }
        }
        
        bernoulli_cache[key] = result;
        return result;
    }
    
    /**
     * Compute generalized Bernoulli number B_{n,χ}
     * For a Dirichlet character χ mod f:
     * B_{n,χ} = f^{n-1} Σ_{a=1}^{f} χ(a) B_n(a/f)
     * where B_n(x) is the n-th Bernoulli polynomial
     */
    static Qp generalized_bernoulli(long n, long conductor, 
                                   std::function<Cyclotomic(long)> chi_func,
                                   long p, long precision) {
        CharKey key{n, conductor, 0, p, precision};
        
        if (generalized_cache.find(key) != generalized_cache.end()) {
            return generalized_cache[key];
        }
        
        if (conductor == 1) {
            // Trivial character
            return bernoulli(n, p, precision);
        }
        
        Cyclotomic sum(p, precision);
        BigInt f_power = BigInt(conductor).pow(std::max(0L, n - 1));
        
        for (long a = 1; a <= conductor; ++a) {
            if (std::gcd(a, conductor) != 1) continue;
            
            Cyclotomic chi_a = chi_func(a);
            Qp bern_poly = bernoulli_polynomial(n, Qp::from_rational(a, conductor, p, precision), p, precision);
            sum = sum + chi_a * bern_poly;
        }
        
        // Extract the constant term as the generalized Bernoulli number
        Qp result = sum.get_coeff(0) * Qp(p, precision, f_power);
        
        generalized_cache[key] = result;
        return result;
    }
    
    /**
     * Compute the n-th Bernoulli polynomial B_n(x)
     * B_n(x) = Σ_{k=0}^{n} C(n,k) B_k x^{n-k}
     */
    static Qp bernoulli_polynomial(long n, const Qp& x, long p, long precision) {
        Qp result(p, precision, 0);
        Qp x_power(p, precision, 1);
        
        for (long k = n; k >= 0; --k) {
            BigInt binom = BigInt::binomial(static_cast<unsigned long>(n), 
                                           static_cast<unsigned long>(k));
            Qp b_k = bernoulli(k, p, precision);
            result += Qp(p, precision, binom) * b_k * x_power;
            if (k > 0) {
                x_power *= x;
            }
        }
        
        return result;
    }
    
    /**
     * Compute B_{1,χ} for the Reid-Li criterion
     * This is crucial for L_p(0,χ) = -(1 - χ(p)p^{-1}) B_{1,χ}
     */
    static Qp bernoulli_1_chi(long conductor, std::function<long(long)> chi,
                              long p, long precision) {
        if (conductor == 1) {
            return bernoulli(1, p, precision); // -1/2
        }
        
        Qp sum(p, precision, 0);
        
        // B_{1,χ} = Σ_{a=1}^{conductor} χ(a) * a / conductor
        for (long a = 1; a <= conductor; ++a) {
            if (std::gcd(a, conductor) != 1) continue;
            
            long chi_a = chi(a);
            if (chi_a != 0) {
                Qp term = Qp::from_rational(chi_a * a, conductor, p, precision);
                sum += term;
            }
        }
        
        return sum;
    }
    
    /**
     * Clear caches (useful for memory management in long computations)
     */
    static void clear_cache() {
        bernoulli_cache.clear();
        generalized_cache.clear();
    }
    
    /**
     * Kummer congruences for Bernoulli numbers
     * If (p-1) ∤ n and p ∤ n, then:
     * B_n/n ≡ B_{n+p-1}/(n+p-1) (mod p)
     */
    static bool verify_kummer_congruence(long n, long p, long precision) {
        if ((n % (p - 1)) == 0 || (n % p) == 0) {
            return true; // Congruence doesn't apply
        }
        
        Qp bn_over_n = bernoulli(n, p, precision) / Qp(p, precision, n);
        Qp bn_plus_over = bernoulli(n + p - 1, p, precision) / Qp(p, precision, n + p - 1);
        
        Qp diff = bn_over_n - bn_plus_over;
        return diff.valuation() >= 1; // Congruent mod p
    }
};

} // namespace libadic

#endif // LIBADIC_BERNOULLI_H
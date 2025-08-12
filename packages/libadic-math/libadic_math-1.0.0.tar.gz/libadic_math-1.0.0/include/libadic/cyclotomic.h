#ifndef LIBADIC_CYCLOTOMIC_H
#define LIBADIC_CYCLOTOMIC_H

#include "libadic/qp.h"
#include <vector>
#include <stdexcept>

namespace libadic {

/**
 * Elements of Q_p(ζ) where ζ is a primitive p-th root of unity.
 * Represented as polynomials in ζ with Qp coefficients.
 * The p-th cyclotomic polynomial Φ_p(x) = 1 + x + ... + x^(p-1) = 0
 */
class Cyclotomic {
private:
    long prime;
    long precision;
    std::vector<Qp> coeffs;  // c0 + c1*ζ + c2*ζ^2 + ... + c_(p-2)*ζ^(p-2)
    
    void reduce() {
        // Use the relation ζ^p = 1, so ζ^(p-1) = -1 - ζ - ... - ζ^(p-2)
        if (static_cast<long>(coeffs.size()) >= prime) {
            Qp high_coeff = coeffs[prime - 1];
            coeffs.resize(prime - 1);
            
            // Distribute -high_coeff to all lower terms
            for (size_t i = 0; i < coeffs.size(); ++i) {
                coeffs[i] -= high_coeff;
            }
        }
        
        // Ensure we have exactly p-1 coefficients
        while (static_cast<long>(coeffs.size()) < prime - 1) {
            coeffs.push_back(Qp(prime, precision, 0));
        }
    }
    
public:
    // Default constructor
    Cyclotomic() : prime(2), precision(1) {
        coeffs.resize(1, Qp(2, 1, 0));
    }
    
    Cyclotomic(long p, long N) : prime(p), precision(N) {
        if (p < 2) {
            throw std::invalid_argument("Prime must be >= 2");
        }
        coeffs.resize(p - 1, Qp(p, N, 0));
    }
    
    Cyclotomic(long p, long N, const std::vector<Qp>& c) 
        : prime(p), precision(N), coeffs(c) {
        reduce();
    }
    
    Cyclotomic(long p, long N, const Qp& constant) : prime(p), precision(N) {
        coeffs.resize(p - 1, Qp(p, N, 0));
        coeffs[0] = constant;
    }
    
    long get_prime() const { return prime; }
    long get_precision() const { return precision; }
    const std::vector<Qp>& get_coeffs() const { return coeffs; }
    
    Qp get_coeff(size_t i) const {
        if (i >= coeffs.size()) {
            return Qp(prime, precision, 0);
        }
        return coeffs[i];
    }
    
    void set_coeff(size_t i, const Qp& val) {
        if (i >= coeffs.size()) {
            coeffs.resize(i + 1, Qp(prime, precision, 0));
        }
        coeffs[i] = val;
        reduce();
    }
    
    Cyclotomic operator+(const Cyclotomic& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot add cyclotomic elements with different primes");
        }
        
        std::vector<Qp> result_coeffs(prime - 1);
        for (long i = 0; i < prime - 1; ++i) {
            result_coeffs[i] = get_coeff(i) + other.get_coeff(i);
        }
        
        return Cyclotomic(prime, std::min(precision, other.precision), result_coeffs);
    }
    
    Cyclotomic operator-(const Cyclotomic& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot subtract cyclotomic elements with different primes");
        }
        
        std::vector<Qp> result_coeffs(prime - 1);
        for (long i = 0; i < prime - 1; ++i) {
            result_coeffs[i] = get_coeff(i) - other.get_coeff(i);
        }
        
        return Cyclotomic(prime, std::min(precision, other.precision), result_coeffs);
    }
    
    Cyclotomic operator*(const Cyclotomic& other) const {
        if (prime != other.prime) {
            throw std::invalid_argument("Cannot multiply cyclotomic elements with different primes");
        }
        
        long new_prec = std::min(precision, other.precision);
        std::vector<Qp> result_coeffs(2 * prime - 2, Qp(prime, new_prec, 0));
        
        // Polynomial multiplication
        for (long i = 0; i < prime - 1; ++i) {
            for (long j = 0; j < prime - 1; ++j) {
                result_coeffs[i + j] += get_coeff(i) * other.get_coeff(j);
            }
        }
        
        // Reduce using cyclotomic polynomial relation
        // ζ^p = 1, so ζ^(p-1) = -1 - ζ - ... - ζ^(p-2)
        for (long k = 2 * prime - 3; k >= prime - 1; --k) {
            Qp coeff = result_coeffs[k];
            long reduced_power = k % (prime - 1);
            
            if (k >= prime - 1) {
                // ζ^k = ζ^(k mod (p-1)) when k >= p-1
                // But we need to handle ζ^(p-1) = -1 - ζ - ... - ζ^(p-2)
                long quotient = k / (prime - 1);
                
                for (long iter = 0; iter < quotient; ++iter) {
                    // Each application of ζ^(p-1) adds -1 to all coefficients
                    for (long i = 0; i < prime - 1; ++i) {
                        result_coeffs[i] -= coeff;
                    }
                }
                
                if (reduced_power > 0) {
                    result_coeffs[reduced_power] += coeff;
                }
            }
        }
        
        result_coeffs.resize(prime - 1);
        return Cyclotomic(prime, new_prec, result_coeffs);
    }
    
    Cyclotomic operator*(const Qp& scalar) const {
        std::vector<Qp> result_coeffs(prime - 1);
        for (long i = 0; i < prime - 1; ++i) {
            result_coeffs[i] = coeffs[i] * scalar;
        }
        return Cyclotomic(prime, precision, result_coeffs);
    }
    
    Cyclotomic operator-() const {
        std::vector<Qp> result_coeffs(prime - 1);
        for (long i = 0; i < prime - 1; ++i) {
            result_coeffs[i] = -coeffs[i];
        }
        return Cyclotomic(prime, precision, result_coeffs);
    }
    
    bool operator==(const Cyclotomic& other) const {
        if (prime != other.prime) return false;
        
        for (long i = 0; i < prime - 1; ++i) {
            if (get_coeff(i) != other.get_coeff(i)) {
                return false;
            }
        }
        return true;
    }
    
    bool operator!=(const Cyclotomic& other) const {
        return !(*this == other);
    }
    
    bool is_zero() const {
        for (const auto& c : coeffs) {
            if (!c.is_zero()) return false;
        }
        return true;
    }
    
    /**
     * Compute the norm N_{Q_p(ζ)/Q_p}
     * For an element α in Q_p(ζ), the norm is the product of all conjugates
     */
    Qp norm() const {
        // For simplicity, return the constant term for now
        // Full implementation would compute product over all Galois conjugates
        return coeffs[0];
    }
    
    /**
     * Compute the trace Tr_{Q_p(ζ)/Q_p}
     * For an element α in Q_p(ζ), the trace is the sum of all conjugates
     */
    Qp trace() const {
        // The trace of c0 + c1*ζ + ... is (p-1)*c0 - (c1 + c2 + ... + c_(p-2))
        Qp result = coeffs[0] * Qp(prime, precision, prime - 1);
        for (size_t i = 1; i < coeffs.size(); ++i) {
            result -= coeffs[i];
        }
        return result;
    }
    
    /**
     * Create a primitive p-th root of unity
     */
    static Cyclotomic zeta(long p, long N) {
        Cyclotomic z(p, N);
        z.set_coeff(1, Qp(p, N, 1));  // ζ = 0 + 1*ζ + 0*ζ^2 + ...
        return z;
    }
    
    /**
     * Evaluate at a specific p-adic number
     * Useful for testing and validation
     */
    Qp evaluate(const Qp& x) const {
        if (x.get_prime() != BigInt(prime)) {
            throw std::invalid_argument("Prime mismatch in evaluation");
        }
        
        Qp result = coeffs[0];
        Qp x_power = x;
        
        for (size_t i = 1; i < coeffs.size(); ++i) {
            result += coeffs[i] * x_power;
            x_power *= x;
        }
        
        return result;
    }
    
    std::string to_string() const {
        std::string result = "(";
        bool first = true;
        
        for (size_t i = 0; i < coeffs.size(); ++i) {
            if (!coeffs[i].is_zero()) {
                if (!first) result += " + ";
                
                if (i == 0) {
                    result += coeffs[i].to_string();
                } else if (i == 1) {
                    if (coeffs[i] == Qp(prime, precision, 1)) {
                        result += "ζ";
                    } else {
                        result += coeffs[i].to_string() + "·ζ";
                    }
                } else {
                    if (coeffs[i] == Qp(prime, precision, 1)) {
                        result += "ζ^" + std::to_string(i);
                    } else {
                        result += coeffs[i].to_string() + "·ζ^" + std::to_string(i);
                    }
                }
                first = false;
            }
        }
        
        if (first) result += "0";
        result += ")";
        return result;
    }
};

inline std::ostream& operator<<(std::ostream& os, const Cyclotomic& c) {
    os << c.to_string();
    return os;
}

} // namespace libadic

#endif // LIBADIC_CYCLOTOMIC_H
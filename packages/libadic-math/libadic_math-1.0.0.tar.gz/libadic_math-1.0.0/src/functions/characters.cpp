#include "libadic/characters.h"
#include "libadic/l_functions.h"
#include <vector>
#include <map>
#include <numeric>
#include <functional>

namespace libadic {

// Static helper method
long DirichletCharacter::pow_mod(long base, long exp, long mod) {
    long result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}

// Private method implementations
void DirichletCharacter::compute_generators() {
    generators.clear();
    generator_orders.clear();
    
    if (modulus == 1) {
        return;
    }
    
    // Factor modulus
    std::vector<std::pair<long, long>> factorization;
    long n = modulus;
    
    // Check for powers of 2
    long pow2 = 0;
    while (n % 2 == 0) {
        pow2++;
        n /= 2;
    }
    if (pow2 > 0) {
        factorization.push_back({2, pow2});
    }
    
    // Check odd primes
    for (long p = 3; p * p <= n; p += 2) {
        long pow = 0;
        while (n % p == 0) {
            pow++;
            n /= p;
        }
        if (pow > 0) {
            factorization.push_back({p, pow});
        }
    }
    if (n > 1) {
        factorization.push_back({n, 1});
    }
    
    // For each prime power, find a generator
    for (const auto& [p, k] : factorization) {
        long pk = 1;
        for (long i = 0; i < k; ++i) pk *= p;
        
        if (p == 2 && k >= 3) {
            // (Z/2^kZ)* ≅ Z/2 × Z/2^(k-2)
            generators.push_back(-1);  // Generator of Z/2
            generator_orders.push_back(2);
            
            generators.push_back(3);   // Generator of Z/2^(k-2)
            generator_orders.push_back(pk / 4);
        } else if (p == 2 && k == 2) {
            // (Z/4Z)* ≅ Z/2
            generators.push_back(-1);
            generator_orders.push_back(2);
        } else if (p == 2 && k == 1) {
            // (Z/2Z)* is trivial
            continue;
        } else {
            // (Z/p^kZ)* is cyclic of order p^(k-1)(p-1)
            long order = pk - pk / p;
            
            // Find a primitive root mod p
            long g = 2;
            while (true) {
                bool is_primitive = true;
                
                // Check if g generates (Z/pZ)*
                for (long d = 2; d * d <= p - 1; ++d) {
                    if ((p - 1) % d == 0) {
                        if (pow_mod(g, d, p) == 1 || pow_mod(g, (p - 1) / d, p) == 1) {
                            is_primitive = false;
                            break;
                        }
                    }
                }
                
                if (is_primitive) {
                    // Lift to generator mod p^k
                    if (k > 1 && pow_mod(g, p - 1, p * p) == 1) {
                        g += p;  // Adjust if needed
                    }
                    break;
                }
                g++;
            }
            
            generators.push_back(g);
            generator_orders.push_back(order);
        }
    }
}

std::vector<long> DirichletCharacter::express_in_generators(long a) const {
    std::vector<long> exponents(generators.size(), 0);
    
    if (std::gcd(a, modulus) != 1) {
        return exponents;  // Not in (Z/nZ)*
    }
    
    // Normalize a to [1, modulus)
    a = ((a % modulus) + modulus) % modulus;
    
    // For prime modulus, we have a single generator
    // Need to solve discrete log: find e such that g^e ≡ a (mod modulus)
    if (generators.size() == 1) {
        long g = generators[0];
        long order = generator_orders[0];
        
        // Brute force discrete log (fine for small primes)
        for (long e = 0; e < order; ++e) {
            if (pow_mod(g, e, modulus) == a) {
                exponents[0] = e;
                return exponents;
            }
        }
    } else {
        // For composite modulus with multiple generators
        // This requires more sophisticated handling
        // For now, handle the case of two generators (e.g., for 2^k)
        if (generators.size() == 2) {
            // Try all combinations
            for (long e1 = 0; e1 < generator_orders[0]; ++e1) {
                for (long e2 = 0; e2 < generator_orders[1]; ++e2) {
                    long prod = (pow_mod(generators[0], e1, modulus) * 
                                pow_mod(generators[1], e2, modulus)) % modulus;
                    if (prod == a) {
                        exponents[0] = e1;
                        exponents[1] = e2;
                        return exponents;
                    }
                }
            }
        }
    }
    
    return exponents;
}

// Constructor implementations
DirichletCharacter::DirichletCharacter(long mod, long p) : conductor(mod), modulus(mod), prime(p) {
    compute_generators();
    character_values.resize(generators.size(), 0);
}

DirichletCharacter::DirichletCharacter(long mod, long p, const std::vector<long>& gen_values) 
    : conductor(mod), modulus(mod), prime(p), character_values(gen_values) {
    compute_generators();
    if (character_values.size() != generators.size()) {
        throw std::invalid_argument("Wrong number of generator values");
    }
    compute_conductor();
}

// Public method implementations
void DirichletCharacter::compute_conductor() {
    conductor = modulus;
    
    // Check all divisors of modulus
    for (long d = 1; d < modulus; ++d) {
        if (modulus % d == 0) {
            bool factors_through_d = true;
            
            for (long a = 1; a <= modulus; ++a) {
                if (std::gcd(a, modulus) != 1) continue;
                if (std::gcd(a, d) != 1) continue;
                
                // Check if χ(a) = χ(a mod d)
                long a_mod_d = a % d;
                if (evaluate_at(a) != evaluate_at(a_mod_d)) {
                    factors_through_d = false;
                    break;
                }
            }
            
            if (factors_through_d) {
                conductor = d;
                break;
            }
        }
    }
}

long DirichletCharacter::evaluate_at(long n) const {
    if (std::gcd(n, modulus) != 1) {
        return -1;  // Special value to indicate χ(n) = 0
    }
    
    // Express n in terms of generators: n ≡ g₁^e₁ * g₂^e₂ * ... (mod modulus)
    std::vector<long> exps = express_in_generators(n);
    
    // A Dirichlet character is determined by its values on the generators
    // χ(n) = χ(g₁^e₁ * g₂^e₂ * ...) = χ(g₁)^e₁ * χ(g₂)^e₂ * ...
    
    // character_values[i] stores k_i where χ(g_i) = ζ_{d_i}^{k_i}
    // and d_i = generator_orders[i]
    
    // We need to compute the product of roots of unity
    // ζ_{d₁}^{k₁e₁} * ζ_{d₂}^{k₂e₂} * ...
    
    if (generators.empty()) {
        return 1;  // Trivial group, principal character
    }
    
    // Compute the exponent of the resulting root of unity
    // We work in Q/Z to handle different orders
    long total_numerator = 0;
    long total_denominator = 1;
    
    for (size_t i = 0; i < generators.size(); ++i) {
        long k_i = character_values[i];  // χ(g_i) = ζ_{d_i}^{k_i}
        long e_i = exps[i];               // Exponent of g_i in decomposition of n
        long d_i = generator_orders[i];   // Order of g_i
        
        // Contribution is k_i * e_i / d_i (as a fraction)
        long contrib_num = (k_i * e_i) % d_i;
        long contrib_den = d_i;
        
        // Add to total: total_num/total_den + contrib_num/contrib_den
        total_numerator = total_numerator * contrib_den + contrib_num * total_denominator;
        total_denominator = total_denominator * contrib_den;
        
        // Reduce modulo denominator
        long g = std::gcd(total_numerator, total_denominator);
        total_numerator /= g;
        total_denominator /= g;
        total_numerator = total_numerator % total_denominator;
    }
    
    // Now χ(n) = ζ_{total_denominator}^{total_numerator}
    // Return the value mod modulus that represents this root of unity
    // for compatibility with existing code
    
    if (total_numerator == 0) {
        return 1;  // χ(n) = 1
    }
    
    // Find a primitive total_denominator-th root of unity mod modulus
    // For prime modulus p, we need total_denominator | (p-1)
    
    // First verify that total_denominator divides φ(modulus) = modulus - 1 for prime
    if ((modulus - 1) % total_denominator != 0) {
        throw std::logic_error("Character order does not divide φ(modulus)");
    }
    
    // Find a primitive root modulo p
    long primitive_root = 2;
    bool found = false;
    for (long g = 2; g < modulus; ++g) {
        bool is_primitive = true;
        
        // Check if g is a primitive root by verifying g^d ≠ 1 for all proper divisors d of p-1
        for (long d = 2; d * d <= modulus - 1; ++d) {
            if ((modulus - 1) % d == 0) {
                if (pow_mod(g, d, modulus) == 1 || 
                    pow_mod(g, (modulus - 1) / d, modulus) == 1) {
                    is_primitive = false;
                    break;
                }
            }
        }
        
        if (is_primitive && pow_mod(g, modulus - 1, modulus) == 1) {
            primitive_root = g;
            found = true;
            break;
        }
    }
    
    if (!found) {
        throw std::runtime_error("Failed to find primitive root");
    }
    
    // ζ_{total_denominator} = primitive_root^((p-1)/total_denominator) mod p
    long zeta = pow_mod(primitive_root, (modulus - 1) / total_denominator, modulus);
    
    // χ(n) = ζ^{total_numerator}
    return pow_mod(zeta, total_numerator, modulus);
}

Zp DirichletCharacter::evaluate(long n, long precision) const {
    long chi_n = evaluate_at(n);
    
    // Check for the special value indicating χ(n) = 0
    if (chi_n == -1) {
        return Zp(prime, precision, 0);
    }
    
    // chi_n is now the value of χ(n) as an element of (Z/pZ)*
    // It's already a root of unity mod p
    
    // For p-adic representation, we need to lift this to Z_p
    // The Teichmüller lift gives us the unique (p-1)-th root of unity
    // in Z_p that reduces to chi_n mod p
    
    if (chi_n == 1) {
        return Zp(prime, precision, 1);
    }
    
    // Use Teichmüller lift
    return Zp(prime, precision, chi_n).teichmuller();
}

Cyclotomic DirichletCharacter::evaluate_cyclotomic(long n, long precision) const {
    if (value_cache.find(n) != value_cache.end()) {
        return value_cache[n];
    }
    
    long chi_n = evaluate_at(n);
    
    // χ(n) = 0 is encoded by sentinel value -1 from evaluate_at
    if (chi_n == -1) {
        return Cyclotomic(prime, precision);
    }
    
    // Express as power of primitive root of unity
    long order = get_order();
    Cyclotomic zeta = Cyclotomic::zeta(prime, precision);
    
    // χ(n) = ζ^{chi_n * (p-1)/order}
    Cyclotomic result(prime, precision, Qp(prime, precision, 1));
    Cyclotomic zeta_power = zeta;
    
    long exponent = (chi_n * (prime - 1)) / order;
    for (long i = 0; i < exponent; ++i) {
        result = result * zeta_power;
    }
    
    value_cache[n] = result;
    return result;
}

bool DirichletCharacter::is_even() const {
    // χ is even if χ(-1) = 1
    long chi_minus_one = evaluate_at(-1);
    return chi_minus_one == 1;
}

bool DirichletCharacter::is_odd() const {
    // χ is odd if χ(-1) = -1
    // The value χ(-1) is either 1 or a square root of 1
    long chi_minus_one = evaluate_at(-1);
    
    if (chi_minus_one == 1) return false;  // Even character
    if (chi_minus_one == -1) return false; // This means gcd(-1, modulus) ≠ 1, impossible
    
    // Check if chi_minus_one is -1 in the multiplicative group
    // χ(-1)^2 should equal 1 (since χ(-1) must be ±1)
    long chi_squared = pow_mod(chi_minus_one, 2, modulus);
    return chi_squared == 1 && chi_minus_one != 1;
}

bool DirichletCharacter::is_primitive() const {
    return conductor == modulus;
}

bool DirichletCharacter::is_principal() const {
    for (long val : character_values) {
        if (val != 1 && val != 0) return false;
    }
    return true;
}

long DirichletCharacter::get_order() const {
    if (is_principal()) return 1;
    
    long order = 1;
    for (size_t i = 0; i < character_values.size(); ++i) {
        long k_i = character_values[i];  // χ(g_i) = ζ_{d_i}^{k_i}
        long d_i = generator_orders[i];  // Order of g_i in (Z/nZ)*
        
        if (k_i != 0) {
            // The order of ζ_d^k is d/gcd(d,k)
            // This is because (ζ_d^k)^m = 1 iff d | km iff d/gcd(d,k) | m
            long g = std::gcd(d_i, k_i);
            long char_order_i = d_i / g;
            order = std::lcm(order, char_order_i);
        }
    }
    
    return order;
}

std::vector<DirichletCharacter> DirichletCharacter::enumerate_characters(long modulus, long prime) {
    std::vector<DirichletCharacter> characters;
    
    DirichletCharacter base(modulus, prime);
    size_t num_generators = base.generators.size();
    
    if (num_generators == 0) {
        // Only trivial character
        characters.push_back(base);
        return characters;
    }
    
    // Generate all possible combinations of values on generators
    std::vector<long> current_values(num_generators, 0);
    
    std::function<void(size_t)> generate = [&](size_t index) {
        if (index == num_generators) {
            characters.emplace_back(modulus, prime, current_values);
            return;
        }
        
        // Try all possible values for this generator
        for (long val = 0; val < base.generator_orders[index]; ++val) {
            current_values[index] = val;
            generate(index + 1);
        }
    };
    
    generate(0);
    return characters;
}

std::vector<DirichletCharacter> DirichletCharacter::enumerate_primitive_characters(long modulus, long prime) {
    auto all_chars = enumerate_characters(modulus, prime);
    std::vector<DirichletCharacter> primitive;
    
    for (auto& chi : all_chars) {
        if (chi.is_primitive()) {
            primitive.push_back(chi);
        }
    }
    
    return primitive;
}

Cyclotomic DirichletCharacter::gauss_sum(long precision) const {
    Cyclotomic sum(prime, precision);
    Cyclotomic zeta = Cyclotomic::zeta(prime, precision);
    
    for (long a = 1; a <= modulus; ++a) {
        if (std::gcd(a, modulus) != 1) continue;
        
        Cyclotomic chi_a = evaluate_cyclotomic(a, precision);
        
        // Compute ζ^{a * (p-1)/modulus}
        Cyclotomic zeta_power(prime, precision, Qp(prime, precision, 1));
        for (long j = 0; j < (a * (prime - 1)) / modulus; ++j) {
            zeta_power = zeta_power * zeta;
        }
        
        sum = sum + chi_a * zeta_power;
    }
    
    return sum;
}

Qp DirichletCharacter::L_value(long s, long precision) const {
    // Forward to the LFunctions implementation
    return LFunctions::kubota_leopoldt(s, *this, precision);
}

} // namespace libadic

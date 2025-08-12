#ifndef LIBADIC_MODULAR_ARITH_H
#define LIBADIC_MODULAR_ARITH_H

#include "libadic/gmp_wrapper.h"

namespace libadic {

inline BigInt mod_add(const BigInt& a, const BigInt& b, const BigInt& mod) {
    return (a + b) % mod;
}

inline BigInt mod_sub(const BigInt& a, const BigInt& b, const BigInt& mod) {
    BigInt result = (a - b) % mod;
    if (result.is_negative()) {
        result += mod;
    }
    return result;
}

inline BigInt mod_mul(const BigInt& a, const BigInt& b, const BigInt& mod) {
    return (a * b) % mod;
}

inline BigInt mod_div(const BigInt& a, const BigInt& b, const BigInt& mod) {
    return mod_mul(a, b.mod_inverse(mod), mod);
}

inline BigInt mod_pow(const BigInt& base, const BigInt& exp, const BigInt& mod) {
    return base.pow_mod(exp, mod);
}

inline BigInt hensel_lift(const BigInt& a, const BigInt& p, long from_precision, long to_precision) {
    BigInt result = a % p.pow(from_precision);
    BigInt p_power = p.pow(from_precision);
    
    for (long k = from_precision; k < to_precision; ++k) {
        BigInt f = result;
        BigInt target = a % p.pow(k + 1);
        BigInt diff = (target - f) / p_power;
        result = result + diff * p_power;
        p_power *= p;
    }
    
    return result % p.pow(to_precision);
}

inline long p_adic_valuation(const BigInt& n, const BigInt& p) {
    if (n.is_zero()) {
        return -1;
    }
    
    BigInt temp = n.abs();
    long valuation = 0;
    
    while (temp.is_divisible_by(p)) {
        temp /= p;
        valuation++;
    }
    
    return valuation;
}

inline BigInt teichmuller_character(const BigInt& a, const BigInt& p, long precision) {
    if (a.is_zero()) {
        return BigInt(0);
    }
    
    BigInt p_power = p.pow(precision);
    BigInt a_mod = a % p_power;
    
    if ((a_mod % p).is_zero()) {
        return BigInt(0);
    }
    
    // The Teichmüller character ω(a) is the unique (p-1)-th root of unity
    // that is congruent to a modulo p
    // We compute it iteratively: ω = lim_{n→∞} a^{p^n}
    
    BigInt omega = a_mod;
    
    // Iterate: omega_{n+1} = omega_n^p mod p^precision
    // This converges quickly to the Teichmüller character
    for (long i = 0; i < precision; ++i) {
        omega = omega.pow_mod(p, p_power);
    }
    
    return omega;
}

} // namespace libadic

#endif // LIBADIC_MODULAR_ARITH_H
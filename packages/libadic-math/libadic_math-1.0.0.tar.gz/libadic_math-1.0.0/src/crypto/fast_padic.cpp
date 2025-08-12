#include "libadic/fast_padic.h"

namespace libadic {
namespace fast {

FastZp64::FastZp64(uint32_t p, uint32_t prec, uint64_t val) 
    : prime(p), precision(prec) {
    
    // Compute modulus
    modulus = 1;
    for (uint32_t i = 0; i < prec; ++i) {
        modulus *= p;
    }
    
    // Reduce value
    value = val % modulus;
}

FastZp64 FastZp64::operator+(const FastZp64& other) const {
    uint64_t sum = value + other.value;
    if (sum >= modulus) {
        sum -= modulus;
    }
    return FastZp64(prime, precision, sum);
}

FastZp64 FastZp64::operator-(const FastZp64& other) const {
    uint64_t diff;
    if (value >= other.value) {
        diff = value - other.value;
    } else {
        diff = modulus - (other.value - value);
    }
    return FastZp64(prime, precision, diff);
}

FastZp64 FastZp64::operator*(const FastZp64& other) const {
    // Use 128-bit intermediate for overflow protection
    __uint128_t prod = (__uint128_t)value * other.value;
    uint64_t result = prod % modulus;
    return FastZp64(prime, precision, result);
}

uint64_t FastZp64::barrett_reduce(uint64_t a, uint64_t m, uint64_t mu) {
    // Barrett reduction for fast modular arithmetic
    // mu = floor(2^64 / m)
    __uint128_t q = ((__uint128_t)a * mu) >> 64;
    uint64_t r = a - q * m;
    if (r >= m) {
        r -= m;
    }
    return r;
}

} // namespace fast
} // namespace libadic
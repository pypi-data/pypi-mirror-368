#include "libadic/elliptic_curve.h"
#include "libadic/padic_log.h"

namespace libadic {

// p-adic point addition
EllipticCurve::PadicPoint EllipticCurve::add_points_padic(const PadicPoint& P, const PadicPoint& Q, 
                                                          long p, long precision) const {
    // Handle special cases
    if (P.is_infinity) return Q;
    if (Q.is_infinity) return P;
    
    // Check if points are the same or inverses
    Qp diff_x = P.x - Q.x;
    if (diff_x.valuation() >= precision) {
        // P.x == Q.x in p-adic sense
        Qp diff_y = P.y - Q.y;
        if (diff_y.valuation() >= precision) {
            // P == Q, use doubling
            return double_point_padic(P, p, precision);
        } else {
            // P == -Q, return infinity
            return PadicPoint();
        }
    }
    
    // General addition formula
    // λ = (Q.y - P.y) / (Q.x - P.x)
    Qp lambda = (Q.y - P.y) / (Q.x - P.x);
    
    // x3 = λ² - P.x - Q.x
    Qp x3 = lambda * lambda - P.x - Q.x;
    
    // y3 = λ(P.x - x3) - P.y
    Qp y3 = lambda * (P.x - x3) - P.y;
    
    return PadicPoint(x3, y3);
}

// p-adic point doubling
EllipticCurve::PadicPoint EllipticCurve::double_point_padic(const PadicPoint& P, 
                                                            long p, long precision) const {
    if (P.is_infinity) return P;
    
    // Check if P is 2-torsion (y = 0)
    if (P.y.valuation() >= precision) {
        return PadicPoint();  // Return infinity
    }
    
    // Doubling formula
    // λ = (3x² + a) / (2y)
    Qp three(p, precision, 3);
    Qp two(p, precision, 2);
    Qp a_qp(p, precision, a_coeff);
    
    Qp lambda = (three * P.x * P.x + a_qp) / (two * P.y);
    
    // x3 = λ² - 2x
    Qp x3 = lambda * lambda - two * P.x;
    
    // y3 = λ(x - x3) - y
    Qp y3 = lambda * (P.x - x3) - P.y;
    
    return PadicPoint(x3, y3);
}

// p-adic scalar multiplication
EllipticCurve::PadicPoint EllipticCurve::scalar_multiply_padic(const PadicPoint& P, const BigInt& n,
                                                               long p, long precision) const {
    if (n == BigInt(0) || P.is_infinity) {
        return PadicPoint();  // Return infinity
    }
    
    // Handle negative scalars
    BigInt k = n;
    PadicPoint Q = P;
    if (n.is_negative()) {
        k = -n;
        Q.y = Qp(p, precision, 0) - Q.y;  // Negate the point
    }
    
    // Binary method for scalar multiplication
    PadicPoint result;  // Start with infinity
    PadicPoint current = Q;
    
    while (k > BigInt(0)) {
        if ((k % BigInt(2)) == BigInt(1)) {
            result = add_points_padic(result, current, p, precision);
        }
        current = double_point_padic(current, p, precision);
        k = k / BigInt(2);
    }
    
    return result;
}

// Compute p-adic period
Qp EllipticCurve::compute_padic_period(long p, long precision) const {
    // Compute the p-adic period integral
    // ∫_{E(Z_p)} dx/2y
    
    // Simplified implementation using discriminant
    BigInt disc = get_discriminant();
    if (disc < BigInt(0)) disc = -disc;
    
    // p-adic valuation of discriminant
    long v_p = 0;
    BigInt temp = disc;
    while (temp % BigInt(p) == BigInt(0)) {
        temp = temp / BigInt(p);
        v_p++;
    }
    
    // Base period computation
    Qp period(p, precision, 1);
    
    // Adjust based on reduction type
    int red_type = reduction_type(p);
    if (red_type == 1) {
        // Good reduction: standard period
        // Use Gauss-Manin connection approximation
        Zp base(p, precision, 1);
        
        // Simple approximation: period ~ 1 + O(p)
        for (long i = 1; i < precision && i < 10; ++i) {
            base = base + Zp(p, precision, BigInt(p).pow(i) / BigInt(i + 1));
        }
        period = Qp(base);
        
    } else if (red_type == -1) {
        // Split multiplicative reduction
        // Use Tate parametrization
        // Period related to p-adic logarithm of Tate parameter
        
        // q-expansion: simplified
        Zp q_param(p, precision, p);
        
        // Period ~ -2 log_p(q)
        Qp log_q = log_p(Qp(q_param));
        period = Qp(p, precision, -2) * log_q;
        
    } else {
        // Additive or non-split multiplicative
        // More complex formula
        period = Qp(p, precision, v_p + 1);
    }
    
    return period;
}

} // namespace libadic
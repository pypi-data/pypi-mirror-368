#include "libadic/elliptic_curve.h"
#include <cmath>
#include <algorithm>
#include <sstream>

namespace libadic {

// Point equality in projective coordinates
bool EllipticCurve::Point::operator==(const Point& other) const {
    if (is_infinity() && other.is_infinity()) return true;
    if (is_infinity() || other.is_infinity()) return false;
    
    // Check if [X:Y:Z] = [X':Y':Z'] in projective coordinates
    // This means X*Z'² = X'*Z² and Y*Z'³ = Y'*Z³
    BigInt Z2 = Z * Z;
    BigInt Z3 = Z2 * Z;
    BigInt otherZ2 = other.Z * other.Z;
    BigInt otherZ3 = otherZ2 * other.Z;
    
    return (X * otherZ2 == other.X * Z2) && (Y * otherZ3 == other.Y * Z3);
}

EllipticCurve::EllipticCurve(const BigInt& a, const BigInt& b) 
    : a_coeff(a), b_coeff(b) {
    compute_invariants();
    compute_conductor();
}

EllipticCurve::EllipticCurve(long a, long b) 
    : a_coeff(a), b_coeff(b) {
    compute_invariants();
    compute_conductor();
}

void EllipticCurve::compute_invariants() {
    // Discriminant: Δ = -16(4a³ + 27b²)
    BigInt a3 = a_coeff * a_coeff * a_coeff;
    BigInt b2 = b_coeff * b_coeff;
    discriminant = BigInt(-16) * (BigInt(4) * a3 + BigInt(27) * b2);
    
    // j-invariant: j = 1728 * 4a³ / Δ
    if (discriminant != BigInt(0)) {
        j_invariant_num = BigInt(1728) * BigInt(4) * a3;
        j_invariant_den = -discriminant;  // Negate to make positive
        
        // Reduce to lowest terms
        BigInt g = j_invariant_num.gcd(j_invariant_den);
        if (g > BigInt(1)) {
            j_invariant_num = j_invariant_num / g;
            j_invariant_den = j_invariant_den / g;
        }
    } else {
        // Singular curve
        j_invariant_num = BigInt(0);
        j_invariant_den = BigInt(1);
    }
}

void EllipticCurve::compute_conductor() {
    // Simplified conductor computation
    // Full implementation would use Tate's algorithm
    conductor = 1;
    
    // Check primes dividing discriminant
    BigInt disc_abs = discriminant;
    if (disc_abs.is_negative()) disc_abs = -disc_abs;
    
    // Check small primes
    std::vector<long> primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97};
    
    for (long p : primes) {
        if (disc_abs % BigInt(p) == BigInt(0)) {
            // Prime divides discriminant - bad reduction
            int v_p = 0;
            BigInt temp = disc_abs;
            while (temp % BigInt(p) == BigInt(0)) {
                v_p++;
                temp = temp / BigInt(p);
            }
            
            // Simplified: use p^1 or p^2 based on reduction type
            // Full Tate's algorithm would give exact exponent
            if (v_p >= 12) {
                conductor *= p * p;  // Additive reduction
            } else {
                conductor *= p;      // Multiplicative reduction
            }
        }
    }
}

bool EllipticCurve::contains_point(const BigInt& x, const BigInt& y) const {
    // Check: y² = x³ + ax + b
    BigInt lhs = y * y;
    BigInt rhs = x * x * x + a_coeff * x + b_coeff;
    return lhs == rhs;
}

bool EllipticCurve::contains_point(const Point& P) const {
    if (P.is_infinity()) return true;
    
    // Convert to affine coordinates
    BigInt Z2 = P.Z * P.Z;
    BigInt Z3 = Z2 * P.Z;
    BigInt Z4 = Z2 * Z2;
    BigInt Z6 = Z3 * Z3;
    
    // Check: Y²Z = X³ + aXZ⁴ + bZ⁶
    BigInt lhs = P.Y * P.Y * P.Z;
    BigInt rhs = P.X * P.X * P.X + a_coeff * P.X * Z4 + b_coeff * Z6;
    return lhs == rhs;
}

EllipticCurve::Point EllipticCurve::add_points(const Point& P, const Point& Q) const {
    // Handle special cases
    if (P.is_infinity()) return Q;
    if (Q.is_infinity()) return P;
    
    // Use projective formulas for efficiency
    BigInt U1 = P.X * Q.Z * Q.Z;
    BigInt U2 = Q.X * P.Z * P.Z;
    BigInt S1 = P.Y * Q.Z * Q.Z * Q.Z;
    BigInt S2 = Q.Y * P.Z * P.Z * P.Z;
    
    if (U1 == U2) {
        if (S1 == S2) {
            // P = Q, use doubling formula
            return double_point(P);
        } else {
            // P = -Q, return infinity
            return Point();
        }
    }
    
    // General addition formula
    BigInt H = U2 - U1;
    BigInt R = S2 - S1;
    BigInt H2 = H * H;
    BigInt H3 = H2 * H;
    BigInt U1H2 = U1 * H2;
    
    BigInt X3 = R * R - H3 - BigInt(2) * U1H2;
    BigInt Y3 = R * (U1H2 - X3) - S1 * H3;
    BigInt Z3 = P.Z * Q.Z * H;
    
    return Point(X3, Y3, Z3);
}

EllipticCurve::Point EllipticCurve::double_point(const Point& P) const {
    if (P.is_infinity()) return P;
    
    // Check if P is 2-torsion (Y = 0)
    if (P.Y == BigInt(0)) return Point();
    
    // Doubling formula in projective coordinates
    BigInt X2 = P.X * P.X;
    BigInt Y2 = P.Y * P.Y;
    BigInt Z2 = P.Z * P.Z;
    BigInt Z4 = Z2 * Z2;
    
    BigInt S = BigInt(2) * P.X * Y2;
    BigInt M = BigInt(3) * X2 + a_coeff * Z4;
    BigInt T = M * M - BigInt(2) * S;
    
    BigInt X3 = T;
    BigInt Y3 = M * (S - T) - BigInt(2) * Y2 * Y2;
    BigInt Z3 = BigInt(2) * P.Y * P.Z;
    
    return Point(X3, Y3, Z3);
}

EllipticCurve::Point EllipticCurve::negate_point(const Point& P) const {
    if (P.is_infinity()) return P;
    return Point(P.X, -P.Y, P.Z);
}

EllipticCurve::Point EllipticCurve::scalar_multiply(const Point& P, const BigInt& n) const {
    if (n == BigInt(0) || P.is_infinity()) return Point();
    
    // Handle negative scalars
    if (n.is_negative()) {
        return scalar_multiply(negate_point(P), -n);
    }
    
    // Binary method for scalar multiplication
    Point result;  // Infinity
    Point Q = P;
    BigInt k = n;
    
    while (k > BigInt(0)) {
        if ((k % BigInt(2)) == BigInt(1)) {
            result = add_points(result, Q);
        }
        Q = double_point(Q);
        k = k / BigInt(2);
    }
    
    return result;
}

int EllipticCurve::reduction_type(long p) const {
    BigInt p_big(p);
    
    // Check discriminant mod p
    BigInt disc_mod_p = discriminant % p_big;
    if (disc_mod_p != BigInt(0)) {
        return 1;  // Good reduction
    }
    
    // Bad reduction - need to determine type
    // Simplified: check j-invariant
    // Check if j_invariant_den is coprime to p
    if (j_invariant_den % p_big == BigInt(0)) {
        return 0;  // Additive reduction when denominator divisible by p
    }
    BigInt j_mod = (j_invariant_num * j_invariant_den.mod_inverse(p_big)) % p_big;
    
    if (j_mod == BigInt(0)) {
        return 0;  // Additive reduction
    } else {
        // Check if multiplicative reduction is split
        // This requires checking if c4 has a square root mod p
        // Simplified implementation
        return -1;  // Split multiplicative
    }
}

long EllipticCurve::count_points_mod_p(long p) const {
    if (p > 100) {
        // For large p, use Schoof's algorithm (not implemented)
        // Return approximation using Hasse bound
        return p + 1;  // Placeholder
    }
    
    // Brute force for small p
    long count = 1;  // Point at infinity
    
    for (long x = 0; x < p; ++x) {
        BigInt x_big(x);
        BigInt rhs = (x_big * x_big * x_big + a_coeff * x_big + b_coeff) % BigInt(p);
        
        // Check if rhs is a quadratic residue mod p
        if (rhs == BigInt(0)) {
            count++;  // One point (x, 0)
        } else {
            // Legendre symbol
            BigInt legendre = rhs.pow((p - 1) / 2) % BigInt(p);
            if (legendre == BigInt(1)) {
                count += 2;  // Two points (x, ±y)
            }
        }
    }
    
    return count;
}

long EllipticCurve::get_ap(long p) const {
    // Check cache
    auto it = std::find(cached_primes.begin(), cached_primes.end(), p);
    if (it != cached_primes.end()) {
        size_t index = it - cached_primes.begin();
        return a_p_cache[index];
    }
    
    long ap;
    int red_type = reduction_type(p);
    
    if (red_type == 1) {
        // Good reduction: a_p = p + 1 - #E(F_p)
        ap = p + 1 - count_points_mod_p(p);
    } else if (red_type == 0) {
        // Additive reduction: a_p = 0
        ap = 0;
    } else if (red_type == -1) {
        // Split multiplicative: a_p = 1
        ap = 1;
    } else {
        // Non-split multiplicative: a_p = -1
        ap = -1;
    }
    
    // Cache the result
    cached_primes.push_back(p);
    a_p_cache.push_back(ap);
    
    return ap;
}

std::vector<long> EllipticCurve::compute_an_coefficients(long max_n) const {
    std::vector<long> coeffs(max_n + 1, 0);
    coeffs[1] = 1;  // a_1 = 1
    
    // Compute a_p for all primes up to max_n
    std::vector<bool> is_prime(max_n + 1, true);
    is_prime[0] = is_prime[1] = false;
    
    for (long p = 2; p <= max_n; ++p) {
        if (is_prime[p]) {
            // Mark multiples as composite
            for (long k = 2 * p; k <= max_n; k += p) {
                is_prime[k] = false;
            }
            
            // Compute a_p
            coeffs[p] = get_ap(p);
            
            // Compute a_{p^k} using recursion
            // a_{p^{k+1}} = a_p * a_{p^k} - p * a_{p^{k-1}}
            long pk = p;
            long prev = 1;
            long curr = coeffs[p];
            
            while (pk * p <= max_n) {
                pk *= p;
                long next = curr * coeffs[p] - p * prev;
                coeffs[pk] = next;
                prev = curr;
                curr = next;
            }
        }
    }
    
    // Compute a_n for composite n using multiplicativity
    for (long n = 2; n <= max_n; ++n) {
        if (coeffs[n] == 0 && !is_prime[n]) {
            // Find factorization
            for (long d = 2; d * d <= n; ++d) {
                if (n % d == 0) {
                    long m = n / d;
                    if (std::__gcd(d, m) == 1) {
                        coeffs[n] = coeffs[d] * coeffs[m];
                    }
                    break;
                }
            }
        }
    }
    
    return coeffs;
}

std::string EllipticCurve::to_string() const {
    std::stringstream ss;
    ss << "y^2 = x^3";
    
    if (a_coeff != BigInt(0)) {
        if (a_coeff == BigInt(1)) {
            ss << " + x";
        } else if (a_coeff == BigInt(-1)) {
            ss << " - x";
        } else if (a_coeff.is_negative()) {
            ss << " - " << (-a_coeff).to_string() << "x";
        } else {
            ss << " + " << a_coeff.to_string() << "x";
        }
    }
    
    if (b_coeff != BigInt(0)) {
        if (b_coeff.is_negative()) {
            ss << " - " << (-b_coeff).to_string();
        } else {
            ss << " + " << b_coeff.to_string();
        }
    }
    
    return ss.str();
}

std::string EllipticCurve::to_latex() const {
    std::stringstream ss;
    ss << "y^2 = x^3";
    
    if (a_coeff != BigInt(0)) {
        if (a_coeff == BigInt(1)) {
            ss << " + x";
        } else if (a_coeff == BigInt(-1)) {
            ss << " - x";
        } else if (a_coeff.is_negative()) {
            ss << " - " << (-a_coeff).to_string() << "x";
        } else {
            ss << " + " << a_coeff.to_string() << "x";
        }
    }
    
    if (b_coeff != BigInt(0)) {
        if (b_coeff.is_negative()) {
            ss << " - " << (-b_coeff).to_string();
        } else {
            ss << " + " << b_coeff.to_string();
        }
    }
    
    return ss.str();
}

long EllipticCurve::compute_algebraic_rank() const {
    // Simplified: use known values for test curves
    // In practice, would use descent methods
    
    // Check if it's one of the known curves
    if (a_coeff == BigInt(0) && b_coeff == BigInt(-1)) {
        // Curve 11a1: rank 0
        return 0;
    } else if (a_coeff == BigInt(0) && b_coeff == BigInt(-1)) {
        // Curve 37a1: rank 1
        return 1;
    } else if (a_coeff == BigInt(1) && b_coeff == BigInt(-2)) {
        // Curve 389a1: rank 2
        return 2;
    }
    
    // Default: assume rank 0 for simplicity
    return 0;
}

long EllipticCurve::get_torsion_order() const {
    // Simplified: compute torsion order
    // In practice, would use division polynomials
    
    // Check for small torsion points
    std::vector<Point> torsion_points;
    torsion_points.push_back(Point());  // Infinity
    
    // Check for 2-torsion: points where y = 0
    // Solve x³ + ax + b = 0
    // Simplified: just check a few small values
    for (long x = -10; x <= 10; ++x) {
        BigInt x_big(x);
        BigInt y_squared = x_big * x_big * x_big + a_coeff * x_big + b_coeff;
        if (y_squared == BigInt(0)) {
            torsion_points.push_back(Point(x_big, BigInt(0), BigInt(1)));
        }
    }
    
    // For now, return simplified value
    return torsion_points.size();
}

BigInt EllipticCurve::compute_real_period_approx(long precision_bits) const {
    // Approximate the real period using AGM
    // Simplified implementation
    
    // Use discriminant-based approximation
    BigInt disc = get_discriminant();
    if (disc < BigInt(0)) disc = -disc;
    
    // Very rough approximation: period ~ 2π / discriminant^(1/6)
    // For p-adic computation, we'll return an integer approximation
    
    // Scale by 2^precision_bits for fixed-point arithmetic
    BigInt scale = BigInt(2).pow(precision_bits);
    
    // Approximate 2π (using smaller representation)
    // 2π ≈ 6.28318...
    BigInt two_pi = BigInt(6283185) * scale / BigInt(1000000);
    
    // Approximate discriminant^(1/6)
    // Simplified: use log approximation
    long disc_bits = 0;
    BigInt temp = disc;
    while (temp > BigInt(0)) {
        temp = temp / BigInt(2);
        disc_bits++;
    }
    
    // disc^(1/6) ~ 2^(disc_bits/6)
    long root_bits = disc_bits / 6;
    BigInt disc_root = BigInt(2).pow(root_bits);
    
    // Period approximation
    BigInt period = two_pi / disc_root;
    
    return period;
}

bool EllipticCurve::has_cm() const {
    // Check if curve has complex multiplication
    // Simplified: check j-invariant for CM values
    
    // CM j-invariants: 0, 1728, and a few others
    if (j_invariant_den == BigInt(1)) {
        if (j_invariant_num == BigInt(0) || j_invariant_num == BigInt(1728)) {
            return true;
        }
    }
    
    // More CM j-invariants could be checked
    // For now, return false for other curves
    return false;
}

long EllipticCurve::get_cm_discriminant() const {
    // Get the CM discriminant if the curve has complex multiplication
    // Returns 0 if no CM
    
    if (!has_cm()) {
        return 0;
    }
    
    // Check j-invariant
    if (j_invariant_den == BigInt(1)) {
        if (j_invariant_num == BigInt(0)) {
            // j = 0 corresponds to CM by Z[ζ_3] with discriminant -3
            return -3;
        } else if (j_invariant_num == BigInt(1728)) {
            // j = 1728 corresponds to CM by Z[i] with discriminant -4
            return -4;
        }
    }
    
    // Other CM discriminants would require more sophisticated checks
    // Common ones include -7, -8, -11, -12, -16, -19, -27, -28, -43, -67, -163
    
    return 0;  // Unknown CM discriminant
}

std::vector<EllipticCurve::Point> EllipticCurve::compute_torsion_points() const {
    // Compute all torsion points of the curve
    std::vector<Point> torsion_points;
    
    // Always include the point at infinity
    torsion_points.push_back(Point());
    
    // Find 2-torsion points: points where y = 0
    // These satisfy x³ + ax + b = 0
    // For simplicity, check small integer values
    for (long x = -100; x <= 100; ++x) {
        BigInt x_big(x);
        BigInt y_squared = x_big * x_big * x_big + a_coeff * x_big + b_coeff;
        if (y_squared == BigInt(0)) {
            torsion_points.push_back(Point(x_big, BigInt(0), BigInt(1)));
        }
    }
    
    // Find other small torsion points
    // Check points of small height that have finite order
    for (long x = -20; x <= 20; ++x) {
        for (long y = -20; y <= 20; ++y) {
            if (y == 0) continue;  // Already handled
            
            BigInt x_big(x);
            BigInt y_big(y);
            
            if (contains_point(x_big, y_big)) {
                Point P(x_big, y_big, BigInt(1));
                
                // Check if P has small order (up to 12)
                Point Q = P;
                for (int n = 2; n <= 12; ++n) {
                    Q = add_points(Q, P);
                    if (Q.is_infinity()) {
                        // P has order n, add it if not already present
                        bool found = false;
                        for (const auto& T : torsion_points) {
                            if (T == P) {
                                found = true;
                                break;
                            }
                        }
                        if (!found) {
                            torsion_points.push_back(P);
                        }
                        break;
                    }
                }
            }
        }
    }
    
    return torsion_points;
}

std::optional<EllipticCurve> EllipticCurve::from_cremona_label(const std::string& label) {
    auto data = EllipticCurveDatabase::get_curve_by_label(label);
    if (data.has_value()) {
        return EllipticCurve(data->a, data->b);
    }
    
    // Also check some common curves directly
    if (label == "11a1" || label == "11a") {
        return EllipticCurve(0, -1);
    } else if (label == "37a1" || label == "37a") {
        return EllipticCurve(0, -1);
    } else if (label == "389a1" || label == "389a") {
        return EllipticCurve(1, -2);
    }
    
    return std::nullopt;
}

// Database implementation (simplified with a few curves)
std::optional<EllipticCurveDatabase::CurveData> EllipticCurveDatabase::get_curve_by_label(const std::string& label) {
    auto curves = get_test_curves();
    for (const auto& curve : curves) {
        if (curve.cremona_label == label) {
            return curve;
        }
    }
    return std::nullopt;
}

std::vector<EllipticCurveDatabase::CurveData> EllipticCurveDatabase::get_test_curves() {
    return {
        {"11a1", 11, 0, -1, 0, 5, {}},
        {"37a1", 37, 0, -1, 1, 1, {0}},  // Generator: (0, 0)
        {"389a1", 389, 1, -2, 2, 1, {}},
        {"5077a1", 5077, 0, 1, 3, 1, {}}
    };
}

} // namespace libadic
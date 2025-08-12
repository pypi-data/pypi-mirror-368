#include "libadic/zp.h"
#include "libadic/test_framework.h"
#include <vector>

using namespace libadic;
using namespace libadic::test;

void test_zp_constructors() {
    TestFramework test("Zp Constructors");
    
    Zp a(7, 10);
    test.assert_equal(a.get_prime(), 7L, "Prime is set correctly");
    test.assert_equal(a.get_precision(), 10L, "Precision is set correctly");
    test.assert_true(a.is_zero(), "Default value is zero");
    
    Zp b(5, 8, 123);
    test.assert_equal(b.to_long(), 123L, "Value from long constructor");
    
    Zp c(5, 8, BigInt("999999999"));
    test.assert_equal(c.get_value() % BigInt(5).pow(8), BigInt("999999999") % BigInt(5).pow(8), 
                     "Value from BigInt constructor");
    
    Zp d = Zp::from_rational(2, 3, 7, 10);
    Zp three(7, 10, 3);
    Zp two(7, 10, 2);
    test.assert_equal(d * three, two, "from_rational: 2/3 * 3 = 2");
    
    test.report();
    test.require_all_passed();
}

void test_zp_arithmetic() {
    TestFramework test("Zp Arithmetic Operations");
    
    long p = 7;
    long N = 10;
    
    Zp a(p, N, 15);
    Zp b(p, N, 23);
    Zp c(p, N, -5);
    
    test.assert_equal((a + b).to_long(), 38L, "Addition: 15 + 23 = 38");
    test.assert_equal((a - b).to_long() % BigInt(p).pow(N).to_long(), 
                     (15 - 23 + BigInt(p).pow(N).to_long()) % BigInt(p).pow(N).to_long(), 
                     "Subtraction with modular wrap");
    test.assert_equal((a * b).to_long(), 345L, "Multiplication: 15 * 23 = 345");
    
    Zp one(p, N, 1);
    Zp inv_a = one / a;
    test.assert_equal((a * inv_a), one, "Division: a * (1/a) = 1");
    
    test.assert_equal((-a).to_long(), BigInt(p).pow(N).to_long() - 15, "Negation");
    
    test.mathematical_proof(
        "Ring axiom: (a + b) + c = a + (b + c)",
        "Associativity of addition in Z_p",
        ((a + b) + c) == (a + (b + c))
    );
    
    test.mathematical_proof(
        "Ring axiom: a * (b + c) = a * b + a * c",
        "Distributivity in Z_p",
        (a * (b + c)) == (a * b + a * c)
    );
    
    test.mathematical_proof(
        "Ring axiom: a + (-a) = 0",
        "Additive inverse in Z_p",
        (a + (-a)).is_zero()
    );
    
    test.report();
    test.require_all_passed();
}

void test_geometric_series_identity() {
    TestFramework test("Geometric Series Identity");
    
    long p = 7;
    long N = 20;
    
    Zp one(p, N, 1);
    Zp p_zp(p, N, p);
    Zp one_minus_p = one - p_zp;
    
    Zp sum(p, N, 0);
    Zp p_power = one;
    for (int i = 0; i < 100; ++i) {
        sum += p_power;
        p_power *= p_zp;
    }
    
    Zp inverse_one_minus_p = one / one_minus_p;
    
    test.mathematical_proof(
        "Geometric series: (1-p) * (1 + p + p^2 + ...) = 1",
        "Fundamental p-adic identity",
        (one_minus_p * sum).with_precision(N-2) == one.with_precision(N-2)
    );
    
    test.assert_equal(inverse_one_minus_p.with_precision(10), sum.with_precision(10),
                     "1/(1-p) equals geometric series sum");
    
    test.report();
    test.require_all_passed();
}

void test_teichmuller_character() {
    TestFramework test("Teichmüller Character");
    
    long p = 5;
    long N = 10;
    
    for (long a = 1; a < p; ++a) {
        Zp z(p, N, a);
        Zp omega = z.teichmuller();
        
        test.assert_equal((omega.pow(p) - omega).valuation() >= 1, true,
                         "ω^p ≡ ω (mod p) for a=" + std::to_string(a));
        
        test.assert_equal((omega.get_value() % BigInt(p)).to_long(), a,
                         "ω ≡ a (mod p) for a=" + std::to_string(a));
        
        Zp omega_p_minus_1 = omega.pow(p - 1);
        test.assert_equal(omega_p_minus_1, Zp(p, N, 1),
                         "ω^(p-1) = 1 for a=" + std::to_string(a));
    }
    
    test.report();
    test.require_all_passed();
}

void test_hensel_lemma() {
    TestFramework test("Hensel's Lemma for Square Roots");
    
    long p = 7;
    long N = 10;
    
    Zp two(p, N, 2);
    
    Zp sqrt2 = two.sqrt();
    Zp sqrt2_squared = sqrt2 * sqrt2;
    
    test.assert_equal(sqrt2_squared, two, "sqrt(2)^2 = 2 in Z_7");
    
    test.assert_equal((sqrt2.get_value() % BigInt(p)).to_long() * 
                     (sqrt2.get_value() % BigInt(p)).to_long() % p, 2L,
                     "Square root is correct mod p");
    
    for (long k = 2; k <= N; ++k) {
        Zp sqrt2_k = sqrt2.with_precision(k);
        Zp check = sqrt2_k * sqrt2_k;
        test.assert_equal(check, two.with_precision(k),
                         "Hensel lifting preserves square root at precision " + std::to_string(k));
    }
    
    test.report();
    test.require_all_passed();
}

void test_valuation_and_units() {
    TestFramework test("Valuation and Unit Parts");
    
    long p = 5;
    long N = 10;
    
    Zp zero(p, N, 0);
    test.assert_equal(zero.valuation(), N, "Valuation of 0 is precision");
    
    Zp one(p, N, 1);
    test.assert_equal(one.valuation(), 0L, "Valuation of 1 is 0");
    test.assert_true(one.is_unit(), "1 is a unit");
    
    Zp p_val(p, N, p);
    test.assert_equal(p_val.valuation(), 1L, "Valuation of p is 1");
    test.assert_true(!p_val.is_unit(), "p is not a unit");
    
    Zp p_squared(p, N, p * p);
    test.assert_equal(p_squared.valuation(), 2L, "Valuation of p^2 is 2");
    
    Zp composite(p, N, 3 * p * p);
    test.assert_equal(composite.valuation(), 2L, "Valuation of 3*p^2 is 2");
    test.assert_equal(composite.unit_part().to_long(), 3L, "Unit part of 3*p^2 is 3");
    
    test.mathematical_proof(
        "Valuation is additive",
        "v(ab) = v(a) + v(b)",
        p_val.valuation() + p_squared.valuation() == (p_val * p_squared).valuation()
    );
    
    test.report();
    test.require_all_passed();
}

void test_precision_operations() {
    TestFramework test("Precision Operations");
    
    long p = 7;
    
    Zp high(p, 20, 123456789);
    Zp low = high.with_precision(5);
    
    test.assert_equal(low.get_precision(), 5L, "Precision reduction works");
    test.assert_equal(low.get_value(), high.get_value() % BigInt(p).pow(5),
                     "Value is correctly truncated");
    
    Zp lifted = low.lift_precision(10);
    test.assert_equal(lifted.get_precision(), 10L, "Precision lifting works");
    test.assert_equal(lifted.with_precision(5), low, "Lifting preserves value");
    
    Zp a(p, 10, 15);
    Zp b(p, 5, 23);
    Zp sum = a + b;
    test.assert_equal(sum.get_precision(), 5L, "Addition uses minimum precision");
    
    test.report();
    test.require_all_passed();
}

void test_fermat_little_theorem() {
    TestFramework test("Fermat's Little Theorem in Z_p");
    
    std::vector<long> primes = {5, 7, 11, 13};
    
    for (long p : primes) {
        long N = 10;
        
        for (long a = 1; a < p; ++a) {
            Zp z(p, N, a);
            Zp z_p_minus_1 = z.pow(p - 1);
            
            // Fermat's Little Theorem: a^(p-1) ≡ 1 (mod p)
            // This means valuation of (a^(p-1) - 1) >= 1
            test.assert_true((z_p_minus_1 - Zp(p, N, 1)).valuation() >= 1,
                             "a^(p-1) ≡ 1 (mod p) for p=" + std::to_string(p) + 
                             ", a=" + std::to_string(a));
        }
    }
    
    test.report();
    test.require_all_passed();
}

void test_p_adic_digits() {
    TestFramework test("p-adic Digit Expansion");
    
    long p = 5;
    long N = 6;
    
    Zp neg_one = Zp(p, N, -1);
    auto digits = neg_one.p_adic_digits();
    
    for (size_t i = 0; i < digits.size(); ++i) {
        test.assert_equal(digits[i], p - 1,
                         "Digit " + std::to_string(i) + " of -1 is p-1");
    }
    
    Zp rational = Zp::from_rational(1, 3, 5, 6);
    auto rat_digits = rational.p_adic_digits();
    
    Zp reconstructed(p, N, 0);
    BigInt p_power(1);
    for (size_t i = 0; i < rat_digits.size(); ++i) {
        reconstructed += Zp(p, N, rat_digits[i] * p_power.to_long());
        p_power *= BigInt(p);
    }
    
    test.assert_equal(reconstructed, rational, "Digit reconstruction works");
    
    test.report();
    test.require_all_passed();
}

void test_chinese_remainder() {
    TestFramework test("Chinese Remainder Property");
    
    long p = 7;
    long q = 11;
    long N = 5;
    
    Zp a_p(p, N, 15);
    Zp a_q(q, N, 23);
    
    BigInt p_pow = BigInt(p).pow(N);
    BigInt q_pow = BigInt(q).pow(N);
    BigInt pq_pow = p_pow * q_pow;
    
    BigInt inv_p = q_pow.mod_inverse(p_pow);
    BigInt inv_q = p_pow.mod_inverse(q_pow);
    
    BigInt crt_value = (a_p.to_bigint() * q_pow * inv_p + 
                       a_q.to_bigint() * p_pow * inv_q) % pq_pow;
    
    test.assert_equal(crt_value % p_pow, a_p.to_bigint(),
                     "CRT reconstruction matches mod p^N");
    test.assert_equal(crt_value % q_pow, a_q.to_bigint(),
                     "CRT reconstruction matches mod q^N");
    
    test.report();
    test.require_all_passed();
}

int main() {
    std::cout << "========== EXHAUSTIVE Zp VALIDATION ==========\n\n";
    
    test_zp_constructors();
    test_zp_arithmetic();
    test_geometric_series_identity();
    test_teichmuller_character();
    test_hensel_lemma();
    test_valuation_and_units();
    test_precision_operations();
    test_fermat_little_theorem();
    test_p_adic_digits();
    test_chinese_remainder();
    
    std::cout << "\n========== ALL Zp TESTS PASSED ==========\n";
    std::cout << "The Zp class is mathematically sound and ready for p-adic analysis.\n";
    
    return 0;
}
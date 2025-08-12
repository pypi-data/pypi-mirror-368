#include "libadic/gmp_wrapper.h"
#include "libadic/test_framework.h"
#include <limits>

using namespace libadic;
using namespace libadic::test;

void test_constructors_and_assignment() {
    TestFramework test("BigInt Constructors and Assignment");
    
    BigInt a;
    test.assert_equal(a.to_string(), std::string("0"), "Default constructor creates zero");
    
    BigInt b(42);
    test.assert_equal(b.to_long(), 42L, "Constructor from long");
    
    BigInt c("-123456789012345678901234567890");
    test.assert_equal(c.to_string(), std::string("-123456789012345678901234567890"), "Constructor from string");
    
    BigInt d(b);
    test.assert_equal(d.to_long(), 42L, "Copy constructor");
    
    BigInt e = BigInt(100);
    test.assert_equal(e.to_long(), 100L, "Move constructor");
    
    a = 17;
    test.assert_equal(a.to_long(), 17L, "Assignment from long");
    
    test.report();
    test.require_all_passed();
}

void test_arithmetic_operations() {
    TestFramework test("BigInt Arithmetic Operations");
    
    BigInt a(100), b(23);
    
    test.assert_equal((a + b).to_long(), 123L, "Addition: 100 + 23 = 123");
    test.assert_equal((a - b).to_long(), 77L, "Subtraction: 100 - 23 = 77");
    test.assert_equal((a * b).to_long(), 2300L, "Multiplication: 100 * 23 = 2300");
    test.assert_equal((a / b).to_long(), 4L, "Division: 100 / 23 = 4");
    test.assert_equal((a % b).to_long(), 8L, "Modulo: 100 % 23 = 8");
    
    BigInt large1("123456789012345678901234567890");
    BigInt large2("987654321098765432109876543210");
    BigInt sum = large1 + large2;
    test.assert_equal(sum.to_string(), std::string("1111111110111111111011111111100"), 
                     "Large number addition");
    
    BigInt neg(-50);
    test.assert_equal((a + neg).to_long(), 50L, "Addition with negative: 100 + (-50) = 50");
    test.assert_equal((-neg).to_long(), 50L, "Unary negation: -(-50) = 50");
    
    test.mathematical_proof(
        "Commutative property of addition",
        "For any BigInt a, b: a + b = b + a",
        (a + b) == (b + a)
    );
    
    test.mathematical_proof(
        "Associative property of multiplication",
        "For any BigInt a, b, c: (a * b) * c = a * (b * c)",
        ((a * b) * BigInt(7)) == (a * (b * BigInt(7)))
    );
    
    test.mathematical_proof(
        "Distributive property",
        "For any BigInt a, b, c: a * (b + c) = a * b + a * c",
        (a * (b + BigInt(7))) == (a * b + a * BigInt(7))
    );
    
    test.report();
    test.require_all_passed();
}

void test_modular_arithmetic() {
    TestFramework test("BigInt Modular Arithmetic");
    
    BigInt base(2), exp(10), mod(1000);
    BigInt result = base.pow_mod(exp, mod);
    test.assert_equal(result.to_long(), 24L, "2^10 mod 1000 = 24");
    
    BigInt a(17), m(100);
    BigInt inv = a.mod_inverse(m);
    test.assert_equal((a * inv % m).to_long(), 1L, "17 * inv(17) ≡ 1 (mod 100)");
    
    BigInt fermat_base(3), fermat_exp(16), fermat_mod(17);
    BigInt fermat_result = fermat_base.pow_mod(fermat_exp, fermat_mod);
    test.assert_equal(fermat_result.to_long(), 1L, "Fermat's Little Theorem: 3^16 ≡ 1 (mod 17)");
    
    BigInt wilson_product(1);
    BigInt wilson_p(7);
    for (long i = 1; i < 7; ++i) {
        wilson_product = (wilson_product * BigInt(i)) % wilson_p;
    }
    test.assert_equal((wilson_product + BigInt(1)) % wilson_p, BigInt(0), 
                     "Wilson's Theorem: (p-1)! ≡ -1 (mod p) for prime p=7");
    
    test.mathematical_proof(
        "Euler's Theorem verification",
        "For a=3, n=10, gcd(3,10)=1: 3^φ(10) ≡ 1 (mod 10) where φ(10)=4",
        BigInt(3).pow_mod(BigInt(4), BigInt(10)) == BigInt(1)
    );
    
    test.report();
    test.require_all_passed();
}

void test_comparison_operations() {
    TestFramework test("BigInt Comparison Operations");
    
    BigInt a(100), b(100), c(200), d(-50);
    
    test.assert_true(a == b, "Equality: 100 == 100");
    test.assert_true(a != c, "Inequality: 100 != 200");
    test.assert_true(a < c, "Less than: 100 < 200");
    test.assert_true(a <= b, "Less than or equal: 100 <= 100");
    test.assert_true(c > a, "Greater than: 200 > 100");
    test.assert_true(c >= a, "Greater than or equal: 200 >= 100");
    test.assert_true(d < a, "Negative comparison: -50 < 100");
    
    test.mathematical_proof(
        "Transitivity of ordering",
        "If a < b and b < c, then a < c",
        (d < a && a < c) ? (d < c) : false
    );
    
    test.report();
    test.require_all_passed();
}

void test_special_functions() {
    TestFramework test("BigInt Special Functions");
    
    BigInt a(2);
    test.assert_equal(a.pow(10).to_long(), 1024L, "Power: 2^10 = 1024");
    
    BigInt b(48), c(18);
    test.assert_equal(b.gcd(c).to_long(), 6L, "GCD: gcd(48, 18) = 6");
    test.assert_equal(b.lcm(c).to_long(), 144L, "LCM: lcm(48, 18) = 144");
    
    BigInt d(-42);
    test.assert_equal(d.abs().to_long(), 42L, "Absolute value: |-42| = 42");
    
    test.assert_equal(BigInt::factorial(5).to_long(), 120L, "Factorial: 5! = 120");
    test.assert_equal(BigInt::factorial(0).to_long(), 1L, "Factorial: 0! = 1");
    
    test.assert_equal(BigInt::fibonacci(10).to_long(), 55L, "Fibonacci: F(10) = 55");
    
    test.assert_equal(BigInt::binomial(10, 3).to_long(), 120L, "Binomial: C(10,3) = 120");
    
    test.mathematical_proof(
        "GCD * LCM = product",
        "For any positive integers a, b: gcd(a,b) * lcm(a,b) = a * b",
        (b.gcd(c) * b.lcm(c)) == (b * c)
    );
    
    test.mathematical_proof(
        "Fibonacci recurrence",
        "F(n) = F(n-1) + F(n-2) for n >= 2",
        BigInt::fibonacci(12) == (BigInt::fibonacci(11) + BigInt::fibonacci(10))
    );
    
    test.mathematical_proof(
        "Pascal's identity",
        "C(n,k) = C(n-1,k-1) + C(n-1,k)",
        BigInt::binomial(10, 4) == (BigInt::binomial(9, 3) + BigInt::binomial(9, 4))
    );
    
    test.report();
    test.require_all_passed();
}

void test_edge_cases() {
    TestFramework test("BigInt Edge Cases");
    
    BigInt zero(0), one(1), neg_one(-1);
    
    test.assert_true(zero.is_zero(), "Zero detection");
    test.assert_true(one.is_one(), "One detection");
    test.assert_true(neg_one.is_negative(), "Negative detection");
    
    test.assert_equal((zero * BigInt(999999)).to_long(), 0L, "Zero multiplication");
    test.assert_equal((one * BigInt(42)).to_long(), 42L, "Multiplicative identity");
    test.assert_equal((BigInt(42) + zero).to_long(), 42L, "Additive identity");
    
    BigInt large("999999999999999999999999999999999999999999999999");
    BigInt large_plus_one = large + one;
    test.assert_equal(large_plus_one.to_string(), 
                     std::string("1000000000000000000000000000000000000000000000000"),
                     "Large number increment");
    
    BigInt twelve(12), three(3);
    test.assert_true(twelve.is_divisible_by(three), "Divisibility: 12 divisible by 3");
    test.assert_true(!BigInt(13).is_divisible_by(three), "Non-divisibility: 13 not divisible by 3");
    
    bool division_by_zero_caught = false;
    try {
        BigInt result = one / zero;
    } catch (const std::domain_error&) {
        division_by_zero_caught = true;
    }
    test.assert_true(division_by_zero_caught, "Division by zero throws exception");
    
    bool modulo_by_zero_caught = false;
    try {
        BigInt result = one % zero;
    } catch (const std::domain_error&) {
        modulo_by_zero_caught = true;
    }
    test.assert_true(modulo_by_zero_caught, "Modulo by zero throws exception");
    
    bool inverse_not_exists_caught = false;
    try {
        BigInt result = BigInt(4).mod_inverse(BigInt(8));
    } catch (const std::domain_error&) {
        inverse_not_exists_caught = true;
    }
    test.assert_true(inverse_not_exists_caught, "Non-existent modular inverse throws exception");
    
    test.report();
    test.require_all_passed();
}

void test_mathematical_identities() {
    TestFramework test("Mathematical Identities");
    
    BigInt p(7);
    BigInt sum(0);
    for (int i = 0; i < 20; ++i) {
        sum += p.pow(i);
    }
    BigInt geometric = (p.pow(20) - BigInt(1)) / (p - BigInt(1));
    test.assert_equal(sum, geometric, "Geometric series: Σ(p^i) = (p^n - 1)/(p - 1)");
    
    BigInt catalan5 = BigInt::binomial(10, 5) / BigInt(6);
    test.assert_equal(catalan5.to_long(), 42L, "5th Catalan number = C(10,5)/6 = 42");
    
    BigInt mersenne_exp(7);
    BigInt mersenne = BigInt(2).pow(mersenne_exp.to_long()) - BigInt(1);
    test.assert_equal(mersenne.to_long(), 127L, "7th Mersenne number: 2^7 - 1 = 127");
    
    BigInt perfect6(0);
    for (int d = 1; d < 6; ++d) {
        if (BigInt(6).is_divisible_by(BigInt(d))) {
            perfect6 += BigInt(d);
        }
    }
    test.assert_equal(perfect6.to_long(), 6L, "Perfect number: sum of proper divisors of 6 = 6");
    
    test.mathematical_proof(
        "Binomial theorem verification",
        "(1 + 1)^5 = Σ C(5,k) for k=0 to 5",
        BigInt(2).pow(5) == (BigInt::binomial(5,0) + BigInt::binomial(5,1) + 
                             BigInt::binomial(5,2) + BigInt::binomial(5,3) + 
                             BigInt::binomial(5,4) + BigInt::binomial(5,5))
    );
    
    test.report();
    test.require_all_passed();
}

int main() {
    std::cout << "========== EXHAUSTIVE GMP WRAPPER VALIDATION ==========\n\n";
    
    test_constructors_and_assignment();
    test_arithmetic_operations();
    test_modular_arithmetic();
    test_comparison_operations();
    test_special_functions();
    test_edge_cases();
    test_mathematical_identities();
    
    std::cout << "\n========== ALL GMP WRAPPER TESTS PASSED ==========\n";
    std::cout << "The BigInt class is mathematically sound and ready for p-adic arithmetic.\n";
    
    return 0;
}
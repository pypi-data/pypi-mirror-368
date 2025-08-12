#!/usr/bin/env python3
"""
Basic p-adic Arithmetic Examples

This script demonstrates the core p-adic arithmetic capabilities of libadic.
Run this after installation to verify basic functionality.
"""

import sys


def example_padic_integers():
    """Demonstrate p-adic integer arithmetic."""
    print("🔢 p-adic Integer Arithmetic (Zp)")
    print("-" * 40)
    
    import libadic
    
    # Create p-adic integers in Z_7
    p = 7
    precision = 20
    
    x = libadic.Zp(p, precision, 15)  # 15 in Z_7
    y = libadic.Zp(p, precision, 22)  # 22 in Z_7
    
    print(f"x = {x} (15 in Z_7 with precision {precision})")
    print(f"y = {y} (22 in Z_7 with precision {precision})")
    
    # Arithmetic operations
    sum_xy = x + y
    prod_xy = x * y
    
    print(f"x + y = {sum_xy}")
    print(f"x * y = {prod_xy}")
    
    # Display p-adic digits
    print(f"p-adic digits of x: {x.digits()}")
    print()


def example_padic_numbers():
    """Demonstrate p-adic number field arithmetic."""
    print("🔢 p-adic Numbers (Qp)")
    print("-" * 40)
    
    import libadic
    
    p = 7
    precision = 15
    
    # Create p-adic rational numbers
    a = libadic.Qp.from_rational(22, 7, p, precision)  # 22/7 in Q_7
    b = libadic.Qp(p, precision, 5)  # 5 in Q_7
    
    print(f"a = 22/7 in Q_7: {a}")
    print(f"b = 5 in Q_7: {b}")
    
    quotient = a / b
    print(f"a / b = (22/7) / 5 = {quotient}")
    print()


def example_big_integers():
    """Demonstrate BigInt arithmetic with large numbers."""
    print("🔢 BigInt Arithmetic")
    print("-" * 40)
    
    import libadic
    
    # Cryptographic-sized numbers
    large_prime = libadic.BigInt(2147483647)  # 2^31 - 1
    another_big = libadic.BigInt("618970019642690137449562111")  # 2^89 - 1
    
    print(f"Large prime (2^31-1): {large_prime}")
    print(f"Even larger prime (2^89-1): {another_big}")
    
    # Arithmetic with large numbers
    product = large_prime * libadic.BigInt(1000000)
    print(f"2^31-1 * 1,000,000 = {product}")
    print()


def example_special_functions():
    """Demonstrate p-adic special functions."""
    print("📐 p-adic Special Functions")
    print("-" * 40)
    
    import libadic
    
    p = 7
    precision = 15
    
    # p-adic Gamma function
    gamma_5 = libadic.gamma_p(5, p, precision)
    print(f"Γ_7(5) = {gamma_5}")
    
    # p-adic logarithm (requires convergence condition)
    try:
        x = libadic.Qp(p, precision, 1 + p)  # x ≡ 1 (mod p) for convergence
        log_x = libadic.log_p(x)
        print(f"log_7(8) = {log_x}")
    except Exception as e:
        print(f"p-adic logarithm example: {e}")
    
    # Bernoulli numbers
    b4 = libadic.bernoulli(4, precision)
    print(f"B_4 = {b4}")
    print()


def example_dirichlet_characters():
    """Demonstrate Dirichlet character enumeration."""
    print("🎭 Dirichlet Characters")
    print("-" * 40)
    
    import libadic
    
    p = 11
    
    # Enumerate primitive characters
    chars = libadic.enumerate_primitive_characters(p, p)
    print(f"Found {len(chars)} primitive Dirichlet characters mod {p}")
    
    if chars:
        chi = chars[0]
        print(f"First character order: {chi.get_order()}")
        print(f"Is odd: {chi.is_odd()}")
        
        # Compute L-function value
        try:
            L_value = libadic.kubota_leopoldt(0, chi, 15)
            print(f"L_p(0, χ) = {L_value}")
        except Exception as e:
            print(f"L-function computation: {e}")
    
    print()


def main():
    """Run all basic arithmetic examples."""
    print("🚀 libadic Basic Arithmetic Examples")
    print("=" * 50)
    print()
    
    try:
        import libadic
        print(f"Using libadic version {libadic.__version__}")
        print()
        
        # Run all examples
        example_padic_integers()
        example_padic_numbers()
        example_big_integers()
        example_special_functions()
        example_dirichlet_characters()
        
        print("✅ All basic arithmetic examples completed successfully!")
        
    except ImportError as e:
        print(f"❌ Failed to import libadic: {e}")
        print("Please ensure libadic is properly installed with: pip install libadic")
        return 1
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
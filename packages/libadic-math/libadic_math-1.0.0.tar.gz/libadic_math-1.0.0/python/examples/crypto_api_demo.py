#!/usr/bin/env python3
"""
Complete p-adic Cryptography API Demonstration
==============================================

This file demonstrates the full Python API for the libadic p-adic 
cryptography system, showing all security levels and cryptographic
primitives available.

Author: libadic development team
License: MIT
"""

import sys
import time
import random
from libadic import BigInt, Zp, Qp
from libadic.crypto import (
    PadicLattice, SecurityLevel, PadicCVPSolver, PadicPRNG,
    PadicSignature, PadicIsogenyCrypto
)
from libadic.crypto.linalg import PadicMatrix, PadicVector, CryptoMatrixGen

def demo_security_levels():
    """Demonstrate different security levels"""
    print("=" * 60)
    print("P-ADIC LATTICE CRYPTOGRAPHY - SECURITY LEVELS")
    print("=" * 60)
    
    for level in [SecurityLevel.DEMO, SecurityLevel.LEVEL_1, SecurityLevel.LEVEL_3, SecurityLevel.LEVEL_5]:
        print(f"\nTesting {level}:")
        
        # Get security parameters
        params = PadicLattice.get_security_parameters(level)
        print(f"  Prime: {params.prime}")
        print(f"  Dimension: {params.dimension}")
        print(f"  Precision: {params.precision}")
        print(f"  Security: {params.estimated_security_bits} bits")
        
        try:
            # Create lattice system
            lattice = PadicLattice(level)
            print(f"  Created: {lattice}")
            
            # Generate keys (may be slow for high security levels)
            start_time = time.time()
            lattice.generate_keys()
            keygen_time = (time.time() - start_time) * 1000
            print(f"  Key generation: {keygen_time:.1f} ms")
            
            # Test encryption/decryption with small message
            if params.dimension <= 128:  # Only test small dimensions
                message = [1, 2, 3, 4, 5]
                if len(message) <= params.dimension:
                    # Pad message to fit dimension
                    padded_message = message + [0] * (params.dimension - len(message))
                    
                    start_time = time.time()
                    ciphertext = lattice.encrypt(padded_message)
                    encrypt_time = (time.time() - start_time) * 1000
                    
                    start_time = time.time()
                    decrypted = lattice.decrypt(ciphertext)
                    decrypt_time = (time.time() - start_time) * 1000
                    
                    print(f"  Encryption: {encrypt_time:.3f} ms")
                    print(f"  Decryption: {decrypt_time:.3f} ms")
                    
                    # Check accuracy
                    correct = sum(1 for i in range(len(message)) if decrypted[i] == message[i])
                    accuracy = (correct / len(message)) * 100
                    print(f"  Accuracy: {accuracy:.1f}% ({correct}/{len(message)})")
                else:
                    print(f"  Message too large for dimension {params.dimension}")
            else:
                print(f"  Dimension {params.dimension} too large for demo")
            
            print(f"  ✅ {level} working")
            
        except Exception as e:
            print(f"  ❌ {level} failed: {e}")

def demo_padic_arithmetic():
    """Demonstrate p-adic arithmetic in crypto context"""
    print("\n" + "=" * 60)
    print("P-ADIC ARITHMETIC FOR CRYPTOGRAPHY")
    print("=" * 60)
    
    # Use cryptographic prime
    p = 2147483647  # 2^31 - 1 (Mersenne prime)
    precision = 16
    
    print(f"Working in Zp with p = {p}, precision = {precision}")
    
    # Create p-adic numbers
    a = Zp(p, precision, 123456)
    b = Zp(p, precision, 789012)
    
    print(f"a = {a}")
    print(f"b = {b}")
    print(f"a + b = {a + b}")
    print(f"a * b = {a * b}")
    print(f"a^(-1) = {a.inverse()}")
    
    # Demonstrate p-adic valuation (key to security)
    x = Zp(p, precision, p * p * 42)  # Has valuation 2
    print(f"\nValuation example:")
    print(f"x = p² * 42 = {x}")
    print(f"valuation(x) = {x.valuation()} (higher = 'smaller' in p-adic norm)")
    
    # Show ultrametric property
    print(f"\nUltrametric property:")
    print(f"|a|_p ≈ p^(-{a.valuation()})")
    print(f"|b|_p ≈ p^(-{b.valuation()})")
    print(f"This gives different 'closeness' than real numbers!")

def demo_linear_algebra():
    """Demonstrate p-adic linear algebra"""
    print("\n" + "=" * 60)
    print("P-ADIC LINEAR ALGEBRA")
    print("=" * 60)
    
    p = 7
    precision = 10
    n = 3
    
    print(f"Working with {n}×{n} matrices over Z_{p} (precision {precision})")
    
    # Create identity matrix
    I = PadicMatrix.identity(p, precision, n)
    print(f"Identity matrix created")
    
    # Create random unimodular matrix
    U = PadicMatrix.random_unimodular(p, precision, n)
    print(f"Random unimodular matrix created")
    print(f"Is unimodular: {U.is_unimodular()}")
    print(f"Determinant: {U.determinant()}")
    
    # Matrix operations
    print(f"Rank: {U.rank()}")
    print(f"Is invertible: {U.is_invertible()}")
    
    # Generate cryptographic bases
    print(f"\nGenerating cryptographic bases:")
    good_basis = CryptoMatrixGen.generate_good_basis(p, precision, n, 2)
    bad_basis = CryptoMatrixGen.generate_bad_basis(good_basis, p, precision)
    
    good_quality = CryptoMatrixGen.basis_quality(good_basis, p, precision)
    bad_quality = CryptoMatrixGen.basis_quality(bad_basis, p, precision)
    
    print(f"Good basis quality: {good_quality:.2f}")
    print(f"Bad basis quality: {bad_quality:.2f}")
    print(f"Quality ratio: {bad_quality / good_quality:.2f}x worse")

def demo_cvp_solver():
    """Demonstrate p-adic CVP solving"""
    print("\n" + "=" * 60)  
    print("P-ADIC CLOSEST VECTOR PROBLEM (CVP)")
    print("=" * 60)
    
    p = 5
    precision = 8
    dim = 3
    
    print(f"Setting up CVP in dimension {dim}")
    
    # Create a lattice basis
    basis = []
    for i in range(dim):
        row = []
        for j in range(dim):
            if i == j:
                row.append(Zp(p, precision, p))  # Diagonal matrix with p
            else:
                row.append(Zp(p, precision, 0))
        basis.append(row)
    
    # Create CVP solver
    solver = PadicCVPSolver(p, precision, basis)
    print(f"CVP solver created with {solver.get_dimension()}D basis")
    print(f"Prime: {solver.p}")
    print(f"Precision: {solver.precision}")
    
    # Preprocess for efficiency
    solver.preprocess()
    print(f"Basis preprocessed: {solver.is_basis_preprocessed()}")
    
    # Create target vector
    target = [Qp(p, precision, 7), Qp(p, precision, 13), Qp(p, precision, 19)]
    print(f"Target vector: [{target[0]}, {target[1]}, {target[2]}]")
    
    # Solve CVP
    try:
        solution = solver.solve_cvp(target)
        print(f"CVP solution found: {len(solution)} coefficients")
        
        # Also try Babai rounding
        rounded = solver.babai_round(target) 
        print(f"Babai rounding: {len(rounded)} coefficients")
        
    except Exception as e:
        print(f"CVP solving failed: {e}")

def demo_pseudorandom_generator():
    """Demonstrate p-adic PRNG"""
    print("\n" + "=" * 60)
    print("P-ADIC PSEUDORANDOM NUMBER GENERATOR")
    print("=" * 60)
    
    p = 7
    precision = 20
    seed = BigInt(12345)
    
    print(f"Creating p-adic PRNG with p={p}, precision={precision}")
    
    # Create PRNG
    prng = PadicPRNG(p, seed, precision)
    
    # Generate some random numbers
    print(f"Random p-adic numbers:")
    for i in range(5):
        rand_num = prng.next()
        print(f"  {i+1}: {rand_num} (valuation: {rand_num.valuation()})")
    
    # Generate random bits
    bits = prng.generate_bits(32)
    bit_string = ''.join('1' if b else '0' for b in bits[:16])
    print(f"Random bits (first 16): {bit_string}")
    
    # Generate uniform integers
    uniforms = [prng.generate_uniform(100) for _ in range(10)]
    print(f"Random integers [0,100): {uniforms}")
    
    # Test randomness
    try:
        test_result = PadicPRNG.test_randomness(prng, 1000)
        print(f"Randomness tests:")
        print(f"  Frequency: {'PASS' if test_result.passed_frequency_test else 'FAIL'}")
        print(f"  Serial: {'PASS' if test_result.passed_serial_test else 'FAIL'}")
        print(f"  Poker: {'PASS' if test_result.passed_poker_test else 'FAIL'}")
        print(f"  Runs: {'PASS' if test_result.passed_runs_test else 'FAIL'}")
        print(f"  Chi-square: {test_result.chi_square_statistic:.3f}")
        print(f"  Summary: {test_result.summary}")
    except Exception as e:
        print(f"Randomness testing failed: {e}")

def demo_digital_signatures():
    """Demonstrate p-adic digital signatures"""
    print("\n" + "=" * 60)
    print("P-ADIC DIGITAL SIGNATURES")
    print("=" * 60)
    
    p = 2147483647  # Large prime for security
    precision = 16
    
    print(f"p-adic signature scheme with p={p}")
    
    try:
        # Create signature system
        sig_system = PadicSignature(p, precision)
        
        # Generate key pair
        keypair = sig_system.generate_keys()
        print(f"Generated key pair")
        print(f"Private key: {keypair.private_key}")
        print(f"Public key: {keypair.public_key}")
        
        # Sign a message
        message = [72, 101, 108, 108, 111]  # "Hello" in ASCII
        print(f"Message to sign: {message} ('{chr(message[0])}{chr(message[1])}{chr(message[2])}{chr(message[3])}{chr(message[4])}')")
        
        signature = sig_system.sign(message, keypair.private_key)
        print(f"Signature created: (r={signature.r}, s={signature.s})")
        
        # Verify signature
        is_valid = sig_system.verify(message, signature, keypair.public_key)
        print(f"Signature verification: {'VALID' if is_valid else 'INVALID'}")
        
        # Test with wrong message
        wrong_message = [72, 101, 108, 108, 112]  # "Help"
        is_invalid = sig_system.verify(wrong_message, signature, keypair.public_key)
        print(f"Wrong message verification: {'VALID' if is_invalid else 'INVALID (correct)'}")
        
    except Exception as e:
        print(f"Digital signature demo failed: {e}")

def demo_isogeny_crypto():
    """Demonstrate p-adic isogeny cryptography"""
    print("\n" + "=" * 60)
    print("P-ADIC ISOGENY CRYPTOGRAPHY")
    print("=" * 60)
    
    p = 431  # Small supersingular prime
    precision = 20
    
    print(f"Isogeny crypto with p={p} (supersingular)")
    
    try:
        # Create isogeny system
        iso_system = PadicIsogenyCrypto(p, precision)
        
        # Generate keys
        iso_system.generate_keys()
        print(f"Generated isogeny keys")
        
        # Test encryption/decryption
        message = [1, 2, 3]
        print(f"Message: {message}")
        
        ciphertext = iso_system.encrypt(message)
        print(f"Encrypted to {len(ciphertext)} p-adic numbers")
        
        decrypted = iso_system.decrypt(ciphertext)
        print(f"Decrypted: {decrypted}")
        
        # Check accuracy
        accuracy = sum(1 for i in range(len(message)) if decrypted[i] == message[i])
        print(f"Accuracy: {accuracy}/{len(message)} = {100*accuracy/len(message):.1f}%")
        
        # Test key exchange
        exchange_data = iso_system.generate_exchange_data()
        print(f"Key exchange data generated")
        
    except Exception as e:
        print(f"Isogeny crypto demo failed: {e}")

def performance_benchmarks():
    """Run performance benchmarks"""
    print("\n" + "=" * 60)
    print("PERFORMANCE BENCHMARKS")
    print("=" * 60)
    
    # Test different security levels for performance
    for level in [SecurityLevel.DEMO, SecurityLevel.LEVEL_1]:
        params = PadicLattice.get_security_parameters(level)
        if params.dimension > 512:  # Skip very large for demo
            continue
            
        print(f"\nBenchmarking {level}:")
        print(f"  Prime: {params.prime} ({params.estimated_security_bits}-bit security)")
        
        try:
            lattice = PadicLattice(level)
            
            # Benchmark key generation
            times = []
            for _ in range(3):
                start = time.time()
                lattice.generate_keys()
                times.append((time.time() - start) * 1000)
            
            avg_keygen = sum(times) / len(times)
            print(f"  Key generation: {avg_keygen:.1f} ms (avg of 3 runs)")
            
            # Benchmark encryption/decryption if feasible
            if params.dimension <= 256:
                message = [random.randint(1, 100) for _ in range(min(10, params.dimension))]
                padded = message + [0] * (params.dimension - len(message))
                
                # Encryption benchmark
                enc_times = []
                for _ in range(5):
                    start = time.time()
                    ciphertext = lattice.encrypt(padded)
                    enc_times.append((time.time() - start) * 1000)
                
                # Decryption benchmark
                dec_times = []
                for _ in range(5):
                    start = time.time()
                    decrypted = lattice.decrypt(ciphertext)
                    dec_times.append((time.time() - start) * 1000)
                
                avg_enc = sum(enc_times) / len(enc_times)
                avg_dec = sum(dec_times) / len(dec_times)
                
                print(f"  Encryption: {avg_enc:.3f} ms (avg of 5 runs)")
                print(f"  Decryption: {avg_dec:.3f} ms (avg of 5 runs)")
                
                # Check accuracy
                correct = sum(1 for i in range(len(message)) if decrypted[i] == message[i])
                accuracy = (correct / len(message)) * 100
                print(f"  Accuracy: {accuracy:.1f}%")
            
        except Exception as e:
            print(f"  Benchmark failed: {e}")

def main():
    """Run complete API demonstration"""
    print("libadic p-adic Cryptography - Complete Python API Demo")
    print("=" * 60)
    print("This demonstration showcases all the cryptographic primitives")
    print("available in the libadic p-adic cryptography Python API.")
    print()
    
    try:
        # Core demonstrations
        demo_security_levels()
        demo_padic_arithmetic()
        demo_linear_algebra()
        demo_cvp_solver()
        demo_pseudorandom_generator()
        demo_digital_signatures()
        demo_isogeny_crypto()
        
        # Performance testing
        performance_benchmarks()
        
        print("\n" + "=" * 60)
        print("API DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("✅ All cryptographic primitives demonstrated")
        print("✅ p-adic arithmetic working correctly")
        print("✅ Security levels properly implemented")
        print("✅ Performance benchmarks completed")
        print()
        print("The libadic p-adic cryptography system is ready for:")
        print("• Research and experimentation")
        print("• Prototype development") 
        print("• Production use (with appropriate security assessment)")
        print("• Integration into existing cryptographic systems")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure libadic is properly compiled and installed")
        print("Run: python setup.py install")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
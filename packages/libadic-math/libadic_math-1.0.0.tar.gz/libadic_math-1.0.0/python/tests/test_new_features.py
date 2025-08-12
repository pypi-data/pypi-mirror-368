#!/usr/bin/env python3
"""
Test script for new elliptic curve and cryptography Python bindings
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import libadic
    print("✓ libadic module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import libadic: {e}")
    print("\nPlease build the Python bindings first:")
    print("  cd build")
    print("  cmake -DBUILD_PYTHON_BINDINGS=ON ..")
    print("  make")
    sys.exit(1)

def test_elliptic_curves():
    """Test elliptic curve bindings"""
    print("\n" + "="*50)
    print("Testing Elliptic Curve Bindings")
    print("="*50)
    
    try:
        # Test curve creation
        E = libadic.EllipticCurve(0, -1)
        print(f"✓ Created curve: {E.to_string()}")
        
        # Test invariants
        disc = E.get_discriminant()
        print(f"✓ Discriminant: {disc}")
        
        conductor = E.get_conductor()
        print(f"✓ Conductor: {conductor}")
        
        # Test point creation
        P = libadic.EllipticCurve.Point(libadic.BigInt(2), libadic.BigInt(3))
        print(f"✓ Created point: ({P.X}, {P.Y})")
        
        # Test point arithmetic
        Q = libadic.EllipticCurve.Point(libadic.BigInt(0), libadic.BigInt(1))
        R = E.add_points(P, Q)
        print(f"✓ Point addition: P + Q = ({R.X}, {R.Y})")
        
        # Test L-series
        ap = E.get_ap(5)
        print(f"✓ L-series coefficient a_5 = {ap}")
        
        # Test torsion
        torsion_order = E.get_torsion_order()
        print(f"✓ Torsion order: {torsion_order}")
        
        print("\n✓ All elliptic curve tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Elliptic curve test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_elliptic_l_functions():
    """Test elliptic L-function bindings"""
    print("\n" + "="*50)
    print("Testing Elliptic L-Function Bindings")
    print("="*50)
    
    try:
        E = libadic.EllipticCurve(0, -1)
        p = 5
        precision = 20
        
        # Test L_p(E, 1)
        L_p_1 = libadic.EllipticLFunctions.L_p_at_one(E, p, precision)
        print(f"✓ L_p(E, 1) computed: {L_p_1}")
        
        # Test p-adic period
        omega_p = libadic.EllipticLFunctions.p_adic_period(E, p, precision)
        print(f"✓ p-adic period Ω_p: {omega_p}")
        
        # Test analytic rank
        rank = libadic.EllipticLFunctions.compute_analytic_rank(E, p, precision)
        print(f"✓ Analytic rank: {rank}")
        
        print("\n✓ All L-function tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ L-function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bsd_conjecture():
    """Test BSD conjecture bindings"""
    print("\n" + "="*50)
    print("Testing BSD Conjecture Bindings")
    print("="*50)
    
    try:
        E = libadic.EllipticCurve(0, -1)
        primes = [3, 5, 7]
        precision = 20
        
        # Test BSD verification
        bsd_data = libadic.BSDConjecture.verify_bsd(E, primes, precision)
        print(f"✓ BSD verification complete")
        print(f"  Algebraic rank: {bsd_data.algebraic_rank}")
        print(f"  Analytic rank: {bsd_data.analytic_rank}")
        print(f"  Ranks match: {bsd_data.ranks_match}")
        print(f"  BSD quotient: {bsd_data.bsd_quotient}")
        
        # Test Sha prediction
        sha = libadic.BSDConjecture.predict_sha_order(E)
        print(f"✓ Predicted #Sha: {sha}")
        
        print("\n✓ All BSD tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ BSD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crypto_lattice():
    """Test p-adic lattice cryptography bindings"""
    print("\n" + "="*50)
    print("Testing p-adic Lattice Cryptography Bindings")
    print("="*50)
    
    try:
        # Check if crypto submodule exists
        if not hasattr(libadic, 'crypto'):
            print("✗ crypto submodule not found")
            return False
            
        p = 7
        dimension = 4
        precision = 20
        
        # Create lattice
        lattice = libadic.crypto.PadicLattice(p, dimension, precision)
        print(f"✓ Created p-adic lattice")
        
        # Generate keys
        lattice.generate_keys()
        print(f"✓ Generated keys")
        
        # Encrypt/decrypt
        message = [1, 2, 3, 4]
        ciphertext = lattice.encrypt(message)
        print(f"✓ Encrypted message")
        
        decrypted = lattice.decrypt(ciphertext)
        print(f"✓ Decrypted: {decrypted}")
        
        if decrypted == message:
            print("✓ Encryption/decryption successful!")
        else:
            print("✗ Decryption failed!")
            return False
        
        # Test security analysis
        security_bits = libadic.crypto.SecurityAnalysis.estimate_security_bits(p, dimension, precision)
        print(f"✓ Security estimate: {security_bits} bits")
        
        print("\n✓ All lattice crypto tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Lattice crypto test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crypto_prng():
    """Test p-adic PRNG bindings"""
    print("\n" + "="*50)
    print("Testing p-adic PRNG Bindings")
    print("="*50)
    
    try:
        if not hasattr(libadic, 'crypto'):
            print("✗ crypto submodule not found")
            return False
            
        p = 17
        seed = libadic.BigInt(42)
        precision = 30
        
        # Create PRNG
        prng = libadic.crypto.PadicPRNG(p, seed, precision)
        print(f"✓ Created PRNG with seed {seed}")
        
        # Generate random numbers
        random_vals = []
        for i in range(5):
            val = prng.next()
            random_vals.append(val)
        print(f"✓ Generated {len(random_vals)} random p-adic numbers")
        
        # Generate bits
        bits = prng.generate_bits(32)
        print(f"✓ Generated {len(bits)} random bits")
        
        # Generate uniform integer
        uniform = prng.generate_uniform(100)
        print(f"✓ Generated uniform integer: {uniform}")
        
        # Test randomness
        test_result = libadic.crypto.PadicPRNG.test_randomness(prng, 1000)
        print(f"✓ Randomness tests:")
        print(f"  Frequency: {'PASS' if test_result.passed_frequency_test else 'FAIL'}")
        print(f"  Serial: {'PASS' if test_result.passed_serial_test else 'FAIL'}")
        
        print("\n✓ All PRNG tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ PRNG test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crypto_signatures():
    """Test p-adic signature bindings"""
    print("\n" + "="*50)
    print("Testing p-adic Digital Signatures Bindings")
    print("="*50)
    
    try:
        if not hasattr(libadic, 'crypto'):
            print("✗ crypto submodule not found")
            return False
            
        p = 101
        precision = 30
        
        # Create signature system
        sig = libadic.crypto.PadicSignature(p, precision)
        print(f"✓ Created signature system")
        
        # Generate keys
        sig.generate_keys()
        print(f"✓ Generated signing keys")
        
        # Sign message
        message = list(b"Test message")
        signature = sig.sign(message)
        print(f"✓ Signed message")
        
        # Verify
        is_valid = sig.verify(message, signature, sig.public_key)
        print(f"✓ Signature verification: {'VALID' if is_valid else 'INVALID'}")
        
        if not is_valid:
            print("✗ Signature verification failed!")
            return False
        
        # Test tampering detection
        tampered = list(b"Tampered message")
        is_valid_tampered = sig.verify(tampered, signature, sig.public_key)
        print(f"✓ Tampered message verification: {'INVALID (good!)' if not is_valid_tampered else 'VALID (bad!)'}")
        
        if is_valid_tampered:
            print("✗ Failed to detect tampering!")
            return False
        
        print("\n✓ All signature tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Signature test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("╔" + "="*48 + "╗")
    print("║" + " " * 10 + "Testing New Python Bindings" + " " * 10 + "║")
    print("╚" + "="*48 + "╝")
    
    all_passed = True
    
    # Test elliptic curves
    if not test_elliptic_curves():
        all_passed = False
    
    if not test_elliptic_l_functions():
        all_passed = False
    
    if not test_bsd_conjecture():
        all_passed = False
    
    # Test cryptography
    if not test_crypto_lattice():
        all_passed = False
    
    if not test_crypto_prng():
        all_passed = False
    
    if not test_crypto_signatures():
        all_passed = False
    
    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. Please check the output above.")
    print("="*50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
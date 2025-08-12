#!/usr/bin/env python3
"""
p-adic Cryptography Demonstration

This script showcases the cryptographic capabilities of libadic,
including lattice-based encryption, digital signatures, PRNGs,
and homomorphic encryption using p-adic arithmetic.
"""

import libadic
import time
import hashlib

def demo_lattice_crypto():
    """Demonstrate p-adic lattice-based cryptography"""
    print("\n" + "="*60)
    print("p-adic Lattice-Based Cryptography Demo")
    print("="*60)
    
    # Setup parameters
    p = 7
    dimension = 4
    precision = 30
    
    print(f"\nParameters:")
    print(f"  Prime p = {p}")
    print(f"  Lattice dimension = {dimension}")
    print(f"  p-adic precision = {precision}")
    
    # Create cryptosystem
    lattice = libadic.crypto.PadicLattice(p, dimension, precision)
    
    # Generate keys
    print("\nGenerating public/private key pair...")
    start = time.time()
    lattice.generate_keys()
    keygen_time = time.time() - start
    print(f"  Key generation time: {keygen_time:.3f} seconds")
    
    # Encrypt a message
    message = [1, 2, 3, 4]
    print(f"\nOriginal message: {message}")
    
    start = time.time()
    ciphertext = lattice.encrypt(message)
    encrypt_time = time.time() - start
    print(f"Encryption time: {encrypt_time:.3f} seconds")
    print(f"Ciphertext (first 3 components): {[str(c)[:20] + '...' for c in ciphertext[:3]]}")
    
    # Decrypt
    start = time.time()
    decrypted = lattice.decrypt(ciphertext)
    decrypt_time = time.time() - start
    print(f"\nDecryption time: {decrypt_time:.3f} seconds")
    print(f"Decrypted message: {decrypted}")
    
    # Verify correctness
    if decrypted == message:
        print("✓ Encryption/Decryption successful!")
    else:
        print("✗ Encryption/Decryption failed!")
    
    # Security analysis
    print("\nSecurity Analysis:")
    security_bits = libadic.crypto.SecurityAnalysis.estimate_security_bits(p, dimension, precision)
    print(f"  Estimated security: {security_bits} bits")
    
    # Test different dimensions
    print("\nSecurity vs Dimension:")
    for dim in [2, 4, 8, 16]:
        bits = libadic.crypto.SecurityAnalysis.estimate_security_bits(p, dim, precision)
        print(f"  dim={dim:2d}: {bits} bits")

def demo_digital_signatures():
    """Demonstrate p-adic digital signatures"""
    print("\n" + "="*60)
    print("p-adic Digital Signatures Demo")
    print("="*60)
    
    # Setup
    p = 1009  # Large prime for security
    precision = 50
    
    print(f"\nParameters:")
    print(f"  Prime p = {p}")
    print(f"  Precision = {precision}")
    
    # Create signature system
    sig_system = libadic.crypto.PadicSignature(p, precision)
    
    # Generate keys
    print("\nGenerating signature keys...")
    sig_system.generate_keys()
    print("  Keys generated")
    
    # Sign messages
    messages = [
        b"Transfer $1000 to Alice",
        b"Transfer $1000 to Bob",
        b"Hello, p-adic world!"
    ]
    
    print("\nSigning messages:")
    signatures = []
    for msg in messages:
        signature = sig_system.sign(list(msg))
        signatures.append(signature)
        print(f"  Message: '{msg.decode()[:30]}...'")
        print(f"    Signature: r={str(signature.r)[:20]}..., s={str(signature.s)[:20]}...")
    
    # Verify signatures
    print("\nVerifying signatures:")
    for i, (msg, sig) in enumerate(zip(messages, signatures)):
        is_valid = sig_system.verify(list(msg), sig, sig_system.public_key)
        print(f"  Message {i+1}: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Test tampering detection
    print("\nTampering detection:")
    tampered_msg = b"Transfer $9000 to Bob"  # Modified amount
    is_valid = sig_system.verify(list(tampered_msg), signatures[1], sig_system.public_key)
    print(f"  Tampered message validates: {'✗ Yes (BAD!)' if is_valid else '✓ No (Good!)'}")
    
    # Test signature malleability
    print("\nSignature integrity:")
    corrupted_sig = libadic.crypto.PadicSignature.Signature()
    corrupted_sig.r = signatures[0].r
    corrupted_sig.s = sig_system.public_key  # Wrong s value
    is_valid = sig_system.verify(list(messages[0]), corrupted_sig, sig_system.public_key)
    print(f"  Corrupted signature validates: {'✗ Yes (BAD!)' if is_valid else '✓ No (Good!)'}")

def demo_prng():
    """Demonstrate p-adic pseudorandom number generation"""
    print("\n" + "="*60)
    print("p-adic PRNG Demo")
    print("="*60)
    
    # Setup
    p = 17
    seed = libadic.BigInt(42)
    precision = 40
    
    print(f"\nParameters:")
    print(f"  Prime p = {p}")
    print(f"  Seed = {seed}")
    print(f"  Precision = {precision}")
    
    # Create PRNG
    prng = libadic.crypto.PadicPRNG(p, seed, precision)
    
    # Generate random p-adic numbers
    print("\nGenerating random p-adic numbers:")
    for i in range(5):
        val = prng.next()
        print(f"  Random {i+1}: {str(val)[:40]}...")
    
    # Generate random bits
    print("\nGenerating random bits:")
    bits = prng.generate_bits(64)
    bit_string = ''.join(map(str, map(int, bits)))
    print(f"  64 bits: {bit_string}")
    print(f"  As hex: {hex(int(bit_string, 2))}")
    
    # Generate uniform random integers
    print("\nGenerating uniform random integers [0, 100):")
    uniform_vals = [prng.generate_uniform(100) for _ in range(10)]
    print(f"  Values: {uniform_vals}")
    
    # Statistical tests
    print("\nRunning statistical tests (10000 samples)...")
    test_result = libadic.crypto.PadicPRNG.test_randomness(prng, 10000)
    
    print("Test Results:")
    print(f"  ✓ Frequency test: {'PASS' if test_result.passed_frequency_test else 'FAIL'}")
    print(f"  ✓ Serial test: {'PASS' if test_result.passed_serial_test else 'FAIL'}")
    print(f"  ✓ Poker test: {'PASS' if test_result.passed_poker_test else 'FAIL'}")
    print(f"  ✓ Runs test: {'PASS' if test_result.passed_runs_test else 'FAIL'}")
    print(f"  Chi-square statistic: {test_result.chi_square_statistic:.4f}")
    
    # Period detection
    print("\nPeriod detection (max 100000 iterations):")
    period = libadic.crypto.PadicPRNG.detect_period(prng, 100000)
    if period:
        print(f"  Period detected: {period}")
    else:
        print(f"  No period detected (good for cryptographic use)")
    
    # Benchmark generation speed
    print("\nBenchmarking generation speed:")
    start = time.time()
    for _ in range(1000):
        prng.next()
    elapsed = time.time() - start
    print(f"  1000 p-adic numbers: {elapsed:.3f} seconds")
    print(f"  Rate: {1000/elapsed:.0f} numbers/second")

def demo_homomorphic_encryption():
    """Demonstrate homomorphic encryption with p-adic numbers"""
    print("\n" + "="*60)
    print("p-adic Homomorphic Encryption Demo")
    print("="*60)
    
    # Setup
    p = 7
    precision = 40
    noise_precision = 10
    
    print(f"\nParameters:")
    print(f"  Prime p = {p}")
    print(f"  Precision = {precision}")
    print(f"  Noise precision = {noise_precision}")
    
    # Create system
    he_system = libadic.crypto.PadicHomomorphic(p, precision, noise_precision)
    
    # Generate keys
    print("\nGenerating homomorphic encryption keys...")
    he_system.generate_keys()
    print("  Keys generated")
    
    # Demonstrate homomorphic addition
    print("\nHomomorphic Addition:")
    a, b = 5, 3
    print(f"  Plaintexts: a = {a}, b = {b}")
    
    # Encrypt
    cipher_a = he_system.encrypt(a)
    cipher_b = he_system.encrypt(b)
    print(f"  Encrypted a and b")
    
    # Add encrypted values
    cipher_sum = libadic.crypto.PadicHomomorphic.add(cipher_a, cipher_b)
    
    # Decrypt result
    result_sum = he_system.decrypt(cipher_sum)
    print(f"  Decrypted sum: {result_sum}")
    print(f"  Expected: {a + b}")
    print(f"  ✓ Correct!" if result_sum == a + b else "✗ Error!")
    
    # Demonstrate homomorphic multiplication
    print("\nHomomorphic Multiplication:")
    cipher_prod = libadic.crypto.PadicHomomorphic.multiply(cipher_a, cipher_b)
    result_prod = he_system.decrypt(cipher_prod)
    print(f"  Decrypted product: {result_prod}")
    print(f"  Expected: {a * b}")
    print(f"  ✓ Correct!" if result_prod == a * b else "✗ Error!")
    
    # Complex computation: (a + b) * (a - b) = a² - b²
    print("\nComplex Homomorphic Computation: (a + b) * (a - b)")
    
    # Compute a - b homomorphically
    cipher_neg_b = he_system.encrypt(-b % p)  # Additive inverse
    cipher_diff = libadic.crypto.PadicHomomorphic.add(cipher_a, cipher_neg_b)
    
    # Multiply (a + b) * (a - b)
    cipher_result = libadic.crypto.PadicHomomorphic.multiply(cipher_sum, cipher_diff)
    
    # Decrypt and verify
    result = he_system.decrypt(cipher_result)
    expected = (a * a - b * b) % p
    print(f"  Decrypted result: {result}")
    print(f"  Expected (a² - b²): {expected}")
    print(f"  ✓ Correct!" if result == expected else "✗ Error!")
    
    # Noise analysis
    print("\nNoise Growth Analysis:")
    noise_original = libadic.crypto.PadicHomomorphic.estimate_noise(cipher_a)
    noise_sum = libadic.crypto.PadicHomomorphic.estimate_noise(cipher_sum)
    noise_prod = libadic.crypto.PadicHomomorphic.estimate_noise(cipher_prod)
    noise_complex = libadic.crypto.PadicHomomorphic.estimate_noise(cipher_result)
    
    print(f"  Original ciphertext: {noise_original}")
    print(f"  After addition: {noise_sum}")
    print(f"  After multiplication: {noise_prod}")
    print(f"  After complex operation: {noise_complex}")
    
    # Check if bootstrapping needed
    if noise_complex > precision // 2:
        print("\n⚠ High noise detected! Bootstrapping recommended.")
        cipher_refreshed = he_system.bootstrap(cipher_result)
        noise_refreshed = libadic.crypto.PadicHomomorphic.estimate_noise(cipher_refreshed)
        print(f"  Noise after bootstrapping: {noise_refreshed}")

def demo_hash_function():
    """Demonstrate p-adic hash function"""
    print("\n" + "="*60)
    print("p-adic Hash Function Demo")
    print("="*60)
    
    # Setup
    p = 31
    output_size = 32  # 32 p-adic digits
    precision = 50
    
    print(f"\nParameters:")
    print(f"  Prime p = {p}")
    print(f"  Output size = {output_size} p-adic digits")
    print(f"  Precision = {precision}")
    
    # Create hash function
    padic_hash = libadic.crypto.PadicHash(p, output_size, precision)
    
    # Hash different messages
    messages = [
        b"Hello, World!",
        b"Hello, World",  # One character different
        b"The quick brown fox jumps over the lazy dog",
        b"",  # Empty message
        b"a" * 1000  # Long message
    ]
    
    print("\nHashing messages:")
    hashes = []
    for msg in messages:
        hash_val = padic_hash.hash(list(msg))
        hex_hash = padic_hash.to_hex(hash_val)
        hashes.append(hex_hash)
        
        if len(msg) <= 30:
            print(f"  Message: '{msg.decode() if msg else '(empty)'}'")
        else:
            print(f"  Message: '{msg.decode()[:27]}...' ({len(msg)} bytes)")
        print(f"    Hash: {hex_hash[:32]}...")
    
    # Test avalanche effect
    print("\nAvalanche Effect Test:")
    msg1 = b"Test message 1"
    msg2 = b"Test message 2"  # One character changed
    
    hash1 = padic_hash.hash(list(msg1))
    hash2 = padic_hash.hash(list(msg2))
    
    # Count different digits
    digits1 = hash1.digits()
    digits2 = hash2.digits()
    differences = sum(1 for d1, d2 in zip(digits1, digits2) if d1 != d2)
    
    print(f"  Message 1: '{msg1.decode()}'")
    print(f"  Message 2: '{msg2.decode()}'")
    print(f"  Different digits: {differences}/{len(digits1)}")
    print(f"  Avalanche ratio: {differences/len(digits1)*100:.1f}%")
    
    # Collision resistance test (simplified)
    print("\nCollision Resistance (simplified test):")
    hash_set = set()
    collision_found = False
    
    for i in range(1000):
        msg = f"Message {i}".encode()
        hash_val = padic_hash.to_hex(padic_hash.hash(list(msg)))
        
        if hash_val in hash_set:
            print(f"  ✗ Collision found at message {i}!")
            collision_found = True
            break
        hash_set.add(hash_val)
    
    if not collision_found:
        print(f"  ✓ No collisions in 1000 messages")
    
    # Verify security properties
    print("\nSecurity Properties Verification:")
    is_secure = libadic.crypto.PadicHash.verify_security_properties(p, precision)
    print(f"  Security properties verified: {'✓ Yes' if is_secure else '✗ No'}")

def main():
    """Run all cryptography demonstrations"""
    print("╔" + "="*58 + "╗")
    print("║" + " " * 15 + "p-adic Cryptography Suite" + " " * 18 + "║")
    print("║" + " " * 17 + "libadic Demonstration" + " " * 20 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Run each demo
        demo_lattice_crypto()
        demo_digital_signatures()
        demo_prng()
        demo_homomorphic_encryption()
        demo_hash_function()
        
        print("\n" + "="*60)
        print("All demonstrations completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
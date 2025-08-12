#!/usr/bin/env python3
"""
Demonstration of p-adic Lattice-based Cryptography

This example shows how to use the quantum-resistant p-adic lattice
cryptographic system implemented in libadic.
"""

import sys
import os

# Add parent directory to path to import libadic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

try:
    from libadic import BigInt
    from libadic.crypto import PadicLattice
except ImportError:
    print("Error: libadic module not found. Please build the library first:")
    print("  cmake -S . -B build")
    print("  cmake --build build --target libadic_python")
    sys.exit(1)

def demo_basic_encryption():
    """Demonstrate basic encryption and decryption"""
    print("\n" + "=" * 60)
    print("BASIC ENCRYPTION DEMO")
    print("=" * 60)
    
    # Create a p-adic lattice cryptosystem
    prime = 31
    dimension = 4
    precision = 10
    
    print(f"\nInitializing cryptosystem:")
    print(f"  Prime p = {prime}")
    print(f"  Lattice dimension = {dimension}")
    print(f"  p-adic precision = {precision}")
    
    lattice = PadicLattice(prime, dimension, precision)
    
    # Generate public/private key pair
    print("\nGenerating keys...")
    lattice.generate_keys()
    print("✅ Keys generated successfully")
    
    # Message to encrypt (must be a list of integers with length = dimension)
    message = [42, 17, 88, 5]
    print(f"\nOriginal message: {message}")
    
    # Encrypt the message
    print("\nEncrypting...")
    ciphertext = lattice.encrypt(message)
    print(f"✅ Encrypted to {len(ciphertext)} p-adic numbers")
    
    # Show ciphertext (as p-adic valuations for brevity)
    print(f"Ciphertext sample: {ciphertext[0]} (first element)")
    
    # Decrypt the message
    print("\nDecrypting...")
    decrypted = lattice.decrypt(ciphertext)
    print(f"✅ Decrypted message: {list(decrypted)}")
    
    # Verify correctness
    if list(decrypted) == message:
        print("\n🎉 SUCCESS: Encryption and decryption worked perfectly!")
    else:
        print("\n⚠️ Warning: Decrypted message doesn't match original")
    
    return lattice

def demo_security_properties(lattice):
    """Demonstrate security properties"""
    print("\n" + "=" * 60)
    print("SECURITY PROPERTIES")
    print("=" * 60)
    
    # Access cryptographic parameters
    print("\nCryptographic parameters:")
    print(f"  Prime: {lattice.prime}")
    print(f"  Dimension: {lattice.dimension}")
    print(f"  Precision: {lattice.precision}")
    
    # Get the bases (public and private keys)
    public_basis = lattice.public_basis
    private_basis = lattice.private_basis
    
    print(f"\nKey sizes:")
    print(f"  Public key: {len(public_basis)}x{len(public_basis[0])} matrix")
    print(f"  Private key: {len(private_basis)}x{len(private_basis[0])} matrix")
    
    print("\nSecurity features:")
    print("  ✅ Quantum-resistant (based on p-adic SVP)")
    print("  ✅ Uses ultrametric distance (unique to p-adics)")
    print("  ✅ Trapdoor-based (private basis is 'good', public is 'bad')")
    print("  ✅ Message space: integers modulo scale factor")

def demo_different_messages():
    """Demonstrate encryption of various message types"""
    print("\n" + "=" * 60)
    print("VARIOUS MESSAGE TYPES")
    print("=" * 60)
    
    # Use parameters that work reliably
    lattice = PadicLattice(11, 4, 10)  # Changed from dim=3 to dim=4
    lattice.generate_keys()
    
    test_messages = [
        ([0, 0, 0, 0], "Zero message"),
        ([1, 2, 3, 4], "Simple sequence"),
        ([-5, 10, -3, 2], "Negative values"),
        ([100, -50, 75, 25], "Large values"),
    ]
    
    for msg, description in test_messages:
        ct = lattice.encrypt(msg)
        dec = lattice.decrypt(ct)
        status = "✅" if list(dec) == msg else "❌"
        print(f"{status} {description}: {msg} -> {list(dec)}")

def demo_bigint_support():
    """Demonstrate support for large primes using BigInt"""
    print("\n" + "=" * 60)
    print("LARGE PRIME SUPPORT")
    print("=" * 60)
    
    # Use a larger prime via BigInt
    large_prime = BigInt("2147483647")  # 2^31 - 1 (Mersenne prime)
    
    print(f"\nUsing large prime: {large_prime}")
    print("(This is a 31-bit Mersenne prime)")
    
    # Note: For demonstration, we use small dimensions
    # Real cryptographic use would have larger dimensions
    lattice = PadicLattice(large_prime, 2, 8)
    lattice.generate_keys()
    
    message = [12345, 67890]
    ct = lattice.encrypt(message)
    dec = lattice.decrypt(ct)
    
    if list(dec) == message:
        print(f"✅ Large prime encryption works: {message} -> {list(dec)}")
    else:
        print(f"❌ Issue with large prime: {message} -> {list(dec)}")

def main():
    print("=" * 60)
    print("p-ADIC LATTICE CRYPTOGRAPHY DEMONSTRATION")
    print("=" * 60)
    print("\nThis demo showcases quantum-resistant encryption using")
    print("p-adic numbers and lattice-based cryptography.")
    
    # Run demonstrations
    lattice = demo_basic_encryption()
    demo_security_properties(lattice)
    demo_different_messages()
    demo_bigint_support()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("""
The p-adic lattice cryptosystem provides:
- Quantum resistance through hard lattice problems
- Unique security from p-adic (ultrametric) geometry  
- Efficient operations using p-adic arithmetic
- Support for various message types and large primes

For production use, consider:
- Larger dimensions (512-1024) for higher security
- Appropriate prime selection for your security level
- Careful parameter tuning for your use case
""")

if __name__ == "__main__":
    main()
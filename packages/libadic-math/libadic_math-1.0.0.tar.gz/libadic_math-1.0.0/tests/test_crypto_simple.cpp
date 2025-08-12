#include "libadic/padic_crypto.h"
#include <iostream>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "Testing p-adic crypto with p=2, precision=10\n";
    
    try {
        // Test with small prime
        PadicPRNG prng(2, BigInt(42), 10);
        
        std::cout << "Generating first number...\n";
        Zp val = prng.next();
        std::cout << "Generated: " << val.to_bigint().to_string() << "\n";
        
        std::cout << "Test passed!\n";
    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << "\n";
    }
    
    return 0;
}
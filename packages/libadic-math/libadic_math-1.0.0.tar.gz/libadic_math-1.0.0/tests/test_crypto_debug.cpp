#include "libadic/padic_crypto.h"
#include <iostream>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "Starting p-adic crypto debug test\n" << std::flush;
    
    try {
        std::cout << "Testing PRNG with p=2...\n" << std::flush;
        PadicPRNG prng2(2, BigInt(42), 10);
        Zp val2 = prng2.next();
        std::cout << "p=2 worked: " << val2.to_bigint().to_string() << "\n" << std::flush;
        
        std::cout << "Testing PRNG with p=5...\n" << std::flush;
        PadicPRNG prng5(5, BigInt(42), 10);
        Zp val5 = prng5.next();
        std::cout << "p=5 worked: " << val5.to_bigint().to_string() << "\n" << std::flush;
        
        std::cout << "Testing PRNG with p=13...\n" << std::flush;
        PadicPRNG prng13(13, BigInt(42), 10);
        Zp val13 = prng13.next();
        std::cout << "p=13 worked: " << val13.to_bigint().to_string() << "\n" << std::flush;
        
        std::cout << "Testing PRNG with p=31...\n" << std::flush;
        PadicPRNG prng31(31, BigInt(42), 10);
        std::cout << "Created PRNG for p=31\n" << std::flush;
        Zp val31 = prng31.next();
        std::cout << "p=31 worked: " << val31.to_bigint().to_string() << "\n" << std::flush;
        
        std::cout << "All tests passed!\n";
    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << "\n";
    }
    
    return 0;
}
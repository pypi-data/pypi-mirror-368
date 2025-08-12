#include "libadic/cryptanalysis.h"
#include <iostream>

using namespace libadic;
using namespace libadic::cryptanalysis;

int main() {
    std::cout << "Simple Cryptanalysis Test\n";
    std::cout << "=========================\n\n";
    
    // Test 1: p-adic LLL on small matrix
    std::cout << "1. Testing p-adic LLL:\n";
    long p = 5;
    long precision = 10;
    PadicLLL lll(p, precision, 0.75);
    
    // Create a simple 2x2 basis
    std::vector<std::vector<Zp>> basis = {
        {Zp(p, precision, 10), Zp(p, precision, 5)},
        {Zp(p, precision, 3), Zp(p, precision, 7)}
    };
    
    std::cout << "   Original basis: [[10,5], [3,7]]\n";
    auto reduced = lll.reduce(basis);
    std::cout << "   Reduced basis: [[" 
              << reduced[0][0].to_bigint().to_string() << "," 
              << reduced[0][1].to_bigint().to_string() << "], ["
              << reduced[1][0].to_bigint().to_string() << ","
              << reduced[1][1].to_bigint().to_string() << "]]\n";
    
    // Test 2: Simple discrete log
    std::cout << "\n2. Testing p-adic Discrete Log:\n";
    PadicDiscreteLog dlog(5, 10);
    Zp base(5, 10, 2);
    Zp target(5, 10, 32);  // 2^5 = 32
    
    std::cout << "   Solving 2^x ≡ 32 (mod 5^10)\n";
    auto result = dlog.solve(base, target, BigInt(100));
    if (result.has_value()) {
        std::cout << "   Found x = " << result.value().to_string() << "\n";
    } else {
        std::cout << "   No solution found\n";
    }
    
    std::cout << "\nTests completed successfully!\n";
    return 0;
}
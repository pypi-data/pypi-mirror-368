#include "libadic/padic_crypto.h"
#include <iostream>
#include <cstdlib>

using namespace libadic;
using namespace libadic::crypto;

int main() {
    std::cout << "=== Tracing Babai CVP Solver ===\n\n";
    
    std::srand(42);
    
    // Very simple test case - tiny parameters
    const long p = 7;
    const long dim = 2;
    const long prec = 8;
    
    std::cout << "Parameters: p=" << p << ", dim=" << dim << ", prec=" << prec << "\n\n";
    
    PadicLattice lattice(p, dim, prec);
    lattice.generate_keys();
    
    // Test with zero message first
    std::vector<long> msg = {0, 0};
    std::cout << ">>> Testing message: [" << msg[0] << ", " << msg[1] << "]\n";
    
    // Encrypt
    auto ct = lattice.encrypt(msg);
    
    // Decrypt
    auto dec = lattice.decrypt(ct);
    
    std::cout << ">>> Result: [" << dec[0] << ", " << dec[1] << "]\n";
    std::cout << ">>> Expected: [" << msg[0] << ", " << msg[1] << "]\n";
    
    if (dec == msg) {
        std::cout << "✅ SUCCESS\n";
    } else {
        std::cout << "❌ FAIL\n";
    }
    
    return 0;
}
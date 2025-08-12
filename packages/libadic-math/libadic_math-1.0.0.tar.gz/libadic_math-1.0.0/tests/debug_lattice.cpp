#include "libadic/padic_crypto.h"
#include "libadic/padic_cvp_solver.h"
#include "libadic/padic_basis_gen.h"
#include <iostream>
#include <iomanip>

using namespace libadic;
using namespace libadic::crypto;

void print_basis(const std::string& name, const std::vector<std::vector<Zp>>& basis) {
    std::cout << name << " (first row valuations): ";
    if (!basis.empty() && !basis[0].empty()) {
        for (const auto& elem : basis[0]) {
            std::cout << elem.valuation() << " ";
        }
    }
    std::cout << "\n";
}

void debug_encryption_process() {
    std::cout << "\n=== DEBUGGING LATTICE ENCRYPTION ===\n\n";
    
    // Use small parameters for debugging
    long p = 7;
    long dim = 2;
    long prec = 10;
    
    std::cout << "Parameters: p=" << p << ", dim=" << dim << ", precision=" << prec << "\n\n";
    
    // Create lattice
    PadicLattice lattice(p, dim, prec);
    
    std::cout << "Step 1: Generating keys...\n";
    lattice.generate_keys();
    std::cout << "  Keys generated\n\n";
    
    // Test message
    std::vector<long> message = {5, 12};
    std::cout << "Step 2: Original message: [" << message[0] << ", " << message[1] << "]\n\n";
    
    // Encrypt
    std::cout << "Step 3: Encrypting...\n";
    auto ciphertext = lattice.encrypt(message);
    
    std::cout << "  Ciphertext generated:\n";
    for (size_t i = 0; i < ciphertext.size(); ++i) {
        std::cout << "    c[" << i << "]: valuation=" << ciphertext[i].valuation() 
                  << ", unit=" << ciphertext[i].get_unit().get_value() << "\n";
        
        // Check if ciphertext is zero
        if (ciphertext[i].is_zero()) {
            std::cout << "    WARNING: Ciphertext component " << i << " is ZERO!\n";
        }
    }
    std::cout << "\n";
    
    // Decrypt
    std::cout << "Step 4: Decrypting...\n";
    auto decrypted = lattice.decrypt(ciphertext);
    
    std::cout << "  Decrypted message: [" << decrypted[0] << ", " << decrypted[1] << "]\n\n";
    
    // Analysis
    std::cout << "Step 5: Analysis:\n";
    bool success = (message[0] == decrypted[0] && message[1] == decrypted[1]);
    
    if (success) {
        std::cout << "  ✓ SUCCESS: Decryption recovered the original message!\n";
    } else {
        std::cout << "  ✗ FAILURE: Decryption did not recover the original message\n";
        std::cout << "  Expected: [" << message[0] << ", " << message[1] << "]\n";
        std::cout << "  Got:      [" << decrypted[0] << ", " << decrypted[1] << "]\n";
    }
}

void test_with_different_parameters() {
    std::cout << "\n=== TESTING WITH DIFFERENT PARAMETERS ===\n\n";
    
    struct TestCase {
        long p;
        long dim;
        long prec;
        std::vector<long> message;
    };
    
    std::vector<TestCase> test_cases = {
        {7, 2, 10, {5, 12}},
        {7, 2, 15, {5, 12}},
        {13, 2, 10, {5, 12}},
        {13, 3, 15, {5, 12, 8}},
        {31, 4, 20, {5, 12, 3, 8}},
    };
    
    for (const auto& tc : test_cases) {
        std::cout << "Test: p=" << tc.p << ", dim=" << tc.dim 
                  << ", prec=" << tc.prec << "\n";
        std::cout << "  Message: [";
        for (size_t i = 0; i < tc.message.size(); ++i) {
            if (i > 0) std::cout << ", ";
            std::cout << tc.message[i];
        }
        std::cout << "]\n";
        
        try {
            PadicLattice lattice(tc.p, tc.dim, tc.prec);
            lattice.generate_keys();
            
            auto ciphertext = lattice.encrypt(tc.message);
            auto decrypted = lattice.decrypt(ciphertext);
            
            bool success = (tc.message == decrypted);
            
            std::cout << "  Result: ";
            if (success) {
                std::cout << "✓ PASS\n";
            } else {
                std::cout << "✗ FAIL - Got [";
                for (size_t i = 0; i < decrypted.size(); ++i) {
                    if (i > 0) std::cout << ", ";
                    std::cout << decrypted[i];
                }
                std::cout << "]\n";
            }
        } catch (const std::exception& e) {
            std::cout << "  ERROR: " << e.what() << "\n";
        }
        
        std::cout << "\n";
    }
}

void test_cvp_directly() {
    std::cout << "\n=== TESTING CVP SOLVER DIRECTLY ===\n\n";
    
    long p = 7;
    long dim = 2;
    long prec = 10;
    
    // Create a simple basis
    linalg::Matrix basis(dim, linalg::Vector(dim));
    basis[0][0] = Zp(p, prec, 1);
    basis[0][1] = Zp(p, prec, 0);
    basis[1][0] = Zp(p, prec, 0);
    basis[1][1] = Zp(p, prec, 1);
    
    std::cout << "Using identity basis\n";
    
    PadicCVPSolver solver(p, prec, basis);
    solver.preprocess();
    
    // Create a target point
    linalg::QVector target(dim);
    target[0] = Qp(p, prec, 5);
    target[1] = Qp(p, prec, 12);
    
    std::cout << "Target: [5, 12]\n";
    
    // Add some noise
    target[0] = target[0] + Qp(p, prec, 0, Zp(p, prec, 1));  // Add small noise
    target[1] = target[1] + Qp(p, prec, 0, Zp(p, prec, 1));
    
    std::cout << "Target with noise: [" << target[0].to_bigint() 
              << ", " << target[1].to_bigint() << "]\n";
    
    // Solve CVP
    auto closest = solver.solve_cvp(target);
    
    std::cout << "Closest lattice point: [" << closest[0].get_value() 
              << ", " << closest[1].get_value() << "]\n";
    
    bool success = (closest[0].get_value() == BigInt(5) && closest[1].get_value() == BigInt(12));
    std::cout << "Result: " << (success ? "✓ PASS" : "✗ FAIL") << "\n";
}

void test_simplified_encryption() {
    std::cout << "\n=== SIMPLIFIED ENCRYPTION TEST ===\n\n";
    
    long p = 31;
    long dim = 2;
    long prec = 20;
    
    // Manual encryption/decryption
    std::cout << "Creating simple lattice with known basis...\n";
    
    // Create public basis (bad)
    std::vector<std::vector<Zp>> public_basis(dim, std::vector<Zp>(dim));
    public_basis[0][0] = Zp(p, prec, 17);
    public_basis[0][1] = Zp(p, prec, 23);
    public_basis[1][0] = Zp(p, prec, 11);
    public_basis[1][1] = Zp(p, prec, 29);
    
    // Create private basis (good - nearly identity)
    std::vector<std::vector<Zp>> private_basis(dim, std::vector<Zp>(dim));
    private_basis[0][0] = Zp(p, prec, 1);
    private_basis[0][1] = Zp(p, prec, 0);
    private_basis[1][0] = Zp(p, prec, 0);
    private_basis[1][1] = Zp(p, prec, 1);
    
    std::vector<long> message = {5, 12};
    std::cout << "Message: [" << message[0] << ", " << message[1] << "]\n\n";
    
    // Simple encryption: multiply message by public basis
    std::cout << "Encrypting with public basis...\n";
    std::vector<Qp> ciphertext(dim);
    for (int i = 0; i < dim; ++i) {
        ciphertext[i] = Qp(p, prec, 0);
        for (int j = 0; j < dim; ++j) {
            ciphertext[i] = ciphertext[i] + 
                Qp(public_basis[i][j]) * Qp(p, prec, message[j]);
        }
    }
    
    std::cout << "Ciphertext: [" << ciphertext[0].to_bigint() 
              << ", " << ciphertext[1].to_bigint() << "]\n\n";
    
    // Simple decryption with private basis (identity)
    std::cout << "Decrypting with private basis...\n";
    std::vector<long> decrypted(dim);
    
    // Since private basis is identity, just extract the values
    // In reality, we'd use CVP solver here
    PadicCVPSolver solver(p, prec, private_basis);
    solver.preprocess();
    
    linalg::QVector ct_vec(ciphertext.begin(), ciphertext.end());
    auto closest = solver.solve_cvp(ct_vec);
    
    for (int i = 0; i < dim; ++i) {
        decrypted[i] = closest[i].get_value().to_long() % 1000;
    }
    
    std::cout << "Decrypted: [" << decrypted[0] << ", " << decrypted[1] << "]\n\n";
    
    bool success = (message == decrypted);
    std::cout << "Result: " << (success ? "✓ SUCCESS" : "✗ FAILURE") << "\n";
}

int main() {
    debug_encryption_process();
    test_with_different_parameters();
    test_cvp_directly();
    test_simplified_encryption();
    
    std::cout << "\n=== DEBUGGING COMPLETE ===\n";
    return 0;
}
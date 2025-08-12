// Main Python binding module for libadic
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <sstream>

namespace py = pybind11;

// Forward declarations for binding functions
void bind_bigint(py::module_ &m);
void bind_modular_arith(py::module_ &m);
void bind_zp(py::module_ &m);
void bind_qp(py::module_ &m);
void bind_padic_functions(py::module_ &m);
void bind_characters(py::module_ &m);
void bind_l_functions(py::module_ &m);
void bind_bernoulli(py::module_ &m);
void bind_cyclotomic(py::module_ &m);
void bind_elliptic(py::module_ &m);
void bind_crypto(py::module_ &m);

PYBIND11_MODULE(libadic, m) {
    m.doc() = R"pbdoc(
        libadic: High-performance p-adic arithmetic library
        ====================================================
        
        A Python interface to the libadic C++ library for p-adic number theory
        and the Reid-Li criterion for the Riemann Hypothesis.
        
        Core Classes:
            BigInt: Arbitrary precision integers
            Zp: p-adic integers
            Qp: p-adic numbers
            
        Mathematical Functions:
            padic_log: p-adic logarithm
            gamma_p: Morita's p-adic Gamma function
            kubota_leopoldt: p-adic L-functions
            
        Example:
            >>> from libadic import Zp, gamma_p
            >>> x = Zp(7, 20, 15)  # 15 in Z_7 with precision O(7^20)
            >>> g = gamma_p(5, 7, 20)  # Γ_7(5)
    )pbdoc";
    
    // Add version information
    m.attr("__version__") = "1.0.0";
    
    // Bind core types
    bind_bigint(m);
    bind_modular_arith(m);
    
    // Bind p-adic fields
    bind_zp(m);
    bind_qp(m);
    
    // Bind mathematical functions
    bind_padic_functions(m);
    bind_characters(m);
    bind_l_functions(m);
    bind_bernoulli(m);
    bind_cyclotomic(m);
    
    // Bind elliptic curves and cryptography
    bind_elliptic(m);
    bind_crypto(m);
}
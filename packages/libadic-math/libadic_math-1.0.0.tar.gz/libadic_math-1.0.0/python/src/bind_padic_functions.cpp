// Python bindings for p-adic mathematical functions
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <libadic/padic_log.h>
#include <libadic/padic_gamma.h>
#include <libadic/qp.h>
#include <libadic/zp.h>

namespace py = pybind11;
using namespace libadic;

void bind_padic_functions(py::module_ &m) {
    // p-adic logarithm function
    m.def("log_p", 
          &PadicLog::log,
          py::arg("x"),
          R"pbdoc(
        Compute p-adic logarithm.
        
        Args:
            x: p-adic number (Qp) that must satisfy convergence condition
            
        Returns:
            log_p(x) as a Qp
            
        Convergence:
            - For p ≠ 2: x ≡ 1 (mod p)
            - For p = 2: x ≡ 1 (mod 4)
            
        Raises:
            std::domain_error: If convergence condition not met
            
        Example:
            >>> x = Qp(7, 20, 1 + 7)  # 1 + 7 ≡ 1 (mod 7)
            >>> log_x = log_p(x)
    )pbdoc");
    
    m.def("log_unit",
          &PadicLog::log_unit,
          py::arg("u"),
          R"pbdoc(
        Compute logarithm of a unit in Z_p.
        
        Args:
            u: Unit value (coprime to p)
            prime: The prime p
            precision: Desired precision
            
        Returns:
            log_p(u) with specified precision
    )pbdoc");
    
    m.def("log_via_exp_inverse",
          &PadicLog::log_via_exp_inverse,
          py::arg("x"), py::arg("iterations") = 10,
          R"pbdoc(
        Compute logarithm using exponential series inversion.
        
        Alternative algorithm for computing p-adic logarithm.
        May have different convergence properties.
    )pbdoc");
    
    // p-adic Gamma function - overload for integer argument
    m.def("gamma_p",
          [](long a, long p, long precision) {
              Zp x(p, precision, a);
              return PadicGamma::gamma(x);
          },
          py::arg("a"), py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Compute Morita's p-adic Gamma function Γ_p(a) for integer a.
        
        Args:
            a: Integer argument
            prime: The prime p
            precision: Desired precision
            
        Returns:
            Γ_p(a) as a Zp
            
        Example:
            >>> g = gamma_p(5, 7, 20)  # Γ_7(5)
    )pbdoc");
    
    // p-adic Gamma function - overload for Zp argument
    m.def("gamma_p",
          &PadicGamma::gamma,
          py::arg("x"),
          R"pbdoc(
        Compute Morita's p-adic Gamma function Γ_p(x).
        
        Args:
            x: p-adic integer (Zp)
            
        Returns:
            Γ_p(x) as a Zp
            
        Mathematical Definition:
            Γ_p(x) = lim_{n→∞} (-1)^n ∏_{0<k<pn, (k,p)=1} k
            
        Properties:
            - Γ_p(x+1) = -x·Γ_p(x) for x ∉ Z_p^×
            - Γ_p(x)·Γ_p(1-x) = ±1 (reflection formula)
            
        Example:
            >>> x = Zp(7, 20, 5)
            >>> g = gamma_p(x)  # Γ_7(5)
            >>> print(g)
    )pbdoc");
    
    m.def("log_gamma_p",
          &PadicGamma::log_gamma,
          py::arg("x"),
          R"pbdoc(
        Compute logarithm of p-adic Gamma function.
        
        Args:
            x: p-adic integer (Zp)
            
        Returns:
            log_p(Γ_p(x)) as a Qp
            
        Note:
            More stable than computing gamma then log for large arguments
    )pbdoc");
    
    m.def("gamma_positive_integer",
          &PadicGamma::gamma_positive_integer,
          py::arg("n"), py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Compute Γ_p(n) for positive integer n using factorial formula.
        
        Args:
            n: Positive integer
            prime: The prime p
            precision: Desired precision
            
        Returns:
            Γ_p(n) computed via modified factorial
            
        Formula:
            Γ_p(n) = (-1)^n · ∏_{1≤k<n, (k,p)=1} k
    )pbdoc");
    
    // Helper functions for validation
    m.def("verify_gamma_reflection",
          [](long x, long p, long precision) {
              Zp x_zp(p, precision, x);
              Zp gamma_x = PadicGamma::gamma(x_zp);
              Zp one_minus_x(p, precision, p - x);
              Zp gamma_1mx = PadicGamma::gamma(one_minus_x);
              Zp product = gamma_x * gamma_1mx;
              
              // Check if product is ±1
              Zp one(p, precision, 1);
              Zp minus_one(p, precision, -1);
              
              bool is_plus_one = (product == one);
              bool is_minus_one = (product == minus_one);
              
              return py::make_tuple(is_plus_one || is_minus_one, product);
          },
          py::arg("x"), py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Verify the Gamma reflection formula: Γ_p(x)·Γ_p(1-x) = ±1
        
        Args:
            x: Argument to test
            prime: The prime p
            precision: Precision for computation
            
        Returns:
            Tuple of (formula_holds: bool, product: Zp)
            
        Example:
            >>> valid, prod = verify_gamma_reflection(3, 7, 20)
            >>> print(f"Reflection formula holds: {valid}")
    )pbdoc");
    
    m.def("compute_log_convergence_radius",
          [](long p) {
              if (p == 2) {
                  return 4L;  // x ≡ 1 (mod 4) for p=2
              } else {
                  return p;   // x ≡ 1 (mod p) for p≠2
              }
          },
          py::arg("prime"),
          R"pbdoc(
        Get the convergence radius for p-adic logarithm.
        
        Args:
            prime: The prime p
            
        Returns:
            Modulus m such that log_p converges for x ≡ 1 (mod m)
    )pbdoc");
    
    // Constants and special values
    m.def("euler_constant_padic",
          [](long /*p*/, long /*precision*/) {
              // Placeholder for p-adic Euler constant
              // This would need proper implementation
              throw std::runtime_error("p-adic Euler constant not yet implemented");
          },
          py::arg("prime"), py::arg("precision"),
          "p-adic Euler-Mascheroni constant (not yet implemented)");
}
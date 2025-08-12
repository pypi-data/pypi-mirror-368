// Python bindings for cyclotomic field operations
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <libadic/cyclotomic.h>
#include <libadic/qp.h>

namespace py = pybind11;
using namespace libadic;

void bind_cyclotomic(py::module_ &m) {
    py::class_<Cyclotomic>(m, "Cyclotomic", R"pbdoc(
        Cyclotomic field element in Q_p(ζ_p) where ζ_p is a primitive p-th root of unity.
        
        This class handles arithmetic in cyclotomic extensions of p-adic fields.
        Elements are represented as polynomials in ζ_p of degree < p-1.
        
        Args:
            prime: The prime p
            precision: p-adic precision
            coeffs: Coefficients as Qp objects (optional)
            
        Example:
            >>> elem = Cyclotomic(7, 20)  # Element in Q_7(ζ_7)
    )pbdoc")
        .def(py::init<long, long>(),
             py::arg("prime"), py::arg("precision"),
             "Construct zero element in Q_p(ζ_p)")
        
        .def(py::init<long, long, const std::vector<Qp>&>(),
             py::arg("prime"), py::arg("precision"), py::arg("coeffs"),
             "Construct element from coefficients")
        
        .def("get_prime", &Cyclotomic::get_prime,
             "Get the prime p")
        
        .def("get_precision", &Cyclotomic::get_precision,
             "Get p-adic precision")
        
        .def("get_coeffs", &Cyclotomic::get_coeffs,
             "Get coefficients as vector of Qp")
        
        .def("get_coeff", &Cyclotomic::get_coeff,
             py::arg("i"),
             "Get i-th coefficient")
        
        .def("__add__", &Cyclotomic::operator+,
             py::arg("other"),
             "Add two cyclotomic elements")
        
        .def("__sub__", py::overload_cast<const Cyclotomic&>(&Cyclotomic::operator-, py::const_),
             py::arg("other"),
             "Subtract two cyclotomic elements")
        
        .def("__mul__", py::overload_cast<const Cyclotomic&>(&Cyclotomic::operator*, py::const_),
             py::arg("other"),
             "Multiply two cyclotomic elements")
        
        .def("__mul__", py::overload_cast<const Qp&>(&Cyclotomic::operator*, py::const_),
             py::arg("scalar"),
             "Multiply by scalar Qp")
        
        .def("__neg__", py::overload_cast<>(&Cyclotomic::operator-, py::const_),
             "Negate element")
        
        .def("__eq__", &Cyclotomic::operator==,
             py::arg("other"),
             "Check equality")
        
        .def("__ne__", &Cyclotomic::operator!=,
             py::arg("other"),
             "Check inequality")
        
        .def("__repr__", [](const Cyclotomic& self) {
            return "<Cyclotomic element in Q_" + std::to_string(self.get_prime()) + "(ζ_" + 
                   std::to_string(self.get_prime()) + ")>";
        })
        
        // Additional methods that exist
        .def("norm", &Cyclotomic::norm,
             R"pbdoc(
        Compute norm N_{Q_p(ζ)/Q_p}(self).
        
        Returns:
            Norm as element of Q_p
            
        Note:
            The norm is the product of all Galois conjugates
    )pbdoc")
        
        .def("trace", &Cyclotomic::trace,
             R"pbdoc(
        Compute trace Tr_{Q_p(ζ)/Q_p}(self).
        
        Returns:
            Trace as element of Q_p
            
        Note:
            The trace is the sum of all Galois conjugates
    )pbdoc")
        
        .def("evaluate", &Cyclotomic::evaluate, py::arg("x"),
             R"pbdoc(
        Evaluate cyclotomic polynomial at x.
        
        Args:
            x: Value to evaluate at (Qp)
            
        Returns:
            self(x) as Qp
            
        Note:
            Treats self as polynomial in ζ and evaluates at x
    )pbdoc")
        
        // Custom power method using multiplication
        .def("__pow__", [](const Cyclotomic& self, long k) {
            if (k == 0) {
                // Return 1
                std::vector<Qp> one_coeffs(self.get_prime() - 1);
                one_coeffs[0] = Qp(self.get_prime(), self.get_precision(), 1);
                for (long i = 1; i < self.get_prime() - 1; ++i) {
                    one_coeffs[i] = Qp(self.get_prime(), self.get_precision(), 0);
                }
                return Cyclotomic(self.get_prime(), self.get_precision(), one_coeffs);
            }
            
            Cyclotomic result = self;
            long exp = std::abs(k) - 1;
            
            // Power by repeated multiplication
            for (long i = 0; i < exp; ++i) {
                result = result * self;
            }
            
            // Handle negative exponents (would need inverse)
            if (k < 0) {
                throw std::runtime_error("Cyclotomic inverse not implemented");
            }
            
            return result;
        }, py::arg("exponent"),
        R"pbdoc(
        Raise cyclotomic element to integer power.
        
        Args:
            exponent: Integer exponent (must be >= 0)
            
        Returns:
            self^exponent
            
        Note:
            Negative exponents not currently supported
    )pbdoc");
    
    // Factory functions for common cyclotomic elements
    m.def("cyclotomic_unity_root",
          [](long prime, long k, long precision) {
              // Create ζ_p^k
              std::vector<Qp> coeffs(prime - 1);
              for (long i = 0; i < prime - 1; ++i) {
                  coeffs[i] = Qp(prime, precision, 0);
              }
              if (k % prime != 0) {
                  long idx = (k % prime) - 1;
                  if (idx >= 0 && idx < prime - 1) {
                      coeffs[idx] = Qp(prime, precision, 1);
                  }
              }
              return Cyclotomic(prime, precision, coeffs);
          },
          py::arg("prime"), py::arg("k"), py::arg("precision"),
          R"pbdoc(
        Create k-th power of primitive p-th root of unity.
        
        Args:
            prime: The prime p
            k: Power
            precision: p-adic precision
            
        Returns:
            ζ_p^k as a Cyclotomic element
    )pbdoc");
    
    m.def("cyclotomic_from_rational",
          [](long value, long prime, long precision) {
              std::vector<Qp> coeffs(prime - 1);
              coeffs[0] = Qp(prime, precision, value);
              for (long i = 1; i < prime - 1; ++i) {
                  coeffs[i] = Qp(prime, precision, 0);
              }
              return Cyclotomic(prime, precision, coeffs);
          },
          py::arg("value"), py::arg("prime"), py::arg("precision"),
          R"pbdoc(
        Create cyclotomic element from rational value.
        
        Args:
            value: Rational value
            prime: The prime p
            precision: p-adic precision
            
        Returns:
            Cyclotomic element representing the rational
    )pbdoc");
}
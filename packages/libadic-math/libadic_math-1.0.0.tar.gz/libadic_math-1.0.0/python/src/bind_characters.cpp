// Python bindings for Dirichlet characters
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <libadic/characters.h>
#include <libadic/zp.h>
#include <complex>

namespace py = pybind11;
using namespace libadic;

void bind_characters(py::module_ &m) {
    py::class_<DirichletCharacter>(m, "DirichletCharacter", R"pbdoc(
        Dirichlet character modulo n.
        
        A Dirichlet character χ modulo n is a completely multiplicative function
        from (Z/nZ)* to C* that extends to Z by setting χ(a) = 0 if gcd(a,n) > 1.
        
        Args:
            modulus: The modulus n
            prime: The prime p for p-adic computations
            values: Values on generators of (Z/nZ)*
            
        Example:
            >>> chi = DirichletCharacter(7, 5, [1, -1])  # Character mod 7, p=5
            >>> print(chi(3))  # Evaluate at 3
    )pbdoc")
        .def(py::init<long, long>(),
             py::arg("modulus"), py::arg("prime"),
             "Construct trivial character")
        .def(py::init<long, long, const std::vector<long>&>(),
             py::arg("modulus"), py::arg("prime"), py::arg("values"),
             "Construct character from values on generators")
        
        .def("evaluate_at", &DirichletCharacter::evaluate_at,
             py::arg("n"),
             "Evaluate character at n (returns integer value)")
        
        .def("evaluate", &DirichletCharacter::evaluate,
             py::arg("n"), py::arg("precision"),
             R"pbdoc(
        Evaluate character at n and lift to p-adic number.
        
        Args:
            n: Integer to evaluate at
            precision: p-adic precision
            
        Returns:
            χ(n) as a Zp using Teichmüller lift
    )pbdoc")
        
        .def("get_conductor", &DirichletCharacter::get_conductor,
             "Get the conductor of the character")
        
        .def("get_modulus", &DirichletCharacter::get_modulus,
             "Get the modulus of the character")
        
        .def("get_prime", &DirichletCharacter::get_prime,
             "Get the prime p for p-adic computations")
        
        .def("is_primitive", &DirichletCharacter::is_primitive,
             "Check if character is primitive")
        
        .def("is_even", &DirichletCharacter::is_even,
             "Check if character is even: χ(-1) = 1")
        
        .def("is_odd", &DirichletCharacter::is_odd,
             "Check if character is odd: χ(-1) = -1")
        
        .def("is_principal", &DirichletCharacter::is_principal,
             "Check if character is principal (trivial)")
        
        .def("get_order", &DirichletCharacter::get_order,
             "Get multiplicative order of the character")
        
        .def("gauss_sum", &DirichletCharacter::gauss_sum,
             py::arg("a") = 1,
             R"pbdoc(
        Compute Gauss sum g_a(χ) = Σ χ(t)e^(2πiat/n)
        
        Args:
            a: Parameter (default 1)
            
        Returns:
            Complex Gauss sum
    )pbdoc")
        
        .def("L_value", &DirichletCharacter::L_value,
             py::arg("s"), py::arg("precision"),
             R"pbdoc(
        Compute L-function value L(s, χ).
        
        Args:
            s: Argument
            precision: Desired precision
            
        Returns:
            L(s, χ) as Qp
            
        Note:
            This is typically computed via LFunctions module
    )pbdoc")
        
        .def("__mul__", [](const DirichletCharacter& self, const DirichletCharacter& other) {
            if (self.modulus != other.modulus) {
                throw std::invalid_argument("Characters must have same modulus for multiplication");
            }
            if (self.prime != other.prime) {
                throw std::invalid_argument("Characters must have same prime for multiplication");
            }
            
            // Product of characters: (χ₁ · χ₂)(n) = χ₁(n) · χ₂(n)
            std::vector<long> product_values;
            for (size_t i = 0; i < self.character_values.size(); ++i) {
                long val = (self.character_values[i] * other.character_values[i]) % self.modulus;
                product_values.push_back(val);
            }
            
            return DirichletCharacter(self.modulus, self.prime, product_values);
        }, py::arg("other"),
        R"pbdoc(
        Multiply two Dirichlet characters.
        
        Args:
            other: Another character with same modulus
            
        Returns:
            Product character χ₁ · χ₂
            
        Raises:
            ValueError: If characters have different moduli
    )pbdoc")
        
        .def("__pow__", [](const DirichletCharacter& self, long k) {
            // k-th power of character: χ^k(n) = χ(n)^k
            std::vector<long> power_values;
            
            for (long val : self.character_values) {
                long result = 1;
                long base = val;
                long exp = k;
                
                // Handle negative exponents by finding inverse
                if (exp < 0) {
                    exp = -exp;
                    // For multiplicative group elements, find inverse
                    // This is simplified - may need more robust implementation
                    base = 1; // Placeholder - needs proper modular inverse
                }
                
                // Power by repeated squaring
                while (exp > 0) {
                    if (exp & 1) {
                        result = (result * base) % self.modulus;
                    }
                    base = (base * base) % self.modulus;
                    exp >>= 1;
                }
                power_values.push_back(result);
            }
            
            return DirichletCharacter(self.modulus, self.prime, power_values);
        }, py::arg("exponent"),
        R"pbdoc(
        Raise character to a power.
        
        Args:
            exponent: Integer exponent
            
        Returns:
            Character χ^k
    )pbdoc")
        
        // Add access to internal values for advanced use
        .def_readonly("character_values", &DirichletCharacter::character_values,
                      "Values on generators (advanced use)")
        .def_readonly("generators", &DirichletCharacter::generators,
                      "Generators of (Z/nZ)* (advanced use)")
        .def_readonly("generator_orders", &DirichletCharacter::generator_orders,
                      "Orders of generators (advanced use)");
    
    // Module functions for character enumeration
    m.def("enumerate_characters",
          &DirichletCharacter::enumerate_characters,
          py::arg("modulus"), py::arg("prime"),
          R"pbdoc(
        Enumerate all Dirichlet characters modulo n.
        
        Args:
            modulus: The modulus n
            prime: The prime p for p-adic computations
            
        Returns:
            List of all characters mod n
    )pbdoc");
    
    m.def("enumerate_primitive_characters",
          &DirichletCharacter::enumerate_primitive_characters,
          py::arg("modulus"), py::arg("prime"),
          R"pbdoc(
        Enumerate all primitive Dirichlet characters modulo n.
        
        Args:
            modulus: The modulus n
            prime: The prime p for p-adic computations
            
        Returns:
            List of primitive characters mod n
            
        Note:
            Primitive characters have conductor equal to modulus
    )pbdoc");
}
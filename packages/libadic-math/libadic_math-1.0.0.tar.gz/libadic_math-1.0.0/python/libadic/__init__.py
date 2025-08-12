"""
libadic: High-performance p-adic arithmetic library

A Python interface to the libadic C++ library for p-adic number theory
and the Reid-Li criterion for the Riemann Hypothesis.

Core Classes:
    - BigInt: Arbitrary precision integers
    - Zp: p-adic integers
    - Qp: p-adic numbers
    - DirichletCharacter: Dirichlet characters
    - CyclotomicField: Cyclotomic field extensions

Mathematical Functions:
    - log_p: p-adic logarithm
    - gamma_p: Morita's p-adic Gamma function
    - kubota_leopoldt: p-adic L-functions
    - bernoulli: Bernoulli numbers

Example:
    >>> from libadic import Zp, gamma_p
    >>> x = Zp(7, 20, 15)  # 15 in Z_7 with precision O(7^20)
    >>> g = gamma_p(5, 7, 20)  # \u0393_7(5)
"""

try:
    from ._version import __version__, show_versions
except ImportError:
    __version__ = "1.0.0-dev"
    def show_versions():
        print(f"libadic: {__version__} (development version)")

__author__ = "libadic Contributors"

_libadic = None
try:
    from . import libadic_python as _libadic
except ImportError as e:
    import warnings
    warnings.warn(
        f"Could not import compiled libadic extension: {e}\n"
        "Please ensure the library is properly built with: python setup.py build_ext --inplace",
        ImportWarning
    )

__all__ = []
if _libadic:
    for name in dir(_libadic):
        if not name.startswith('__'):
            globals()[name] = getattr(_libadic, name)
            __all__.append(name)

"""
libadic Examples Package

This package contains example scripts demonstrating various features of libadic.

Available examples:
- crypto_api_demo: Complete cryptographic API demonstration
- basic_arithmetic: Basic p-adic arithmetic examples
- special_functions: p-adic special functions examples
"""

__all__ = ["crypto_api_demo"]

# Import main example modules for easy access
try:
    from . import crypto_api_demo
except ImportError:
    # Allow package to work even if some examples have issues
    pass
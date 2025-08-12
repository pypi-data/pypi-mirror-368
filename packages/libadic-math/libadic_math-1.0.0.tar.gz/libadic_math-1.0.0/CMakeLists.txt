cmake_minimum_required(VERSION 3.14)
project(libadic VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler flags for optimization and debugging
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0 -DDEBUG")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG -march=native")

# Find required libraries
find_library(GMP_LIBRARY gmp REQUIRED)
find_library(MPFR_LIBRARY mpfr REQUIRED)

if(NOT GMP_LIBRARY)
    message(FATAL_ERROR "GMP library not found. Please install libgmp-dev")
endif()

if(NOT MPFR_LIBRARY)
    message(FATAL_ERROR "MPFR library not found. Please install libmpfr-dev")
endif()

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)

# Source files
set(LIBADIC_SOURCES
    src/base/gmp_wrapper.cpp
    src/base/modular_arith.cpp
    src/base/montgomery.cpp
    src/fields/zp.cpp
    src/fields/qp.cpp
    src/fields/cyclotomic.cpp
    src/functions/padic_log.cpp
    src/functions/padic_gamma.cpp
    src/functions/l_functions.cpp
    src/functions/characters.cpp
    src/functions/bernoulli.cpp
    src/elliptic/elliptic_curve.cpp
    src/elliptic/elliptic_curve_padic.cpp
    src/elliptic/elliptic_l_functions.cpp
    src/elliptic/bsd_conjecture.cpp
    # src/crypto/padic_prng.cpp  # Temporarily disabled - API mismatch
    src/crypto/padic_lattice.cpp
    # src/crypto/padic_isogeny.cpp  # Temporarily disabled - API mismatch
    src/crypto/padic_lll.cpp
    src/crypto/padic_discrete_log.cpp
    src/crypto/padic_linear_algebra.cpp
    src/crypto/padic_cvp_solver.cpp
    src/crypto/padic_cvp_ultrametric.cpp
    src/crypto/padic_babai_proper.cpp
    src/crypto/padic_basis_gen.cpp
    src/crypto/padic_kem.cpp
    src/crypto/padic_hash.cpp
    src/crypto/montgomery_context.cpp
    src/crypto/fast_padic.cpp
    src/rh/op_verifications.cpp
)

# Library options
option(BUILD_SHARED_LIBS "Build shared libraries" OFF)
option(BUILD_PYTHON_BINDINGS "Build Python bindings" ON)

# Create the library (static or shared based on BUILD_SHARED_LIBS)
add_library(adic ${LIBADIC_SOURCES})
target_link_libraries(adic PUBLIC ${GMP_LIBRARY} ${MPFR_LIBRARY})

# Set library properties
set_target_properties(adic PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    PUBLIC_HEADER "${CMAKE_SOURCE_DIR}/include/libadic/*.h"
    POSITION_INDEPENDENT_CODE ON  # Required for Python bindings
)

# Enable testing
enable_testing()

# Test executables
add_executable(test_gmp_wrapper tests/test_gmp_wrapper.cpp)
target_link_libraries(test_gmp_wrapper adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_gmp_wrapper COMMAND test_gmp_wrapper)

add_executable(test_zp tests/test_zp.cpp)
target_link_libraries(test_zp adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_zp COMMAND test_zp)

add_executable(test_qp tests/test_qp.cpp)
target_link_libraries(test_qp adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_qp COMMAND test_qp)

add_executable(test_functions tests/test_functions.cpp)
target_link_libraries(test_functions adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_functions COMMAND test_functions)

add_executable(test_math_validations tests/test_math_validations.cpp)
target_link_libraries(test_math_validations adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_math_validations COMMAND test_math_validations)

# Milestone test
add_executable(milestone1_test tests/milestone1_test.cpp)
target_link_libraries(milestone1_test adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME milestone1_test COMMAND milestone1_test 7 60)

# Reid-Li limit finder
add_executable(find_reid_li_limits tests/find_reid_li_limits.cpp)
target_link_libraries(find_reid_li_limits adic ${GMP_LIBRARY} ${MPFR_LIBRARY})

# BSD Conjecture test
add_executable(test_bsd_conjecture tests/test_bsd_conjecture.cpp)
target_link_libraries(test_bsd_conjecture adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_bsd_conjecture COMMAND test_bsd_conjecture)

# p-adic Cryptography test
add_executable(test_padic_crypto tests/test_padic_crypto.cpp)
target_link_libraries(test_padic_crypto adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_padic_crypto COMMAND test_padic_crypto)

# KEM test vectors
add_executable(test_padic_kem tests/test_padic_kem.cpp)
target_link_libraries(test_padic_kem adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_padic_kem COMMAND test_padic_kem)

# Cryptanalysis test - commented out for now
# add_executable(test_cryptanalysis tests/test_cryptanalysis.cpp)
# target_link_libraries(test_cryptanalysis adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
# add_test(NAME test_cryptanalysis COMMAND test_cryptanalysis)

# Examples (optional build)
option(BUILD_EXAMPLES "Build example programs" ON)
if(BUILD_EXAMPLES)
    add_executable(validate_mathematics examples/validate_mathematics.cpp)
    target_link_libraries(validate_mathematics adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
    add_test(NAME validate_mathematics COMMAND validate_mathematics)
    
    add_executable(interactive_demo examples/interactive_demo.cpp)
    target_link_libraries(interactive_demo adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
    
    # RH Propositions verification
    add_executable(verify_rh_ops examples/verify_rh_ops.cpp)
    target_link_libraries(verify_rh_ops adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
    
    # Iwasawa integration test
    add_executable(test_iwasawa_integration examples/test_iwasawa_integration.cpp)
    target_link_libraries(test_iwasawa_integration adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
endif()

# RH Propositions test
add_executable(test_rh_propositions tests/test_rh_propositions.cpp)
target_link_libraries(test_rh_propositions adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
add_test(NAME test_rh_propositions COMMAND test_rh_propositions)

# Install rules
include(GNUInstallDirs)
install(TARGETS adic
    EXPORT libadicTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
install(DIRECTORY include/libadic 
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.h"
)

# Install CMake package files
install(EXPORT libadicTargets
    FILE libadicTargets.cmake
    NAMESPACE libadic::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/libadic
)

# Create package config file
include(CMakePackageConfigHelpers)
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/libadicConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/libadicConfig.cmake"
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/libadic
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/libadicConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/libadicConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/libadicConfigVersion.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/libadic
)

# CPack configuration for creating packages
set(CPACK_PACKAGE_NAME "libadic")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "High-performance p-adic arithmetic library")
set(CPACK_PACKAGE_DESCRIPTION "The only implementation of the Reid-Li criterion for the Riemann Hypothesis")
set(CPACK_PACKAGE_VENDOR "Reid-Li Team")
set(CPACK_PACKAGE_CONTACT "asmith@example.com")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_SOURCE_DIR}/LICENSE")
set(CPACK_RESOURCE_FILE_README "${CMAKE_SOURCE_DIR}/README.md")

# Debian specific
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "A. Smith <asmith@example.com>")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "libgmp10, libmpfr6")
set(CPACK_DEBIAN_PACKAGE_SECTION "libs")
set(CPACK_DEBIAN_PACKAGE_PRIORITY "optional")

# RPM specific
set(CPACK_RPM_PACKAGE_LICENSE "MIT")
set(CPACK_RPM_PACKAGE_GROUP "Development/Libraries")
set(CPACK_RPM_PACKAGE_REQUIRES "gmp, mpfr")

# Source package
set(CPACK_SOURCE_GENERATOR "TGZ;ZIP")
set(CPACK_SOURCE_IGNORE_FILES
    "/build/;/.git/;/.github/;/.vscode/;/\\\\.DS_Store"
)

include(CPack)

# Python bindings
if(BUILD_PYTHON_BINDINGS)
    # Add pybind11
    add_subdirectory(extern/pybind11)
    
    # Find Python
    find_package(Python COMPONENTS Interpreter Development)
    
    if(Python_FOUND)
        # Python binding sources
        set(PYTHON_BINDING_SOURCES
            python/src/libadic_python.cpp
            python/src/bind_bigint.cpp
            python/src/bind_zp.cpp
            python/src/bind_qp.cpp
            python/src/bind_padic_functions.cpp
            python/src/bind_characters.cpp
            python/src/bind_l_functions.cpp
            python/src/bind_bernoulli.cpp
            python/src/bind_modular_arith.cpp
            python/src/bind_cyclotomic.cpp
            python/src/bind_elliptic.cpp
            python/src/bind_crypto.cpp
        )
        
        # Create Python module
        pybind11_add_module(libadic_python ${PYTHON_BINDING_SOURCES})
        
        # Link with the main library - use WHOLE_ARCHIVE to ensure all symbols are included
        if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
            target_link_libraries(libadic_python PRIVATE 
                -Wl,--whole-archive adic -Wl,--no-whole-archive
                ${GMP_LIBRARY} ${MPFR_LIBRARY})
        else()
            target_link_libraries(libadic_python PRIVATE adic ${GMP_LIBRARY} ${MPFR_LIBRARY})
        endif()
        
        # Set output name (remove _python suffix)
        set_target_properties(libadic_python PROPERTIES OUTPUT_NAME "libadic")
        
        # Install Python module
        install(TARGETS libadic_python
            LIBRARY DESTINATION ${Python_SITELIB}
        )
        
        message(STATUS "Python bindings will be built")
        message(STATUS "Python version: ${Python_VERSION}")
        message(STATUS "Python executable: ${Python_EXECUTABLE}")
    else()
        message(WARNING "Python not found. Python bindings will not be built.")
    endif()
endif()

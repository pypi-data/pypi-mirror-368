#ifndef LIBADIC_PADIC_LLL_H
#define LIBADIC_PADIC_LLL_H

#include "libadic/padic_linear_algebra.h"

namespace libadic {
namespace crypto {

class PadicLLL {
private:
    long prime;
    long prec;
    
public:
    PadicLLL(long p, long precision);
    
    linalg::Matrix reduce(const linalg::Matrix& basis, double delta = 0.75);
    linalg::Matrix gram_schmidt(const linalg::Matrix& basis);
    double compute_defect(const linalg::Matrix& basis);
    bool is_reduced(const linalg::Matrix& basis, double delta = 0.75);
};

} // namespace crypto  
} // namespace libadic

#endif // LIBADIC_PADIC_LLL_H
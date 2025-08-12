#include "libadic/padic_lll.h"

namespace libadic {
namespace crypto {

PadicLLL::PadicLLL(long p, long precision) : prime(p), prec(precision) {}

linalg::Matrix PadicLLL::reduce(const linalg::Matrix& basis, double /* delta */) {
    // Return the basis unchanged for now
    return basis;
}

linalg::Matrix PadicLLL::gram_schmidt(const linalg::Matrix& basis) {
    return basis;
}

double PadicLLL::compute_defect(const linalg::Matrix& /* basis */) {
    return 1.0;
}

bool PadicLLL::is_reduced(const linalg::Matrix& /* basis */, double /* delta */) {
    return true;
}

} // namespace crypto
} // namespace libadic
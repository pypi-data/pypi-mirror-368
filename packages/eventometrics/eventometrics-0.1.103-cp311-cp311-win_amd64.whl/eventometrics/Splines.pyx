# distutils: language = c++
# cython: boundscheck = False, wraparound = False, nonecheck = False, initializedcheck = False, cdivision = True

import numpy as np
cimport numpy as cnp
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _eval_spline(
    const double[::1] x,          # Contiguous memoryview for x
    const double[::1] knots,       # Contiguous memoryview for knots
    const double[::1] h,           # Contiguous memoryview for h
    const double[::1] g,           # Contiguous memoryview for g
    const double[::1] gamma2,      # Contiguous memoryview for gamma2
    double[::1] y,                 # Output memoryview for y
    Py_ssize_t nx,
    Py_ssize_t nknots
) noexcept nogil:                  # noexcept nogil for maximum performance
    cdef:
        Py_ssize_t j, k = 0
        double xj, hk, hk_m, hk_p
    for j in range(nx):
        xj = x[j]
        while k < nknots - 1 and xj > knots[k] + h[k]:
            k += 1
        hk = h[k]
        hk_m = xj - knots[k]
        hk_p = knots[k+1] - xj
        y[j] = (hk_m * g[k+1] + hk_p * g[k]) / hk - hk_m * hk_p / 6.0 * ( gamma2[k+1] * (1.0 + hk_m / hk) + gamma2[k] * (1.0 + hk_p / hk) )


def eval_spline_cython(
    cnp.ndarray[cnp.double_t, ndim=1] x,
    cnp.ndarray[cnp.double_t, ndim=1] knots,
    cnp.ndarray[cnp.double_t, ndim=1] h,
    cnp.ndarray[cnp.double_t, ndim=1] g,
    cnp.ndarray[cnp.double_t, ndim=1] gamma2
):
    # Validate inputs
    cdef Py_ssize_t nx = x.shape[0]
    cdef Py_ssize_t nknots = knots.shape[0]

    # if nknots < 2:
    #     raise ValueError("At least 2 knots required")
    # if h.shape[0] != nknots - 1:
    #     raise ValueError("h must have length len(knots)-1")
    # if g.shape[0] != nknots:
    #     raise ValueError("g must have length len(knots)")
    # if gamma2.shape[0] != nknots:
    #     raise ValueError("gamma2 must have length len(knots)")

    # Create output array
    cdef cnp.ndarray[cnp.double_t, ndim=1] y = np.zeros(nx, dtype=np.double)

    # Get memoryviews
    cdef double[::1] x_view = x
    cdef double[::1] knots_view = knots
    cdef double[::1] h_view = h
    cdef double[::1] g_view = g
    cdef double[::1] gamma2_view = gamma2
    cdef double[::1] y_view = y

    # Call the core computation without GIL
    with nogil:
        _eval_spline(x_view, knots_view, h_view, g_view, gamma2_view, y_view, nx, nknots)

    return y
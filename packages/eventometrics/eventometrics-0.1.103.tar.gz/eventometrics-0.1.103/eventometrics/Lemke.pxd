cimport numpy as np

# Declare the function signature
cpdef tuple Lemke_cython(
    np.ndarray[np.double_t, ndim=2] M,
    np.ndarray[np.double_t, ndim=1] q,
    int maxIter
)

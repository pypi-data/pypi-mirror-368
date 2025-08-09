# distutils: language = c++
# cython: boundscheck = False
# cython: wraparound = False
# cython: initializedcheck = False
# cython: cdivision = True

import numpy as np
cimport numpy as np
import cython
from libc.math cimport INFINITY, isnan
from libc.string cimport memcpy, strncpy
from libc.stdlib cimport malloc, calloc, free
#from libcpp cimport bool

# Define constants
cdef int W = 0, Z = 1, Y = 2, Q = 3

# Helper function for column swapping
cdef void _swap_columns(
    double** T,
    int** Tind,
    int* wPos,
    int* zPos,
    int col1,
    int col2,
    int n
) noexcept nogil:
    """Swap two columns in the tableau and update index arrays"""
    cdef double temp_d
    cdef int temp_i, i
    cdef int v1, idx1, v2, idx2

    # Update position arrays
    v1 = Tind[0][col1]
    idx1 = Tind[1][col1]
    if v1 == W:
        wPos[idx1] = col2
    elif v1 == Z:
        zPos[idx1] = col2

    v2 = Tind[0][col2]
    idx2 = Tind[1][col2]
    if v2 == W:
        wPos[idx2] = col1
    elif v2 == Z:
        zPos[idx2] = col1

    # Swap columns in tableau T
    for i in range(n):
        temp_d = T[i][col1]
        T[i][col1] = T[i][col2]
        T[i][col2] = temp_d

    # Swap columns in index array Tind
    for i in range(2):
        temp_i = Tind[i][col1]
        Tind[i][col1] = Tind[i][col2]
        Tind[i][col2] = temp_i


# Core Lemke algorithm
cdef void c_Lemke(
    double[:, :] M_view,
    double[:] q_view,
    int maxIter,
    double[:] z,
    int* exit_code,
    char* exit_msg
) noexcept nogil:
    # Get dimensions

    cdef bint goto_cleanup = False
    cdef int n = q_view.shape[0]
    cdef int n_x_2 = 2 * n
    cdef int total_cols = n_x_2 + 2
    cdef int drive_col = total_cols - 2  # Always second last column
    cdef int q_col = total_cols - 1     # Always last column

    # Allocate and initialize tableau T with calloc (auto-zeroed)
    cdef double** T = <double**>malloc(n * sizeof(double*))
    cdef int i, j, k
    for i in range(n):
        T[i] = <double*>calloc(total_cols, sizeof(double))  # Auto-zeroed

    # Allocate position arrays
    cdef int* wPos = <int*>malloc(n * sizeof(int))
    cdef int* zPos = <int*>malloc(n * sizeof(int))
    for i in range(n):
        wPos[i] = i
        zPos[i] = n + i

    # Allocate and initialize Tind with calloc (auto-zeroed)
    cdef int** Tind = <int**>malloc(2 * sizeof(int*))
    for i in range(2):
        Tind[i] = <int*>calloc(total_cols, sizeof(int))  # Auto-zeroed

    # Initialize tableau T: [I | -M | -ones | q]
    for i in range(n):
        T[i][i] = 1.0  # Identity matrix
        for j in range(n):
            T[i][n + j] = -M_view[i, j]  # -M block
        T[i][drive_col] = -1.0  # -ones
        T[i][q_col] = q_view[i]  # q-vector

    # Initialize Tind: [W0, W1,... | Z0, Z1,... | Y0 | Q0]
    for j in range(n):
        Tind[0][j] = W      # W block
        Tind[1][j] = j
        Tind[0][n + j] = Z  # Z block
        Tind[1][n + j] = j
    Tind[0][drive_col] = Y        # Drive variable
    Tind[1][drive_col] = 0
    Tind[0][q_col] = Q    # q-column
    Tind[1][q_col] = 0

    # Algorithm variables
    cdef int v, ind, ind2, ppos
    cdef double a_val, b_val, minRatio, newRatio
    cdef double minQ = INFINITY
    cdef int min_index = 0


    # Find minimum q-value
    for i in range(n):
        if T[i][q_col] < minQ:
            minQ = T[i][q_col]
            min_index = i
    ind = min_index

    # Phase 1: Handle negative q-values
    if minQ < -1e-12:
        a_val = T[ind][drive_col]  # Drive column element

        # Normalize pivot row
        for j in range(total_cols):
            T[ind][j] /= a_val

        # Update other rows
        for i in range(n):
            if i != ind:
                b_val = T[i][drive_col]
                for j in range(total_cols):
                    T[i][j] -= b_val * T[ind][j]

        # Determine leaving variable
        v = Tind[0][ind]
        ind2 = Tind[1][ind]
        if v == W:
            ppos = zPos[ind2]
        elif v == Z:
            ppos = wPos[ind2]

        # Swap columns if W or Z variable
        if v == W or v == Z:
            _swap_columns(T, Tind, wPos, zPos, ind, ppos % total_cols, n)

        # Swap with drive column
        _swap_columns(T, Tind, wPos, zPos, ind, drive_col , n)
    else:
        # Trivial solution
        for i in range(n):
            z[i] = 0.0
        exit_code[0] = 0
        strncpy(exit_msg, "Solution Found", 99)
        goto_cleanup = True;  # Jump to cleanup

    if not goto_cleanup :

        # Phase 2: Main iterations

        for k in range(maxIter):
            minRatio = INFINITY
            ind = -1

            # Find pivot row (minimum ratio test)
            for i in range(n):
                if T[i][drive_col] > 0: #1e-12:  # Avoid floating-point issues
                    newRatio = T[i][q_col] / T[i][drive_col]
                    if newRatio < minRatio:
                        minRatio = newRatio
                        ind = i

            # Check termination conditions
            if ind == -1:
                z[0] = INFINITY  # Use INFINITY as NaN placeholder
                exit_code[0] = -1
                strncpy(exit_msg, "Secondary ray found", 99)
                goto_cleanup = True;

            if not goto_cleanup :
                # Normalize pivot row
                a_val = T[ind][drive_col]
                for j in range(total_cols):
                    T[ind][j] /= a_val

                # Update other rows
                for i in range(n):
                    if i != ind:
                        b_val = T[i][drive_col]
                        for j in range(total_cols):
                            T[i][j] -= b_val * T[ind][j]

                # Determine leaving variable
                v = Tind[0][ind]
                ind2 = Tind[1][ind]
                if v == W:
                    ppos = zPos[ind2]
                elif v == Z:
                    ppos = wPos[ind2]

                # Swap columns if W or Z variable
                if v == W or v == Z:
                    _swap_columns(T, Tind, wPos, zPos, ind, ppos % total_cols, n)

                # Swap with drive column
                _swap_columns(T, Tind, wPos, zPos, ind, drive_col, n)

                # Check termination condition
                if Tind[0][drive_col] == Y:
                    # Initialize solution to zero
                    for i in range(n):
                        z[i] = 0.0

                    # Extract solution
                    for i in range(n):
                        if Tind[0][i] == Z:
                            z[Tind[1][i]] = T[i][q_col]

                    exit_code[0] = k
                    strncpy(exit_msg, "Solution Found", 99)
                    goto_cleanup = True;

    if not goto_cleanup :
        # Max iterations exceeded
        z[0] = INFINITY  # Use INFINITY as NaN placeholder
        exit_code[0] = -2
        strncpy(exit_msg, "Max Iterations Exceeded", 99)


    # Cleanup memory
    #cleanup:

    for i in range(n):
        if T != NULL and T[i] != NULL:
            free(T[i])
    if T != NULL:
        free(T)
    if wPos != NULL:
        free(wPos)
    if zPos != NULL:
        free(zPos)
    for i in range(2):
        if Tind != NULL and Tind[i] != NULL:
            free(Tind[i])
    if Tind != NULL:
        free(Tind)

# Python wrapper matching the declaration
cpdef tuple Lemke_cython(
    np.ndarray[np.double_t, ndim=2] M,
    np.ndarray[np.double_t, ndim=1] q,
    int maxIter
):
    # cdef np.ndarray[np.double_t, ndim=2] M_arr = np.asarray(M, dtype=np.double)
    # cdef np.ndarray[np.double_t, ndim=1] q_arr = np.asarray(q, dtype=np.double)
    # cdef np.ndarray[np.double_t, ndim=1] z_arr = np.zeros(M_arr.shape[0], dtype=np.double)
    cdef np.ndarray[np.double_t, ndim=1] z_arr = np.zeros(M.shape[0], dtype=np.double)
    cdef int exit_code
    cdef char exit_msg[100]  # Fixed-size buffer for message

    # cdef double[:, :] M_view = M_arr
    # cdef double[:] q_view = q_arr
    cdef double[:, :] M_view = M
    cdef double[:] q_view = q

    # Call the C-level implementation
    c_Lemke(M_view, q_view, maxIter, z_arr, &exit_code, exit_msg)

    # Convert to Python string
    cdef bytes msg_bytes = exit_msg

    # Handle NaN placeholder
    if isnan(z_arr[0]) or z_arr[0] == INFINITY:
        z_arr = np.array([np.nan])

    return z_arr, exit_code, msg_bytes.decode('utf-8')
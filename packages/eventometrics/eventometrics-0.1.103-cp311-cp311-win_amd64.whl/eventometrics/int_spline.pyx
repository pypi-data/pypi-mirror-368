# distutils: language = c++
# cython: boundscheck = False
# cython: wraparound = False
# cython: initializedcheck = False
# cython: cdivision = True
# cython: nonecheck = False

import numpy as np
cimport numpy as np
import cython
from libc.math cimport INFINITY

from Lemke cimport Lemke_cython



cpdef monotone_int_spline_Lemke_cython(
    np.ndarray[np.double_t, ndim=1] t,
    np.ndarray[np.double_t, ndim=1] Y,
    int m,
    double alpha
):
    # Create x array
    cdef int x_len = int(t[t.shape[0]-1] - t[0]) + 1
    cdef np.ndarray[np.double_t, ndim=1] x = np.linspace(t[0], t[t.shape[0]-1], x_len)

    # Get observation coordinates
    cdef int n = t.shape[0]

    # Create knots
    cdef np.ndarray[np.double_t, ndim=1] s = np.linspace(t[0], t[n-1], m)
    cdef double[:] s_view = s

    # Calculate distances between knots
    cdef np.ndarray[np.double_t, ndim=1] h = np.zeros(m-1, dtype=np.double)
    cdef double[:] h_view = h
    cdef int i
    for i in range(m-1):
        h_view[i] = s_view[i+1] - s_view[i]

    # Matrix Q
    cdef np.ndarray[np.double_t, ndim=2] Q = np.zeros((m, m-2), dtype=np.double)
    cdef double[:, :] Q_view = Q
    for i in range(m-2):
        Q_view[i, i] = 1.0 / h_view[i]
        Q_view[i+1, i] = -1.0/h_view[i] - 1.0/h_view[i+1]
        Q_view[i+2, i] = 1.0 / h_view[i+1]

    # Matrix R
    cdef np.ndarray[np.double_t, ndim=2] R = np.zeros((m-2, m-2), dtype=np.double)
    cdef double[:, :] R_view = R
    for i in range(m-2):
        R_view[i, i] = (h_view[i] + h_view[i+1]) / 3.0
        if i < m-3:
            R_view[i+1, i] = h_view[i+1] / 6.0
            R_view[i, i+1] = h_view[i+1] / 6.0

    # Matrix K calculation
    cdef np.ndarray[np.double_t, ndim=2] inv_R = np.linalg.inv(R)
    cdef np.ndarray[np.double_t, ndim=2] t_Q = Q.T
    cdef np.ndarray[np.double_t, ndim=2] K = Q @ inv_R @ t_Q

    # V and P matrices
    cdef np.ndarray[np.double_t, ndim=2] V = np.zeros((n-1, m), dtype=np.double)
    cdef np.ndarray[np.double_t, ndim=2] P = np.zeros((n-1, m), dtype=np.double)
    cdef double[:, :] V_view = V
    cdef double[:, :] P_view = P

    cdef int k = 0, L, l, j
    cdef double temp_val

    # Find initial k
    while k < m-1 and s_view[k+1] <= t[0]:
        k += 1

    for i in range(n-1):
        # Find L
        L = 0
        while k+L+1 < m and t[i+1] > s_view[k+L+1]:
            L += 1

        # Calculate V and P values
        temp_val = (s_view[k+1] - t[i])
        V_view[i, k] = temp_val * temp_val / (2.0 * h_view[k])
        P_view[i, k] = (h_view[k]**3)/24.0 - (t[i]-s_view[k])**2 * (temp_val+h_view[k])**2 / (24.0 * h_view[k])

        l = 1
        while l <= L:
            V_view[i, k+l] = (h_view[k+l-1] + h_view[k+l]) / 2.0
            P_view[i, k+l] = (h_view[k+l-1]**3 + h_view[k+l]**3) / 24.0
            l += 1

        temp_val = (t[i] - s_view[k])
        V_view[i, k+1] -= temp_val * temp_val / (2.0 * h_view[k])
        P_view[i, k+1] += temp_val * temp_val * (temp_val * temp_val - 2.0 * h_view[k] * h_view[k]) / (24.0 * h_view[k])

        temp_val = (s_view[k+L+1] - t[i+1])
        V_view[i, k+L] -= temp_val * temp_val / (2.0 * h_view[k+L])
        P_view[i, k+L] += temp_val * temp_val * (temp_val * temp_val - 2.0 * h_view[k+L] * h_view[k+L]) / (24.0 * h_view[k+L])

        temp_val = (t[i+1] - s_view[k+L])
        V_view[i, k+L+1] = temp_val * temp_val / (2.0 * h_view[k+L])
        P_view[i, k+L+1] = (h_view[k+L]**3)/24.0 - (s_view[k+L+1]-t[i+1])**2 * (t[i+1]-s_view[k+L]+h_view[k+L])**2 / (24.0 * h_view[k+L])

        k += L

    # Prepare P matrix
    cdef np.ndarray[np.double_t, ndim=2] P_reduced = P[:, 1:(m-1)]

    # Matrix C calculation
    cdef np.ndarray[np.double_t, ndim=2] C = V - P_reduced @ inv_R @ t_Q
    cdef np.ndarray[np.double_t, ndim=2] t_C = C.T

    # Prepare A and q for Lemke
    cdef np.ndarray[np.double_t, ndim=2] A = t_C @ C + alpha * K
    cdef np.ndarray[np.double_t, ndim=1] q_vec = -t_C @ Y

    # Solve using Lemke
    cdef np.ndarray[np.double_t, ndim=1] g = np.zeros(m)
    cdef int exit_code
    cdef str exit_msg

    # Lemke_cython(A, q_vec, 10000, g, &exit_code, exit_msg)
    g, exit_code, exit_msg = Lemke_cython(A, q_vec, 10000)

    # Check for solution failure
    if np.isnan(g[0]):
        return np.array([np.nan])

    # Calculate gamma
    cdef np.ndarray[np.double_t, ndim=1] gamma = inv_R @ t_Q @ g

    # Prepare second derivative array
    cdef np.ndarray[np.double_t, ndim=1] g2 = np.zeros(m) #+2
    g2[1:m-1] = gamma
    cdef double[:] g2_view = g2
    cdef double[:] g_view = g

    # Calculate spline values
    cdef np.ndarray[np.double_t, ndim=1] y = np.zeros(x_len)
    cdef double[:] y_view = y
    cdef double[:] x_view = x
    cdef double x_m_sk
    cdef double skp1_m_x
    k = 0

    for j in range(x_len):
        # Find the interval for x[j]
        while k < m-1 and x_view[j] > s_view[k] + h_view[k]:
            k += 1

        # Calculate spline value
        #y_view[j] = calculate_spline_value(x_view[j], s_view, h_view, g_view, g2_view, k, m)
        #y[j] = ((x[j]-s[k])*g[k+1]+(s[k+1]-x[j])*g[k])/h[k] - 1/6*(x[j]-s[k])*(s[k+1]-x[j])*(g2[k+1]*(1+(x[j]-s[k])/h[k])+g2[k]*(1+(s[k+1]-x[j])/h[k]) )


        x_m_sk = x_view[j] - s_view[k]
        skp1_m_x = s_view[k+1] - x_view[j]
        y_view[j] = ( (x_m_sk * g_view[k+1] + skp1_m_x * g_view[k])/h_view[k]
                    - x_m_sk * skp1_m_x / (6*h_view[k]) *
                      (g2_view[k+1]*(h_view[k] + x_m_sk) + g2_view[k]*(h_view[k] + skp1_m_x) )
                    )
    return y
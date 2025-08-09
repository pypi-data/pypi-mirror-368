# Quinn_Fernandes.pyx
import numpy as np
cimport numpy as cnp
cimport cython
from libc.math cimport cos, sin, acos, fabs
from libc.stdlib cimport malloc, free
from libc.string cimport memset

cnp.import_array()

# Python wrapper for clean interface
def Quinn_Fernandes_cython(yy, int Nfut, int Nharm=10, double FreqTOL=0.000001, int MaxIterations=10000):
    cdef int Npast = yy.shape[0]
    # Allocate output arrays
    cdef bint need_initialize = False
    cdef cnp.ndarray[double, ndim=1] xm_arr
    cdef cnp.ndarray[double, ndim=1] ym_arr
    if Npast > 1000:
        av = np.sum(yy)/Npast
        xm_arr = np.ones(Npast, dtype=np.double)*av
        ym_arr = np.ones(Nfut, dtype=np.double)*av
    else:
        xm_arr = np.empty(Npast, dtype=np.double)
        ym_arr = np.empty(Nfut, dtype=np.double)
        need_initialize = True
    
    # Call C core function
    c_Quinn_Fernandes(
        <double*>cnp.PyArray_DATA(yy),
        <double*>cnp.PyArray_DATA(xm_arr),
        <double*>cnp.PyArray_DATA(ym_arr),
        Npast,
        Nfut,
        Nharm,
        FreqTOL,
        MaxIterations,
        need_initialize
    )
    return xm_arr, ym_arr

# Core computation function
cdef void c_Quinn_Fernandes(
    double* yy,
    double* xm,
    double* ym,
    int Npast,
    int Nfut,
    int Nharm,
    double FreqTOL,
    int MaxIterations,
    bint need_initialize
) noexcept nogil:
    cdef:
        int i, j, harm, iterations
        double av = 0.0
        double alpha, beta, num, den, w
        double Sc, Ss, Scc, Sss, Scs, Sx, Sxc, Sxs
        double c_val, s_val, dx, denom, a, b, m
        double* z = <double*>malloc(Npast * sizeof(double))

    if need_initialize:
        # Initialize xm and ym with average
        for i in range(Npast):
            av += yy[i]
        av /= Npast

        for i in range(Npast):
            xm[i] = av
        for j in range(Nfut):
            ym[j] = av
    
    # Main harmonic loop
    for harm in range(Nharm):
        # Reset z array
        memset(z, 0, Npast * sizeof(double))
        
        alpha = 0.0
        beta = 2.0
        z[0] = yy[0] - xm[0]
        iterations = 0
        
        # Frequency estimation loop
        while fabs(alpha - beta) > FreqTOL and iterations < MaxIterations:
            iterations += 1
            alpha = beta
            z[1] = yy[1] - xm[1] + alpha * z[0]
            num = z[0] * z[1]
            den = z[0] * z[0]
            
            for i in range(2, Npast):
                z[i] = yy[i] - xm[i] + alpha * z[i-1] - z[i-2]
                num += z[i-1] * (z[i] + z[i-2])
                den += z[i-1] * z[i-1]
            
            beta = num / den
            if beta > 2.0:
                beta = 2.0
        
        # Calculate angular frequency
        w = acos(beta / 2.0)
        
        # Reset accumulators
        Sc = 0.0; Ss = 0.0; Scc = 0.0; Sss = 0.0; Scs = 0.0
        Sx = 0.0; Sxc = 0.0; Sxs = 0.0
        
        # Calculate sums for linear parameters
        for i in range(Npast):
            c_val = cos(w * (i + 1))
            s_val = sin(w * (i + 1))
            dx = yy[i] - xm[i]
            Sc += c_val
            Ss += s_val
            Scc += c_val * c_val
            Sss += s_val * s_val
            Scs += c_val * s_val
            Sx += dx
            Sxc += dx * c_val
            Sxs += dx * s_val
        
        # Normalize sums
        Sc /= Npast; Ss /= Npast; Scc /= Npast; Sss /= Npast; Scs /= Npast
        Sx /= Npast; Sxc /= Npast; Sxs /= Npast
        
        # Handle zero frequency case
        if w == 0.0:
            m = Sx
            a = 0.0
            b = 0.0
        else:
            # Calculate linear parameters
            denom = (Scs - Sc * Ss)**2 - (Scc - Sc*Sc) * (Sss - Ss*Ss)
            a = ((Sxs - Sx*Ss) * (Scs - Sc*Ss) - (Sxc - Sx*Sc) * (Sss - Ss*Ss)) / denom
            b = ((Sxc - Sx*Sc) * (Scs - Sc*Ss) - (Sxs - Sx*Ss) * (Scc - Sc*Sc)) / denom
            m = Sx - a*Sc - b*Ss
        
        # Update past and future estimates
        for i in range(Npast):
            xm[i] += m + a * cos(w * i) + b * sin(w * i)
        
        for j in range(Nfut):
            ym[j] += m + a * cos(w * (Npast + j)) + b * sin(w * (Npast + j))
    
    # Clean up temporary memory
    free(z)
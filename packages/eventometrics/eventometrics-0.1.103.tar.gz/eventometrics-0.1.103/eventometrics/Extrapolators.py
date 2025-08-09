import numpy as np
from .Quinn_Fernandes import Quinn_Fernandes_cython

from .base import BaseEstimator

class QuinnFernandesExtrapolator(BaseEstimator):
    extrapolate_params = ["n1", "n2"]

    def __init__(self,
                 n1: int = 0,
                 n2: int = 0,
                 n_predict: int = None,
                 # model = None,
                 Nharm: int = 10,  # Harmonics in model
                 FreqTOL=0.000001,  # Tolerance of frequency calculations
                 MaxIterations=10000,
                 ):

        self.n1 = n1
        self.n2 = n2
        self.n_predict = n_predict
        # self.model = model
        self.Nharm = Nharm
        self.FreqTOL = FreqTOL
        self.MaxIterations = MaxIterations
        self.x_past = None
        self.y_past = None
        self.x_n2fut = None
        self.y_n2fut = None
        self.x_pastn2 = None
        self.y_pastn2 = None
        self.x_fut = None
        self.y_fut = None

    def check_need_re_extrapolate(self, n1 = None, n2 = None, n_predict = None, **kwargs):
        if n1 is not None and n1 != self.n1:
            return True
        if n2 is not None and n2 != self.n2:
            return True
        if n_predict is not None and n_predict != self.n_predict:
            return True

    def extrapolate(self, x, y, n1 = None, n2 = None, n_predict = None, x_step = None, **kwargs):
        """
        Decomposes y into a limited number of harmonics (n_harm), preliminary
        discarding n1 and n2 (0 by default) points on the left and right.

        Parameters:
        ----------
        x -- vector, use x_step if given to extrapolate x

        y -- vector (time series) to extrapolate

        n_predict -- number of predicted points

        x_step -- step to add new x points

        Returns:
        ----------
        x_fut - prediction result for x

        y_fut - prediction result for y

        y_last - scalar, predicted value for y[-1] (not extrapolated)
        """
        # todo: validate parameters
        #assert n1 < 0 or n2 < 0, " n1 and n2 must be non-negative"

        if n1 is not None:
            self.n1 = n1
        if n2 is not None:
            self.n2 = n2
        if n_predict is not None:
            self.n_predict = n_predict
        n = len(x)
        assert n == len(y), "length of x and y must be same"

        y = np.ascontiguousarray(y[self.n1: n - self.n2], dtype=np.double)
        Nfut = n_predict + self.n2  # Predicted future values
        y_past, y_fut = Quinn_Fernandes_cython(y, Nfut, self.Nharm, self.FreqTOL, self.MaxIterations)

        if x_step == None:
            x_step = x[1] - x[0]

        self.x_past = x[self.n1: n - self.n2]
        self.y_past = y_past
        self.x_n2fut = np.append(x[n - self.n2:],
                                 np.linspace(x[-1] + x_step, x[-1] + x_step * n_predict, n_predict)
                                 )
        self.y_n2fut = y_fut

        self.x_pastn2 = x[self.n1:]
        self.y_pastn2 = np.append(y_past, y_fut[0:self.n1])
        self.x_fut = np.ascontiguousarray(np.linspace(x[-1] + x_step, x[-1] + x_step * n_predict, n_predict))
        self.y_fut = np.ascontiguousarray(y_fut[self.n2:])

        return self.x_fut, self.y_fut, self.y_pastn2[-1]

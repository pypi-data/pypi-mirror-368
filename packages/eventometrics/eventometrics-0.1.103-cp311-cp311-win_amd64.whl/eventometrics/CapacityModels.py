import numpy as np
import warnings
from copy import copy

from .base import BaseEstimator
from .Lemke import Lemke_cython
from .Splines import eval_spline_cython
from .Extrapolators import QuinnFernandesExtrapolator

from .Search import clone





class SimpleCapacity(BaseEstimator):
    fit_params = ["alpha"]

    def __init__(self,
                 t = None,
                 Y = None,
                 weights = None,
                 knots_number = None,
                 alpha = 10**5,
                 knots = None,
                 x = None,
                 x_step = 1,
                 x_num = None,
                 All_Positive = True,
                 Positive_abs_tol = 0.0001,
                 Positive_rel_tol = 1e-6,
                 max_recalculate_positive_iterations = 4,
                 extrapolator = None,
                 skip_input_parameters_validation = False,
                 ):
        self.knots_number = knots_number
        assert alpha >= 0, "alpha should be not negative"
        self.alpha = alpha
        self.knots = knots
        self.x = x
        self.x_step = x_step
        self.x_num = x_num
        self.All_Positive = All_Positive
        self.Positive_abs_tol = Positive_abs_tol
        self.Positive_rel_tol = Positive_rel_tol
        self.max_recalculate_positive_iterations = max_recalculate_positive_iterations
        self.extrapolator = extrapolator

        self.skip_input_parameters_validation = skip_input_parameters_validation
        if t is not None and Y is not None:
            self.validate_input(t, Y, weights)
            self.have_data = True
        else:
            self.t = None
            self.Y = None
            self.weights = weights
            self.n = 0
            self.have_data = False
        self.matrix_ready = False
        self.matrix_D_ready = False
        self.spline_params_ready = False

        # Parameters
        self.Consumption_rate = None
        self.max_Storage = None
        self.Events_mechanism_parameters_ready = False
        # Parameters for extrapolation
        self.x_fut = None
        self.y_fut = None
        self.y_last = None
        self.parameters_extrapolated = False
        # Parameters for local search optimization
        self.child_models = None
        self.child_models_initialized= False

    def validate_input(self, t, Y, weights = None):
        if not self.skip_input_parameters_validation:
            # todo: need validate input here
            assert len(Y) == len(t), 'Length Y must be same as length t'
            self.n = len(t)
            self.t = np.array(t, dtype = np.double)
            self.Y = np.array(Y, dtype = np.double)
            if weights is None:
                self.weights = np.ones(self.n-1, dtype = np.double)
            else:
                assert len(weights) == self.n-1, 'length of weights must be n-1, because last Y is not used'
                self.weights = np.array(weights, dtype=np.double)
            # sort events by t
            ord = np.argsort(self.t)
            self.t = self.t[ord]
            self.Y = self.Y[ord]
            self.skip_input_parameters_validation = True
        else:
            self.n = len(t)
            self.t = t
            self.Y = Y
            self.weights = weights

    def prepare_matrix(self):
        """
        Prepare matrixes for calculation
        """
        if not self.matrix_ready:
            assert self.have_data, 'Data t and Y not ready'
            if self.knots is not None:
                self.knots = np.array( self.knots, dtype = np.double)
                self.knots_number = len(self.knots)
            else:
                if self.knots_number is None:
                    if len(self.t)>0:
                        self.knots_number = len(self.t)
                    else:
                        self.knots_number = 0

            assert self.knots_number >= 2, 'knots_number or observations should not be less than 2'

            if self.knots is None or self.knots_number != len(self.knots):  # when knots_number defined, but knots not defined
                self.knots = np.linspace(np.min(self.t), np.max(self.t), self.knots_number, dtype = np.double)

            if self.x is None:
                if self.x_num is not None:
                    assert self.x_num>=2, 'x_num must be >=2'
                    self.x, self.x_step = np.linspace(self.knots[0], self.knots[-1], self.x_num, retstep=True, dtype = np.double)
                else:
                    self.x = np.arange(self.knots[0], self.knots[-1], self.x_step, dtype = np.double)
                    if self.x[-1] < self.knots[-1]:
                        self.x = np.append(self.x, self.knots[-1])
                    self.x_num = len(self.x)
            else:
                self.x_num = len(self.x)
                self.x_step = (self.x[-1]-self.x[0])/(self.x_num-1)

            m = self.knots_number  # for short

            # array of distance between knots
            self.h = self.knots[1:m] - self.knots[0:(m - 1)]

            # Matrix Q
            self.Q = np.zeros((m, m - 2), dtype = np.double)
            for i in range(m - 2):
                self.Q[i, i] = 1 / self.h[i]
                self.Q[i + 1, i] = -1 / self.h[i] - 1 / self.h[i + 1]
                self.Q[i + 2, i] = 1 / self.h[i + 1]

            # Matrix R
            self.R = np.zeros((m - 2, m - 2), dtype = np.double)
            for i in range(m - 2):
                self.R[i, i] = (self.h[i] + self.h[i + 1]) / 3
                if (i < m - 2 - 1):
                    self.R[i + 1, i] = self.h[i + 1] / 6
                    self.R[i, i + 1] = self.h[i + 1] / 6

            # Matrix K calculation
            self.inv_R = np.linalg.inv(self.R)
            self.t_Q = np.transpose(self.Q)
            self.inv_R_dot_QT = self.inv_R @ self.t_Q
            self.K = self.Q @ self.inv_R_dot_QT

            # Weights matrix
            self.W = np.diag(self.weights)

            # Filling in V and P matrices
            self.V = np.zeros((self.n - 1, m), dtype = np.double)
            self.P = np.zeros((self.n - 1, m), dtype = np.double)
            k = 0
            while ((self.knots[k] <= self.t[0]) and (self.knots[k + 1] < self.t[0])):  # find first k, that knots[k+1]>t[0]
                k = k + 1

            for i in range(self.n - 1):
                # finding L, it can be 0
                L = 0
                while self.t[i+1] > self.knots[k + L + 1] and k + L + 1 < m - 1:
                    L += 1
                hk_m = self.t[i] - self.knots[k]
                hk_p = self.knots[k + 1] - self.t[i]
                hkL_m = self.t[i+1] - self.knots[k + L]
                hkL_p = self.knots[k + L + 1] - self.t[i+1]

                self.V[i, k] = hk_p ** 2 / self.h[k] / 2
                self.P[i, k] = self.h[k] ** 3 / 24 - hk_m ** 2 * (hk_p + self.h[k]) ** 2 / self.h[k] / 24

                l = 1
                while l <= L:
                    self.V[i, k + l] = (self.h[k + l - 1] + self.h[k + l]) / 2
                    self.P[i, k + l] = (self.h[k + l - 1] ** 3 + self.h[k + l] ** 3) / 24
                    l = l + 1

                self.V[i, k + 1] = self.V[i, k + 1] - hk_m ** 2 / self.h[k] / 2
                self.P[i, k + 1] = self.P[i, k + 1] + hk_m ** 2 * (hk_m ** 2 - 2 * self.h[k] ** 2) / self.h[k] / 24
                self.V[i, k + L] = self.V[i, k + L] - hkL_p ** 2 / self.h[k + L] / 2
                self.P[i, k + L] = self.P[i, k + L] + hkL_p ** 2 * ( hkL_p ** 2 - 2 * self.h[k + L] ** 2) / self.h[k + L] / 24
                self.V[i, k + L + 1] = hkL_m ** 2 / self.h[k + L] / 2
                self.P[i, k + L + 1] = self.h[k + L] ** 3 / 24 - hkL_p ** 2 * ( hkL_m + self.h[k + L]) ** 2 / self.h[k + L] / 24
                k = k + L

            #don't need first and last column
            self.P = self.P[:, 1:(m - 1)]
            self.P = np.ascontiguousarray(self.P)

            # Matrix C calculation
            self.C = self.V - self.P @ self.inv_R_dot_QT
            self.t_C = np.transpose(self.C )

            # Matrix for Quadratic programming
            self.t_C_dot_W_dot_C = self.t_C @ self.W @ self.C
            Y2 = self.Y[0:-1] #.reshape((-1, 1))
            self.c = self.t_C @ self.W @ Y2 # Last Y not used in consumption rate restoration

    def calculate_positive_spline_params(self):
        need_repeat = True  # when we added new condition we need recalculate
        Z = []  # extra conditions will be stored here
        iteration = 0
        while need_repeat:
            if len(Z)>0:
                M = np.vstack((np.hstack((self.D, -np.array(Z).transpose())),
                               np.hstack((np.array(Z), np.zeros((len(Z), len(Z)))))
                               ))

                # q = np.vstack((-self.c,
                #                np.zeros((len(Z), 1))
                #                ))
                q = np.hstack((-self.c, np.zeros(len(Z))  )  ) # cython Lemke need flat array
                # solve quadratic problem
                _g, exit_code, exit_string = Lemke_cython(M, q, 10000)
                _g = _g[0:self.knots_number] # dont need Lagrange multipliers
            else:
                _g, exit_code, exit_string = Lemke_cython(self.D, -self.c, maxIter=10000)

            assert exit_code >= 0, "Error in Lemke_cython function with exit_code = " + str(exit_code) + " , exit string = "+ exit_string

            # self.g = _g.reshape((self.knots_number, 1))
            self.g =  np.ascontiguousarray(_g)
            max_g = np.max(_g)
            self.gamma = self.inv_R_dot_QT @ self.g
            self.gamma2 = np.append(np.append([0], self.gamma),0)

            if iteration < self.max_recalculate_positive_iterations:
                # find minimum between knots
                num_new_conditions = 0
                for k in range(self.knots_number - 1):
                    dg = (self.g[k + 1] - self.g[k]) / self.h[k] - self.h[k] * (self.gamma2[k + 1] + 2 * self.gamma2[k]) / 6
                    dddg = (self.gamma2[k + 1] - self.gamma2[k]) / self.h[k]
                    discr = self.gamma2[k] ** 2 - 2 * dg * dddg
                    if discr < 0:
                        continue
                    dt1 = (-self.gamma2[k] - np.sqrt(discr)) / (dddg)
                    dt2 = (-self.gamma2[k] + np.sqrt(discr)) / (dddg)
                    if dt1 > dt2:
                        dt1, dt2 = dt2, dt1
                    if dt1 > 0 and dt1 < self.h[k]:
                        hk_m = dt1
                        hk_p = self.h[k] - dt1
                        v = (hk_m * self.g[k + 1] + hk_p * self.g[k]) / self.h[k] - 1 / 6 * hk_m * hk_p * (
                                self.gamma2[k + 1] * (1 + hk_m / self.h[k]) + self.gamma2[k] * (1 + hk_p / self.h[k]))
                        if v < -self.Positive_abs_tol and v < -max_g*self.Positive_abs_tol:
                            V_cond = np.zeros(self.knots_number, dtype = np.double)
                            P_cond = np.zeros(self.knots_number, dtype = np.double)
                            V_cond[k] = hk_p / self.h[k]
                            V_cond[k + 1] = hk_m / self.h[k]
                            P_cond[k] = hk_m * hk_p * (self.h[k] + hk_p) / (self.h[k] * 6)
                            P_cond[k + 1] = hk_m * hk_p * (self.h[k] + hk_m) / (self.h[k] * 6)
                            P_cond = np.ascontiguousarray( P_cond[1:-1] )
                            Zi = V_cond - P_cond @ self.inv_R_dot_QT
                            Z.append(Zi)
                            num_new_conditions += 1

                    if dt2 > 0 and dt2 < self.h[k]:
                        hk_m = dt2
                        hk_p = self.h[k] - dt2
                        v = (hk_m * self.g[k + 1] + hk_p * self.g[k]) / self.h[k] - 1 / 6 * hk_m * hk_p * (
                                self.gamma2[k + 1] * (1 + hk_m / self.h[k]) + self.gamma2[k] * (1 + hk_p / self.h[k]))
                        if v < -self.Positive_abs_tol and v < -max_g*self.Positive_abs_tol:
                            V_cond = np.zeros(self.knots_number, dtype = np.double)
                            P_cond = np.zeros(self.knots_number, dtype = np.double)
                            V_cond[k] = hk_p / self.h[k]
                            V_cond[k + 1] = hk_m / self.h[k]
                            P_cond[k] = (hk_m * hk_p * (self.h[k] + hk_p) / (self.h[k] * 6))
                            P_cond[k + 1] = (hk_m * hk_p * (self.h[k] + hk_m) / (self.h[k] * 6))
                            P_cond = np.ascontiguousarray(P_cond[1:-1])
                            Zi = V_cond - P_cond @ self.inv_R_dot_QT
                            Z.append(Zi)
                            num_new_conditions += 1

                if num_new_conditions == 0:
                    need_repeat = False
                iteration += 1

            else:
                need_repeat = False

    def fit(self, t=None, Y=None, weights = None, alpha = None, **kwargs):
        if t is not None and Y is not None:
            self.validate_input(t,Y, weights)
            self.have_data = True
            self.matrix_ready = False
            self.spline_params_ready = False
        if not self.matrix_ready:
            self.prepare_matrix()
            self.matrix_ready = True
            self.matrix_D_ready = False
        if alpha is not None and alpha != self.alpha:
            assert alpha>=0, "alpha should be not negative"
            self.alpha = alpha
            self.matrix_D_ready = False
        if not self.matrix_D_ready:
            self.D = self.t_C_dot_W_dot_C + self.alpha * self.K
            self.matrix_D_ready = True
            self.spline_params_ready = False
        if not self.spline_params_ready:
            if self.All_Positive:
                self.calculate_positive_spline_params()
                self.spline_params_ready = True
            else:
                self.g = np.linalg.solve(self.D, self.c)
                self.gamma = self.inv_R_dot_QT @ self.g
                self.gamma2 = np.ascontiguousarray(np.append(np.append([0], self.gamma), 0))
                self.spline_params_ready = True
        if not self.Events_mechanism_parameters_ready:
            # calculate Resource consumption rate
            self.Consumption_rate = eval_spline_cython(self.x, self.knots, self.h, self.g, self.gamma2)
            self.parameters_extrapolated = False

            # calculate max Storage
            self.max_Storage = np.sum(self.Y)
            # if len(self.x)==(self.t[-1]-self.t[0]) and np.all(self.x[np.round(self.t[1:]-self.t[0])]==self.t):
            #     self.max_Storage -=  np.sum(self.y[np.round(t[:] - t[0])] / 2)
            # else:
            y_ti = eval_spline_cython(self.t, self.knots, self.h, self.g, self.gamma2)
            self.max_Storage -= np.sum(y_ti)/2
            self.max_Storage /= self.n
            self.Events_mechanism_parameters_ready = True

    def extrapolate_parameters(self, force = False, extrapolator = None, **kwargs):
        if force or not self.parameters_extrapolated or self.extrapolator.check_need_re_extrapolate(**kwargs):
            assert self.Events_mechanism_parameters_ready, "Parameters not ready to be extrapolated. Call fit method first"
            if extrapolator is not None:
                self.extrapolator = extrapolator
            if self.extrapolator is None:
                self.extrapolator = QuinnFernandesExtrapolator()
            self.x_fut, self.y_fut, self.y_last = self.extrapolator.extrapolate(x = self.x, y = self.Consumption_rate, x_step = self.x_step, **kwargs)
            self.parameters_extrapolated = True

    def predict(self, n_predict = None, n_events = 1, **kwargs ):
        if n_predict is None:
            if self.extrapolator is not None:
                n_predict = self.extrapolator.n_predict
            else:
                n_predict = 200
        if not self.parameters_extrapolated:# or len(self.x_fut) != n_predict :
            self.extrapolate_parameters(n_predict)
        elif len(self.x_fut) != n_predict:
            warnings.warn('Because n_predict is different from length(x_fut) calculate extrapolation again')
            self.extrapolate_parameters(n_predict)
        if n_events > 1:
            t_predict = []
            Y_predict = []

        Storage = self.Y[-1]
        Storage -= self.y_last/2  # Correction
        num_events = 0
        i = 0
        while i < n_predict:
            Storage -= self.y_fut[i]
            if Storage < 0:
                if n_events > 1:
                    t_predict.append(self.x_fut[i])
                    Y_predict.append(self.max_Storage - Storage)
                    Storage = self.max_Storage
                    num_events += 1
                    if num_events >= n_events:
                        return t_predict, Y_predict
                else:
                    return self.x_fut[i], self.max_Storage - Storage
            i += 1
        if num_events > 0:
            return t_predict, Y_predict
        else:
            return None, None

    def fit_and_score(self, Parameters, scorer, extra_scorer=None, scalars=False, num_val_events=1, **kwargs):
        # todo: terminate computation and return big number if parameters incorrect
        # if alpha < 0 or n1 < 0 or n2 < 0:
        #     return np.inf
        if not self.child_models_initialized:
            child_models = []
            for i in range(num_val_events):
                child_model = clone(self)
                new_n = self.n - num_val_events + i
                # child_model.t = copy(self.t[0:new_n])
                # child_model.Y = copy(self.Y[0:new_n])
                # if self.weights is not None:
                #     child_model.weights = copy(self.weights[0:new_n]-1)
                if self.weights is not None:
                    ch_weights = self.weights[0:new_n-1]
                else:
                    ch_weights = None
                child_model.validate_input(self.t[0:new_n], self.Y[0:new_n], ch_weights)
                child_models.append(child_model)
            self.child_models = child_models
            self.child_models_initialized = True

        # fit_kwargs = {}
        # for key in self.fit_params:
        #     if key in Parameters:
        #         fit_kwargs[key] = Parameters[key]
        # extrapolate_kwargs = {}
        # for key in self.extrapolator.extrapolate_params:
        #     if key in Parameters:
        #         extrapolate_kwargs[key] = Parameters[key]

        if scalars:
            Scores = np.zeros(num_val_events)
        else:
            t_true_arr = self.t[self.n - num_val_events:]
            t_lag_true = self.t[self.n - num_val_events - 1]
            t_predict_arr = np.zeros(num_val_events)
            Y_true_arr = self.Y[self.n - num_val_events:]
            Y_predict_arr = np.zeros(num_val_events)

        for ind, ch_model in enumerate(self.child_models):
            # ch_model.fit(**fit_kwargs)
            # ch_model.extrapolate_parameters(force = True, **extrapolate_kwargs)
            # t_predict, Y_predict = ch_model.predict()
            ch_model.fit(**Parameters, **kwargs)
            ch_model.extrapolate_parameters(force=True, **Parameters, **kwargs)
            t_predict, Y_predict = ch_model.predict(**Parameters, **kwargs)

            if t_predict is None or Y_predict is None:
                return np.inf
            if scalars:
                ind_true = self.n - num_val_events + ind
                score = scorer(t_true=self.t[ind_true],
                               t_lag_true=ch_model.t[-1],
                               t_pred=t_predict,
                               Y_true=self.Y[ind_true],
                               Y_pred=Y_predict,
                               mix_weight=kwargs["mix_weight"]
                               )
                if score == np.nan or score == np.inf:
                    return np.inf
                Scores[ind] = score
            else:
                t_predict_arr[ind] = t_predict
                Y_predict_arr[ind] = Y_predict

        if scalars:
            score = extra_scorer(Scores, weights=kwargs["sample_weights"])  # one of np.average or root_mean_squares
        else:
            score = scorer(t_true=t_true_arr,
                           t_lag_true=t_lag_true,
                           t_pred=t_predict_arr,
                           Y_true=Y_true_arr,
                           Y_pred=Y_predict_arr,
                           **kwargs)
        if score == np.nan:
            return np.inf
        return score

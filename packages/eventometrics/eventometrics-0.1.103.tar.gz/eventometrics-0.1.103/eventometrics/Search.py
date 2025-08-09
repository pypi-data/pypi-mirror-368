from itertools import product

import numpy

# import inspect
import copy
import numbers
import decimal
# from functools import partial

from joblib import Parallel, delayed
import warnings
import time

from .optimization import optNM_dicts
from .Metrics import _SCORERS, _Extra_SCORES, mean_relative_error

non_numeric_types = (bool, str, numpy.bool_)
numeric_types = (numbers.Real, decimal.Decimal, numpy.integer, numpy.floating)


def is_numeric(value):
    return not isinstance(value, non_numeric_types) and isinstance(value, numeric_types)


def clone(obj, safe=True):
    if not hasattr(obj, "get_params") or isinstance(obj, type):
        if not safe:
            return copy.deepcopy(obj)
        else:
            if isinstance(obj, type):
                raise TypeError("Should be instance of estimator, not a class (i.e. type)")
            else:
                TypeError(f"Cannot clone object {repr(obj)} (type {type(obj)}): it does not have get_params method.")

    new_object_params = obj.get_params(deep=False)
    for name, param in new_object_params.items():
        param_type = type(param)
        if param_type is dict:
            new_object_params[name] = {k: clone(v, safe=safe) for k, v in param.items()}
        elif param_type in (list, tuple, set, frozenset):
            new_object_params[name] = param_type([clone(e, safe=safe) for e in param])
        elif not hasattr(param, "get_params"):
            new_object_params[name] = copy.deepcopy(param)
        else:
            new_object_params[name] = clone(param, safe=False)  # recursive clone

    new_object = obj.__class__(**new_object_params)
    # quick sanity check of the parameters of the clone
    params_set = new_object.get_params(deep=False)
    for name in new_object_params:
        param1 = new_object_params[name]
        param2 = params_set[name]
        if param1 is not param2:
            raise RuntimeError(f"Cannot clone object {obj}, as the constructor either does not"
                               f" set or modifies parameter {name}. "
                               f"New_object_params[{name}] = {param1}, params_set[{name}] = {params_set[name]}")
    return new_object


def start_local_search( model,
                        parameters,
                        L_Bounds,
                        R_Bounds,
                        L_Bounds_global,
                        R_Bounds_global,
                        dif,
                        is_int,
                        excluded_from_local_search=None,
                        verbose=0,
                        cand_idx=0,
                        n_candidates=0,  # candidate_progress=(cand_idx, n_candidates),
                        **kwargs):
    # if cand_idx != 1:
    #     return {}, numpy.inf, False, 0, 0, "!"
    # print(model.extrapolator.Nharm, model.max_recalculate_positive_iterations)
    # Looks like we don't need use set_parames
    progress_str = f"{cand_idx + 1}/{n_candidates}"
    if verbose > 0:
        print(f"[{progress_str}] START {parameters}")

    if excluded_from_local_search is None:
        excluded_from_local_search = []
    included_parameters = {}
    excluded_parameters = {}
    for key in parameters:
        if key in excluded_from_local_search:
            excluded_parameters[key] = parameters[key]
        else:
            included_parameters[key] = parameters[key]

    start_time = time.time()
    # _fit_and_score = partial(model.fit_and_score, **excluded_parameters, **kwargs)
    best_params, value, converged, iterations, Total_calls, break_message = (
        optNM_dicts(objective=model.fit_and_score,
                    parameters=included_parameters,
                    L_Bounds=L_Bounds,
                    R_Bounds=R_Bounds,
                    L_Bounds_global=L_Bounds_global,
                    R_Bounds_global=R_Bounds_global,
                    dif=dif,
                    is_int=is_int,
                    **excluded_parameters,
                    **kwargs))

    fit_score_time = time.time() - start_time

    # combine the best_params with excluded parameters
    best_params = best_params | excluded_parameters
    if verbose > 0:
        print("["+progress_str+"] End :",
              " score = ", value,
              ", converged = ", converged,
              ", best parameters = ", best_params,
              ", iterations = ", iterations,
              ", total_cals = ", Total_calls,
              ", time : ", fit_score_time,
              ", break message = ", break_message)

    return best_params, value, converged, iterations, Total_calls, break_message


class GridSearchCV:

    def __init__(self,
                 estimator,
                 param_grid,
                 excluded_from_local_search=None,
                 eval_func=None,
                 extra_eval_func=None,
                 n_jobs=-2,  # in Parallel -1 mean all CPU cores, -2 mean 1 core left free
                 refit=True,
                 num_val_events=3,
                 n_predict=200,
                 mix_weight=0.1,
                 is_int=None,
                 simplex_start_size=0.05,
                 overlap=1,
                 verbose=1
                 ):
        self.estimator = estimator
        self.param_grid = param_grid
        self.excluded_from_local_search = excluded_from_local_search
        self.eval_func = eval_func
        self.extra_eval_func = extra_eval_func
        self.n_jobs = n_jobs
        self.refit = refit
        self.num_val_events = num_val_events
        self.n_predict = n_predict
        self.mix_weight = mix_weight
        self.is_int = is_int
        self.simplex_start_size = simplex_start_size
        self.overlap = overlap
        self.verbose = verbose

        self.best_params = None
        self.best_estimator = None
        self.best_value = None

    def prepare_parameters_lists(self):
        # find global bounds
        if self.excluded_from_local_search is None:
            self.excluded_from_local_search = []  # non-numeric parameters are excluded from local search
        Left_Bounds_global = {}
        Right_Bounds_global = {}
        for k, v in self.param_grid.items():
            if k not in self.excluded_from_local_search:
                if (not isinstance(v, (list, numpy.ndarray))
                        or len(v) <= 1 or
                        not all(list(map(is_numeric, v)))):
                    self.excluded_from_local_search.append(k)
                else:
                    Left_Bounds_global[k] = min(v)
                    Right_Bounds_global[k] = max(v)

        # split dict on two: numeric and non-numeric
        numeric_param_grid = {}
        non_numeric_param_grid = {}
        for key in self.param_grid:
            if key in self.excluded_from_local_search:
                non_numeric_param_grid[key] = self.param_grid[key]
            else:
                numeric_param_grid[key] = self.param_grid[key]

        # find cell bounds and middle points
        keys = numeric_param_grid.keys()      # list of keys without excluded
        values = numeric_param_grid.values()  # list of lists
        L_Bounds = [v[:-1] for v in values]
        R_Bounds = [v[1:] for v in values]

        Middle = [((numpy.array(R_Bounds[i]) + numpy.array(L_Bounds[i])) / 2).tolist() for i in range(len(L_Bounds))]
        # correcting np.inf or np.nan in middle points
        for i in range(len(Middle)):
            for j in range(len(Middle[i])):
                if numpy.isnan(Middle[i][j]):
                    Middle[i][j] = 0
                if Middle[i][j] == -numpy.inf:
                    if j + 2 < len(L_Bounds[i]):
                        Middle[i][j] = L_Bounds[i][j + 1] - 10 * (L_Bounds[i][j + 2] - L_Bounds[i][j + 1])
                    else:
                        Middle[i][j] = R_Bounds[i][j]
                if Middle[i][j] == numpy.inf:
                    if j - 2 >= 0:
                        Middle[i][j] = R_Bounds[i][j - 1] + 10 * (R_Bounds[i][j - 1] - R_Bounds[i][j - 2])
                    else:
                        Middle[i][j] = L_Bounds[i][j]

        # calculate simplex size
        dif = [((numpy.array(R_Bounds[i]) - numpy.array(L_Bounds[i])) * self.simplex_start_size).tolist()
               for i in range(len(L_Bounds))]
        for i in range(len(dif)):
            for j in range(len(dif[i])):
                if dif[i][j] == numpy.inf:
                    dif[i][j] = abs(Middle[i][j] * self.simplex_start_size)
                if dif[i][j] == 0:
                    dif[i][j] = 0.0001

        if self.is_int is None:
            self.is_int = []
        is_int_bool = [True if key in self.is_int else False for key in keys]
        # round integer parameters
        if any(is_int_bool):
            for i in range(len(is_int_bool)):
                if is_int_bool[i]:
                    for j in range(len(Middle[i])):
                        Middle[i][j] = round(Middle[i][j])
                        dif[i][j] = max(1, round(dif[i][j]))  # * sign(dif[i][j])

        # overlap, shift right bound to next cell
        if self.overlap > 0:
            for i in range(len(R_Bounds)):
                for j in range(len(R_Bounds[i])):
                    R_Bounds[i][j] = R_Bounds[i][min(len(R_Bounds[i]) - 1, j + self.overlap)]

        # return back non-numeric parameters values (just to make product() work correct)
        for key, value in non_numeric_param_grid.items():
            L_Bounds.append(value)
            R_Bounds.append(value)
            Middle.append(value)
            dif.append(value)

        keys = self.param_grid.keys()  # list of keys (with excluded)
        L_Bounds_list = []
        R_Bounds_list = []
        Middle_list = []
        dif_list = []
        for v in product(*L_Bounds):
            b = dict(zip(keys, v))
            b = {key: val for key, val in b.items() if key not in self.excluded_from_local_search}
            L_Bounds_list.append(b)
        for v in product(*R_Bounds):
            b = dict(zip(keys, v))
            b = {key: val for key, val in b.items() if key not in self.excluded_from_local_search}
            R_Bounds_list.append(b)
        for v in product(*Middle):
            Middle_list.append( dict(zip(keys, v)))
        for v in product(*dif):
            b = dict(zip(keys, v))
            b = {key: val for key, val in b.items() if key not in self.excluded_from_local_search}
            dif_list.append(b)

        return Middle_list, L_Bounds_list, R_Bounds_list, dif_list, Left_Bounds_global, Right_Bounds_global

    def fit(self, t=None, y=None, weights=None, **kwargs):
        # todo: validate parameters
        if callable(self.eval_func):
            eval_func = self.eval_func
        elif isinstance(self.eval_func, str) and self.eval_func in _SCORERS:
            eval_func = _SCORERS[self.eval_func]
        else:
            eval_func = mean_relative_error
        scalars = True
        if callable(self.extra_eval_func):
            extra_eval_func = self.extra_eval_func
        elif isinstance(self.extra_eval_func, str) and self.extra_eval_func in _Extra_SCORES:
            extra_eval_func = _Extra_SCORES[self.extra_eval_func]
        else:
            extra_eval_func = None
            scalars = False

        # prepare list of parameters (grid cell)
        (params_list, L_Bounds_list, R_Bounds_list, dif_list,
         L_Bounds_global, R_Bounds_global) = self.prepare_parameters_lists()

        n_candidates = len(params_list)

        fit_and_score_kwargs = dict(
            scorer=eval_func,
            extra_scorer=extra_eval_func,
            scalars=scalars,
            n_predict=self.n_predict,
            num_val_events=self.num_val_events,
            mix_weight=self.mix_weight,
            sample_weights=weights,
            verbose=self.verbose
        )

        base_model = clone(self.estimator)
        if t is not None and y is not None:
            base_model.validate_input(t, y, weights)

        if self.verbose > 0:
            print("Starting grid search for ", n_candidates, " candidates")

        with Parallel(n_jobs=self.n_jobs) as parallel:
            results = parallel(
                    delayed(start_local_search)(
                                                model=clone(base_model),
                                                parameters=params,
                                                L_Bounds=L_Bounds,
                                                R_Bounds=R_Bounds,
                                                L_Bounds_global=L_Bounds_global,
                                                R_Bounds_global=R_Bounds_global,
                                                dif=dif,
                                                is_int=self.is_int,
                                                exclude_from_local_search=self.excluded_from_local_search,
                                                cand_idx=cand_idx,
                                                n_candidates=n_candidates,
                                                **fit_and_score_kwargs,
                                                **kwargs
                                                )
                    for (cand_idx, params), L_Bounds, R_Bounds, dif in
                    zip(enumerate(params_list), L_Bounds_list, R_Bounds_list, dif_list)
                )
            # parallel.terminate()
            parallel._backend.terminate()
        # print(len(results))

        if len(results) <= 0:
            raise ValueError("Parallel execution returned 0 fit results")
        if len(results) != len(params_list):
            warnings.warn(f"Parallel execution returned inconsistent results. Expected {len(params_list)} "
                          f" but got {len(results)}")
        best_params_list, values_list, converged_list, iterations_list, Total_calls_list, break_message_list \
            = zip(*results)

        ord_index = numpy.argsort(values_list)
        best_index = ord_index[0]
        self.best_params = best_params_list[best_index]
        self.best_value = values_list[best_index]
        if not converged_list[best_index]:
            warnings.warn(f"Best result obtained when local search not converged properly, "
                          f"local search stopped on {iterations_list[best_index]} interation "
                          f"(did {Total_calls_list[best_index]} function calls, "
                          f"break message = '{break_message_list[best_index]}'")
        self.best_estimator = clone(self.estimator)
        # // setparameters...
        if self.refit:
            self.best_estimator.fit(t, y, **self.best_params, **kwargs)
            self.best_estimator.extrapolate_parameters(n_predict=self.n_predict, **self.best_params, **kwargs)

        return self

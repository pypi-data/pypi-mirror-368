import numpy as np
eps = np.finfo(np.double).eps


def mean_absolute_error(t_true, t_pred, Y_true, Y_pred, mix_weight = 0.1, sample_weights = None, **kwargs):
    if (t_pred is None or Y_pred is None or
            np.ndim(t_pred) == 0 and t_pred == np.nan or
            np.ndim(Y_pred) == 0 and Y_pred == np.nan or
            np.ndim(t_pred) > 0 and np.any(t_pred == np.nan) or
            np.ndim(Y_pred) > 0 and np.any(Y_pred == np.nan)
    ) :
        return np.inf
    # todo : validate parameters
    if np.ndim(t_true)==0:
        if np.ndim(Y_true)==0:
            return abs(t_true - t_pred) + mix_weight * abs(Y_true - Y_pred)
        else:
            return abs(t_true - t_pred) + mix_weight * np.mean(np.abs(Y_true - Y_pred))
    else:
        if len(Y_true.shape) == 1:
            return np.average(np.abs(t_true - t_pred) + mix_weight * abs(Y_true - Y_pred), weights = sample_weights)
        else:
            return np.average(np.abs(t_true - t_pred) + mix_weight * np.mean(abs(Y_true - Y_pred), axis = 1), weights = sample_weights)


def mean_relative_error(t_true, t_lag_true, t_pred, Y_true, Y_pred, mix_weight=0.1, sample_weights=None, **kwargs):
    if (t_pred is None or Y_pred is None or
            np.ndim(t_pred) == 0 and t_pred == np.nan or
            np.ndim(t_pred) > 0 and np.any(t_pred == np.nan) or
            np.ndim(Y_pred) == 0 and Y_pred == np.nan or
            np.ndim(Y_pred) > 0 and np.any(Y_pred == np.nan)) :
        return np.inf
    # todo : validate parameters
    # eps = np.finfo(np.double).eps
    if np.ndim(t_true)==0:
        t_div = max(abs(t_true - t_lag_true) , eps)
        if np.ndim(Y_true)==0:
            Y_div = max(abs(Y_true), eps)
            return abs(t_true - t_pred)/t_div + mix_weight * abs(Y_true - Y_pred)/Y_div
        else:
            Y_div = abs(Y_true)
            Y_div[Y_div == 0] = eps
            return abs(t_true - t_pred)/t_div + mix_weight * np.mean(np.abs(Y_true - Y_pred)/Y_div)
    else:
        t_div = np.zeros(len(t_true))
        t_div[1:] = t_true[1:] - t_true[0:-1]
        t_div[0] = t_true[0] - t_lag_true
        t_div = np.abs(t_div)
        t_div[t_div == 0] = eps
        Y_div = abs(Y_true)
        Y_div[Y_div == 0] = eps
        if len(Y_true.shape) == 1:
            return np.average(np.abs(t_true - t_pred)/t_div + mix_weight * abs(Y_true - Y_pred)/Y_div, weights = sample_weights)
        else:
            return np.average(np.abs(t_true - t_pred)/t_div + mix_weight * np.mean(abs(Y_true - Y_pred)/Y_div, axis = 1), weights = sample_weights)


def root_mean_squared_error(t_true, t_pred, Y_true, Y_pred, mix_weight = 0.1, sample_weights = None, **kwargs):
    if (t_pred is None or Y_pred is None or
            np.ndim(t_pred) == 0 and t_pred == np.nan or
            np.ndim(t_pred) > 0 and np.any(t_pred == np.nan) or
            np.ndim(Y_pred) == 0 and Y_pred == np.nan or
            np.ndim(Y_pred) > 0 and np.any(Y_pred == np.nan)) :
        return np.inf
    # todo : validate parameters
    if np.ndim(t_true)==0:
        if np.ndim(Y_true)==0:
            return abs(t_true - t_pred) + mix_weight * abs(Y_true - Y_pred)
        else:
            return abs(t_true - t_pred) + mix_weight * np.sqrt(np.sum((Y_true - Y_pred)**2)/len(Y_true))
    else:
        if len(Y_true.shape) == 1:
            if sample_weights is None:
                return np.sqrt(np.sum((np.abs(t_true - t_pred) + mix_weight * abs(Y_true - Y_pred))**2)/len(t_true))
            else:
                return np.sqrt(np.sum((np.abs(t_true - t_pred) + mix_weight * abs(Y_true - Y_pred))**2 * sample_weights )/np.sum(sample_weights) )
        else:
            if sample_weights is None:
                return np.sqrt(np.sum((np.abs(t_true - t_pred) + mix_weight * np.sqrt(np.mean((Y_true - Y_pred)**2, axis=1))  )**2)/len(t_true))
            else:
                return np.sqrt(np.sum((np.abs(t_true - t_pred) + mix_weight * np.sqrt(np.mean((Y_true - Y_pred)**2, axis=1))  )**2 * sample_weights )/np.sum(sample_weights) )


def root_mean_squared_relative_error(t_true, t_lag_true, t_pred, Y_true, Y_pred, mix_weight=0.1, sample_weights=None, **kwargs):
    if (t_pred is None or Y_pred is None or
            np.ndim(t_pred) == 0 and t_pred == np.nan or
            np.ndim(t_pred) > 0 and np.any(t_pred == np.nan) or
            np.ndim(Y_pred) == 0 and Y_pred == np.nan or
            np.ndim(Y_pred) > 0 and np.any(Y_pred == np.nan)) :
        return np.inf
    # todo : validat parameters
    if np.ndim(t_true)==0:
        t_div = max(abs(t_true - t_lag_true) , eps)
        if np.ndim(Y_true)==0:
            Y_div = max(abs(Y_true), eps)
            return abs(t_true - t_pred)/t_div + mix_weight * abs(Y_true - Y_pred)/Y_div
        else:
            Y_div = abs(Y_true)
            Y_div[Y_div == 0] = eps
            return abs(t_true - t_pred)/t_div + mix_weight * np.sqrt(np.mean((np.abs(Y_true - Y_pred)/Y_div)**2))
    else:
        t_div = np.zeros(len(t_true))
        t_div[1:] = t_true[1:] - t_true[0:-1]
        t_div[0] = t_true[0] - t_lag_true
        t_div = np.abs(t_div)
        t_div[t_div == 0] = eps
        Y_div = abs(Y_true)
        Y_div[Y_div == 0] = eps
        if len(Y_true.shape) == 1:
            if sample_weights is None:
                return np.sqrt( np.sum((np.abs(t_true - t_pred) / t_div + mix_weight * abs(Y_true - Y_pred) / Y_div)**2)/len(t_true))
            else:
                return np.sqrt(np.sum(( np.abs(t_true - t_pred) / t_div + mix_weight * abs(Y_true - Y_pred)/Y_div)**2 * sample_weights)/ np.sum(sample_weights))
        else:
            if sample_weights is None:
                print("!")
                return np.sqrt(np.sum( (np.abs(t_true - t_pred) / t_div + mix_weight * np.sqrt(np.mean( ( (Y_true - Y_pred) / Y_div )**2, axis=1) ) )**2 )/len(t_true))
            else:
                return np.sqrt(np.sum( (np.abs(t_true - t_pred) / t_div + mix_weight * np.sqrt(np.mean( ( (Y_true - Y_pred) / Y_div )**2, axis=1) ) )**2 * sample_weights )/np.sum(sample_weights))


def scalar_absolute_error(t_true, t_pred, Y_true, Y_pred, mix_weight = 0.1, **kwargs):
    if t_pred is None or Y_pred is None or t_pred == np.nan or Y_pred == np.nan:
        return np.inf
    # todo : validate parameters
    return abs(t_true - t_pred) + mix_weight * abs(Y_true - Y_pred)


def scalar_relative_error(t_true,t_lag_true, t_pred, Y_true, Y_pred, mix_weight=0.1, **kwargs):
    if t_pred is None or Y_pred is None or t_pred == np.nan or Y_pred == np.nan:
        return np.inf
    # todo : validate parameters
    if Y_true == 0:
        return np.inf
    dt = t_true - t_lag_true
    if dt == 0:
        return np.inf
    return abs((t_true - t_pred)/dt) + mix_weight * abs(Y_true - Y_pred)/Y_true


def root_mean_squares(scores, weights = None):
    return np.average(scores**2, weights = weights)**0.5

# todo : add other metrics

_SCORERS = {
    "mae": mean_absolute_error,
    "mre": mean_relative_error,
    "rmse": root_mean_squared_error,
    "rmsre": root_mean_squared_relative_error,
    "ae": scalar_absolute_error,
    "re": scalar_relative_error
}

_Extra_SCORES = {
    "mean": np.average,
    "rms": root_mean_squares
}

import inspect

class BaseEstimator:
    def get_params(self, deep=True):
        if self.__init__ is object.__init__:
            return []
        init_signature = inspect.signature(self.__init__)
        parameters = [p for p in init_signature.parameters.values() if
                      p.name != "self" and p.kind != p.VAR_KEYWORD and p.kind != p.VAR_POSITIONAL]
        param_names = sorted([p.name for p in parameters])
        out = dict()
        for key in param_names:
            value = getattr(self, key)
            if deep and hasattr(value, "get_params") and not isinstance(value, type):
                deep_items = value.get_params().items()
                out.update((key + "__" + k, val) for k, val in deep_items)
            out[key] = value
        return out
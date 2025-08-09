# names you want to expose
__all__ = ["tokenize","Parser","evalcr","crgen","npgen","mtp","naiveinit","benchmark"]

_api = None

def _load_api():
    global _api
    if _api is None:
        import importlib
        _api = importlib.import_module(".api", __name__)  # <- no fromlist recursion
    return _api

def __getattr__(name):
    if name in __all__:
        return getattr(_load_api(), name)
    raise AttributeError(name)

def __dir__():
    return sorted(list(globals().keys()) + __all__)
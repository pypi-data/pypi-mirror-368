import inspect
from functools import wraps

__all__ = ['SELF', 'decorator']

class SELF(tuple):
    def __new__(cls, value, owner):
        return super().__new__(cls, (value, owner))
    def __repr__(self) -> str:
        return f'<SELF bound {self.self} of {self.cls}>'
    @property
    def self(self): return self[0]
    @property
    def cls(self): return self[1]


class _instance_classmethod(object):

    def __init__(self, func):
        self.func = func
        self.firstargname = [*inspect.signature(func).parameters][0]

    def __get__(self, instance, owner):
        @wraps(self.func)
        def newfunc(*args, **kwargs):
            if instance is not None:
                return self.func(SELF(instance, owner), *args, **kwargs)
            arguments = inspect.getcallargs(self.func, *args, **kwargs)
            clsself = SELF(arguments[self.firstargname], owner)
            arguments[self.firstargname] = clsself
            return self.func(**arguments)
        return newfunc


class decorator:

    @property
    def instance_classmethod(self) -> object:
        return _instance_classmethod

decorator = decorator()

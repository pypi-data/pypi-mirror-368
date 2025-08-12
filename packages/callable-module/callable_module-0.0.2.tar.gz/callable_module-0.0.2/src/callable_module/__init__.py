""" Turn a callable into a module """

__all__ = [
    'from_function',
    'from_module',
]

import types

def from_function(callable, name=None):

    class CallableModule(types.ModuleType):
        __qualname__ = 'CallableModule'
        __call__ = staticmethod(callable)
        def __dir__(self):
            return sorted(super().__dir__() + ['__call__'])

    if name is None:
        name = callable.__name__

    module = CallableModule(name)
    return module

def from_module(callable, old):
    new = from_function(callable, name=old.__name__)
    new = copy_module_attrs(old, new)
    return new

def copy_module_attrs(old, new):

    module_attrs = [
         '__builtins__',
         '__cached__',
         '__doc__',
         '__file__',
         '__loader__',
         '__name__',
         '__package__',
         '__path__',
         '__spec__'
    ]
    for attr in module_attrs:
        new.__dict__[attr] = old.__dict__[attr]

    return new

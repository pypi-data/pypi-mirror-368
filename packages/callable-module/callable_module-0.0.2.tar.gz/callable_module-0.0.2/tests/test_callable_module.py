import types
import callable_module

def add_one(x):
    return x+1

def test_callable_module():
    mod = callable_module.from_function(add_one)
    assert isinstance(mod, types.ModuleType)
    assert mod(41) == 42


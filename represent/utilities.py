import sys
import warnings


class _DeprecatedValue(object):
    def __init__(self, value, message, warning_class):
        self.value = value
        self.message = message
        self.warning_class = warning_class


class _ModuleWithDeprecations(object):
    def __init__(self, module):
        self.__dict__["_module"] = module

    def __getattr__(self, attr):
        obj = getattr(self._module, attr)
        if isinstance(obj, _DeprecatedValue):
            warnings.warn(obj.message, obj.warning_class, stacklevel=2)
            obj = obj.value
        return obj

    def __setattr__(self, attr, value):
        setattr(self._module, attr, value)

    def __dir__(self):
        return ["_module"] + dir(self._module)


def deprecated(value, module_name, message, warning_class):
    module = sys.modules[module_name]
    if not isinstance(module, _ModuleWithDeprecations):
        sys.modules[module_name] = module = _ModuleWithDeprecations(module)
    return _DeprecatedValue(value, message, warning_class)

import importlib

import builtins

_imp = builtins.__dict__["__import__"]


class _LazyImport:
    def __init__(self, name, globals_=None, locals_=None, fromlist=(), level=0) -> None:
        self.__name = name
        self.__globals = globals_
        self.__locals = locals_
        self.__fromlist = fromlist
        self.__level = level

    def __import(self):
        try:
            return _imp(
                self.__name,
                self.__globals,
                self.__locals,
                self.__fromlist,
                self.__level,
            )
        except KeyError as e:
            raise

    def __getattr__(self, __name: str):
        names = __name
        package = self.__import()
        self = package
        try:
            return getattr(self, __name)
        except:
            print(__name)
            raise

    def __call__(self, *args, **kw):
        package = self.__import()

        self = package(*args, **kw)
        return self


class LazyImport(_LazyImport):
    def __init__(self, name, package=None):
        self.__name = name
        self.__package = package

    def __import(self):
        return importlib.import_module(self.__name, package=self.__package)


def lazy_import(name: str, globals_=None, locals_=None, fromlist=(), level=0):
    return _LazyImport(name, globals_, locals_, fromlist, level)


def enable_lazy_import(global_=globals(), import_=lazy_import):
    global_["__import__"] = import_

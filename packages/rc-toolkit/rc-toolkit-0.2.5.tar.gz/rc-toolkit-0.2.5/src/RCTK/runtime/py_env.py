import os
import sys
from pathlib import Path
from ..io_.file import get_name


from ..core.logger import get_log


log = get_log("RCTK.Runtime.PyENV")


def set_global(key: str, value: object):
    import builtins

    builtins.__dict__[key] = value
    log.info(f"Set global {key} as {value.__str__()}")


def add_path(*args: str | Path):
    if len(args) <= 0:
        raise ValueError("Missing args!")
    args_ = [str(x) for x in map(str, args)]
    sys.path.extend(args_)


def remove_path(path: str | Path):
    sys.path.remove(str(path))


def load_pyd(f_path: str | Path, name: str | None = None) -> object:
    import importlib.util as imp_u

    if name is None:
        name = str(get_name(f_path)[0]).split(".")[0]

    if f_path and os.path.exists(f_path):
        if spec := imp_u.spec_from_file_location(name, f_path):
            main = imp_u.module_from_spec(spec)
            if spec.loader:
                spec.loader.exec_module(main)
                return main
        else:
            raise ImportError(f"Cannot load {f_path} as a module")
    else:
        raise FileNotFoundError(f"File {f_path} does not exist")

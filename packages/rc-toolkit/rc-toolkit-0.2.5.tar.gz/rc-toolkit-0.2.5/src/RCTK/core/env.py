"""
This module contains functions to control the Python interpreter.
"""

import os
import sys

from .logger import get_log

from typing import TYPE_CHECKING

log = get_log("RCTK.Core.Env")


class Env:
    @staticmethod
    def add_path(path: str) -> None:
        Env.set_env("path", Env.get_env("path") + ";" + path)  # type: ignore

    @staticmethod
    def set_env(key: str, value: str) -> None:
        os.environ[key] = value

    @staticmethod
    def get_env(key: str, default: str | None = None) -> str | None:
        return (
            os.environ.get(key, default) if default is not None else os.environ.get(key)
        )

    @staticmethod
    def is_debug() -> bool:
        return bool(Env.get_env("DEBUG", default="False"))


is_debug = Env.is_debug


def get_pycache() -> str | None:
    return sys.pycache_prefix


def is_module(name, path: str) -> bool:
    return os.path.isfile(os.path.join(path, name))


def exit_py():
    sys.exit()

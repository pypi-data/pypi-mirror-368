import platform
from enum import Enum
from functools import lru_cache


class System(Enum):
    Other = "other"
    AIX = "aix"
    Linux = "linux"
    Win32 = "win32"
    Cygwin = "cygwin"
    macOS = "darwin"
    FreeBSD = "freebsd"

    @classmethod
    @lru_cache(3)
    def get_os(cls, os_str: str = platform.system()) -> "System":
        match os_str:
            case "Windows":
                return cls.Win32
            case "Linux":
                return cls.Linux
            case "Darwin":
                return cls.macOS
            case "Aix":
                return cls.AIX
            case os_str if os_str.startswith("Freebsd"):
                return cls.FreeBSD
            case _:
                return cls.Other


class Arch(Enum):
    x86 = "i386"
    x64 = "amd64"
    ARM = "arm"
    ARM64 = "arm64"
    Other = "other"

    @classmethod
    @lru_cache(1)
    def get_arch(cls, arch_str: str = platform.machine()) -> "Arch":
        arch_str = arch_str.lower().replace("_", "")
        match arch_str:
            case "amd64":
                return cls.x64
            case "i386":
                return cls.x86
            case "arm":
                return cls.ARM
            case "arm64":
                return cls.ARM64
            case _:
                return cls.Other

env_os = System.get_os()

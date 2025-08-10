"""
Store the enums used in the package.
"""

from enum import Enum


def mode_func(*args, **kw): ...


class MISSING_TYPE:
    pass


MISSING = MISSING_TYPE()


class DataType(Enum):
    File = b"0000"
    Object = b"0001"
    Text = b"0010"
    JSON = b"0011"
    Dict = b"0100"


class CompactType(Enum):
    ZIP = b"0000"
    TAR = b"0001"
    GZTAR = b"0010"
    BZTAR = b"0011"
    XZTAR = b"0100"
    ZSTD = b"0101"


class EncryptType(Enum):
    RSA_2048 = b"0000"
    ED25519 = b"0001"
    ECDSA = b"0010"


class HashType(Enum):
    SHA_256 = "sha256"
    SHA_384 = "sha384"
    SHA_512 = "sha512"
    BLAKE2 = "blake2b"


class Release(Enum):
    ALPHA = "a"
    BETA = "b"
    RELEASE = "r"
    DEBUG = "d"

    @classmethod
    def from_str(cls, rel_str: str) -> "Release":
        if rel_str == "a":
            return cls.ALPHA
        if rel_str == "b":
            return cls.BETA
        if rel_str == "r":
            return cls.RELEASE
        if rel_str == "d":
            return cls.DEBUG
        raise ValueError("Invalid release string")


class Version:
    def __init__(self, ver_1: int, ver_2: int, ver_3: int, build: int = 0):
        self.ver: tuple[int, int, int] = (ver_1, ver_2, ver_3)
        self.build: int = build

    @classmethod
    def from_str(cls, ver_str: str) -> "Version":
        return cls(*cls.dump_ver(ver_str))

    def set_build(self, build: int) -> None:
        self.build = build

    def get_build(self) -> int:
        return self.build

    def set_ver(self, ver: tuple[int, int, int]) -> None:
        self.ver = ver

    def get_ver(self) -> tuple[int, int, int]:
        return self.ver

    def update(self, ver_path: int = 3) -> None:
        if ver_path < 1 or ver_path > 3:
            raise ValueError("ver_path must be between 1 and 3")
        ver_list = list(self.ver)
        ver_list[ver_path - 1] += 1
        ver = tuple(ver_list)
        self.ver = tuple(ver_list)  # type: ignore

        if self.build != 0:
            self.build += 1

    @staticmethod
    def dump_ver(ver_str: str) -> tuple[int, ...]:
        def _str_ver(ver_str: str) -> tuple[int, ...]:
            return tuple(map(int, ver_str.split(".")))

        ver_list = ver_str.split("_")
        ver = _str_ver(ver_list[0])
        if len(ver_list) > 1:
            if ver_list[1].startswith("b"):
                build = int(ver_list[1][1:])
                return ver + (build,)
        return ver

    def __str__(self) -> str:
        rt = f"v{self.ver[0]}.{self.ver[1]}.{self.ver[2]}"
        if self.build == 0:
            return rt
        return rt + f"_b{self.build}"

    def __repr__(self) -> str:
        return self.__str__()

    # region
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise NotImplemented
        return self.ver == other.ver and self.build == other.build

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise NotImplemented
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise NotImplemented
        return self.ver < other.ver or (
            self.ver == other.ver and self.build < other.build
        )

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise NotImplemented
        return self.ver < other.ver or (
            self.ver == other.ver and self.build <= other.build
        )

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise NotImplemented
        return self.ver > other.ver or (
            self.ver == other.ver and self.build > other.build
        )

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise NotImplemented
        return self.ver > other.ver or (
            self.ver == other.ver and self.build >= other.build
        )

    # endregion


class MAGIC(Enum):
    MAGIC_NUMBER = b"MGNB"  # 4bit magic/
    VERSION = b"\x01"  # 1bit version
    HEADER_SIZE = 8  # 3bit save


class RCCP_MAGIC(Enum):
    MAGIC_NUMBER = b"RCCP"  # 4bit magic/
    VERSION = b"\x01"  # 1bit version
    HEADER_SIZE = 8  # 3bit save

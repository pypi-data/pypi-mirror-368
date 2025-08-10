import hashlib
from pathlib import Path
from os import makedirs as os_mkdirs
from functools import partial
from typing import Tuple, Optional, overload, Union, List
from io import BufferedWriter, BufferedReader

from ..core.env import is_debug
from ..core.enums import HashType, MAGIC


# region dir
def _mkdir(f_path: Path) -> int:
    if f_path.is_dir():
        return 0
    try:
        os_mkdirs(f_path)
        return 0
    except:
        if not is_debug():
            return -1
        raise


def mkdir(f_path: Union[Path, str], is_dir: bool = False) -> int:
    if isinstance(f_path, str):
        f_path = Path(f_path)
    if not is_dir:
        f_path = f_path.parent
    return _mkdir(f_path)


def mkdirs(f_root: Union[Path, str], f_group: List[str]) -> int:
    if isinstance(f_root, str):
        f_root = Path(f_root)
    rt = 0
    if f_group is None:
        return 0
    for f_sub in f_group:
        if (x := _mkdir(f_root / f_sub)) == 0:
            rt = x
    return rt


# endregion


# region file
def get_name(f_path: Union[Path, str]) -> list[str]:
    f_path = Path(f_path)
    return [f_path.stem, f_path.suffix]


def write_magic(magic: MAGIC, buffer: BufferedWriter) -> None:
    buffer.write(
        (mg := (magic.MAGIC_NUMBER.value + magic.VERSION.value))
        + b"\x00" * (magic.HEADER_SIZE.value - len(mg))
    )


def verify_magic(magic: MAGIC, buffer: BufferedReader) -> int:
    if len(header := buffer.read(magic.HEADER_SIZE.value)) < magic.HEADER_SIZE.value:
        return -1  # Magic number Error
    if header[:4] != magic.MAGIC_NUMBER.value:
        return 1  # Not Support File Type
    if header[4] != ord(magic.VERSION.value):
        return 2  # Not Support Version
    return 0  # ok


# endregion


# region hash
@overload
def get_hash(file, algorithm: HashType, *, chunk_size: int = 128 * 1048576) -> str: ...
@overload
def get_hash(
    file,
    algorithm: HashType = HashType.BLAKE2,
    *,
    digest_size: int | None = None,
    chunk_size: int = 128 * 1048576,
) -> str: ...
def get_hash(
    file,
    algorithm: HashType = HashType.BLAKE2,
    *,
    digest_size: Optional[int] = None,
    chunk_size: int = 128 * 1048576,
) -> str:

    hash_obj = (
        hashlib.blake2b(digest_size=(8 if digest_size is None else digest_size))
        if algorithm == HashType.BLAKE2
        else hashlib.new(algorithm.value)
    )
    with open(file, "rb") as f:
        for chunk in iter(partial(f.read, chunk_size), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def verify_hash(
    file, hash_str, algorithm: HashType = HashType.BLAKE2
) -> tuple[bool, str]:
    if (act_hash := get_hash(file, algorithm)) == hash_str.lower():
        return True, act_hash
    return False, act_hash


# endregion

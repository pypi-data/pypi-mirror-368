import tarfile
from pathlib import Path
from io import BytesIO
from typing import overload, IO
from zstandard.backend_c import ZstdCompressor, ZstdDecompressor

from ..core.enums import RCCP_MAGIC
from .file import write_magic, verify_magic


def _follow(path: Path, deep: int) -> list[Path]:
    rt = []
    deep = deep + 1
    if deep >= 1000:
        raise IndexError("Too deep")
    for sub in path.iterdir():
        if sub.is_dir():
            rt.extend(_follow(sub, deep))
        else:
            rt.append(sub)
    return rt


def mark_arc(
    f_obj: list[Path | str] | dict[str, Path | str], follow: bool = False
) -> tuple[list, dict[str, Path]]:
    """
    {arc, path}
    """
    arc_dict = (
        {str(f_path.name): f_path for f_path in map(Path, f_obj)}
        if isinstance(f_obj, list)
        else f_obj
    )
    i = []
    rt_dict: dict[str, Path] = {}
    for k, v in arc_dict.items():
        if (v := Path(v)).exists():
            if follow and v.is_dir():
                f = frozenset(_follow(v, 1))
                rt_dict.update({str(k / f_path.relative_to(v)): f_path for f_path in f})
            else:
                rt_dict[k] = v
        else:
            i.append(k)
    return i, rt_dict


@overload
def compress_with_zstd(
    f_obj: list, f_name: Path | str, *, follow: bool = False
) -> int: ...
@overload
def compress_with_zstd(
    f_obj: dict[str | Path, str], f_name: Path | str, *, follow: bool = False
) -> int: ...
@overload
def compress_with_zstd(
    f_obj: bytes, f_name: Path | str, *, arcname: str | None = "main"
) -> int: ...
def compress_with_zstd(
    f_obj: list | dict | bytes,
    f_name: Path | str,
    *,
    arcname: str | None = None,
    follow: bool = False,
) -> int:
    cctx = ZstdCompressor()  # create zstd compress

    with open(f_name, "wb") as f_opt:
        write_magic(RCCP_MAGIC, f_opt)  # type: ignore
        with cctx.stream_writer(f_opt) as stream:
            with tarfile.open(mode="w|", fileobj=stream) as tar:  # create tar stream
                if isinstance(f_obj, list) or isinstance(f_obj, dict):
                    f_fail, f_dict = mark_arc(f_obj=f_obj, follow=follow)
                    if f_fail is not None:
                        return -2
                    for f_arc, f_path in f_dict.items():
                        tar.add(f_path, arcname=f_arc, recursive=True)
                elif isinstance(f_obj, bytes):
                    t_info = tarfile.TarInfo(
                        name="main" if arcname == None else arcname
                    )
                    t_info.size = len(f_obj)
                    tar.addfile(t_info, BytesIO(f_obj))
                else:
                    return -1
    return 0


@overload
def decompress_with_zstd(f_zst: str, *, dump: str) -> int: ...
@overload
def decompress_with_zstd(f_zst: str, *, arcname: str = "main") -> int | IO[bytes]: ...
def decompress_with_zstd(
    f_zst: str,
    *,
    dump: str | None = None,
    arcname: str | None = None,
    chunk_size: int = 1024 * 1024,
) -> int | IO[bytes]:
    buffer = BytesIO()

    with open(f_zst, "rb") as f_obj:
        if verify_magic(RCCP_MAGIC, f_obj) != 0:  # type: ignore
            return -1
        dctx = ZstdDecompressor()
        with dctx.stream_reader(f_obj) as reader:
            while True:
                if not (chunk := reader.read(chunk_size)):
                    break
                buffer.write(chunk)

    buffer.seek(0)  # rebuff and and dump
    with tarfile.open(fileobj=buffer, mode="r:") as tar:
        if dump != None:
            tar.extractall(
                dump,
                members=[
                    m for m in tar if m.isfile() and not m.name.startswith(("/", "\\"))
                ],
            )
            return 0
        elif arcname != None:
            return x if (x := tar.extractfile(member=arcname)) else -2
        return -1


def compress_zstd(f_byte, filename, arcname: str = "main") -> int:
    return compress_with_zstd(f_byte, filename, arcname=arcname)


def decompress_zstd(filename, arcname: str = "main") -> int | IO[bytes]:
    return decompress_with_zstd(filename, arcname=arcname)

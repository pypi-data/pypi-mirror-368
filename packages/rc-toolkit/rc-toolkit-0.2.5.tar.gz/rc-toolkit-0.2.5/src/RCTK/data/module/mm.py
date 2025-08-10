from ...runtime.lazy_import import enable_lazy_import

enable_lazy_import(globals())

import json
from pathlib import Path
from collections import UserDict
from typing import Any

from ...io_ import compress
from ...core.enums import MISSING, MISSING_TYPE


def _load_json(file: Path) -> dict:
    buffer = compress.decompress_with_zstd(f_zst=str(file), arcname="main")
    if isinstance(buffer, int):  # decompress failed
        raise ValueError(f"Failed to decompress {file} with error code {buffer}")
    return json.load(buffer)


def _write_json(file: Path, data: dict) -> None:
    compress.compress_with_zstd(
        f_obj=json.dumps(data).encode("utf-8"), f_name=str(file), arcname="main"
    )


class MM(UserDict):
    def __init__(self, file: str | Path | None = None, **kw) -> None:
        super().__init__(self, **kw)
        self.file: Path | None = file if file is None else Path(file)
        if self.file:
            self.load() if self.file.is_file() else self.write()

    def load(self) -> dict | int:
        if not self.file:
            return -1
        self.data = _load_json(self.file)
        return self.data

    def write(self) -> int | None:
        if not self.file:
            return -1
        _write_json(self.file, self.data)

    def write_back(self, key, value: Any | MISSING_TYPE = MISSING) -> int | None:
        if not self.file:
            return -1
        if value == MISSING:
            value = self.data[key]
        self.load()
        self.data[key] = value
        self.write()

    def sync(self) -> int | None:
        if not self.file:
            return -1
        f_data = _load_json(self.file)
        f_data.update(self.data)
        self.data = f_data
        _write_json(self.file, self.data)

    def clear(self) -> dict:  # type: ignore
        data = self.data
        self.data = {}
        return data

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from logging import Logger

def get_log(logger_name: Optional[str] = None) -> "Logger": ...
def lazy_import() -> object: ...

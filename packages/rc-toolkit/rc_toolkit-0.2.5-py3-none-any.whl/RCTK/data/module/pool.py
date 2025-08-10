from dataclasses import dataclass
from typing import Any, Callable, Sequence
from collections import deque


@dataclass
class Call:
    data: Any
    loader: list[str]
    level: int


class Pool:
    def __init__(
        self, downer: Callable | None, upper: Callable | None, max_size: int
    ) -> None:
        self.downer = downer
        self.upper = upper
        self.stack: Sequence[Call] = deque(maxlen=max_size)

    def new_call(self) -> Call: ...

from dataclasses import dataclass, field
from typing import Any, Optional, Generator, Iterator


@dataclass(init=True)
class Node:
    node_pre: Optional["Node"] = field(default=None, compare=False, hash=False)
    node_data: Any = field(default=None, compare=True, hash=True)
    node_next: Optional["Node"] = field(default=None, compare=False, hash=False)


class LinkArray:
    def __init__(self, tp: Optional[Iterator] = None) -> None:
        self.len: int = 0
        self.s_node: Optional[Node] = None
        self.e_node: Optional[Node] = None
        if tp is not None and isinstance(tp, (list, tuple)):
            self._by_iterator(tp)

    def _by_iterator(self, tp: Iterator):
        for i in tp:
            self.append(i)

    def _get_node(self, key) -> Node:
        if not isinstance(key, int):
            raise TypeError()
        if key < 0:
            key += self.len
        if key >= self.len:
            raise IndexError()
        if key < self.len // 2:
            node = self.s_node
            for _ in range(key):
                node = node.node_next  # type: ignore
        else:
            node = self.e_node
            for _ in range(self.len - 1 - key):
                node = node.node_pre  # type: ignore
        return node  # type: ignore

    def __bool__(self) -> bool:
        return self.len == 0

    def __len__(self) -> int:
        return self.len

    def __getitem__(self, key: int) -> Any:
        return self._get_node(key).node_data

    def __setitem__(self, key: int, value: Any) -> None:
        if key == (self.len + 1) or (key == 0 and self.len == 0):
            self.append(value)
        self._get_node(key).node_data = value

    def __delitem__(self, key: int) -> Any:
        node = self._get_node(key)

        if self.len == 1:
            self.s_node, self.e_node = None, None
        elif node == self.s_node:
            self.s_node = self.s_node.node_next  # type: ignore
            self.s_node.node_pre = None  # type: ignore
        elif node == self.e_node:
            self.e_node = self.e_node.node_pre  # type: ignore
            self.e_node.node_next = None  # type: ignore
        else:
            node.node_pre.node_next = node.node_next  # type: ignore
            node.node_next.node_pre = node.node_pre  # type: ignore
        self.len -= 1
        return node.node_data

    def __iter__(self) -> Generator:
        node = self.s_node
        while node:
            yield node.node_data
            node = node.node_next

    def __reversed__(self) -> Generator:
        node = self.e_node
        while node:
            yield node.node_data
            node = node.node_pre

    def __contains__(self, item) -> bool:
        for node in self.__iter__():
            if node == item:
                return True
        return False

    def __str__(self) -> str:
        return "<->".join(map(str, self.__iter__()))

    def __hash__(self) -> int:
        return hash(self.__str__())

    def __repr__(self) -> str:
        return str(map(str, self.__iter__()))

    def __add__(self, lt: Iterator) -> "LinkArray":
        if isinstance(lt, LinkArray):
            self.e_node.node_next = lt.s_node  # type: ignore
            lt.s_node = self.e_node
            self.e_node = lt.e_node
            self.len += lt.len
        else:
            self._by_iterator(lt)
        return self

    def append(self, value: Any) -> None:
        new_node = Node(node_data=value)
        if self:
            self.s_node, self.e_node = new_node, new_node
        else:
            new_node.node_pre = self.e_node
            self.e_node.node_next = new_node  # type: ignore
            self.e_node = new_node
        self.len += 1

    def index(self, value) -> int:
        i = 0
        for node in self.__iter__():
            if node == value:
                return i
            i += 1
        return i

    def pop(self, key: int = -1) -> Any:
        return self.__delitem__(key)

    # def insert(self, key: int, value: Any) -> None:
    #     ...

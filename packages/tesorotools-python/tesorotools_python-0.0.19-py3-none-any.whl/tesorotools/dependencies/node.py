from collections.abc import Callable
from typing import Self

import pandas as pd

from . import functions


class Node:
    def __init__(self, name: str) -> None:
        self._name: str = name
        self._edges: list[Self] = []

    def add_edge(self, node: Self) -> None:
        self._edges.append(node)

    def build_edges(self, *, dependencies: list[str], function: str) -> None:
        self._resolving_function: Callable[..., float | pd.Series] = getattr(
            functions, function
        )
        for d in dependencies:
            self.add_edge(Node(d))

    @property
    def name(self) -> str:
        return self._name

    @property
    def edges(self) -> list[Self]:
        return self._edges

    @property
    def resolving_function(self) -> Callable[..., float | pd.Series]:
        return self._resolving_function

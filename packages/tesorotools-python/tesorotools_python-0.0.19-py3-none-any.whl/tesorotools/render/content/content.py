from typing import Protocol, Self

from docx.document import Document
from yaml import Loader, MappingNode


class Content(Protocol):
    def render(self, document: Document) -> Document: ...

    @classmethod
    def from_yaml(cls, loader: Loader, node: MappingNode) -> Self: ...

    @property
    def level(self) -> int: ...

    @level.setter
    def level(self, level: int) -> None: ...

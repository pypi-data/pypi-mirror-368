from typing import Any, Self

from docx.document import Document
from yaml import Loader, MappingNode

from tesorotools.render.content.content import Content


class Text:
    def __init__(self, text: str) -> None:
        self._text = text

    @classmethod
    def from_yaml(cls, loader: Loader, node: MappingNode) -> Self:
        values: dict[str, Any] = loader.construct_mapping(node, deep=True)
        values.pop("id")
        text: str = values.pop("text", None)
        section: Self = cls(text=text)
        return section

    def render(self, document: Document) -> Document:
        document.add_paragraph(self._text)
        return document

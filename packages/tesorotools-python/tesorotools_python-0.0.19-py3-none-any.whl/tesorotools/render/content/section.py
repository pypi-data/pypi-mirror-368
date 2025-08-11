from typing import Any, Self

from docx.document import Document
from yaml import Loader, MappingNode

from tesorotools.render.content.content import Content


class Section:
    def __init__(
        self,
        id: str,
        title: str | None = None,
        contents: dict[str, Content] | None = None,
    ) -> None:
        self._id: str = id
        self._title: str = title if title is not None else ""
        self._contents: dict[str, Content] = (
            contents if contents is not None else {}
        )
        self._level = 1

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, level: int) -> None:
        self._level = level

    @classmethod
    def from_yaml(cls, loader: Loader, node: MappingNode) -> Self:
        values: dict[str, Any] = loader.construct_mapping(node, deep=True)
        id: str = values.pop("id")
        title: str = values.pop("title", None)
        contents: dict[str, Content] = values
        section: Self = cls(id=id, title=title, contents=contents)
        section.nest()
        return section

    def render(self, document: Document) -> Document:
        # Use the "Heading `level`" style from the base document
        document.add_heading(self._title, level=self._level)
        for _, content in self._contents.items():
            document.add_paragraph()
            document = content.render(document)
        return document

    def nest(self):
        for _, content in self._contents.items():
            if isinstance(content, Section):
                content.level += 1
                content.nest()

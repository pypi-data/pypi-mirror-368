from typing import Any, Self

from docx.document import Document
from yaml import MappingNode

from tesorotools.utils.config import TemplateLoader


class Title:
    def __init__(
        self, title: str | None = None, comment: str | None = None
    ) -> None:
        self._title: str = "" if title is None else title
        self._comment: str = "" if comment is None else comment

    @classmethod
    def from_yaml(cls, loader: TemplateLoader, node: MappingNode) -> Self:
        title_cfg: dict[str, Any] = loader.construct_mapping(node, deep=True)
        title: str | None = title_cfg.get("title", None)
        comment: str | None = title_cfg.get("comment", None)
        return cls(title, comment)

    def render(self, document: Document) -> Document:
        if (self.title == "") and (self.comment == ""):
            title_text: str = ""
        elif (self.title == "") and (self.comment != ""):
            title_text: str = self.comment
        else:
            title_text: str = f"{self.title}: {self.comment}"
        # Use the "Title" style in the word template
        document.add_heading(text=title_text, level=0)
        return document

    @property
    def title(self) -> str:
        return self._title

    @property
    def comment(self) -> str:
        return self._comment

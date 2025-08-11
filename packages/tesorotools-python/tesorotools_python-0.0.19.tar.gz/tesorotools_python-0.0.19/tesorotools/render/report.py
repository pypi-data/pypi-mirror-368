from typing import Any, Self

from docx.document import Document
from yaml import Loader, MappingNode

from tesorotools.render.content.content import Content
from tesorotools.render.content.title import Title


class Report:
    def __init__(
        self,
        title: str,
        contents: dict[str, Content],
    ):
        self.title: str = title
        self.contents: dict[str, Content] = contents

    @classmethod
    def from_yaml(cls, loader: Loader, node: MappingNode) -> Self:
        report_cfg: dict[str, Any] = loader.construct_mapping(node, deep=True)
        title: str = report_cfg.pop("id")
        return cls(title=title, contents=report_cfg)

    def render(self, document: Document) -> Document:
        document._body.clear_content()
        for _, content in self.contents.items():
            content.render(document)
            if not isinstance(content, Title):
                document.add_paragraph()
        return document

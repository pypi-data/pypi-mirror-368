from datetime import date, datetime, time
from typing import Any, Self

from babel.dates import format_datetime
from docx.document import Document
from yaml import MappingNode

from tesorotools.utils.config import TemplateLoader


class Subtitle:
    def __init__(self, date_time: datetime | None = None) -> None:
        if date_time is None:
            date_time: datetime = datetime.now()
        self._date_time: datetime = date_time

    @classmethod
    def from_yaml(cls, loader: TemplateLoader, node: MappingNode) -> Self:
        subtitle_cfg: dict[str, Any] = loader.construct_mapping(node, deep=True)
        # parse date
        date_cfg: str | date | None = subtitle_cfg.get("date", None)
        if date_cfg is None:
            date_time: datetime = datetime.now()
        elif isinstance(date_cfg, date):
            date_time: datetime = datetime.combine(date_cfg, time.min)
        elif isinstance(date_cfg, str):
            date_time: datetime = datetime.strptime(date_cfg, "%Y-%m-%d")

        # parse hour
        hour_cfg: str | None = subtitle_cfg.get("hour", None)
        if hour_cfg is not None:
            hour_str, minute_str = hour_cfg.split(sep=":")
            date_time = date_time.replace(
                hour=int(hour_str), minute=int(minute_str)
            )

        return cls(date_time)

    def set_time(self, hour: int, minute: int) -> None:
        self._date_time = self._date_time.replace(hour=hour, minute=minute)

    def _format_datetime(self) -> str:
        date_fmt: str = format_datetime(
            self._date_time, "EEEE, dd 'de' MMMM 'de' yyyy, HH:mm", locale="es"
        )
        date_fmt = date_fmt.capitalize()
        return date_fmt

    def render(self, document: Document) -> Document:
        date_fmt = self._format_datetime()
        document.add_paragraph(date_fmt, style="Subtitle")
        document.add_paragraph()
        return document

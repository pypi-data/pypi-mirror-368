from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from win32com.client import constants

from .base import Base
from .color import rgb


@dataclass(repr=False)
class Font(Base):
    def __repr__(self) -> str:
        clsname = self.__class__.__name__
        return f"<{clsname} {self.name!r}>"

    @property
    def name(self) -> str:
        return self.api.Name

    @name.setter
    def name(self, value: str) -> None:
        self.api.Name = value

    @property
    def size(self) -> float:
        return self.api.Size

    @size.setter
    def size(self, size: float) -> None:
        self.api.Size = size

    @property
    def bold(self) -> bool:
        return self.api.Bold == constants.msoTrue

    @bold.setter
    def bold(self, value: bool) -> None:
        self.api.Bold = value

    @property
    def italic(self) -> bool:
        return self.api.Italic == constants.msoTrue

    @italic.setter
    def italic(self, value: bool) -> None:
        self.api.Italic = value

    @property
    def color(self) -> int:
        return self.api.Color.RGB

    @color.setter
    def color(self, value: int | str | tuple[int, int, int]) -> None:
        self.api.Color.RGB = rgb(value)

    def set(
        self,
        name: str | None = None,
        size: float | None = None,
        bold: bool | None = None,
        italic: bool | None = None,
        color: int | str | tuple[int, int, int] | None = None,
    ) -> Self:
        if name is not None:
            self.name = name
        if size is not None:
            self.size = size
        if bold is not None:
            self.bold = bold
        if italic is not None:
            self.italic = italic
        if color is not None:
            self.color = color

        return self

    def update(self, font: Font) -> Self:
        self.name = font.name
        self.size = font.size
        self.bold = font.bold
        self.italic = font.italic
        self.color = font.color
        return self

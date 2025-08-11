from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Literal, overload

from win32com.client import constants

from .base import Collection, Element
from .shape import Line, Shape

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import Self


@dataclass(repr=False)
class Table(Shape):
    @property
    def rows(self) -> Rows:
        return Rows(self.api.Table.Rows, self)

    @property
    def columns(self) -> Columns:
        return Columns(self.api.Table.Columns, self)

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.columns)

    def cell(self, row: int, column: int | None = None) -> Cell:
        if column is None:
            n = len(self.columns)
            row, column = row // n, row % n

        return self.rows[row].cells[column]

    def __len__(self) -> int:
        return len(self.rows)

    @overload
    def __getitem__(self, index: int) -> Row: ...

    @overload
    def __getitem__(self, index: tuple[int, int]) -> Cell: ...

    @overload
    def __getitem__(self, index: tuple[int, slice]) -> Row: ...

    @overload
    def __getitem__(self, index: tuple[slice, int]) -> Column: ...

    def __getitem__(
        self,
        index: int | tuple[int, int] | tuple[int, slice] | tuple[slice, int],
    ) -> Cell | Row | Column:
        if isinstance(index, int):
            return self.rows[index]

        if isinstance(index, tuple):
            if isinstance(index[0], int) and isinstance(index[1], int):
                return self.cell(index[0], index[1])

            if isinstance(index[0], int) and index[1] == slice(None):
                return self.rows[index[0]]

            if index[0] == slice(None) and isinstance(index[1], int):
                return self.columns[index[1]]

        raise NotImplementedError

    def __iter__(self) -> Iterator[Row]:
        for i in range(len(self)):
            yield self[i]

    def minimize_height(self) -> None:
        for row in self.rows:
            row.height = 1

    def reset_style(
        self,
        weight: float = 2,
        weight_inside: float = 1,
        color: int | str | tuple[int, int, int] = "black",
        color_inside: int | str | tuple[int, int, int] = "black",
    ) -> None:
        api = self.api.Table
        api.FirstRow = False
        api.HorizBanding = False
        self.fill.set(visible=False)

        for row in self.rows:
            row.borders["bottom"].set(color=color_inside, weight=weight_inside)

        for column in self.columns:
            column.borders["right"].set(color=color_inside, weight=weight_inside)

        self.rows[0].borders["top"].set(color=color, weight=weight)
        self.rows[-1].borders["bottom"].set(color=color, weight=weight)
        self.columns[0].borders["left"].set(color=color, weight=weight)
        self.columns[-1].borders["right"].set(color=color, weight=weight)


def set_text(
    cells: Iterable[Cell],
    texts: Iterable[str],
    *,
    size: float | None = None,
    bold: bool = False,
    merge: bool = False,
) -> None:
    texts = list(texts)
    cells = list(cells)

    prev = 0
    for k, (cell, text) in enumerate(zip(cells, texts, strict=False)):
        if not merge or k == 0 or text != texts[k - 1]:
            cell.text = text
            cell.shape.font.set(size=size, bold=bold)
            prev = k

        elif text == texts[k - 1]:
            cell.merge(cells[prev])


@dataclass(repr=False)
class Axis(Element):
    parent: Table
    collection: Rows | Columns

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    @property
    def cells(self) -> CellRange:
        return CellRange(self.api.Cells, self)

    @property
    def borders(self) -> Borders:
        return self.cells.borders

    def __len__(self) -> int:
        return len(self.cells)

    def __getitem__(self, index: int) -> Cell:
        return self.cells[index]

    def __iter__(self) -> Iterator[Cell]:
        for i in range(len(self)):
            yield self[i]

    def text(
        self,
        texts: Iterable[str],
        *,
        size: float | None = None,
        bold: bool = False,
        merge: bool = False,
    ) -> None:
        set_text(self, texts, size=size, bold=bold, merge=merge)


@dataclass(repr=False)
class Row(Axis):
    parent: Table
    collection: Rows

    @property
    def height(self) -> float:
        return self.api.Height

    @height.setter
    def height(self, value: float) -> None:
        self.api.Height = value


@dataclass(repr=False)
class Column(Axis):
    parent: Table
    collection: Columns

    @property
    def width(self) -> float:
        return self.api.Width

    @width.setter
    def width(self, value: float) -> None:
        self.api.Width = value


@dataclass(repr=False)
class Rows(Collection[Row]):
    parent: Table
    type: ClassVar[type[Element]] = Row

    @property
    def height(self) -> list[float]:
        return [row.height for row in self]

    @height.setter
    def height(self, value: list[float]) -> None:
        for row, height in zip(self, value, strict=True):
            row.height = height

    @property
    def borders(self) -> BordersCollection:
        return BordersCollection([row.borders for row in self])


@dataclass(repr=False)
class Columns(Collection[Column]):
    parent: Table
    type: ClassVar[type[Element]] = Column

    @property
    def width(self) -> list[float]:
        return [column.width for column in self]

    @width.setter
    def width(self, value: list[float]) -> None:
        for column, width in zip(self, value, strict=True):
            column.width = width

    @property
    def borders(self) -> BordersCollection:
        return BordersCollection([column.borders for column in self])


@dataclass(repr=False)
class Cell(Element):
    parent: Table
    collection: CellRange

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    @property
    def shape(self) -> Shape:
        return Shape(self.api.Shape, self.parent.parent, self.parent.collection)

    @property
    def text(self) -> str:
        return self.shape.text

    @text.setter
    def text(self, value: str) -> None:
        self.shape.text = value

    @property
    def borders(self) -> Borders:
        return Borders(self.api.Borders, self.parent)

    def merge(self, merge_to: Cell) -> None:
        self.api.Merge(merge_to.api)


@dataclass(repr=False)
class CellRange(Collection[Cell]):
    parent: Axis
    type: ClassVar[type[Element]] = Cell

    @property
    def borders(self) -> Borders:
        return Borders(self.api.Borders, self.parent.parent)


@dataclass(repr=False)
class LineFormat(Element, Line):
    parent: Table
    collection: Borders

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


@dataclass(repr=False)
class LineFormatCollection:
    items: list[LineFormat]

    def set(
        self,
        weight: float | None = None,
        color: int | str | tuple[int, int, int] | None = None,
        alpha: float | None = None,
    ) -> Self:
        for item in self.items:
            item.set(weight=weight, color=color, alpha=alpha)

        return self


@dataclass(repr=False)
class Borders(Collection[LineFormat]):
    parent: Table
    type: ClassVar[type[Element]] = LineFormat

    def __getitem__(
        self,
        index: int | Literal["bottom", "left", "right", "top"],
    ) -> LineFormat:
        if isinstance(index, int):
            return super().__getitem__(index)

        index = getattr(constants, "ppBorder" + index[0].upper() + index[1:])
        return LineFormat(self.api(index), self.parent, self)  # type: ignore


@dataclass(repr=False)
class BordersCollection:
    items: list[Borders]

    def __getitem__(
        self,
        index: int | Literal["bottom", "left", "right", "top"],
    ) -> LineFormatCollection:
        return LineFormatCollection([item[index] for item in self.items])

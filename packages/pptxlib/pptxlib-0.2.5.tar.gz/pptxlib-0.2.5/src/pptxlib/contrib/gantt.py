from __future__ import annotations

from datetime import datetime
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta

if TYPE_CHECKING:
    from pptxlib.shape import Shape
    from pptxlib.slide import Slide
    from pptxlib.table import Table


def date_index(kind: str, start: datetime, end: datetime) -> list[datetime]:
    if kind in ["month", "monthly"]:
        start = datetime(start.year, start.month, 1)
        end = datetime(end.year, end.month, 1)
        delta = relativedelta(end, start)
        n = 12 * delta.years + delta.months
        return [start + relativedelta(months=k) for k in range(n + 1)]

    if kind in ["week", "weekly"]:
        start -= relativedelta(days=start.weekday())
        end -= relativedelta(days=end.weekday())
        n = (end - start).days // 7
        return [start + relativedelta(days=7 * k) for k in range(n + 1)]

    if kind in ["day", "daily"]:
        n = (end - start).days
        return [start + relativedelta(days=k) for k in range(n + 1)]

    msg = f"Unsupported kind: {kind}"
    raise ValueError(msg)


def fiscal_year(date: datetime) -> str:
    if 1 <= date.month <= 3:
        return f"FY{date.year - 1}"

    return f"FY{date.year}"


class GanttKind(Enum):
    MONTH = "month"
    WEEK = "week"
    DAY = "day"


class GanttFrame:
    kind: GanttKind
    date_index: list[datetime]
    columns: list[list[str]]

    def __init__(self, kind: str, start: datetime, end: datetime) -> None:
        self.date_index = date_index(kind, start, end)

        years = [fiscal_year(date) for date in self.date_index]
        months = [str(date.month) for date in self.date_index]
        days = [str(date.day) for date in self.date_index]

        if kind in ["month", "monthly"]:
            self.columns = [years, months]
            self.kind = GanttKind.MONTH
        elif kind in ["week", "weekly"]:
            weeks = [f"{m}/{d}" for m, d in zip(months, days, strict=True)]
            self.columns = [years, weeks]
            self.kind = GanttKind.WEEK
        elif kind in ["day", "daily"]:
            self.columns = [months, days]
            self.kind = GanttKind.DAY
        else:
            raise NotImplementedError

    @property
    def name(self) -> str:
        start = self.date_index[0].strftime("%Y/%m/%d")
        end = self.date_index[-1].strftime("%Y/%m/%d")
        return f"{start}-{end}-{self.kind.value}"

    @property
    def days(self) -> int:
        return (self.date_index[-1] - self.date_index[0]).days


class GanttChart:
    frame: GanttFrame
    slide: Slide
    table: Table

    def __init__(
        self,
        kind: str,
        start: datetime,
        end: datetime,
    ) -> None:
        self.frame = GanttFrame(kind, start, end)

    def add_table(
        self,
        slide: Slide,
        left: float,
        top: float,
        right: float | None = None,
        bottom: float | None = None,
        index_width: float = 100,
        index_font_size: float = 14,
        font_size: float = 12,
    ) -> Table:
        if right is None:
            right = left
        if bottom is None:
            bottom = top

        num_rows = len(self.frame.columns) + 1
        num_columns = len(self.frame.columns[0]) + 1
        width = slide.width - left - right
        height = slide.height - top - bottom

        table = slide.shapes.add_table(
            num_rows=num_rows,
            num_columns=num_columns,
            left=left,
            top=top,
            width=width,
            height=height,
        )

        table.reset_style(color_inside="gray")
        table.rows[-1].borders["top"].set(color="black", weight=1)
        table.columns[0].borders["right"].set(color="black", weight=1)

        table.columns[0].width = index_width
        column_width = (width - index_width) / (num_columns - 1)
        for k in range(1, num_columns):
            table.columns[k].width = column_width

        for k, columns in enumerate(self.frame.columns):
            size = index_font_size
            table.rows[k].text(["", *columns], size=size, bold=True, merge=True)
        for cell in table.rows[-1]:
            cell.shape.font.set(size=font_size)
        table.cell(0, 0).merge(table.cell(1, 0))

        table.minimize_height()
        table.rows[-1].height = height - sum(table.rows.height[:-1])

        slide.name = self.frame.name
        table.name = self.frame.name
        self.slide = slide
        self.table = table

        return self.table

    @cached_property
    def origin(self) -> tuple[float, float]:
        cell = self.table.cell(-1, 1)
        return cell.shape.left, cell.shape.top

    @cached_property
    def day_width(self) -> float:
        start = self.table.cell(-1, 1).shape.left
        end = self.table.cell(-1, -1).shape.left
        return (end - start) / self.frame.days

    def x(self, date: datetime) -> float:
        start = self.origin[0] + self.day_width / 2
        return start + (date - self.frame.date_index[0]).days * self.day_width

    def y(self, offset: float) -> float:
        return self.origin[1] + offset

    def add(
        self,
        date: datetime,
        offset: float,
        width: float = 20,
        height: float | None = None,
        kind: str = "Oval",
        text: str = "day",
        color: int | str | tuple[int, int, int] | None = None,
    ) -> Shape:
        if height is None:
            height = width
        left = self.x(date) - width / 2
        top = self.y(offset) - height / 2
        shape = self.slide.shapes.add(kind, left, top, width, height)

        if text == "day":
            text = str(date.day)
        shape.text = text
        shape.align_center()
        shape.text_margin(left=0, top=0, right=0, bottom=0)

        if color is not None:
            shape.line.set(color=color)
            shape.fill.set(color=color)

        return shape

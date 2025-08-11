from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, ClassVar, Literal

from win32com.client import constants

from .base import Base, Collection, Element
from .color import rgb
from .font import Font

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Self

    from matplotlib.figure import Figure
    from PIL.Image import Image
    from win32com.client import DispatchBaseClass

    from .slide import Slide
    from .table import Table


@dataclass(repr=False)
class Color(Base):
    @property
    def color(self) -> int:
        return self.api.ForeColor.RGB

    @color.setter
    def color(self, value: int | str | tuple[int, int, int]) -> None:
        self.api.ForeColor.RGB = rgb(value)

    @property
    def alpha(self) -> float:
        return self.api.Transparency

    @alpha.setter
    def alpha(self, value: float) -> None:
        self.api.Transparency = value

    @property
    def visible(self) -> bool:
        return bool(self.api.Visible)

    @visible.setter
    def visible(self, value: bool) -> None:
        self.api.Visible = value

    def set(
        self,
        color: int | str | tuple[int, int, int] | None = None,
        alpha: float | None = None,
        visible: bool | None = None,
    ) -> Self:
        if color is not None:
            self.color = color
        if alpha is not None:
            self.alpha = alpha
        if visible is not None:
            self.visible = visible
        return self

    def update(self, color: Color) -> None:
        self.color = color.color
        self.alpha = color.alpha


@dataclass(repr=False)
class Fill(Color):
    pass


@dataclass(repr=False)
class Line(Color):
    @property
    def weight(self) -> float:
        return self.api.Weight

    @weight.setter
    def weight(self, value: float) -> None:
        self.api.Weight = value

    def set(
        self,
        weight: float | None = None,
        color: int | str | tuple[int, int, int] | None = None,
        alpha: float | None = None,
    ) -> Self:
        if color is not None:
            self.color = color
        if weight is not None:
            self.weight = weight
        if alpha is not None:
            self.alpha = alpha

        return self

    def update(self, line: Line) -> None:
        self.color = line.color
        self.alpha = line.alpha
        self.weight = line.weight

    @property
    def dash_style(self) -> int:
        return self.api.DashStyle

    @dash_style.setter
    def dash_style(self, value: int | str) -> None:
        if isinstance(value, str):
            value = getattr(constants, f"msoLine{value}")
        self.api.DashStyle = value

    def dash(self, dash_style: int | str = "Dash") -> Self:
        self.dash_style = dash_style
        return self

    @property
    def begin_arrowhead_style(self) -> int:
        return self.api.BeginArrowheadStyle

    @begin_arrowhead_style.setter
    def begin_arrowhead_style(self, value: int | str) -> None:
        if isinstance(value, str):
            value = getattr(constants, f"msoArrowhead{value}")
        self.api.BeginArrowheadStyle = value

    @property
    def end_arrowhead_style(self) -> int:
        return self.api.EndArrowheadStyle

    @end_arrowhead_style.setter
    def end_arrowhead_style(self, value: int | str) -> None:
        if isinstance(value, str):
            value = getattr(constants, f"msoArrowhead{value}")
        self.api.EndArrowheadStyle = value

    @property
    def begin_arrowhead_length(self) -> int:
        return self.api.BeginArrowheadLength

    @begin_arrowhead_length.setter
    def begin_arrowhead_length(self, value: int | str) -> None:
        if isinstance(value, str):
            value = getattr(constants, f"msoArrowhead{value}")
        self.api.BeginArrowheadLength = value

    @property
    def end_arrowhead_length(self) -> int:
        return self.api.EndArrowheadLength

    @end_arrowhead_length.setter
    def end_arrowhead_length(self, value: int | str) -> None:
        if isinstance(value, str):
            value = getattr(constants, f"msoArrowhead{value}")
        self.api.EndArrowheadLength = value

    @property
    def begin_arrowhead_width(self) -> int:
        return self.api.BeginArrowheadWidth

    @begin_arrowhead_width.setter
    def begin_arrowhead_width(self, value: int | str) -> None:
        if isinstance(value, str):
            value = getattr(constants, f"msoArrowhead{value}")
        self.api.BeginArrowheadWidth = value

    @property
    def end_arrowhead_width(self) -> int:
        return self.api.EndArrowheadWidth

    @end_arrowhead_width.setter
    def end_arrowhead_width(self, value: int | str) -> None:
        if isinstance(value, str):
            value = getattr(constants, f"msoArrowhead{value}")
        self.api.EndArrowheadWidth = value

    def begin_arrow(
        self,
        style: int | str | None = None,
        length: int | str | None = None,
        width: int | str | None = None,
    ) -> Self:
        if style is not None:
            self.begin_arrowhead_style = style
        if length is not None:
            self.begin_arrowhead_length = length
        if width is not None:
            self.begin_arrowhead_width = width
        return self

    def end_arrow(
        self,
        style: int | str | None = None,
        length: int | str | None = None,
        width: int | str | None = None,
    ) -> Self:
        if style is not None:
            self.end_arrowhead_style = style
        if length is not None:
            self.end_arrowhead_length = length
        if width is not None:
            self.end_arrowhead_width = width
        return self


@dataclass(repr=False)
class Shape(Element):
    parent: Slide
    collection: Shapes

    @property
    def left(self) -> float:
        return self.api.Left

    @property
    def top(self) -> float:
        return self.api.Top

    @property
    def width(self) -> float:
        return self.api.Width

    @property
    def height(self) -> float:
        return self.api.Height

    @left.setter
    def left(self, value: float | Literal["center"]) -> None:
        slide = self.parent

        if value == "center":
            v = (slide.width - self.width) / 2
        elif value < 0:
            v = slide.width - self.width + value
        else:
            v = value

        self.api.Left = v

    @top.setter
    def top(self, value: float | Literal["center"]) -> None:
        slide = self.parent

        if value == "center":
            v = (slide.height - self.height) / 2
        elif value < 0:
            v = slide.height - self.height + value
        else:
            v = value

        self.api.Top = v

    @width.setter
    def width(self, value: float) -> None:
        self.api.Width = value

    @height.setter
    def height(self, value: float) -> None:
        self.api.Height = value

    @property
    def _text_range(self) -> DispatchBaseClass:
        return self.api.TextFrame.TextRange

    @property
    def text(self) -> str:
        return self._text_range.Text

    @text.setter
    def text(self, text: str) -> None:
        self._text_range.Text = text

    @property
    def font(self) -> Font:
        return Font(self._text_range.Font)

    @property
    def fill(self) -> Fill:
        return Fill(self.api.Fill)

    @property
    def line(self) -> Line:
        return Line(self.api.Line)

    def select(self, *, replace: bool = True) -> ShapeRange:
        self.api.Select(replace)
        api = self.app.api.ActiveWindow.Selection.ShapeRange
        return ShapeRange(api, self.parent, self.collection)

    def copy(self) -> None:
        self.api.Copy()

    def connect(self, shape: Shape, direction: str = "horizontal") -> Shape:
        shapes = self.collection
        return shapes.add_connector(self, shape, direction)

    def export(self, file_name: str | Path, fmt: str | int | None = None) -> None:
        if fmt is None:
            fmt = Path(file_name).suffix[1:]
        if isinstance(fmt, str):
            fmt = getattr(constants, f"ppShapeFormat{fmt.upper()}")
        self.api.Export(str(file_name), fmt)

    def png(self) -> bytes:
        with NamedTemporaryFile(suffix=".png", delete=False) as file:
            file_name = Path(file.name)

        self.export(file_name)
        data = file_name.read_bytes()
        file_name.unlink()
        return data

    def svg(self) -> str:
        with NamedTemporaryFile(suffix=".svg", delete=False) as file:
            file_name = Path(file.name)

        self.export(file_name)
        text = file_name.read_text()
        file_name.unlink()
        return text

    def align_center(self) -> Self:
        text_frame2 = self.api.TextFrame2
        text_frame2.VerticalAnchor = constants.msoAnchorMiddle
        paragraph_format = text_frame2.TextRange.ParagraphFormat
        paragraph_format.Alignment = constants.msoAlignCenter
        return self

    def text_margin(
        self,
        left: float = 0,
        top: float = 0,
        right: float | None = None,
        bottom: float | None = None,
    ) -> Self:
        text_frame2 = self.api.TextFrame2
        text_frame2.MarginLeft = left
        text_frame2.MarginTop = top
        text_frame2.MarginRight = left if right is None else right
        text_frame2.MarginBottom = top if bottom is None else bottom
        return self


@dataclass(repr=False)
class Shapes(Collection[Shape]):
    parent: Slide
    type: ClassVar[type[Element]] = Shape

    @property
    def title(self) -> Shape:
        return Shape(self.api.Title, self.parent, self)

    def add(
        self,
        kind: int | str,
        left: float,
        top: float,
        width: float,
        height: float,
        text: str = "",
    ) -> Shape:
        if isinstance(kind, str):
            kind = getattr(constants, f"msoShape{kind}")

        api = self.api.AddShape(kind, left, top, width, height)
        shape = Shape(api, self.parent, self)
        shape.text = text

        return shape

    def add_line(
        self,
        begin_x: float,
        begin_y: float,
        end_x: float,
        end_y: float,
    ) -> Shape:
        api = self.api.AddLine(begin_x, begin_y, end_x, end_y)
        return Shape(api, self.parent, self)

    def add_label(
        self,
        text: str,
        left: float,
        top: float,
        width: float = 72,
        height: float = 72,
        *,
        auto_size: bool = True,
    ) -> Shape:
        orientation = constants.msoTextOrientationHorizontal
        api = self.api.AddLabel(orientation, left, top, width, height)

        if auto_size is False:
            api.TextFrame.AutoSize = False

        label = Shape(api, self.parent, self)
        label.text = text
        return label

    def add_table(
        self,
        num_rows: int,
        num_columns: int,
        left: float = 100,
        top: float = 100,
        width: float = 100,
        height: float = 100,
    ) -> Table:
        from .table import Table

        api = self.api.AddTable(num_rows, num_columns, left, top, width, height)
        return Table(api, self.parent, self)

    def add_picture(
        self,
        file_name: str | Path,
        left: float = 0,
        top: float = 0,
        width: float = -1,
        height: float = -1,
        scale: float | None = None,
    ) -> Shape:
        file_name = Path(file_name).absolute()

        api = self.api.AddPicture(
            FileName=file_name,
            LinkToFile=False,
            SaveWithDocument=True,
            Left=left,
            Top=top,
            Width=width,
            Height=height,
        )

        if scale is not None:
            api.ScaleWidth(scale, 1)
            api.ScaleHeight(scale, 1)

        return Shape(api, self.parent, self)

    def add_image(
        self,
        image: Image,
        left: float = 0,
        top: float = 0,
        width: float = -1,
        height: float = -1,
        scale: float | None = None,
    ) -> Shape:
        with NamedTemporaryFile(suffix=".png", delete=False) as file:
            file_name = Path(file.name)

        image.save(file_name)
        shape = self.add_picture(file_name, left, top, width, height, scale)
        file_name.unlink()
        return shape

    def add_figure(
        self,
        fig: Figure,
        left: float = 0,
        top: float = 0,
        width: float = -1,
        height: float = -1,
        scale: float | None = None,
        dpi: int | Literal["figure"] = "figure",
        transparent: bool | None = None,
    ) -> Shape:
        with NamedTemporaryFile(suffix=".png", delete=False) as file:
            file_name = Path(file.name)

        fig.savefig(file_name, dpi=dpi, bbox_inches="tight", transparent=transparent)
        shape = self.add_picture(file_name, left, top, width, height, scale)
        file_name.unlink()
        return shape

    def add_connector(
        self,
        shape1: Shape,
        shape2: Shape,
        direction: str = "horizontal",
    ) -> Shape:
        if shape1.top + shape1.height / 2 == shape2.top + shape2.height / 2:
            connector_type = constants.msoConnectorStraight
            begin, end = (4, 2) if shape1.left < shape2.left else (2, 4)

        elif shape1.left + shape1.width / 2 == shape2.left + shape2.width / 2:
            connector_type = constants.msoConnectorStraight
            begin, end = (3, 1) if shape1.top < shape2.top else (1, 3)

        else:
            connector_type = constants.msoConnectorElbow
            if direction == "horizontal":
                begin, end = (4, 2) if shape1.left < shape2.left else (2, 4)
            else:
                begin, end = (3, 1) if shape1.top < shape2.top else (1, 3)

        if shape1.api.ConnectionSiteCount == 8:
            begin = 2 * begin - 1

        if shape2.api.ConnectionSiteCount == 8:
            end = 2 * end - 1

        api = self.api.AddConnector(connector_type, 1, 1, 2, 2)
        api.ConnectorFormat.BeginConnect(shape1.api, begin)
        api.ConnectorFormat.EndConnect(shape2.api, end)

        return Shape(api, self.parent, self)

    def paste(
        self,
        left: float | None = None,
        top: float | None = None,
        width: float | None = None,
        height: float | None = None,
    ) -> Shape:
        api = self.api.Paste()

        if left is not None:
            api.Left = left
        if top is not None:
            api.Top = top
        if width is not None:
            api.Width = width
        if height is not None:
            api.Height = height

        return Shape(api, self.parent, self)

    def paste_special(
        self,
        data_type: int | str = 0,
        left: float | None = None,
        top: float | None = None,
        width: float | None = None,
        height: float | None = None,
    ) -> Shape:
        """
        Args:
            data_type (int):
                0: ppPasteDefault
                1: ppPasteBitmap
                2: ppPasteEnhancedMetafile
                4: ppPasteGIF
                8: ppPasteHTML
                5: ppPasteJPG
                3: ppPasteMetafilePicture
                10: ppPasteOLEObject
                6: ppPastePNG
                9: ppPasteRTF
                11: ppPasteShape
                7: ppPasteText
        """
        if isinstance(data_type, str):
            data_type = getattr(constants, f"ppPaste{data_type}")

        api = self.api.PasteSpecial(data_type)

        if left is not None:
            api.Left = left
        if top is not None:
            api.Top = top
        if width is not None:
            api.Width = width
        if height is not None:
            api.Height = height

        return Shape(api, self.parent, self)

    def range(self, shapes: Iterable[Shape]) -> ShapeRange:
        names = [s.api.Name for s in shapes]
        return ShapeRange(self.api.Range(names), self.parent, self)


@dataclass(repr=False)
class ShapeRange(Shape):
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{self.api.Count}]>"

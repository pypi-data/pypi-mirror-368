from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, ClassVar

from win32com.client import constants

from .base import Collection, Element
from .shape import Shapes

if TYPE_CHECKING:
    from typing import Self

    from win32com.client import DispatchBaseClass

    from .presentation import Presentation


@dataclass(repr=False)
class Slide(Element):
    parent: Presentation
    collection: Slides

    @property
    def shapes(self) -> Shapes:
        return Shapes(self.api.Shapes, self)

    @property
    def title(self) -> str:
        return self.shapes.title.text if len(self.shapes) else ""

    @title.setter
    def title(self, text: str) -> None:
        if len(self.shapes):
            self.shapes.title.text = text

    @property
    def width(self) -> float:
        return self.parent.width

    @property
    def height(self) -> float:
        return self.parent.height

    def export(self, file_name: str | Path, fmt: str | None = None) -> None:
        if fmt is None:
            fmt = Path(file_name).suffix[1:]
        self.api.Export(str(file_name), fmt.upper())

    def png(self) -> bytes:
        with NamedTemporaryFile(suffix=".png", delete=False) as file:
            file_name = Path(file.name)

        self.export(file_name)
        data = file_name.read_bytes()
        file_name.unlink()
        return data

    @property
    def layout(self) -> Layout:
        return Layout(self.api.CustomLayout, self.parent, self.parent.layouts)

    @layout.setter
    def layout(self, layout: int | str | Layout) -> None:
        layout_ = self.parent.layouts._get_api(layout)  # noqa: SLF001
        if isinstance(layout_, int):
            self.api.Layout = layout_
        else:
            self.api.CustomLayout = layout_

    def set(
        self,
        title: str | None = None,
        layout: int | str | Layout | None = None,
    ) -> Self:
        if layout is not None:
            self.layout = layout

        if title is not None:
            self.title = title

        return self


@dataclass(repr=False)
class Layout(Slide):
    parent: Presentation
    collection: Layouts


@dataclass(repr=False)
class Slides(Collection[Slide]):
    parent: Presentation
    type: ClassVar[type[Element]] = Slide

    def add(
        self,
        index: int | None = None,
        layout: int | str | Layout | None = None,
    ) -> Slide:
        if index is None:
            index = len(self)

        if layout is None and index:
            layout_ = self[index - 1].api.CustomLayout
        else:
            layout_ = self.parent.layouts._get_api(layout)  # noqa: SLF001

        if isinstance(layout_, int):
            api = self.api.Add(index + 1, layout_)
        else:
            api = self.api.AddSlide(index + 1, layout_)

        return Slide(api, self.parent, self)

    @property
    def active(self) -> Slide:
        index = self.app.api.ActiveWindow.Selection.SlideRange.SlideIndex - 1
        return self[index]


@dataclass(repr=False)
class Layouts(Collection[Layout]):
    parent: Presentation
    type: ClassVar[type[Element]] = Layout

    def add(self, name: str, slide: Slide | None = None) -> Layout:
        if slide:
            slide.api.CustomLayout.Copy()
            api = self.api.Paste()
        else:
            api = self.api.Add(self.api.Count + 1)

        api.Name = name
        return Layout(api, self.parent, self)

    def get(self, name: str) -> Layout | None:
        for layout in self:
            if layout.name == name:
                return layout

        return None

    def _get_api(self, layout: int | str | Layout | None) -> int | DispatchBaseClass:
        if isinstance(layout, int):
            return layout

        if isinstance(layout, Layout):
            return layout.api  # type: ignore

        if isinstance(layout, str):
            if layout_ := self.get(layout):
                return layout_.api  # type: ignore
            return getattr(constants, f"ppLayout{layout}")

        return constants.ppLayoutTitleOnly

    def copy_from(self, slide: Slide, name: str) -> Layout:
        slide.api.CustomLayout.Copy()
        api = self.api.Paste()
        api.Name = name
        return Layout(api, self.parent, self)

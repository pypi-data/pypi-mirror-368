from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from .base import Collection, Element
from .slide import Layouts, Slides

if TYPE_CHECKING:
    from typing import Self

    from .app import App


@dataclass(repr=False)
class Presentation(Element):
    parent: App
    collection: Presentations

    def close(self) -> None:
        self.api.Close()

    def delete(self) -> None:
        self.close()

    def save(self, file_name: str | Path | None = None) -> None:
        if file_name is None:
            self.api.Save()
            return

        file_name = Path(file_name) if isinstance(file_name, str) else file_name
        file_name = str(file_name.absolute())
        self.api.SaveAs(FileName=file_name)

    @property
    def slides(self) -> Slides:
        return Slides(self.api.Slides, self)

    @property
    def width(self) -> float:
        return self.api.PageSetup.SlideWidth

    @width.setter
    def width(self, value: float) -> None:
        self.api.PageSetup.SlideWidth = value

    @property
    def height(self) -> float:
        return self.api.PageSetup.SlideHeight

    @height.setter
    def height(self, value: float) -> None:
        self.api.PageSetup.SlideHeight = value

    def size(self, width: float, height: float) -> Self:
        self.width = width
        self.height = height
        return self

    @property
    def layouts(self) -> Layouts:
        return Layouts(self.api.SlideMaster.CustomLayouts, self)


@dataclass(repr=False)
class Presentations(Collection[Presentation]):
    parent: App
    type: ClassVar[type[Element]] = Presentation

    def add(self, *, with_window: bool = True) -> Presentation:
        # When WithWindow is False, PowerPoint won't show a window for the presentation
        api = self.api.Add(WithWindow=with_window)
        return Presentation(api, self.parent, self)

    def open(
        self,
        file_name: str | Path,
        *,
        with_window: bool = True,
        read_only: bool = False,
    ) -> Presentation:
        """Open an existing presentation.

        PowerPoint Open signature:
        (FileName, ReadOnly=False, Untitled=False, WithWindow=True).
        Named arguments are used when available.
        """
        file_name = Path(file_name) if isinstance(file_name, str) else file_name
        file_name = str(file_name.absolute())

        api = self.api.Open(
            FileName=file_name,
            ReadOnly=read_only,
            WithWindow=with_window,
        )
        return Presentation(api, self.parent, self)

    def close(self) -> None:
        for pr in self:
            pr.close()

    @property
    def active(self) -> Presentation:
        api = self.app.api.ActivePresentation
        return Presentation(api, self.parent, self)

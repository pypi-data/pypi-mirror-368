from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from .compat import com_error

if TYPE_CHECKING:
    from collections.abc import Iterator

    from win32com.client import CoClassBaseClass, DispatchBaseClass

    from .app import App


@dataclass(repr=False)
class Base:
    api: DispatchBaseClass | CoClassBaseClass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


@dataclass(repr=False)
class Element(Base):
    parent: Element
    collection: Collection
    app: App = field(init=False)

    def __post_init__(self) -> None:
        self.app = self.parent.app

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{self.name}]>"

    @property
    def name(self) -> str:
        try:
            return self.api.Name
        except com_error:
            return ""

    @name.setter
    def name(self, value: str) -> None:
        self.api.Name = value

    def select(self) -> None:
        self.api.Select()

    def delete(self) -> None:
        self.api.Delete()


E = TypeVar("E", bound=Element)


@dataclass(repr=False)
class Collection(Base, Generic[E]):
    parent: Element
    type: ClassVar[type[Element]]
    app: App = field(init=False)

    def __post_init__(self) -> None:
        self.app = self.parent.app

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({len(self)})>"

    def __len__(self) -> int:
        return self.api.Count

    def __getitem__(self, index: int) -> E:
        if index < 0:
            index = len(self) + index

        return self.type(self.api(index + 1), self.parent, self)  # type: ignore

    def __iter__(self) -> Iterator[E]:
        yield from [self[index] for index in range(len(self))]  # list due to deletion

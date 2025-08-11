"""PowerPoint application interface module.

This module provides a high-level interface to interact with Microsoft PowerPoint
application through COM automation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache
from typing import TYPE_CHECKING, Self

import win32com.client
from win32com.client import constants

from .base import Base
from .client import ensure_modules
from .compat import com_error
from .presentation import Presentations

if TYPE_CHECKING:
    from win32com.client import DispatchBaseClass


@dataclass(repr=False)
class App(Base):
    """PowerPoint application interface.

    This class provides a high-level interface to interact with Microsoft PowerPoint
    application. It manages the PowerPoint application instance and provides access
    to presentations and other PowerPoint features.

    Attributes:
        api: The underlying PowerPoint COM object.
        app: Reference to self for consistency with PowerPoint's object model.
    """

    api: DispatchBaseClass = field(init=False)
    app: App = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the PowerPoint application instance."""
        ensure_modules()
        self.api = win32com.client.Dispatch("PowerPoint.Application")  # type: ignore
        self.app = self

    @property
    def presentations(self) -> Presentations:
        """Get the collection of presentations.

        Returns:
            Presentations: A collection of all open presentations.
        """
        return Presentations(self.api.Presentations, self)

    def quit(self) -> None:
        """Quit the PowerPoint application."""
        self.api.Quit()

    def __enter__(self) -> Self:
        """Context manager entry point.

        Returns:
            Self: The App instance.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # noqa: ANN001
        """Context manager exit point.

        Args:
            exc_type: The exception type if an exception was raised.
            exc_value: The exception value if an exception was raised.
            traceback: The traceback if an exception was raised.
        """
        self.quit()

    def unselect(self) -> None:
        """Unselect any selected objects in the active window."""
        self.api.ActiveWindow.Selection.Unselect()

    def minimize(self) -> None:
        """Minimize the PowerPoint main window.

        Note: PowerPoint does not allow hiding the application window via
        `Application.Visible = False`. Use this method to keep the UI out of the way.
        """
        self.api.WindowState = constants.ppWindowMinimized


@cache
def is_powerpoint_available() -> bool:
    """Check if PowerPoint application is available on the system.

    This function attempts to create a PowerPoint application instance to verify
    if PowerPoint is installed and accessible.

    Returns:
        bool: True if PowerPoint is available, False otherwise.
    """
    try:
        with App():
            pass
    except com_error:  # pragma: no cover
        return False

    return True

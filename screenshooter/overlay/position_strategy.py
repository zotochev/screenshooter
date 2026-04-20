from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor, QMouseEvent, QPainter


class PositionStrategy:
    """Base class for frame window positioning strategies."""

    @property
    def label(self) -> str:
        return ""

    @property
    def border_color(self) -> QColor:
        return QColor(255, 80, 80)

    def on_mouse_press(self, event: QMouseEvent) -> None:
        pass

    def on_mouse_move(self, event: QMouseEvent) -> None:
        pass

    def on_mouse_release(self, event: QMouseEvent) -> None:
        pass

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def paint(self, painter: QPainter, rect: QRect) -> bool:
        """Custom painting. Return True to skip default border drawing."""
        return False

    def on_capture_done(self) -> None:
        pass

    @property
    def capture_rect(self) -> QRect | None:
        """Override to capture a specific rect instead of the window's inner rect."""
        return None

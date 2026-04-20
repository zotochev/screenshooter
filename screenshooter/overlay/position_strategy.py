from PyQt6.QtGui import QColor, QMouseEvent


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

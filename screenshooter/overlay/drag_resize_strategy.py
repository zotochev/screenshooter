from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QColor, QMouseEvent
from PyQt6.QtWidgets import QWidget

from screenshooter.overlay.position_strategy import PositionStrategy
from screenshooter.overlay.resize_handle import Handle, CURSORS, hit_test, apply_resize


class DragResizeStrategy(PositionStrategy):
    def __init__(self, window: QWidget, initial_size: QSize) -> None:
        self._window = window
        self._target_size: QSize = initial_size
        self._drag_offset: QPoint = QPoint()
        self._resize_handle: Handle = Handle.NONE
        self._resize_start_pos: QPoint = QPoint()
        self._resize_start_geo: QRect = QRect()

    @property
    def label(self) -> str:
        return "Фикс"

    @property
    def border_color(self) -> QColor:
        return QColor(255, 80, 80)

    @property
    def target_size(self) -> QSize:
        return self._target_size

    def on_mouse_press(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        handle = hit_test(event.pos(), self._window.rect())
        if handle == Handle.NONE:
            self._drag_offset = event.pos()
        else:
            self._resize_handle = handle
            self._resize_start_pos = event.globalPosition().toPoint()
            self._resize_start_geo = self._window.geometry()

    def on_mouse_move(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.NoButton:
            self._window.setCursor(CURSORS[hit_test(event.pos(), self._window.rect())])
            return
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._resize_handle != Handle.NONE:
                delta = event.globalPosition().toPoint() - self._resize_start_pos
                self._window.setGeometry(
                    apply_resize(self._resize_handle, self._resize_start_geo, delta)
                )
            else:
                self._window.move(
                    self._window.mapToGlobal(event.pos()) - self._drag_offset
                )

    def activate(self) -> None:
        self._window.resize(self._target_size)

    def on_mouse_release(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._resize_handle = Handle.NONE
            self._target_size = self._window.size()

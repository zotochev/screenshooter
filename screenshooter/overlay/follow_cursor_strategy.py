from collections.abc import Callable

from PyQt6.QtCore import QObject, QPoint, QRect, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QMouseEvent
from PyQt6.QtWidgets import QApplication, QWidget

from screenshooter.hotkey.hotkey_manager import HotkeyManager
from screenshooter.overlay.position_strategy import PositionStrategy
from screenshooter.overlay.resize_handle import CURSORS, Handle, apply_resize, hit_test


FOLLOW_INTERVAL_MS = 16


class FollowCursorStrategy(QObject, PositionStrategy):
    capture_requested = pyqtSignal()

    def __init__(
        self,
        window: QWidget,
        hotkey_manager: HotkeyManager,
        is_paused: Callable[[], bool] = lambda: False,
    ) -> None:
        QObject.__init__(self)
        self._window = window
        self._is_paused = is_paused
        self._timer = QTimer(self)
        self._timer.setInterval(FOLLOW_INTERVAL_MS)
        self._timer.timeout.connect(self._tick)
        self._resize_handle: Handle = Handle.NONE
        self._resize_start_pos: QPoint = QPoint()
        self._resize_start_geo: QRect = QRect()

    @property
    def label(self) -> str:
        return "Курсор"

    @property
    def border_color(self) -> QColor:
        return QColor(80, 180, 255)

    def activate(self) -> None:
        self._timer.start()

    def deactivate(self) -> None:
        self._resize_handle = Handle.NONE
        self._timer.stop()

    def on_mouse_press(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            handle = hit_test(event.pos(), self._window.rect())
            if handle != Handle.NONE:
                self._resize_handle = handle
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geo = self._window.geometry()
        else:
            self.capture_requested.emit()

    def on_mouse_move(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._resize_handle != Handle.NONE:
                delta = event.globalPosition().toPoint() - self._resize_start_pos
                self._window.setGeometry(
                    apply_resize(self._resize_handle, self._resize_start_geo, delta)
                )
            return
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._window.setCursor(CURSORS[hit_test(event.pos(), self._window.rect())])
        else:
            self._window.setCursor(Qt.CursorShape.ArrowCursor)

    def on_mouse_release(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._resize_handle != Handle.NONE:
            self._resize_handle = Handle.NONE
            self._window.setCursor(Qt.CursorShape.ArrowCursor)

    def _tick(self) -> None:
        ctrl = bool(QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier)
        if ctrl or self._resize_handle != Handle.NONE or self._is_paused():
            return  # frozen while Ctrl held or resize drag in progress
        self._window.setCursor(Qt.CursorShape.ArrowCursor)
        pos = QCursor.pos()
        self._window.move(
            pos.x() - self._window.width() // 2,
            pos.y() - self._window.height() // 2,
        )

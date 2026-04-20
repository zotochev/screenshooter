from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QColor, QCursor, QMouseEvent
from PyQt6.QtWidgets import QApplication, QWidget

from screenshooter.overlay.position_strategy import PositionStrategy


POLL_INTERVAL_MS = 100


class FullscreenStrategy(QObject, PositionStrategy):
    def __init__(self, window: QWidget) -> None:
        QObject.__init__(self)
        self._window = window
        self._timer = QTimer(self)
        self._timer.setInterval(POLL_INTERVAL_MS)
        self._timer.timeout.connect(self._tick)

    @property
    def label(self) -> str:
        return "Экран"

    @property
    def border_color(self) -> QColor:
        return QColor(80, 220, 120)

    def activate(self) -> None:
        self._tick()
        self._timer.start()

    def deactivate(self) -> None:
        self._timer.stop()

    def on_mouse_press(self, event: QMouseEvent) -> None:
        pass

    def _tick(self) -> None:
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        self._window.setGeometry(screen.geometry())

from PyQt6.QtCore import QObject, QPoint, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QMouseEvent, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget

from screenshooter.overlay.position_strategy import PositionStrategy

_MIN_SIZE = 5
_BORDER = 2      # matches BORDER_WIDTH in frame_window
_RADIUS = 10     # matches drawRoundedRect radius in frame_window
_POLL_MS = 100


class SelectionStrategy(QObject, PositionStrategy):
    capture_requested = pyqtSignal()

    def __init__(self, window: QWidget) -> None:
        QObject.__init__(self)
        self._window = window
        self._state = "idle"  # idle | dragging | awaiting_second
        self._start = QPoint()
        self._end = QPoint()
        self._pending_capture_rect: QRect | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(_POLL_MS)
        self._timer.timeout.connect(self._tick)

    @property
    def label(self) -> str:
        return "Выделение"

    @property
    def border_color(self) -> QColor:
        return QColor(255, 160, 0)

    @property
    def capture_rect(self) -> QRect | None:
        return self._pending_capture_rect

    def activate(self) -> None:
        self._state = "idle"
        self._pending_capture_rect = None
        self._window.setCursor(Qt.CursorShape.CrossCursor)
        self._expand_to_screen()
        self._timer.start()

    def deactivate(self) -> None:
        self._timer.stop()
        self._window.setCursor(Qt.CursorShape.ArrowCursor)
        self._state = "idle"
        self._pending_capture_rect = None

    def on_capture_done(self) -> None:
        self._pending_capture_rect = None
        self._expand_to_screen()
        self._window.update()

    def on_mouse_press(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.globalPosition().toPoint()
        if self._state == "idle":
            self._start = pos
            self._end = pos
            self._state = "dragging"
            self._window.update()
        elif self._state == "awaiting_second":
            self._end = pos
            self._commit()

    def on_mouse_move(self, event: QMouseEvent) -> None:
        if self._state in ("dragging", "awaiting_second"):
            self._end = event.globalPosition().toPoint()
            self._window.update()

    def on_mouse_release(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._state != "dragging":
            return
        self._end = event.globalPosition().toPoint()
        if (self._end - self._start).manhattanLength() >= _MIN_SIZE:
            self._commit()
        else:
            self._state = "awaiting_second"
        self._window.update()

    def paint(self, painter: QPainter, rect: QRect) -> bool:
        if self._state == "idle":
            return True  # fully transparent, no border

        sel = self._sel_local()
        if sel and sel.width() >= _MIN_SIZE and sel.height() >= _MIN_SIZE:
            painter.setPen(QPen(self.border_color, _BORDER))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(
                sel.adjusted(_BORDER, _BORDER, -_BORDER, -_BORDER),
                _RADIUS, _RADIUS,
            )
        return True

    def _tick(self) -> None:
        if self._state != "idle":
            return
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if self._window.geometry() != screen.geometry():
            self._window.setGeometry(screen.geometry())

    def _expand_to_screen(self) -> None:
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        self._window.setGeometry(screen.geometry())

    def _sel_local(self) -> QRect | None:
        if self._state == "idle":
            return None
        wp = self._window.pos()
        return QRect(self._start - wp, self._end - wp).normalized()

    def _commit(self) -> None:
        sel = QRect(self._start, self._end).normalized()
        if sel.width() < _MIN_SIZE or sel.height() < _MIN_SIZE:
            self._state = "idle"
            self._window.update()
            return
        self._pending_capture_rect = sel
        self._state = "idle"
        self._window.update()
        self.capture_requested.emit()

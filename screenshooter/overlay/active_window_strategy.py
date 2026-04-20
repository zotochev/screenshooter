import ctypes
import ctypes.wintypes
from collections.abc import Callable

from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget

from screenshooter.overlay.position_strategy import PositionStrategy


_user32 = ctypes.windll.user32
_dwmapi = ctypes.windll.dwmapi
_DWMWA_EXTENDED_FRAME_BOUNDS = 9


class _RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def _get_visible_rect(hwnd: int) -> _RECT | None:
    rect = _RECT()
    if _dwmapi.DwmGetWindowAttribute(hwnd, _DWMWA_EXTENDED_FRAME_BOUNDS,
                                     ctypes.byref(rect), ctypes.sizeof(rect)) == 0:
        return rect
    if _user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return rect
    return None


def _dpi_ratio(hwnd: int) -> float:
    """Physical-to-logical ratio for the monitor that contains hwnd."""
    dpi = _user32.GetDpiForWindow(hwnd)
    return (dpi / 96.0) if dpi else 1.0


POLL_INTERVAL_MS = 100


class ActiveWindowStrategy(QObject, PositionStrategy):
    def __init__(
        self,
        window: QWidget,
        is_paused: Callable[[], bool] = lambda: False,
    ) -> None:
        QObject.__init__(self)
        self._window = window
        self._is_paused = is_paused
        self._timer = QTimer(self)
        self._timer.setInterval(POLL_INTERVAL_MS)
        self._timer.timeout.connect(self._tick)
        self._own_hwnds: set[int] = set()

    @property
    def label(self) -> str:
        return "Окно"

    @property
    def border_color(self) -> QColor:
        return QColor(255, 200, 0)

    def activate(self) -> None:
        self._own_hwnds = {int(self._window.winId())}
        self._timer.start()

    def deactivate(self) -> None:
        self._timer.stop()

    def register_hwnd(self, hwnd: int) -> None:
        self._own_hwnds.add(hwnd)

    def _tick(self) -> None:
        if self._is_paused():
            return
        hwnd = _user32.GetForegroundWindow()
        if not hwnd or hwnd in self._own_hwnds:
            return
        if _user32.IsIconic(hwnd):  # minimized
            return
        rect = _get_visible_rect(hwnd)
        if rect is None:
            return
        ratio = _dpi_ratio(hwnd)
        x = round(rect.left / ratio)
        y = round(rect.top / ratio)
        w = round((rect.right - rect.left) / ratio)
        h = round((rect.bottom - rect.top) / ratio)
        if w <= 0 or h <= 0:
            return
        self._window.setGeometry(x, y, w, h)

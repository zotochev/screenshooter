from PyQt6.QtCore import QObject, QTimer, pyqtSlot
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget


class BorderFlash(QObject):
    """Temporarily overrides border color when a screenshot is taken."""

    FLASH_COLOR = QColor(255, 255, 255)
    DURATION_MS = 150

    def __init__(self, widget: QWidget) -> None:
        super().__init__(widget)
        self._widget = widget
        self._active = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(self.DURATION_MS)
        self._timer.timeout.connect(self._end)

    @pyqtSlot()
    def flash(self) -> None:
        self._active = True
        self._widget.update()
        self._timer.start()

    @property
    def is_active(self) -> bool:
        return self._active

    def _end(self) -> None:
        self._active = False
        self._widget.update()

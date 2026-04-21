from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QKeyEvent, QPainter
from PyQt6.QtWidgets import QApplication, QWidget

from screenshooter.locale import tr


_MODIFIERS = {
    Qt.Key.Key_Shift, Qt.Key.Key_Control,
    Qt.Key.Key_Alt, Qt.Key.Key_Meta,
    Qt.Key.Key_AltGr, Qt.Key.Key_CapsLock,
}


class KeyCaptureDialog(QWidget):
    key_captured = pyqtSignal(int)  # Qt.Key value

    def __init__(self) -> None:
        super().__init__()
        self._setup_window()

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 90)

    def show_and_capture(self) -> None:
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2,
        )
        self.show()
        self.activateWindow()
        self.setFocus()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(30, 30, 30, 240))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, tr("press_key"))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = Qt.Key(event.key())
        if key == Qt.Key.Key_Escape:
            self.hide()
            return
        if key in _MODIFIERS:
            return
        self.hide()
        self.key_captured.emit(int(key))

    def focusOutEvent(self, event) -> None:
        self.hide()

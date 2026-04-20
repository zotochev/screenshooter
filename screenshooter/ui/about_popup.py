from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QWidget

from screenshooter.ui.steering_wheel import COLOR_SEGMENT, COLOR_TEXT, OUTER_RADIUS
from screenshooter.win_border import remove_dwm_border

_SIDE = (OUTER_RADIUS + 6) * 2


class AboutPopup(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(_SIDE, _SIDE)

    def show_at(self, pos: QPointF) -> None:
        self.move(int(pos.x()) - _SIDE // 2, int(pos.y()) - _SIDE // 2)
        self.show()
        remove_dwm_border(int(self.winId()))
        self.grabMouse()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = _SIDE / 2, _SIDE / 2

        painter.setBrush(COLOR_SEGMENT)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), float(OUTER_RADIUS), float(OUTER_RADIUS))

        painter.setPen(COLOR_TEXT)

        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(
            QRectF(cx - OUTER_RADIUS, cy - 30, OUTER_RADIUS * 2, 36),
            Qt.AlignmentFlag.AlignCenter,
            "Screenshooter",
        )

        version_font = QFont()
        version_font.setPointSize(10)
        painter.setFont(version_font)
        painter.setPen(QColor(180, 180, 180))
        painter.drawText(
            QRectF(cx - OUTER_RADIUS, cy + 12, OUTER_RADIUS * 2, 24),
            Qt.AlignmentFlag.AlignCenter,
            "v 0.1.0",
        )

    def mousePressEvent(self, event) -> None:
        self.releaseMouse()
        self.hide()

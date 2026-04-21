from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QDesktopServices, QFont, QPainter
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QWidget

from screenshooter.locale import tr
from screenshooter.ui.steering_wheel import COLOR_SEGMENT, COLOR_TEXT, OUTER_RADIUS
from screenshooter.win_border import remove_dwm_border

_SIDE = (OUTER_RADIUS + 6) * 2
_REPO_URL = "https://github.com/zotochev/screenshooter"
_LINK_COLOR = QColor(100, 180, 255)


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

    def _link_rect(self, cx: float, cy: float) -> QRectF:
        return QRectF(cx - OUTER_RADIUS, cy + 34, OUTER_RADIUS * 2, 24)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = _SIDE / 2, _SIDE / 2

        painter.setBrush(COLOR_SEGMENT)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), float(OUTER_RADIUS), float(OUTER_RADIUS))

        painter.setPen(COLOR_TEXT)

        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(
            QRectF(cx - OUTER_RADIUS, cy - 52, OUTER_RADIUS * 2, 32),
            Qt.AlignmentFlag.AlignCenter,
            "Screenshooter",
        )

        ver_font = QFont()
        ver_font.setPointSize(9)
        painter.setFont(ver_font)
        painter.setPen(QColor(160, 160, 160))
        painter.drawText(
            QRectF(cx - OUTER_RADIUS, cy - 18, OUTER_RADIUS * 2, 20),
            Qt.AlignmentFlag.AlignCenter,
            "v 0.1.0",
        )

        desc_font = QFont()
        desc_font.setPointSize(9)
        painter.setFont(desc_font)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(
            QRectF(cx - OUTER_RADIUS, cy + 8, OUTER_RADIUS * 2, 20),
            Qt.AlignmentFlag.AlignCenter,
            tr("app_description"),
        )

        link_font = QFont()
        link_font.setPointSize(9)
        link_font.setUnderline(True)
        painter.setFont(link_font)
        painter.setPen(_LINK_COLOR)
        painter.drawText(
            self._link_rect(cx, cy),
            Qt.AlignmentFlag.AlignCenter,
            tr("repo"),
        )

    def mousePressEvent(self, event) -> None:
        cx, cy = _SIDE / 2, _SIDE / 2
        if self._link_rect(cx, cy).contains(QPointF(event.pos())):
            QDesktopServices.openUrl(QUrl(_REPO_URL))
        self.releaseMouse()
        self.hide()

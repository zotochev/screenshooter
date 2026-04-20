import math
from collections.abc import Callable
from dataclasses import dataclass, field

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath
from PyQt6.QtWidgets import QWidget

from screenshooter.win_border import remove_dwm_border


OUTER_RADIUS = 110
INNER_RADIUS = 32
SEGMENT_GAP_DEG = 3
ARC_STEPS = 48

COLOR_SEGMENT = QColor(45, 45, 45, 230)
COLOR_SEGMENT_HOVER = QColor(255, 80, 80, 230)
COLOR_CENTER = QColor(30, 30, 30, 230)
COLOR_TEXT = QColor(255, 255, 255)


@dataclass
class WheelSegment:
    label: str | Callable[[], str]
    callback: Callable[[], None] = field(default=lambda: None)

    def get_label(self) -> str:
        return self.label() if callable(self.label) else self.label


class SteeringWheel(QWidget):
    def __init__(self, segments: list[WheelSegment]) -> None:
        super().__init__()
        self._segments = segments
        self._hovered: int | None = None
        self._setup_window()

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        side = (OUTER_RADIUS + 6) * 2
        self.setFixedSize(side, side)

    def show_at(self, global_pos: QPointF) -> None:
        self.move(
            int(global_pos.x()) - self.width() // 2,
            int(global_pos.y()) - self.height() // 2,
        )
        self._hovered = None
        self.show()
        remove_dwm_border(int(self.winId()))
        self.grabMouse()

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _center(self) -> QPointF:
        return QPointF(self.width() / 2.0, self.height() / 2.0)

    def _point_on_circle(self, radius: float, angle_rad: float) -> QPointF:
        """angle_rad: 0 = top (12 o'clock), increasing clockwise."""
        c = self._center()
        return QPointF(
            c.x() + radius * math.sin(angle_rad),
            c.y() - radius * math.cos(angle_rad),
        )

    def _segment_angles(self, index: int) -> tuple[float, float]:
        n = len(self._segments)
        step = 2 * math.pi / n
        center = index * step
        half = step / 2 - math.radians(SEGMENT_GAP_DEG / 2)
        return center - half, center + half

    def _segment_at(self, pos: QPointF) -> int | None:
        c = self._center()
        dx, dy = pos.x() - c.x(), pos.y() - c.y()
        dist = math.hypot(dx, dy)
        if dist < INNER_RADIUS or dist > OUTER_RADIUS:
            return None

        # angle: 0 = top, increasing CW
        angle = math.atan2(dx, -dy) % (2 * math.pi)

        n = len(self._segments)
        step = 2 * math.pi / n
        # Offset by half step so segment i is centered at i*step, not starting at i*step
        index = int((angle + step / 2) % (2 * math.pi) / step) % n
        return index

    def _build_segment_path(self, index: int) -> QPainterPath:
        start, end = self._segment_angles(index)
        path = QPainterPath()

        path.moveTo(self._point_on_circle(INNER_RADIUS, start))
        path.lineTo(self._point_on_circle(OUTER_RADIUS, start))

        for i in range(1, ARC_STEPS + 1):
            t = start + (end - start) * i / ARC_STEPS
            path.lineTo(self._point_on_circle(OUTER_RADIUS, t))

        path.lineTo(self._point_on_circle(INNER_RADIUS, end))

        for i in range(ARC_STEPS - 1, -1, -1):
            t = start + (end - start) * i / ARC_STEPS
            path.lineTo(self._point_on_circle(INNER_RADIUS, t))

        path.closeSubpath()
        return path

    # ------------------------------------------------------------------
    # Qt events
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for i, segment in enumerate(self._segments):
            path = self._build_segment_path(i)
            painter.setBrush(COLOR_SEGMENT_HOVER if i == self._hovered else COLOR_SEGMENT)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)

            start, end = self._segment_angles(i)
            mid = (start + end) / 2
            label_r = (INNER_RADIUS + OUTER_RADIUS) / 2
            lp = self._point_on_circle(label_r, mid)
            painter.setPen(COLOR_TEXT)
            painter.drawText(
                int(lp.x() - 40), int(lp.y() - 16), 80, 32,
                Qt.AlignmentFlag.AlignCenter,
                segment.get_label(),
            )

        painter.setBrush(COLOR_CENTER)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self._center(), float(INNER_RADIUS - 2), float(INNER_RADIUS - 2))

    def mouseMoveEvent(self, event) -> None:
        # With grabMouse, pos may be outside widget bounds — convert via global position
        local = self.mapFromGlobal(event.globalPosition().toPoint())
        hovered = self._segment_at(QPointF(local))
        if hovered != self._hovered:
            self._hovered = hovered
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self._dismiss(activate=True)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._dismiss(activate=False)

    def _dismiss(self, activate: bool) -> None:
        self.releaseMouse()
        self.hide()
        if activate and self._hovered is not None:
            self._segments[self._hovered].callback()
        self._hovered = None


class SubWheel(SteeringWheel):
    """Sub-wheel with left-click confirmation and center-click to go back."""

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        local = self.mapFromGlobal(event.globalPosition().toPoint())
        seg = self._segment_at(QPointF(local))
        if seg is None:
            self._dismiss(activate=False)
        else:
            self._hovered = seg
            self._dismiss(activate=True)

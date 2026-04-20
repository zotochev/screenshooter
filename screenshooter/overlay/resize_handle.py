from enum import Enum, auto

from PyQt6.QtCore import Qt, QPoint, QRect


HANDLE_SIZE = 8
MIN_SIZE = 50


class Handle(Enum):
    NONE = auto()
    TOP_LEFT = auto()
    TOP = auto()
    TOP_RIGHT = auto()
    RIGHT = auto()
    BOTTOM_RIGHT = auto()
    BOTTOM = auto()
    BOTTOM_LEFT = auto()
    LEFT = auto()


CURSORS: dict[Handle, Qt.CursorShape] = {
    Handle.TOP_LEFT: Qt.CursorShape.SizeFDiagCursor,
    Handle.TOP: Qt.CursorShape.SizeVerCursor,
    Handle.TOP_RIGHT: Qt.CursorShape.SizeBDiagCursor,
    Handle.RIGHT: Qt.CursorShape.SizeHorCursor,
    Handle.BOTTOM_RIGHT: Qt.CursorShape.SizeFDiagCursor,
    Handle.BOTTOM: Qt.CursorShape.SizeVerCursor,
    Handle.BOTTOM_LEFT: Qt.CursorShape.SizeBDiagCursor,
    Handle.LEFT: Qt.CursorShape.SizeHorCursor,
    Handle.NONE: Qt.CursorShape.ArrowCursor,
}


def hit_test(pos: QPoint, rect: QRect) -> Handle:
    x, y = pos.x(), pos.y()
    w, h = rect.width(), rect.height()
    s = HANDLE_SIZE

    on_left = x < s
    on_right = x >= w - s
    on_top = y < s
    on_bottom = y >= h - s

    if on_top and on_left:
        return Handle.TOP_LEFT
    if on_top and on_right:
        return Handle.TOP_RIGHT
    if on_bottom and on_left:
        return Handle.BOTTOM_LEFT
    if on_bottom and on_right:
        return Handle.BOTTOM_RIGHT
    if on_top:
        return Handle.TOP
    if on_bottom:
        return Handle.BOTTOM
    if on_left:
        return Handle.LEFT
    if on_right:
        return Handle.RIGHT
    return Handle.NONE


def apply_resize(handle: Handle, geo: QRect, delta: QPoint) -> QRect:
    x, y, w, h = geo.x(), geo.y(), geo.width(), geo.height()
    dx, dy = delta.x(), delta.y()

    if handle in (Handle.TOP_LEFT, Handle.LEFT, Handle.BOTTOM_LEFT):
        new_w = max(MIN_SIZE, w - dx)
        x = x + w - new_w
        w = new_w
    if handle in (Handle.TOP_RIGHT, Handle.RIGHT, Handle.BOTTOM_RIGHT):
        w = max(MIN_SIZE, w + dx)
    if handle in (Handle.TOP_LEFT, Handle.TOP, Handle.TOP_RIGHT):
        new_h = max(MIN_SIZE, h - dy)
        y = y + h - new_h
        h = new_h
    if handle in (Handle.BOTTOM_LEFT, Handle.BOTTOM, Handle.BOTTOM_RIGHT):
        h = max(MIN_SIZE, h + dy)

    return QRect(x, y, w, h)

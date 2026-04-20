import ctypes


class _Margins(ctypes.Structure):
    _fields_ = [("l", ctypes.c_int), ("r", ctypes.c_int), ("t", ctypes.c_int), ("b", ctypes.c_int)]


_DWMWA_BORDER_COLOR = 34
_DWMAPI_COLOR_NONE = 0xFFFFFFFE  # Windows 11: remove the accent border entirely


def remove_dwm_border(hwnd: int) -> None:
    dwmapi = ctypes.windll.dwmapi

    # Remove DWM glass frame
    margins = _Margins(-1, -1, -1, -1)
    dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))

    # Remove Windows 11 colored window border
    color = ctypes.c_int(_DWMAPI_COLOR_NONE)
    dwmapi.DwmSetWindowAttribute(hwnd, _DWMWA_BORDER_COLOR, ctypes.byref(color), ctypes.sizeof(color))

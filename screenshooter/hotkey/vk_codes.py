from PyQt6.QtCore import Qt


# Qt key values for A-Z and 0-9 match Win32 VK codes directly
QT_KEY_TO_VK: dict[Qt.Key, int] = {
    Qt.Key.Key_Escape:      0x1B,
    Qt.Key.Key_Print:       0x2C,
    Qt.Key.Key_ScrollLock:  0x91,
    Qt.Key.Key_Pause:       0x13,
    Qt.Key.Key_Insert:      0x2D,
    Qt.Key.Key_Delete:      0x2E,
    Qt.Key.Key_Home:        0x24,
    Qt.Key.Key_End:         0x23,
    Qt.Key.Key_PageUp:      0x21,
    Qt.Key.Key_PageDown:    0x22,
    Qt.Key.Key_F1:          0x70,
    Qt.Key.Key_F2:          0x71,
    Qt.Key.Key_F3:          0x72,
    Qt.Key.Key_F4:          0x73,
    Qt.Key.Key_F5:          0x74,
    Qt.Key.Key_F6:          0x75,
    Qt.Key.Key_F7:          0x76,
    Qt.Key.Key_F8:          0x77,
    Qt.Key.Key_F9:          0x78,
    Qt.Key.Key_F10:         0x79,
    Qt.Key.Key_F11:         0x7A,
    Qt.Key.Key_F12:         0x7B,
}

# Letters A-Z and digits 0-9: Qt key value == Win32 VK code
for _code in range(ord("A"), ord("Z") + 1):
    QT_KEY_TO_VK[Qt.Key(_code)] = _code
for _code in range(ord("0"), ord("9") + 1):
    QT_KEY_TO_VK[Qt.Key(_code)] = _code


_KEY_NAMES: dict[Qt.Key, str] = {
    Qt.Key.Key_Print:      "PrtScr",
    Qt.Key.Key_ScrollLock: "ScrLk",
    Qt.Key.Key_Pause:      "Pause",
    Qt.Key.Key_Insert:     "Ins",
    Qt.Key.Key_Delete:     "Del",
    Qt.Key.Key_Home:       "Home",
    Qt.Key.Key_End:        "End",
    Qt.Key.Key_PageUp:     "PgUp",
    Qt.Key.Key_PageDown:   "PgDn",
    **{Qt.Key[f"Key_F{i}"]: f"F{i}" for i in range(1, 13)},
}


def key_display_name(qt_key: Qt.Key) -> str:
    if qt_key in _KEY_NAMES:
        return _KEY_NAMES[qt_key]
    value = int(qt_key)
    if ord("A") <= value <= ord("Z"):
        return chr(value)
    if ord("0") <= value <= ord("9"):
        return chr(value)
    return f"0x{value:X}"

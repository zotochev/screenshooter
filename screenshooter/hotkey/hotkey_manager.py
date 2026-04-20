import ctypes
import ctypes.wintypes
from collections.abc import Callable

from PyQt6.QtCore import QAbstractNativeEventFilter
from PyQt6.QtWidgets import QApplication


WM_HOTKEY = 0x0312
_user32 = ctypes.windll.user32


class HotkeyManager(QAbstractNativeEventFilter):
    """Registers global hotkeys via Win32 RegisterHotKey and dispatches callbacks."""

    def __init__(self) -> None:
        super().__init__()
        self._hotkeys: dict[int, Callable[[], None]] = {}
        self._next_id: int = 1
        QApplication.instance().installNativeEventFilter(self)

    def register(self, vk: int, modifiers: int, callback: Callable[[], None]) -> int:
        hotkey_id = self._next_id
        self._next_id += 1
        _user32.RegisterHotKey(None, hotkey_id, modifiers, vk)
        self._hotkeys[hotkey_id] = callback
        return hotkey_id

    def unregister(self, hotkey_id: int) -> None:
        _user32.UnregisterHotKey(None, hotkey_id)
        self._hotkeys.pop(hotkey_id, None)

    def unregister_all(self) -> None:
        for hotkey_id in list(self._hotkeys):
            self.unregister(hotkey_id)

    def nativeEventFilter(self, event_type: bytes, message: int) -> tuple[bool, int]:
        msg = ctypes.wintypes.MSG.from_address(int(message))
        if msg.message == WM_HOTKEY:
            callback = self._hotkeys.get(msg.wParam)
            if callback:
                callback()
        return False, 0

import ctypes
import sys

from PyQt6.QtWidgets import QApplication

from screenshooter.hotkey.hotkey_manager import HotkeyManager
from screenshooter.locale import set_language
from screenshooter.overlay.frame_window import FrameWindow
from screenshooter.settings import storage

_MUTEX_NAME = "screenshooter-single-instance"
_ERROR_ALREADY_EXISTS = 183


def _acquire_instance_lock() -> bool:
    """Returns False if another instance is already running."""
    ctypes.windll.kernel32.CreateMutexW(None, True, _MUTEX_NAME)
    return ctypes.windll.kernel32.GetLastError() != _ERROR_ALREADY_EXISTS


def main() -> None:
    if not _acquire_instance_lock():
        sys.exit(0)

    config = storage.load()
    set_language(config.language)

    app = QApplication(sys.argv)
    hotkey_manager = HotkeyManager()
    window = FrameWindow(hotkey_manager, config)
    window.show()

    exit_code = app.exec()
    storage.save(config)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

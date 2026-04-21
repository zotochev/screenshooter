import sys

from PyQt6.QtWidgets import QApplication

from screenshooter.hotkey.hotkey_manager import HotkeyManager
from screenshooter.locale import set_language
from screenshooter.overlay.frame_window import FrameWindow
from screenshooter.settings import storage


def main() -> None:
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

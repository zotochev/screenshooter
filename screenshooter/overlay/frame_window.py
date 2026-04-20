from pathlib import Path

from PyQt6.QtCore import Qt, QRect, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget

from screenshooter.capture.capturer import capture
from screenshooter.hotkey.hotkey_manager import HotkeyManager
from screenshooter.overlay.border_flash import BorderFlash
from screenshooter.hotkey.vk_codes import QT_KEY_TO_VK, key_display_name
from screenshooter.overlay.active_window_strategy import ActiveWindowStrategy
from screenshooter.overlay.drag_resize_strategy import DragResizeStrategy
from screenshooter.overlay.follow_cursor_strategy import FollowCursorStrategy
from screenshooter.overlay.fullscreen_strategy import FullscreenStrategy
from screenshooter.overlay.position_strategy import PositionStrategy
from screenshooter.overlay.selection_strategy import SelectionStrategy
from screenshooter.settings.config import Config
from screenshooter.win_border import remove_dwm_border
from screenshooter.ui.format_wheel import FormatWheel
from screenshooter.ui.key_capture_dialog import KeyCaptureDialog
from screenshooter.ui.main_wheel import MainWheel
from screenshooter.ui.mode_wheel import ModeWheel
from screenshooter.ui.settings_wheel import SettingsWheel


BORDER_WIDTH = 2
INITIAL_SIZE = QSize(400, 300)
DEFAULT_CAPTURE_KEY = Qt.Key.Key_F9


class FrameWindow(QWidget):
    captured = pyqtSignal()

    def __init__(self, hotkey_manager: HotkeyManager, config: Config) -> None:
        super().__init__()
        self._hotkey_manager = hotkey_manager
        self._config = config
        self._capture_hotkey_id: int | None = None
        self._exit_hotkey_id: int | None = None
        self._toggle_hotkey_id: int | None = None

        follow = FollowCursorStrategy(self, hotkey_manager, is_paused=self._is_wheel_visible)
        follow.capture_requested.connect(self._capture)
        self._active_window_strategy = ActiveWindowStrategy(self, is_paused=self._is_wheel_visible)
        selection = SelectionStrategy(self)
        selection.capture_requested.connect(self._capture)
        self._strategies: list[PositionStrategy] = [
            DragResizeStrategy(self, INITIAL_SIZE),
            follow,
            FullscreenStrategy(self),
            self._active_window_strategy,
            selection,
        ]
        self._strategy_index: int = 0
        self._strategy: PositionStrategy = self._strategies[0]

        self._key_dialog = KeyCaptureDialog()
        self._key_dialog.key_captured.connect(self._on_key_captured)

        self._toggle_key_dialog = KeyCaptureDialog()
        self._toggle_key_dialog.key_captured.connect(self._on_toggle_key_captured)

        self._border_flash = BorderFlash(self)
        self.captured.connect(self._border_flash.flash)

        format_wheel = FormatWheel(config)
        settings_wheel = SettingsWheel(
            format_wheel=format_wheel,
            on_pick_folder=self._pick_output_dir,
            on_capture_key=self._show_key_capture,
            on_toggle_key=self._show_toggle_key_capture,
            current_key_label=lambda: f"Снять: {self._config.capture_key_name}",
            current_toggle_key_label=lambda: f"Скрыть: {self._config.toggle_key_name}",
            current_format_label=lambda: self._config.format.upper(),
        )
        mode_wheel = ModeWheel(
            labels=[s.label for s in self._strategies],
            get_current_index=lambda: self._strategy_index,
            on_select=self._select_strategy,
        )
        self._wheel = MainWheel(
            settings_wheel=settings_wheel,
            mode_wheel=mode_wheel,
            on_open_folder=self._open_output_dir,
            on_capture=self._capture,
            on_minimize=self.hide,
        )
        self._setup_window()
        self._setup_tray()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_tray(self) -> None:
        self._tray = QSystemTrayIcon(self._make_tray_icon(), self)
        self._tray.setToolTip("Screenshooter")

        menu = QMenu()
        menu.addAction("Показать / Скрыть", self._toggle_visibility)
        menu.addSeparator()
        menu.addAction("Выход", self._quit)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    @staticmethod
    def _make_tray_icon() -> QIcon:
        px = QPixmap(32, 32)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(255, 80, 80), 3))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(3, 3, 26, 26, 3, 3)
        p.end()
        return QIcon(px)

    def _toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_visibility()

    def _quit(self) -> None:
        self._strategy.deactivate()
        for hotkey_id in (self._capture_hotkey_id, self._exit_hotkey_id, self._toggle_hotkey_id):
            if hotkey_id is not None:
                self._hotkey_manager.unregister(hotkey_id)
        self._tray.hide()
        QApplication.quit()

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.resize(INITIAL_SIZE)

        capture_key = Qt.Key(self._config.capture_key_code)
        vk = QT_KEY_TO_VK.get(capture_key, QT_KEY_TO_VK[DEFAULT_CAPTURE_KEY])
        self._capture_hotkey_id = self._hotkey_manager.register(vk, 0, self._capture)
        self._exit_hotkey_id = self._hotkey_manager.register(
            QT_KEY_TO_VK[Qt.Key.Key_Escape], 0, self.close
        )
        toggle_key = Qt.Key(self._config.toggle_key_code)
        if toggle_key in QT_KEY_TO_VK:
            self._toggle_hotkey_id = self._hotkey_manager.register(
                QT_KEY_TO_VK[toggle_key], 0, self._toggle_visibility
            )

    # ------------------------------------------------------------------
    # Qt events
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fill interior with alpha=1 so Windows registers mouse hits on transparent area
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))

        if self._strategy.paint(painter, self.rect()):
            return

        border = BorderFlash.FLASH_COLOR if self._border_flash.is_active else self._strategy.border_color
        painter.setPen(QPen(border, BORDER_WIDTH))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            self.rect().adjusted(BORDER_WIDTH, BORDER_WIDTH, -BORDER_WIDTH, -BORDER_WIDTH),
            10, 10,
        )

    def showEvent(self, event) -> None:
        super().showEvent(event)
        remove_dwm_border(int(self.winId()))
        self._active_window_strategy.register_hwnd(int(self.winId()))
        if handle := self.windowHandle():
            handle.screenChanged.connect(self._on_screen_changed)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self._wheel.show_at(event.globalPosition())
            return
        self._strategy.on_mouse_press(event)

    def mouseMoveEvent(self, event) -> None:
        self._strategy.on_mouse_move(event)

    def mouseReleaseEvent(self, event) -> None:
        self._strategy.on_mouse_release(event)

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()

    # ------------------------------------------------------------------
    # Strategy
    # ------------------------------------------------------------------

    def _is_wheel_visible(self) -> bool:
        return self._wheel.isVisible()

    def _select_strategy(self, index: int) -> None:
        if index == self._strategy_index:
            return
        prev = self._strategy
        self._strategy.deactivate()
        self._strategy_index = index
        self._strategy = self._strategies[index]
        if isinstance(prev, FullscreenStrategy) and not isinstance(self._strategy, FullscreenStrategy):
            if isinstance(self._strategy, DragResizeStrategy):
                self._strategy._target_size = INITIAL_SIZE
            else:
                self.resize(INITIAL_SIZE)
        self._strategy.activate()
        self.update()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _show_key_capture(self) -> None:
        QTimer.singleShot(0, self._key_dialog.show_and_capture)

    def _on_key_captured(self, key_code: int) -> None:
        qt_key = Qt.Key(key_code)
        if qt_key not in QT_KEY_TO_VK:
            return
        if self._capture_hotkey_id is not None:
            self._hotkey_manager.unregister(self._capture_hotkey_id)
        vk = QT_KEY_TO_VK[qt_key]
        self._capture_hotkey_id = self._hotkey_manager.register(vk, 0, self._capture)
        self._config.capture_key_code = key_code
        self._config.capture_key_name = key_display_name(qt_key)

    def _show_toggle_key_capture(self) -> None:
        QTimer.singleShot(0, self._toggle_key_dialog.show_and_capture)

    def _on_toggle_key_captured(self, key_code: int) -> None:
        qt_key = Qt.Key(key_code)
        if qt_key not in QT_KEY_TO_VK:
            return
        if self._toggle_hotkey_id is not None:
            self._hotkey_manager.unregister(self._toggle_hotkey_id)
        vk = QT_KEY_TO_VK[qt_key]
        self._toggle_hotkey_id = self._hotkey_manager.register(vk, 0, self._toggle_visibility)
        self._config.toggle_key_code = key_code
        self._config.toggle_key_name = key_display_name(qt_key)

    def _open_output_dir(self) -> None:
        import subprocess
        self._config.output_dir.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer", str(self._config.output_dir)])

    def _pick_output_dir(self) -> None:
        from PyQt6.QtWidgets import QFileDialog
        chosen = QFileDialog.getExistingDirectory(
            self,
            "Папка для скриншотов",
            str(self._config.output_dir),
        )
        if chosen:
            self._config.output_dir = Path(chosen)

    def _on_screen_changed(self, _screen) -> None:
        # Qt rescales the window when crossing monitor boundaries — restore intended size
        drag = self._strategies[0]
        QTimer.singleShot(0, lambda: self.resize(drag.target_size))

    def _capture(self) -> None:
        inner = self._strategy.capture_rect or self.geometry().adjusted(
            BORDER_WIDTH, BORDER_WIDTH, -BORDER_WIDTH, -BORDER_WIDTH
        )
        self.hide()
        # Give the OS a frame to repaint the area under the window before grabbing
        QTimer.singleShot(50, lambda: self._do_capture(inner))

    def _do_capture(self, rect: QRect) -> None:
        path = capture(rect, self._config)
        self.show()
        self.captured.emit()
        self._strategy.on_capture_done()
        print(f"Saved: {path}")

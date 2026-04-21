from collections.abc import Callable

from PyQt6.QtGui import QCursor

from screenshooter.locale import tr
from screenshooter.ui.mode_wheel import ModeWheel
from screenshooter.ui.settings_wheel import SettingsWheel
from screenshooter.ui.steering_wheel import SteeringWheel, WheelSegment


class MainWheel(SteeringWheel):
    def __init__(
        self,
        settings_wheel: SettingsWheel,
        mode_wheel: ModeWheel,
        on_open_folder: Callable[[], None],
        on_capture: Callable[[], None],
        on_minimize: Callable[[], None],
        capture_key_label: Callable[[], str] = lambda: "",
        minimize_key_label: Callable[[], str] = lambda: "",
    ) -> None:
        self._settings_wheel = settings_wheel
        self._mode_wheel = mode_wheel
        self._on_open_folder = on_open_folder
        self._on_capture = on_capture
        self._on_minimize = on_minimize
        self._capture_key_label = capture_key_label
        self._minimize_key_label = minimize_key_label
        super().__init__(self._build_segments())

    def _build_segments(self) -> list[WheelSegment]:
        return [
            WheelSegment(lambda: tr("settings"), self._show_settings_wheel),
            WheelSegment(lambda: tr("mode"), self._show_mode_wheel),
            WheelSegment(lambda: f"{tr('capture')}\n{self._capture_key_label()}", self._on_capture),
            WheelSegment(lambda: tr("open"), self._on_open_folder),
            WheelSegment(lambda: f"{tr('minimize')}\n{self._minimize_key_label()}", self._on_minimize),
        ]

    def _show_settings_wheel(self) -> None:
        self._settings_wheel.show_at(QCursor.pos())

    def _show_mode_wheel(self) -> None:
        self._mode_wheel.show_at(QCursor.pos())

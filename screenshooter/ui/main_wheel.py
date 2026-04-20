from collections.abc import Callable

from PyQt6.QtGui import QCursor

from screenshooter.ui.settings_wheel import SettingsWheel
from screenshooter.ui.steering_wheel import SteeringWheel, WheelSegment


class MainWheel(SteeringWheel):
    def __init__(
        self,
        settings_wheel: SettingsWheel,
        on_open_folder: Callable[[], None],
        on_capture: Callable[[], None],
        next_strategy_label: Callable[[], str],
        on_cycle_strategy: Callable[[], None],
        on_minimize: Callable[[], None],
    ) -> None:
        self._settings_wheel = settings_wheel
        self._on_open_folder = on_open_folder
        self._on_capture = on_capture
        self._next_strategy_label = next_strategy_label
        self._on_cycle_strategy = on_cycle_strategy
        self._on_minimize = on_minimize
        super().__init__(self._build_segments())

    def _build_segments(self) -> list[WheelSegment]:
        return [
            WheelSegment("Настройки", self._show_settings_wheel),
            WheelSegment(self._next_strategy_label, self._on_cycle_strategy),
            WheelSegment("Снимок", self._on_capture),
            WheelSegment("Открыть", self._on_open_folder),
            WheelSegment("Свернуть", self._on_minimize),
        ]

    def _show_settings_wheel(self) -> None:
        self._settings_wheel.show_at(QCursor.pos())

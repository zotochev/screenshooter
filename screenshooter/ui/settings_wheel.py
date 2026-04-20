from collections.abc import Callable

from PyQt6.QtGui import QCursor

from screenshooter.ui.format_wheel import FormatWheel
from screenshooter.ui.steering_wheel import SubWheel, WheelSegment


class SettingsWheel(SubWheel):
    def __init__(
        self,
        format_wheel: FormatWheel,
        on_pick_folder: Callable[[], None],
        on_capture_key: Callable[[], None],
        current_key_label: Callable[[], str],
        current_format_label: Callable[[], str],
    ) -> None:
        self._format_wheel = format_wheel
        self._on_pick_folder = on_pick_folder
        self._on_capture_key = on_capture_key
        self._current_key_label = current_key_label
        self._current_format_label = current_format_label
        super().__init__(self._build_segments())

    def _build_segments(self) -> list[WheelSegment]:
        return [
            WheelSegment(self._current_format_label, self._show_format_wheel),
            WheelSegment("Папка", self._on_pick_folder),
            WheelSegment(self._current_key_label, self._on_capture_key),
        ]

    def _show_format_wheel(self) -> None:
        self._format_wheel.show_at(QCursor.pos())

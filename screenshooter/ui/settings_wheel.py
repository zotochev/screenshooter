from collections.abc import Callable

from PyQt6.QtCore import QPointF

from screenshooter.ui.about_popup import AboutPopup
from screenshooter.ui.format_wheel import FormatWheel
from screenshooter.ui.steering_wheel import SubWheel, WheelSegment


class SettingsWheel(SubWheel):
    def __init__(
        self,
        format_wheel: FormatWheel,
        on_pick_folder: Callable[[], None],
        on_capture_key: Callable[[], None],
        on_toggle_key: Callable[[], None],
        current_key_label: Callable[[], str],
        current_toggle_key_label: Callable[[], str],
        current_format_label: Callable[[], str],
    ) -> None:
        self._format_wheel = format_wheel
        self._on_pick_folder = on_pick_folder
        self._on_capture_key = on_capture_key
        self._on_toggle_key = on_toggle_key
        self._current_key_label = current_key_label
        self._current_toggle_key_label = current_toggle_key_label
        self._current_format_label = current_format_label
        self._about = AboutPopup()
        self._last_center = QPointF()
        super().__init__(self._build_segments())

    def show_at(self, pos: QPointF) -> None:
        self._last_center = pos
        super().show_at(pos)

    def _build_segments(self) -> list[WheelSegment]:
        return [
            WheelSegment(self._current_format_label, self._show_format_wheel),
            WheelSegment("Папка", self._on_pick_folder),
            WheelSegment(self._current_key_label, self._on_capture_key),
            WheelSegment(self._current_toggle_key_label, self._on_toggle_key),
            WheelSegment("О программе", self._show_about),
        ]

    def _show_format_wheel(self) -> None:
        self._format_wheel.show_at(self._last_center)

    def _show_about(self) -> None:
        self._about.show_at(self._last_center)

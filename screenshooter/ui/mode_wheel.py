from collections.abc import Callable

from screenshooter.ui.steering_wheel import SubWheel, WheelSegment


class ModeWheel(SubWheel):
    def __init__(
        self,
        labels: list[str],
        get_current_index: Callable[[], int],
        on_select: Callable[[int], None],
    ) -> None:
        self._labels = labels
        self._get_current_index = get_current_index
        self._on_select = on_select
        super().__init__(self._build_segments())

    def _build_segments(self) -> list[WheelSegment]:
        return [
            WheelSegment(
                lambda i=i: f"● {self._labels[i]}" if self._get_current_index() == i else self._labels[i],
                lambda i=i: self._on_select(i),
            )
            for i in range(len(self._labels))
        ]

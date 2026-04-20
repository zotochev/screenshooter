from screenshooter.settings.config import Config
from screenshooter.ui.steering_wheel import SubWheel, WheelSegment


FORMATS = ["png", "jpeg", "bmp"]


class FormatWheel(SubWheel):
    def __init__(self, config: Config) -> None:
        self._config = config
        super().__init__(self._build_segments())

    def _build_segments(self) -> list[WheelSegment]:
        return [
            WheelSegment(
                lambda fmt=fmt: f"● {fmt.upper()}" if self._config.format == fmt else fmt.upper(),
                lambda fmt=fmt: self._select(fmt),
            )
            for fmt in FORMATS
        ]

    def _select(self, fmt: str) -> None:
        self._config.format = fmt

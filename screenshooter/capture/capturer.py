from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication

from screenshooter.settings.config import Config


def capture(rect: QRect, config: Config) -> Path:
    config.output_dir.mkdir(parents=True, exist_ok=True)

    screen = QApplication.screenAt(rect.center()) or QApplication.primaryScreen()
    ratio = screen.devicePixelRatio()

    local_rect = rect.translated(-screen.geometry().topLeft())
    scaled = QRect(
        round(local_rect.x() * ratio),
        round(local_rect.y() * ratio),
        round(local_rect.width() * ratio),
        round(local_rect.height() * ratio),
    )
    pixmap = screen.grabWindow(0).copy(scaled)

    QApplication.clipboard().setPixmap(pixmap)

    filename = datetime.now().strftime(f"screenshot_%Y-%m-%d_%H-%M-%S.{config.format}")
    path = config.output_dir / filename
    pixmap.save(str(path))
    return path

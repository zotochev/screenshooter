from dataclasses import dataclass, field
from pathlib import Path

from PyQt6.QtCore import Qt


def _default_output_dir() -> Path:
    return Path.home() / "Pictures" / "Screenshots"


@dataclass
class Config:
    output_dir: Path = field(default_factory=_default_output_dir)
    format: str = "png"
    capture_key_code: int = field(default_factory=lambda: int(Qt.Key.Key_F9))
    capture_key_name: str = "F9"

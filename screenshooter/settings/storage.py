import json
import os
from pathlib import Path

from PyQt6.QtCore import Qt

from screenshooter.hotkey.vk_codes import key_display_name
from screenshooter.settings.config import Config


def _app_data_dir() -> Path:
    base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    return base / "screenshooter"


CONFIG_PATH = _app_data_dir() / "config.json"


def load() -> Config:
    if not CONFIG_PATH.exists():
        return Config()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        key_code = data.get("capture_key_code", int(Qt.Key.Key_F9))
        return Config(
            output_dir=Path(data["output_dir"]),
            format=data.get("format", "png"),
            capture_key_code=key_code,
            capture_key_name=key_display_name(Qt.Key(key_code)),
        )
    except (KeyError, ValueError, OSError):
        return Config()


def save(config: Config) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "output_dir": str(config.output_dir),
        "format": config.format,
        "capture_key_code": config.capture_key_code,
    }
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": {
        "show_hide": "Показать / Скрыть",
        "quit": "Выход",
        "language": "Язык",
        "settings": "Настройки",
        "mode": "Режим",
        "capture": "Снимок",
        "open": "Открыть",
        "minimize": "Свернуть",
        "folder": "Папка",
        "about": "О программе",
        "fixed": "Фикс",
        "cursor": "Курсор",
        "screen": "Экран",
        "window": "Окно",
        "selection": "Выделение",
        "screenshots_folder": "Папка для скриншотов",
        "press_key": "Нажмите клавишу…\n(Esc — отмена)",
        "capture_key_label": "Снять: {key}",
        "toggle_key_label": "Скрыть: {key}",
    },
    "en": {
        "show_hide": "Show / Hide",
        "quit": "Quit",
        "language": "Language",
        "settings": "Settings",
        "mode": "Mode",
        "capture": "Capture",
        "open": "Open",
        "minimize": "Minimize",
        "folder": "Folder",
        "about": "About",
        "fixed": "Fixed",
        "cursor": "Cursor",
        "screen": "Screen",
        "window": "Window",
        "selection": "Selection",
        "screenshots_folder": "Screenshots folder",
        "press_key": "Press a key…\n(Esc — cancel)",
        "capture_key_label": "Capture: {key}",
        "toggle_key_label": "Hide: {key}",
    },
}

LANG_NAMES: dict[str, str] = {
    "ru": "Русский",
    "en": "English",
}

_lang: str = "ru"


def tr(key: str) -> str:
    return _TRANSLATIONS.get(_lang, _TRANSLATIONS["ru"]).get(key, key)


def set_language(lang: str) -> None:
    global _lang
    if lang in _TRANSLATIONS:
        _lang = lang


def current_language() -> str:
    return _lang

# screenshooter

A Windows desktop tool that places a transparent overlay frame on screen. Position and resize the frame over any area, then capture it with a global hotkey or from the radial menu.

## Features

- **Five capture modes** — Fixed frame, Follow cursor, Fullscreen, Active window, Free selection
- **Radial menus** — right-click the frame to open a wheel menu; navigate to settings, mode, format, and more
- **System tray** — hide/show the overlay from the tray icon or with a hotkey; quit from the tray menu
- **Configurable hotkeys** — reassign the capture key and the hide/show toggle key (defaults: `F9` / `F10`)
- **Output options** — choose the save folder and format (PNG / JPEG / BMP)
- **Border flash** — the frame border briefly flashes white on a successful capture
- **Localization** — UI available in Russian and English; switch from the tray menu
- **Config persistence** — all settings saved on exit and restored on next launch
- **Standalone executable** — build a single `.exe` with PyInstaller

## Requirements

- Windows 10 / 11
- Python >= 3.11
- [uv](https://github.com/astral-sh/uv)

## Installation

```bash
uv sync
```

## Usage

```bash
uv run screenshooter
```

### Capture modes

| Mode | Behaviour |
|---|---|
| **Fixed** | Drag to move, drag edges/corners to resize |
| **Follow cursor** | Frame tracks the cursor; left-click to capture |
| **Fullscreen** | Covers the entire current monitor |
| **Active window** | Tracks the bounds of the foreground window |
| **Selection** | Draw a region with the mouse to capture |

### Controls

| Action | How |
|---|---|
| Move the frame | Left-click drag (Fixed mode) |
| Resize the frame | Drag any edge or corner (Fixed mode) |
| Open main wheel | Right-click the frame |
| Take a screenshot | `F9` (default), or left-click in Follow/Selection mode |
| Show / hide overlay | `F10` (default), or tray icon left-click |
| Close main wheel | Right-click or `Esc` |

### Radial menu structure

```
Main wheel
├── Settings
│   ├── Format (PNG / JPEG / BMP)
│   ├── Folder — pick output directory
│   ├── Capture key — reassign the screenshot hotkey
│   ├── Hide key — reassign the toggle-visibility hotkey
│   └── About
├── Mode — switch between the five capture modes
├── Capture — take a screenshot immediately
├── Open — open the output folder in Explorer
└── Minimize — hide the overlay
```

Screenshots are auto-named with a timestamp, e.g. `screenshot_2026-04-19_14-30-00.png`, and saved to `~/Pictures/Screenshots/` by default.

## Building a standalone executable

```bash
uv run pyinstaller screenshooter.spec
```

Output: `dist/screenshooter.exe`

## Project structure

```
screenshooter/
├── main.py
├── locale/               # i18n strings (ru / en)
├── overlay/
│   ├── frame_window.py           # Main window + tray
│   ├── position_strategy.py      # Strategy base class
│   ├── drag_resize_strategy.py   # Fixed mode
│   ├── follow_cursor_strategy.py # Follow-cursor mode
│   ├── fullscreen_strategy.py    # Fullscreen mode
│   ├── active_window_strategy.py # Active-window mode
│   ├── selection_strategy.py     # Free-selection mode
│   ├── resize_handle.py          # Edge/corner hit-testing
│   └── border_flash.py           # Flash animation on capture
├── capture/
│   └── capturer.py               # Pixel grab via QScreen
├── hotkey/
│   ├── hotkey_manager.py         # Win32 RegisterHotKey wrapper
│   └── vk_codes.py               # Qt key → VK code mapping
├── settings/
│   ├── config.py                 # Config dataclass
│   └── storage.py                # JSON persistence (%APPDATA%)
└── ui/
    ├── steering_wheel.py         # Radial menu base widget
    ├── main_wheel.py             # Top-level wheel
    ├── settings_wheel.py         # Settings sub-wheel
    ├── mode_wheel.py             # Mode selector sub-wheel
    ├── format_wheel.py           # Format picker sub-wheel
    ├── key_capture_dialog.py     # Hotkey reassignment dialog
    └── about_popup.py            # About dialog
```

## Tech stack

| Purpose | Library |
|---|---|
| UI & overlay | PyQt6 |
| Screen capture | PyQt6 (`QScreen.grabWindow`) |
| Global hotkeys | Win32 API (`RegisterHotKey`) |
| Config persistence | JSON (stdlib, `%APPDATA%/screenshooter/`) |

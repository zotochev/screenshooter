# screenshooter

A Windows desktop tool that places a transparent overlay frame on screen. You position and resize the frame over the area you want to capture, then trigger a screenshot with a global hotkey.

## Features

- **Transparent overlay** — frameless, always-on-top window with a visible border and a fully transparent interior
- **Drag & resize** — reposition the frame by dragging it; resize by dragging edges or corners
- **Follow-cursor mode** — frame centers on the cursor and tracks it in real time; press `Esc` to lock it in place
- **Global hotkey capture** — the configured key triggers a screenshot even when another app is focused (default: `F9`)
- **Border flash** — the frame border briefly flashes on a successful capture
- **Configurable output** — choose the output folder, file format (PNG / JPEG / BMP), and capture hotkey
- **Config persistence** — settings are saved on exit and restored on next launch
- **Standalone executable** — can be built into a single `.exe` with PyInstaller

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

Or after installing the project:

```bash
screenshooter
```

### Controls

| Action | How |
|---|---|
| Move the frame | Left-click drag anywhere inside |
| Resize the frame | Drag any edge or corner |
| Open settings wheel | Right-click anywhere on the frame |
| Take a screenshot | Configured hotkey (default `F9`), or left-click in follow-cursor mode |
| Toggle follow-cursor mode | Settings wheel → cycle mode |
| Lock frame (exit follow mode) | `Esc` |
| Quit | Settings wheel → Exit, or `Esc` in fixed mode |

### Settings wheel

Right-click the frame to open a radial menu with the following options:

- **Format** (PNG / JPEG / BMP) — opens a sub-wheel to pick the output format
- **Folder** — opens a folder picker dialog for the output directory
- **Hotkey** — press any key to reassign the capture hotkey
- **Mode** — cycles between Fixed and Follow-cursor modes
- **Exit** — closes the application

Screenshots are auto-named with a timestamp, e.g. `screenshot_2026-04-19_14-30-00.png`, and saved to `~/Pictures/screenshooter/` by default.

## Building a standalone executable

```bash
uv run pyinstaller screenshooter.spec
```

Output: `dist/screenshooter.exe`

## Project structure

```
screenshooter/
├── main.py                        # Entry point
├── overlay/
│   ├── frame_window.py            # Frameless overlay window
│   ├── drag_resize_strategy.py    # Fixed mode: drag and resize
│   ├── follow_cursor_strategy.py  # Follow-cursor mode
│   ├── position_strategy.py       # Strategy base class
│   ├── resize_handle.py           # Edge/corner resize hit-testing
│   └── border_flash.py            # Brief flash animation on capture
├── capture/
│   └── capturer.py                # Grabs pixels inside the frame rect
├── hotkey/
│   ├── hotkey_manager.py          # Win32 global hotkey registration
│   └── vk_codes.py                # Qt key → Windows VK code mapping
├── settings/
│   ├── config.py                  # Config dataclass
│   └── storage.py                 # JSON persistence
└── ui/
    ├── steering_wheel.py          # Generic radial menu widget
    ├── main_wheel.py              # Settings wheel
    ├── format_wheel.py            # Format picker sub-wheel
    └── key_capture_dialog.py      # Hotkey reassignment dialog
```

## Tech stack

| Purpose | Library |
|---|---|
| UI & overlay | PyQt6 |
| Screen capture | PyQt6 (`QScreen.grabWindow`) |
| Global hotkeys | Win32 API (`RegisterHotKey`) |
| Config persistence | JSON (stdlib) |

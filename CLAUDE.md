# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`screenshooter` is a Python >= 3.11 project managed with `uv`.

## Common commands

```bash
# Install dependencies
uv sync

# Run tests (once a test suite exists)
uv run pytest

# Run a single test
uv run pytest path/to/test_file.py::test_name

# Add a dependency
uv add <package>

# Build standalone exe (output: dist/screenshooter.exe)
uv run pyinstaller screenshooter.spec
```

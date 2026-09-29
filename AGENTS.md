# AGENTS.md

Desktop GUI wrapper around `ebook-converter-lib` (a Calibre-derived conversion
engine). Distributed as a PyInstaller bundle, not as a pip package.

## Stack

- Python 3.11, uv for dependency management and virtualenvs
- Tkinter for the GUI (stdlib, no GUI dependencies)
- pytest for tests, ruff for lint and format
- PyInstaller for macOS/Linux/Windows bundles
- GitHub Actions for CI and tag-triggered releases

`[tool.uv] python-preference = "only-managed"` is deliberate: system and pyenv
Pythons frequently ship a broken or missing `_tkinter`.

## Commands

```bash
uv sync --group dev                              # set up
uv run python -m econverter_desktop              # run the GUI
uv run python -m econverter_desktop IN.docx epub # headless conversion
uv run pytest -q                                 # tests
uv run ruff check .                              # lint
uv run ruff format --check .                     # format check
uv run pyinstaller --noconfirm --clean econverter.spec   # build bundle
```

After an `ebook-converter-lib` release, `uv lock` may resolve against a stale
index cache. Use `uv lock --refresh-package ebook-converter-lib`.

## Architecture

`core.py` holds all conversion logic and imports no GUI code, so it is testable
headlessly. `app.py` is a thin Tk layer that marshals work onto a worker thread
and drains a queue via `after()`. `__main__.py` chooses GUI or headless mode.

Format lists are derived from the engine at import time, never hardcoded.
`INPUT_FORMATS` comes from `input_format_plugins()` rather than
`available_input_formats()`, because the latter advertises `zip` and `rar`
with no plugin behind either.

## Conventions

- `core.convert_file` returns `Result(success, message)` and never raises; the
  GUI must not be able to crash on a malformed book
- Tests are written before the fix, and every bug fix gets a regression test
- Test files mirror the module: `test_core.py`, `test_entrypoint.py`
- Tests never perform real conversions; `core._convert` is monkeypatched.
  Real conversions belong in CI, against the frozen binary
- ruff `line-length = 100`; run `ruff format` before committing
- Conventional Commits, imperative subject, body explains why
- Comments state what the code cannot; no narration

## Verification expectations

A change is not done because it compiles. Claims must be backed by a command
that was actually run. For anything touching packaging, formats, or the engine,
that means rebuilding the bundle and converting a real file through it, because
PyInstaller silently omits the engine's template and XSLT data files.

## Documentation maintenance

User-visible changes (formats, CLI arguments, external binaries, build output)
must update `README.md` in the same commit. Keep `CODEBASE_MAP.md` in sync when
modules move or entrypoints change.

## Glossary

- **engine** - `ebook_converter`, the vendored Calibre-derived conversion code
- **bridge** - `ebook_converter_lib.convert`, the public entry point used here
- **frozen build** - the PyInstaller output in `dist/`
- **Poppler** - optional external tools the engine uses for PDF input when
  present. Not required and not surfaced in the UI, matching the Android app;
  without them the engine falls back to pure-Python `pypdf` extraction

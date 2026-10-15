# Codebase Map

Small repo: four source modules, four test modules, one PyInstaller spec.

## Layout

| Path | Owns |
| --- | --- |
| `econverter_desktop/core.py` | Backend capabilities, temporary EPUB routing, output paths, `convert_file()`. No GUI imports. |
| `econverter_desktop/app.py` | Tkinter UI, worker thread, event queue, asset resolution. |
| `econverter_desktop/__main__.py` | Process entry: console attach, GUI vs headless dispatch. |
| `econverter.spec` | PyInstaller build: `collect_all` for the engine, per-OS icon, macOS bundle. |
| `assets/` | `icon.png` (Tk window), `icon.ico` (Windows), `icon.icns` (macOS bundle). |
| `tests/` | `test_core.py`, `test_app.py`, `test_entrypoint.py`, `test_assets.py`. |
| `.github/workflows/` | `ci.yml` (lint + 3-OS tests + real conversions), `release.yml` (tag-triggered 3-OS builds). |

Not in the repo but generated locally: `dist/`, `build/`, `.venv/`.

## Entrypoints

- `python -m econverter_desktop` - no arguments opens the GUI;
  `INPUT_FILE OUTPUT_FORMAT [auto|calibre|boko]` converts headlessly and exits
- `dist/eConverter.app/Contents/MacOS/econverter` (macOS) or
  `dist/econverter/econverter[.exe]` - same argument contract

There is no `console_scripts`/`gui_scripts` entry point. It was removed because
the wheel ships no `assets/`, so a pip-installed GUI would silently lack its
icon. PyInstaller is the distribution channel.

## Flows

**Conversion (GUI).** `App.start` copies the file list and spawns a daemon
thread running `App._run`, snapshotting the backend and output format. That
thread calls `core.convert_file` per file and
pushes `("log", text)` events onto `self.events`. `App._poll`, rescheduled every
100 ms via `after()`, drains the queue and writes to the Text widget. Tk is only
ever touched from the main thread.

**Conversion (core).** `convert_file` validates that the source exists, that its
extension is in `INPUT_FORMATS`, and that the derived destination is not the
source itself. Calibre calls `core._convert`; direct Boko calls
`core._convert_boko`, which imports `boko_python.convert`. Auto uses Calibre
except for KFX inputs and KFX/Markdown outputs, which pass through temporary
EPUBs using both engines. Any exception is caught and returned as a failed
`Result`; temporary directories are cleaned on every exit.

**Startup format discovery.** Importing `core` imports
`ebook_converter.customize.ui` and enumerates plugins. This costs roughly 80 ms
and couples the app to an internal module of the engine; the payoff is that the
Calibre format lists cannot drift from what the engine can actually do.
Boko capabilities are declared in `core` to match the pinned bindings. The GUI
and core validation use the same backend-specific lists; the default is Auto.

**Frozen startup.** `__main__` calls `_attach_console()` before importing
`core`, because a windowed build has no stdout and the engine's logging would
fail on its first write. `app.asset()` resolves bundled files through
`sys._MEIPASS` when frozen.

## Watch out

- `econverter.spec` needs `collect_all` for `ebook_converter`; the engine's
  templates and XSLT are invisible to PyInstaller's import analysis
- `boko_python` also needs collection to include its native extension
- The engine still advertises `zip` and `rar` as input formats with no plugin
  implementing them
- PyInstaller does not cross-compile, so each OS bundle is built on its own
  runner

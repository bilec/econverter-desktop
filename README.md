# eConverter Desktop

[![CI](https://github.com/bilec/econverter-desktop/actions/workflows/ci.yml/badge.svg)](https://github.com/bilec/econverter-desktop/actions/workflows/ci.yml)
[![Release](https://github.com/bilec/econverter-desktop/actions/workflows/release.yml/badge.svg)](https://github.com/bilec/econverter-desktop/actions/workflows/release.yml)

Desktop ebook converter — epub, mobi, azw3, docx and more. Wraps
[ebook-converter-lib](https://github.com/bilec/ebook-converter-lib), the
Calibre-derived conversion engine, and [boko](https://github.com/zacharydenton/boko)
through `boko-python` in a small Tkinter GUI. Desktop counterpart
to the Android app [eConverter](https://github.com/bilec/econverter).

## Download

Prebuilt bundles for macOS, Linux and Windows are attached to every
[release](https://github.com/bilec/econverter-desktop/releases). They are
unsigned: on macOS use right-click → Open, or run
`xattr -dr com.apple.quarantine eConverter.app`.

## Supported formats

Choose `auto` (the default), `calibre`, or `boko` in the backend selector.
Output choices and the file picker follow the selected backend. Selected files
are retained when switching; incompatible inputs are reported before conversion.

### Calibre

Input: `azw`, `azw3`, `docm`, `docx`, `epub`, `fb2`, `fbz`, `htm`, `html`,
`htmlz`, `lrf`, `markdown`, `md`, `mobi`, `odt`, `opf`, `pdb`, `pdf`, `pobi`,
`prc`, `rtf`, `shtm`, `shtml`, `text`, `textile`, `txt`, `txtz`, `updb`, `xhtm`,
`xhtml`

Output: `azw3`, `docx`, `epub`, `fb2`, `html`, `htmlz`, `lrf`, `mobi`, `oeb`,
`txt`, `txtz`

Calibre's lists are read from its plugins at startup.

### Boko

Input: `epub`, `kfx`, `azw3`, `mobi`

Output: `epub`, `kfx`, `azw3`, `md`

Direct conversion uses the native Boko engine without running Calibre.

### Auto

Accepts both engines' inputs and outputs. KFX input is converted to a temporary
EPUB by Boko before Calibre runs. For KFX or Markdown output, Calibre produces a
temporary EPUB and Boko writes the final file. Other conversions use Calibre.
Temporary files are removed on success or failure.

PDF input supports text-based PDFs. Scanned PDFs require OCR, which is not
supported. PDF input requires `auto` or `calibre`.

## Development

```bash
uv sync --group dev
uv run python -m econverter_desktop   # run the GUI
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

CI runs the same checks on Linux, macOS and Windows, plus real Calibre, Auto KFX,
direct Boko, and PDF→epub conversions on each. See [AGENTS.md](AGENTS.md) and
[CODEBASE_MAP.md](CODEBASE_MAP.md).

## Build a standalone app

```bash
uv run pyinstaller econverter.spec
```

Output lands in `dist/` — `eConverter.app` on macOS, `dist/econverter/` with an
`econverter` executable on Linux and Windows. PyInstaller does not
cross-compile, so releases are built by a three-OS GitHub Actions matrix.

## Headless conversion

Passing an input file and an output format converts without opening the GUI —
useful for scripting and for smoke-testing a frozen build:

```bash
uv run python -m econverter_desktop book.docx epub
uv run python -m econverter_desktop book.epub kfx boko
./dist/eConverter.app/Contents/MacOS/econverter book.docx epub
```

The optional third argument selects `auto`, `calibre`, or `boko`; omitted means
`auto`. Existing two-argument commands still work.

## License

[GPL-3.0-or-later](LICENSE), inherited from Calibre via
`ebook-converter-lib`. The icon is taken from the Android
[eConverter](https://github.com/bilec/econverter) app.

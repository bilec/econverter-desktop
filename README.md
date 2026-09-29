# eConverter Desktop

[![CI](https://github.com/bilec/econverter-desktop/actions/workflows/ci.yml/badge.svg)](https://github.com/bilec/econverter-desktop/actions/workflows/ci.yml)
[![Release](https://github.com/bilec/econverter-desktop/actions/workflows/release.yml/badge.svg)](https://github.com/bilec/econverter-desktop/actions/workflows/release.yml)

Desktop ebook converter — epub, mobi, azw3, docx and more. Wraps
[ebook-converter-lib](https://github.com/bilec/ebook-converter-lib), the
Calibre-derived conversion engine, in a small Tkinter GUI. Desktop counterpart
to the Android app [eConverter](https://github.com/bilec/econverter).

## Download

Prebuilt bundles for macOS, Linux and Windows are attached to every
[release](https://github.com/bilec/econverter-desktop/releases). They are
unsigned: on macOS use right-click → Open, or run
`xattr -dr com.apple.quarantine eConverter.app`.

## Supported formats

Input: `azw`, `azw3`, `azw4`, `cbc`, `cbr`, `cbz`, `chm`, `djv`, `djvu`, `docm`,
`docx`, `epub`, `fb2`, `fbz`, `htm`, `html`, `htmlz`, `lrf`, `markdown`, `md`,
`mobi`, `odt`, `opf`, `pdb`, `pdf`, `pobi`, `prc`, `rtf`, `shtm`, `shtml`,
`text`, `textile`, `txt`, `txtz`, `updb`, `xhtm`, `xhtml`

Output: `epub`, `mobi`, `azw3`, `docx`, `fb2`, `html`, `htmlz`, `lrf`, `oeb`,
`txt`, `txtz`

PDF input supports text-based PDFs. Scanned PDFs require OCR, which is not
supported here.

PDF conversion works out of the box: when the Poppler tools (`pdftohtml`,
`pdfinfo`, `pdftoppm`) are absent the engine falls back to pure-Python `pypdf`
text extraction, the same path the Android app uses. Installing Poppler
(`brew install poppler`, `apt install poppler-utils`, or the Windows binaries)
upgrades PDF conversion to preserve images and layout.

## Run from source

```bash
uv sync --group dev
uv run python -m econverter_desktop
```

## Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

CI runs the same checks on Linux, macOS and Windows, plus a real md→epub→mobi
conversion on each.

## Build a standalone app

```bash
uv run pyinstaller econverter.spec
```

Output lands in `dist/` — `eConverter.app` on macOS, `dist/econverter/` with an
`econverter` executable on Linux and Windows. Build on the platform you are
targeting; PyInstaller does not cross-compile, so releases are built by a
three-OS GitHub Actions matrix.

## Releasing

Push a `v*` tag. The release workflow builds all three platforms, smoke-tests
each frozen binary with an actual conversion, and attaches the archives to a
GitHub release.

```bash
git tag v0.1.0 && git push origin v0.1.0
```

## Headless conversion

Passing an input file and an output format converts without opening the GUI —
useful for scripting and for smoke-testing a frozen build:

```bash
uv run python -m econverter_desktop book.docx epub
./dist/eConverter.app/Contents/MacOS/econverter book.docx epub
```

## License

GPL-3.0-or-later, inherited from Calibre via `ebook-converter-lib`. The icon is
taken from the Android [eConverter](https://github.com/bilec/econverter) app.

"""Conversion logic, kept free of GUI code so it can be tested headlessly."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

INPUT_FORMATS = (
    "azw",
    "azw3",
    "azw4",
    "cbc",
    "cbr",
    "cbz",
    "chm",
    "djv",
    "djvu",
    "docm",
    "docx",
    "epub",
    "fb2",
    "fbz",
    "htm",
    "html",
    "htmlz",
    "lrf",
    "markdown",
    "md",
    "mobi",
    "odt",
    "opf",
    "pdb",
    "pdf",
    "pobi",
    "prc",
    "rtf",
    "shtm",
    "shtml",
    "text",
    "textile",
    "txt",
    "txtz",
    "updb",
    "xhtm",
    "xhtml",
)

OUTPUT_FORMATS = (
    "epub",
    "mobi",
    "azw3",
    "docx",
    "fb2",
    "html",
    "htmlz",
    "lrf",
    "oeb",
    "txt",
    "txtz",
)

POPPLER_TOOLS = ("pdftohtml", "pdfinfo", "pdftoppm")


@dataclass(frozen=True)
class Result:
    success: bool
    message: str
    output: Path | None = None


def _convert(src: str, dst: str, *args: str) -> dict:
    from ebook_converter_lib import convert

    return convert(src, dst, *args)


def is_supported_input(path: Path) -> bool:
    return path.suffix.lstrip(".").lower() in INPUT_FORMATS


def output_path(src: Path, fmt: str, dest_dir: Path | None = None) -> Path:
    fmt = fmt.lstrip(".").lower()
    if fmt not in OUTPUT_FORMATS:
        raise ValueError(f"unsupported output format: {fmt}")
    return (dest_dir or src.parent) / f"{src.stem}.{fmt}"


def missing_poppler_tools() -> list[str]:
    return [tool for tool in POPPLER_TOOLS if shutil.which(tool) is None]


def convert_file(src: Path, fmt: str, dest_dir: Path | None = None) -> Result:
    if not src.is_file():
        return Result(False, f"file not found: {src}")
    if not is_supported_input(src):
        return Result(False, f"unsupported input format: {src.suffix}")

    try:
        dst = output_path(src, fmt, dest_dir)
    except ValueError as exc:
        return Result(False, str(exc))

    try:
        result = _convert(str(src), str(dst))
    except Exception as exc:  # noqa: BLE001 - a bad book must not kill the GUI
        return Result(False, f"{type(exc).__name__}: {exc}")

    if result.get("success"):
        return Result(True, result.get("message") or f"created {dst.name}", dst)
    return Result(False, result.get("message") or "conversion failed")

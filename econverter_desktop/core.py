"""Conversion logic, kept free of GUI code so it can be tested headlessly."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from ebook_converter.customize.ui import available_output_formats, input_format_plugins

# Derived from the plugins, not available_input_formats(), which also advertises
# zip and rar despite no plugin handling either.
INPUT_FORMATS = tuple(sorted({f for plugin in input_format_plugins() for f in plugin.file_types}))
OUTPUT_FORMATS = tuple(sorted(available_output_formats()))
DEFAULT_OUTPUT = "epub"

POPPLER_TOOL = "pdftohtml"


@dataclass(frozen=True)
class Result:
    success: bool
    message: str


def _convert(src: str, dst: str) -> dict:
    from ebook_converter_lib import convert

    return convert(src, dst)


def is_supported_input(path: Path) -> bool:
    return path.suffix.lstrip(".").lower() in INPUT_FORMATS


def output_path(src: Path, fmt: str, dest_dir: Path | None = None) -> Path:
    fmt = fmt.lstrip(".").lower()
    if fmt not in OUTPUT_FORMATS:
        raise ValueError(f"unsupported output format: {fmt}")
    return (dest_dir or src.parent) / f"{src.stem}.{fmt}"


def poppler_available() -> bool:
    return shutil.which(POPPLER_TOOL) is not None


def convert_file(src: Path, fmt: str, dest_dir: Path | None = None) -> Result:
    if not src.is_file():
        return Result(False, f"file not found: {src}")
    if not is_supported_input(src):
        return Result(False, f"unsupported input format: {src.suffix}")

    try:
        dst = output_path(src, fmt, dest_dir)
    except ValueError as exc:
        return Result(False, str(exc))

    if dst == src:
        return Result(False, f"{src.name} is already {fmt}; choose another output folder")

    try:
        result = _convert(str(src), str(dst))
    except Exception as exc:  # noqa: BLE001 - a bad book must not kill the GUI
        return Result(False, f"{type(exc).__name__}: {exc}")

    if result.get("success"):
        return Result(True, result.get("message") or f"created {dst.name}")
    return Result(False, result.get("message") or "conversion failed")

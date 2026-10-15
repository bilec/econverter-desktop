"""Conversion logic, kept free of GUI code so it can be tested headlessly."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from ebook_converter.customize.ui import available_output_formats, input_format_plugins

# Derived from the plugins, not available_input_formats(), which also advertises
# zip and rar despite no plugin handling either.
CALIBRE_INPUTS = {fmt for plugin in input_format_plugins() for fmt in plugin.file_types}
CALIBRE_OUTPUTS = set(available_output_formats())
BOKO_INPUTS = {"epub", "kfx", "azw3", "mobi"}
BOKO_OUTPUTS = {"epub", "kfx", "azw3", "md"}
BACKENDS = ("auto", "calibre", "boko")
DEFAULT_OUTPUT = "epub"


def input_formats(backend: str = "auto") -> tuple[str, ...]:
    return tuple(
        sorted(
            {"auto": CALIBRE_INPUTS | BOKO_INPUTS, "calibre": CALIBRE_INPUTS, "boko": BOKO_INPUTS}[
                backend
            ]
        )
    )


def output_formats(backend: str = "auto") -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                "auto": CALIBRE_OUTPUTS | BOKO_OUTPUTS,
                "calibre": CALIBRE_OUTPUTS,
                "boko": BOKO_OUTPUTS,
            }[backend]
        )
    )


INPUT_FORMATS = input_formats()
OUTPUT_FORMATS = output_formats()


@dataclass(frozen=True)
class Result:
    success: bool
    message: str


def _convert(src: str, dst: str) -> dict:
    from ebook_converter_lib import convert

    return convert(src, dst)


def _convert_boko(src: str, dst: str) -> dict:
    from boko_python import convert

    convert(src, dst)
    return {"success": True}


def _convert_auto(src: Path, dst: Path) -> dict:
    if src.suffix.lower() != ".kfx" and dst.suffix not in (".kfx", ".md"):
        return _convert(str(src), str(dst))
    with TemporaryDirectory(prefix="econverter-") as directory:
        scratch = Path(directory)
        if src.suffix.lower() == ".kfx":
            normalized = scratch / "input.epub"
            result = _convert_boko(str(src), str(normalized))
            if not result.get("success"):
                return result
            src = normalized
        intermediate = scratch / "output.epub" if dst.suffix in (".kfx", ".md") else dst
        result = _convert(str(src), str(intermediate))
        if result.get("success") and intermediate != dst:
            return _convert_boko(str(intermediate), str(dst))
        return result


def is_supported_input(path: Path, backend: str = "auto") -> bool:
    return path.suffix.lstrip(".").lower() in input_formats(backend)


def output_path(src: Path, fmt: str, dest_dir: Path | None = None, backend: str = "auto") -> Path:
    fmt = fmt.lstrip(".").lower()
    if fmt not in output_formats(backend):
        raise ValueError(f"unsupported output format: {fmt}")
    return (dest_dir or src.parent) / f"{src.stem}.{fmt}"


def convert_file(
    src: Path, fmt: str, dest_dir: Path | None = None, backend: str = "auto"
) -> Result:
    if backend not in BACKENDS:
        return Result(False, f"unknown backend: {backend}")
    if not src.is_file():
        return Result(False, f"file not found: {src}")
    if not is_supported_input(src, backend):
        return Result(False, f"unsupported input format: {src.suffix}")

    try:
        dst = output_path(src, fmt, dest_dir, backend)
    except ValueError as exc:
        return Result(False, str(exc))

    if dst == src:
        return Result(False, f"{src.name} is already {fmt}; choose another output folder")

    try:
        if backend == "boko":
            result = _convert_boko(str(src), str(dst))
        elif backend == "calibre":
            result = _convert(str(src), str(dst))
        else:
            result = _convert_auto(src, dst)
    except Exception as exc:  # noqa: BLE001 - a bad book must not kill the GUI
        return Result(False, f"{type(exc).__name__}: {exc}")

    if result.get("success"):
        return Result(True, result.get("message") or f"created {dst.name}")
    return Result(False, result.get("message") or "conversion failed")

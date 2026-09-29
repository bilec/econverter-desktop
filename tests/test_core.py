from pathlib import Path

import pytest

from econverter_desktop import core


def test_output_path_swaps_extension(tmp_path):
    assert core.output_path(tmp_path / "book.docx", "epub") == tmp_path / "book.epub"


def test_output_path_normalises_format():
    assert core.output_path(Path("/x/book.docx"), ".EPUB").name == "book.epub"


def test_output_path_honours_destination(tmp_path):
    out = core.output_path(Path("/x/book.docx"), "epub", tmp_path)
    assert out == tmp_path / "book.epub"


def test_output_path_rejects_unknown_format():
    with pytest.raises(ValueError):
        core.output_path(Path("book.docx"), "pdf")


def test_is_supported_input():
    assert core.is_supported_input(Path("a.EPUB"))
    assert not core.is_supported_input(Path("a.xyz"))


def test_convert_file_reports_success(tmp_path, monkeypatch):
    src = tmp_path / "book.docx"
    src.write_bytes(b"x")
    monkeypatch.setattr(core, "_convert", lambda *a, **k: {"success": True, "message": "ok"})

    result = core.convert_file(src, "epub")

    assert result.success
    assert result.output == tmp_path / "book.epub"


def test_convert_file_reports_failure(tmp_path, monkeypatch):
    src = tmp_path / "book.docx"
    src.write_bytes(b"x")
    monkeypatch.setattr(core, "_convert", lambda *a, **k: {"success": False, "message": "boom"})

    result = core.convert_file(src, "epub")

    assert not result.success
    assert result.message == "boom"


def test_convert_file_wraps_exceptions(tmp_path, monkeypatch):
    src = tmp_path / "book.docx"
    src.write_bytes(b"x")

    def explode(*a, **k):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(core, "_convert", explode)

    result = core.convert_file(src, "epub")

    assert not result.success
    assert "kaboom" in result.message


def test_convert_file_rejects_missing_source(tmp_path):
    result = core.convert_file(tmp_path / "nope.docx", "epub")
    assert not result.success


def test_pdf_converts_without_poppler(monkeypatch, tmp_path):
    """The engine falls back to pypdf text extraction, so PDF must not be blocked."""
    src = tmp_path / "book.pdf"
    src.write_bytes(b"x")
    monkeypatch.setattr(core.shutil, "which", lambda _: None)
    monkeypatch.setattr(core, "_convert", lambda *a, **k: {"success": True, "message": "ok"})

    assert core.convert_file(src, "epub").success


def test_missing_poppler_tools_reports_all(monkeypatch):
    monkeypatch.setattr(core.shutil, "which", lambda _: None)
    assert core.missing_poppler_tools() == list(core.POPPLER_TOOLS)


def test_missing_poppler_tools_empty_when_present(monkeypatch):
    monkeypatch.setattr(core.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert core.missing_poppler_tools() == []

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


def test_formats_come_from_the_engine():
    """Hardcoded lists drift; the plugins are the only source of truth."""
    from ebook_converter.customize.ui import available_output_formats, input_format_plugins

    expected = {fmt for plugin in input_format_plugins() for fmt in plugin.file_types}
    assert core.INPUT_FORMATS == tuple(sorted(expected))
    assert core.OUTPUT_FORMATS == tuple(sorted(available_output_formats()))


def test_unimplemented_archives_are_not_offered():
    """available_input_formats() advertises zip/rar, but no plugin handles them."""
    assert "zip" not in core.INPUT_FORMATS
    assert "rar" not in core.INPUT_FORMATS


def test_real_formats_are_offered():
    for fmt in ("epub", "pdf", "docx", "mobi", "azw3", "fb2"):
        assert fmt in core.INPUT_FORMATS


def test_default_output_is_offered():
    assert core.DEFAULT_OUTPUT in core.OUTPUT_FORMATS


def test_convert_file_reports_success(tmp_path, monkeypatch):
    src = tmp_path / "book.docx"
    src.write_bytes(b"x")
    monkeypatch.setattr(core, "_convert", lambda *a, **k: {"success": True, "message": "ok"})

    assert core.convert_file(src, "epub").success


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


def test_convert_file_never_overwrites_its_own_input(tmp_path, monkeypatch):
    """Converting epub->epub in place would destroy the user's book."""
    src = tmp_path / "book.epub"
    src.write_bytes(b"original")
    monkeypatch.setattr(core, "_convert", lambda *a, **k: pytest.fail("must not run"))

    result = core.convert_file(src, "epub")

    assert not result.success
    assert src.read_bytes() == b"original"


def test_convert_file_allows_same_format_into_another_folder(tmp_path, monkeypatch):
    src = tmp_path / "book.epub"
    src.write_bytes(b"original")
    dest = tmp_path / "out"
    dest.mkdir()
    monkeypatch.setattr(core, "_convert", lambda *a, **k: {"success": True, "message": "ok"})

    assert core.convert_file(src, "epub", dest).success


def test_pdf_converts_without_poppler(monkeypatch, tmp_path):
    """The engine falls back to pypdf text extraction, so PDF must not be blocked."""
    src = tmp_path / "book.pdf"
    src.write_bytes(b"x")
    monkeypatch.setattr(core.shutil, "which", lambda _: None)
    monkeypatch.setattr(core, "_convert", lambda *a, **k: {"success": True, "message": "ok"})

    assert core.convert_file(src, "epub").success


def test_poppler_available(monkeypatch):
    monkeypatch.setattr(core.shutil, "which", lambda _: None)
    assert not core.poppler_available()
    monkeypatch.setattr(core.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert core.poppler_available()

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
    assert core.input_formats("calibre") == tuple(sorted(expected))
    assert core.output_formats("calibre") == tuple(sorted(available_output_formats()))
    assert set(core.INPUT_FORMATS) == expected | core.BOKO_INPUTS
    assert set(core.OUTPUT_FORMATS) == set(available_output_formats()) | core.BOKO_OUTPUTS


def test_unimplemented_archives_are_not_offered():
    """available_input_formats() advertises zip/rar, but no plugin handles them."""
    assert "zip" not in core.INPUT_FORMATS
    assert "rar" not in core.INPUT_FORMATS


def test_real_formats_are_offered():
    for fmt in ("epub", "pdf", "docx", "mobi", "azw3", "fb2"):
        assert fmt in core.INPUT_FORMATS


def test_default_output_is_offered():
    assert core.DEFAULT_OUTPUT in core.OUTPUT_FORMATS


@pytest.mark.parametrize(
    ("backend", "extension", "fmt", "engines"),
    [
        ("auto", "docx", "epub", ["calibre"]),
        ("auto", "kfx", "mobi", ["boko", "calibre"]),
        ("auto", "docx", "kfx", ["calibre", "boko"]),
        ("auto", "kfx", "md", ["boko", "calibre", "boko"]),
        ("boko", "epub", "azw3", ["boko"]),
        ("calibre", "epub", "mobi", ["calibre"]),
    ],
)
def test_backend_routing(tmp_path, monkeypatch, backend, extension, fmt, engines):
    src = tmp_path / f"book.{extension}"
    src.write_bytes(b"original")
    calls = []

    def convert(engine, source, destination):
        assert Path(source).is_file()
        calls.append((engine, Path(destination)))
        Path(destination).write_bytes(b"converted")
        return {"success": True}

    monkeypatch.setattr(core, "_convert", lambda *args: convert("calibre", *args))
    monkeypatch.setattr(core, "_convert_boko", lambda *args: convert("boko", *args), raising=False)

    result = core.convert_file(src, fmt, backend=backend)

    assert result.success, result.message
    assert [engine for engine, _ in calls] == engines
    assert (tmp_path / f"book.{fmt}").read_bytes() == b"converted"
    assert all(not path.exists() for _, path in calls[:-1])
    assert src.read_bytes() == b"original"


@pytest.mark.parametrize(
    ("backend", "extension", "fmt"),
    [
        ("boko", "docx", "epub"),
        ("calibre", "kfx", "epub"),
        ("calibre", "epub", "kfx"),
        ("boko", "epub", "mobi"),
        ("unknown", "epub", "mobi"),
    ],
)
def test_backend_rejects_unsupported_requests(tmp_path, backend, extension, fmt):
    src = tmp_path / f"book.{extension}"
    src.write_bytes(b"original")
    assert not core.convert_file(src, fmt, backend=backend).success


def test_auto_stops_when_intermediate_conversion_fails(tmp_path, monkeypatch):
    src = tmp_path / "book.docx"
    src.write_bytes(b"original")
    monkeypatch.setattr(core, "_convert", lambda *args: {"success": False, "message": "bad"})
    monkeypatch.setattr(
        core, "_convert_boko", lambda *args: pytest.fail("must not run"), raising=False
    )
    result = core.convert_file(src, "kfx")
    assert not result.success
    assert result.message == "bad"


def test_auto_cleans_intermediate_files_after_exception(tmp_path, monkeypatch):
    src = tmp_path / "book.kfx"
    src.write_bytes(b"original")
    intermediates = []

    def normalize(source, destination):
        intermediate = Path(destination)
        intermediate.write_bytes(b"epub")
        intermediates.append(intermediate)
        return {"success": True}

    def explode(*args):
        raise RuntimeError("bad book")

    monkeypatch.setattr(core, "_convert_boko", normalize)
    monkeypatch.setattr(core, "_convert", explode)

    result = core.convert_file(src, "mobi")

    assert not result.success
    assert "bad book" in result.message
    assert intermediates
    assert not intermediates[0].parent.exists()
    assert src.read_bytes() == b"original"


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


def test_pdf_is_a_supported_input(tmp_path, monkeypatch):
    """PDF never needs external binaries: the engine bundles PDFium."""
    src = tmp_path / "book.pdf"
    src.write_bytes(b"x")
    monkeypatch.setattr(core, "_convert", lambda *a, **k: {"success": True, "message": "ok"})

    assert "pdf" in core.INPUT_FORMATS
    assert core.convert_file(src, "epub").success

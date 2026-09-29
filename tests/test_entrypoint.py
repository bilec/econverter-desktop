import sys

import pytest

from econverter_desktop import __main__ as entry


@pytest.fixture
def no_gui(monkeypatch):
    launched = []
    monkeypatch.setattr(entry, "_launch_gui", lambda: launched.append(True))
    return launched


def test_no_arguments_opens_gui(monkeypatch, no_gui):
    monkeypatch.setattr(sys, "argv", ["econverter"])
    assert entry.main() == 0
    assert no_gui


def test_finder_process_serial_number_is_ignored(monkeypatch, no_gui):
    """macOS passes -psn_0_12345 when launching a bundle; it is not a filename."""
    monkeypatch.setattr(sys, "argv", ["econverter", "-psn_0_12345"])
    assert entry.main() == 0
    assert no_gui


def test_wrong_argument_count_is_an_error(monkeypatch, no_gui):
    monkeypatch.setattr(sys, "argv", ["econverter", "book.docx"])
    assert entry.main() == 2
    assert not no_gui


def test_two_arguments_convert(monkeypatch, no_gui, tmp_path):
    monkeypatch.setattr(sys, "argv", ["econverter", "book.docx", "epub"])
    monkeypatch.setattr(entry.core, "convert_file", lambda *a: entry.core.Result(True, "ok"))
    assert entry.main() == 0
    assert not no_gui


def test_failed_conversion_exits_nonzero(monkeypatch, no_gui):
    monkeypatch.setattr(sys, "argv", ["econverter", "book.docx", "epub"])
    monkeypatch.setattr(entry.core, "convert_file", lambda *a: entry.core.Result(False, "bad"))
    assert entry.main() == 1

import queue
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from econverter_desktop import app, core


@pytest.mark.parametrize(("current", "expected"), [("mobi", "epub"), ("kfx", "kfx")])
def test_backend_change_updates_formats(current, expected):
    frame = SimpleNamespace(
        backend=SimpleNamespace(get=lambda: "boko"),
        fmt=Mock(),
        format_box=Mock(),
    )
    frame.fmt.get.return_value = current
    app.App._select_backend(frame)
    frame.format_box.configure.assert_called_once_with(values=core.output_formats("boko"))
    if current == expected:
        frame.fmt.set.assert_not_called()
    else:
        frame.fmt.set.assert_called_once_with(expected)


def test_worker_uses_snapshotted_backend(monkeypatch):
    convert = Mock(return_value=core.Result(True, "ok"))
    monkeypatch.setattr(core, "convert_file", convert)
    frame = SimpleNamespace(events=queue.Queue())
    src = Path("book.epub")
    app.App._run(frame, [src], "kfx", None, "boko")
    convert.assert_called_once_with(src, "kfx", None, "boko")
    assert frame.events.get_nowait()[0] == "log"
    assert frame.events.get_nowait()[0] == "log"
    assert frame.events.get_nowait() == ("done", "")


def test_incompatible_selection_does_not_start_conversion():
    frame = SimpleNamespace(
        sources=[Path("book.docx")],
        backend=SimpleNamespace(get=lambda: "boko"),
        convert_button=Mock(),
        _write=Mock(),
    )
    app.App.start(frame)
    frame._write.assert_called_once_with("Unsupported input for boko: book.docx")
    frame.convert_button.state.assert_not_called()

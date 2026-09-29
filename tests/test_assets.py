from econverter_desktop.app import asset


def test_icon_asset_exists_from_source():
    assert asset("icon.png").is_file()


def test_asset_uses_pyinstaller_root(monkeypatch, tmp_path):
    monkeypatch.setattr("sys._MEIPASS", str(tmp_path), raising=False)
    assert asset("icon.png") == tmp_path / "assets" / "icon.png"

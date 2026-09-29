import sys

from PyInstaller.utils.hooks import collect_all

ICON = {"darwin": "assets/icon.icns", "win32": "assets/icon.ico"}.get(sys.platform, "assets/icon.png")

# ebook_converter ships templates, XSLT and encoding data that PyInstaller cannot see.
datas, binaries, hiddenimports = [], [], []
for package in ("ebook_converter", "ebook_converter_lib", "html5_parser", "msgpack"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    ["econverter_desktop/__main__.py"],
    pathex=[],
    binaries=binaries,
    datas=datas + [("assets/icon.png", "assets")],
    hiddenimports=hiddenimports,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="econverter",
    console=False,
    icon=ICON,
    upx=False,
)

coll = COLLECT(exe, a.binaries, a.datas, upx=False, name="econverter")

app = BUNDLE(
    coll,
    name="eConverter.app",
    icon="assets/icon.icns",
    bundle_identifier="com.econverter.desktop",
    info_plist={"NSHighResolutionCapable": True},
)

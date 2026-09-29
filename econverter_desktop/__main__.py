"""Entry point: launches the GUI, or converts headlessly when given arguments."""

import os
import sys
from pathlib import Path

USAGE = "usage: econverter [INPUT_FILE OUTPUT_FORMAT]"


def _attach_console() -> None:
    """A windowed build has no stdout; engine logging would crash on the first write."""
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.kernel32.AttachConsole(-1)  # -1 = parent process

    for name in ("stdout", "stderr"):
        if getattr(sys, name) is None:
            target = "CONOUT$" if sys.platform == "win32" else os.devnull
            try:
                setattr(sys, name, open(target, "w"))  # noqa: SIM115
            except OSError:
                setattr(sys, name, open(os.devnull, "w"))  # noqa: SIM115


# Must run before the engine is imported, which is why the import below is not at the top.
_attach_console()

from econverter_desktop import core


def _launch_gui() -> None:
    from econverter_desktop.app import main as gui

    gui()


def main() -> int:
    # macOS passes -psn_0_12345 when a bundle is opened from Finder.
    args = [a for a in sys.argv[1:] if not a.startswith("-psn_")]

    if not args:
        _launch_gui()
        return 0
    if len(args) != 2:
        print(USAGE, file=sys.stderr)
        return 2

    result = core.convert_file(Path(args[0]), args[1])
    print(result.message)
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())

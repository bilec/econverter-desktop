"""Entry point: launches the GUI, or converts headlessly when given arguments."""

import os
import sys
from pathlib import Path

from econverter_desktop import core

# A windowed PyInstaller build has no stdout/stderr; library logging would crash on write.
for _name in ("stdout", "stderr"):
    if getattr(sys, _name) is None:
        setattr(sys, _name, open(os.devnull, "w"))  # noqa: SIM115


def main() -> int:
    if len(sys.argv) < 3:
        from econverter_desktop.app import main as gui

        gui()
        return 0

    result = core.convert_file(Path(sys.argv[1]), sys.argv[2])
    print(result.message)
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())

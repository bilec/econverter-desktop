"""Tkinter front-end. All conversion work happens in core.py, on a worker thread."""

from __future__ import annotations

import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from . import core

FILE_TYPES = [
    ("Ebooks", " ".join(f"*.{ext}" for ext in core.INPUT_FORMATS)),
    ("All files", "*.*"),
]


def asset(name: str) -> Path:
    """Resolve a bundled asset, both from source and from a PyInstaller bundle."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / "assets" / name


class App(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=10)
        self.grid(sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.sources: list[Path] = []
        self.dest_dir: Path | None = None
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()

        self._build()
        self._poll()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Button(bar, text="Add files…", command=self.add_files).pack(side="left")
        ttk.Button(bar, text="Clear", command=self.clear_files).pack(side="left", padx=(6, 0))

        self.file_list = tk.Listbox(self, height=8, selectmode="extended")
        self.file_list.grid(row=1, column=0, sticky="nsew", pady=8)

        options = ttk.Frame(self)
        options.grid(row=2, column=0, sticky="ew")
        ttk.Label(options, text="Convert to:").pack(side="left")
        self.fmt = tk.StringVar(value=core.DEFAULT_OUTPUT)
        ttk.Combobox(
            options,
            textvariable=self.fmt,
            values=list(core.OUTPUT_FORMATS),
            state="readonly",
            width=8,
        ).pack(side="left", padx=6)
        self.dest_label = ttk.Label(options, text="Output: next to source")
        self.dest_label.pack(side="left", padx=(12, 6))
        ttk.Button(options, text="Choose…", command=self.choose_dest).pack(side="left")

        self.convert_button = ttk.Button(self, text="Convert", command=self.start)
        self.convert_button.grid(row=3, column=0, sticky="ew", pady=8)

        self.log = tk.Text(self, height=8, state="disabled", wrap="word")
        self.log.grid(row=4, column=0, sticky="nsew")
        self.rowconfigure(4, weight=1)

    def add_files(self) -> None:
        for name in filedialog.askopenfilenames(title="Select ebooks", filetypes=FILE_TYPES):
            path = Path(name)
            if path not in self.sources:
                self.sources.append(path)
                self.file_list.insert("end", path.name)

    def clear_files(self) -> None:
        self.sources.clear()
        self.file_list.delete(0, "end")

    def choose_dest(self) -> None:
        if name := filedialog.askdirectory(title="Output folder"):
            self.dest_dir = Path(name)
            self.dest_label.config(text=f"Output: {self.dest_dir.name}")

    def start(self) -> None:
        if not self.sources:
            self._write("Add at least one file.")
            return
        self.convert_button.state(["disabled"])
        threading.Thread(
            target=self._run, args=(list(self.sources), self.fmt.get(), self.dest_dir), daemon=True
        ).start()

    def _run(self, sources: list[Path], fmt: str, dest_dir: Path | None) -> None:
        for src in sources:
            self.events.put(("log", f"Converting {src.name} → {fmt}…"))
            result = core.convert_file(src, fmt, dest_dir)
            self.events.put(("log", f"  {'OK' if result.success else 'FAILED'}: {result.message}"))
        self.events.put(("done", ""))

    def _poll(self) -> None:
        while True:
            try:
                kind, text = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "done":
                self.convert_button.state(["!disabled"])
            else:
                self._write(text)
        self.after(100, self._poll)

    def _write(self, text: str) -> None:
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")


def main() -> None:
    root = tk.Tk()
    root.title("eConverter")
    root.geometry("560x520")
    icon = asset("icon.png")
    if icon.is_file():
        # Tk drops the icon if the image is garbage collected, so keep a reference.
        root.icon_image = tk.PhotoImage(file=str(icon))
        root.iconphoto(True, root.icon_image)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

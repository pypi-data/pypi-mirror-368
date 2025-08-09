"""Save a canvas."""

from pathlib import Path
from asciiasm.editor.canvas import Canvas


def save_image(canvas: Canvas, path: Path) -> None:
    """Saves rendered canvas to a file."""
    with path.open(mode="w", encoding="UTF-8") as f:
        f.write(canvas.serialise())


def save_data(canvas: Canvas, path: Path) -> None:
    """Save all work data to a directory."""
    for f_name, data in canvas.files().items():
        with (path / f_name).open(mode="w", encoding="UTF-8") as f:
            f.write(data.serialise())

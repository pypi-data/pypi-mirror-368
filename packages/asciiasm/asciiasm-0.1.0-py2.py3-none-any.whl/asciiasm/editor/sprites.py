"""Provide sprite utility.
Filling whitespace recognition and stripping of surrounding whitespace.
"""

class Sprite:
    """Represent a sprite that can be placed on a canvas."""

    name: str
    height: int
    width: int
    layer: int
    row: int
    column: int
    grid: list[list[str | None]]
    text: str

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self.height = len(line_list := text.split("\n"))
        self.width = max(map(len, line_list))
        self.grid = [[char for char in line] for line in line_list]

        self.transparentise_whitespace()

    def serialise(self) -> str:
        """Return a string representation of the sprite."""
        return self.text

    def transparentise_whitespace(self) -> None:
        """Strip outer whitespace and replace it with None."""
        orientations = {"left": config(True, 0, False, 1),
                        "right": config(True, self.width - 1, False, -1),
                        "top": config(False, 0, True, 1),
                        "bottom": config(False, self.height - 1, True, -1)}
        for __, values in orientations.items():
            for i in range(self.height
                           if values["takes height"]
                           else self.width):
                           # self.height, width of current line, width of current line
                j = values["j start"] # length of current line, 0, self.height
                try:
                    while (self.grid[i][j]
                           if (condition := not values["j height"])
                           else self.grid[j][i]) in {" ", None}: # i,j , j,i , j,i
                        self.grid[i if condition else j][j if condition else i] = None # same
                        j += values["sign"] # -1 for right and bottom
                except IndexError:
                    break


def config(*args):
    """Configure the four starting points for sprite transparentisation."""
    return {"takes height": args[0], "j start": args[1],
            "j height": args[2], "sign": args[3]}

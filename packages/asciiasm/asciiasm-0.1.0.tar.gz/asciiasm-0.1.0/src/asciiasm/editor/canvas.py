"""Provide canvas editing and rendering utility."""

from pathlib import Path
from .sprites import Sprite

class Canvas:
    """Canvas on which sprites are placed."""

    sprites: list[Sprite] = []
    used_layers: set[int] = set()

    def serialise(self) -> str:
        """Return a string representation of the canvas."""
        layers: dict[int, list[Sprite]] = {}
        layer_grids: dict[int, list[list[str | None]]] = {}
        max_layer = 0
        width = 0
        height = 0
        for sprite in self.sprites:
            try:
                # group sprites by layer
                layers[sprite.layer].append(sprite)
            except KeyError:
                layers.update({sprite.layer: [sprite]})
            # find dimensions of canvas
            if sprite.layer > max_layer:
                max_layer = sprite.layer
            if (y := sprite.row + sprite.height) > height:
                height = y
            if (x := sprite.column + sprite.width) > width:
                width = x
        # create a grid for each layer and fill it
        used_layer_nums = sorted(list(self.used_layers))
        for i in used_layer_nums:
            layer_grids.update({i: [[None for __ in range(width)] for __ in range(height)]})
            for sprite in layers[i]:
                # dumb approach for now: take each sprite and fill its area in the grid
                # TODO: check for overlaps
                for y, row in enumerate(sprite.grid, sprite.row):
                    for x, char in enumerate(row, sprite.column):
                        layer_grids[i][y][x] = char
        # create the string representation by:
        # 1. iterating through the cells of the final canvas
        # 2. find the first non-None character throughout all layers
        result_grid = [[" " for __ in range(width)] for __ in range(height)]
        for layer in sorted(used_layer_nums):
            for y in range(height):
                for x in range(width):
                    if (new_char := layer_grids[layer][y][x]) is not None:
                        result_grid[y][x] = new_char
        # 3. join characters into a string
        return "\n".join(["".join(row) for row in result_grid])


    def files(self) -> dict[Path, Sprite]:
        """Return a list of files to save as work progress."""
        return {Path(""): Sprite("name", "")}

    def add_sprite(self, sprite: Sprite, layer: int, row: int, column: int) -> None:
        """Add a sprite to the canvas."""
        sprite.layer, sprite.row, sprite.column = layer, row, column
        self.sprites.append(sprite)
        self.used_layers.add(layer)

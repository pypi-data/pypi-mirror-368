"""todo"""

from pathlib import Path
import sys
from unicurses import move, addstr, refresh, getstr, getmaxy, endwin, clear
from ..editor import canvas
from ..editor.sprites import Sprite
from ..files import load, save

class Session:
    sprites: dict[str, Sprite] = {}
    command_log: list[str] = []

    def __init__(self, scr) -> None:
        self.canvas = canvas.Canvas()
        self.scr = scr

    def take_input(self) -> str:
        clear()
        self.display_canvas()
        move(getmaxy(self.scr) - 1, 0)
        addstr("Enter command: ")
        refresh()
        command = getstr()
        return command

    def display_canvas(self):
        clear()
        move(0, 0)
        addstr(self.canvas.serialise())
        refresh()

    def execute(self, command: str) -> None:
        if command:
            self.command_log.append(command)
        command_words = command.split(" ")
        match " ".join(command_words[:2]):
            case "place sprite":
                self.canvas.add_sprite(
                    self.sprites[command_words[2]],
                    *[int(x) for x in command_words[3:6]]
                )
            case "save canvas":
                save.save_image(self.canvas, Path(command_words[2]))
            case "load sprite":
                sprite = load.load_sprite(Path(command_words[2]))
                self.sprites.update({sprite.name: sprite})
            case "exit tool":
                endwin()
                print(*["asciiasm: " + line for line in self.command_log], sep="\n")
                sys.exit(0)

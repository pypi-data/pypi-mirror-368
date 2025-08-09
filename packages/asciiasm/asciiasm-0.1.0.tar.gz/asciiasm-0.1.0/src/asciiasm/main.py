"""Main entry point for application."""

from unicurses import initscr, endwin, refresh, clear
from asciiasm.control import ui


def main():
    """Run the main application control flow."""
    stdscr = initscr()
    try:
        clear()
        refresh()
        session = ui.Session(stdscr)
        while True:
            command = session.take_input()
            session.execute(command)
            session.display_canvas()
    except Exception as e:
        endwin()
        print(*session.command_log, sep="\n")
        if not isinstance(e, KeyboardInterrupt):
            raise e


if __name__ == "__main__":
    main()

import curses

from hexterm.hex_game import HexGame
from hexterm.hex_ui import HexUI


def main(stdscr):
    game = HexGame()
    ui = HexUI(game)
    ui.run(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)

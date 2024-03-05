import curses
from typing import Any

from hexterm.game_states import MainMenu
from hexterm.hex_game import HexGame, STATE_EMPTY, STATE_PLAYERS


class HexUI:
    def __init__(self, game: HexGame):
        self.game = game
        self.current_state = MainMenu(self)
        self.init_colors()

        self.cell_filled = "⬢"
        self.cell_empty = "⬡"

    def init_colors(self):
        # Color setup
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Player 1
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  # Player 2
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Invalid move
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Neutral
        curses.init_pair(5, 247, curses.COLOR_BLACK)  # Grey
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Win path

        self.color_player_1 = curses.color_pair(1)
        self.color_player_2 = curses.color_pair(2)
        self.color_win_path = curses.color_pair(6)
        self.color_invalid = curses.color_pair(3)
        self.color_neutral = curses.color_pair(4)
        self.color_text = curses.color_pair(5)

    def draw_board(
        self,
        stdscr: Any,
        current_row: int,
        current_col: int,
        win_path: list = None,
        display_invalid: bool = True,
    ) -> None:
        """Draws the game board on the terminal.

        The board is drawn in the center of the terminal. The current cell is highlighted with the
        color of the player whose turn it is.

        Args:
            stdscr (curses.window): The window object to draw the game board on.
            win_path (list, optional): The winning path to highlight. Defaults to None. This is
                used to highlight the winning path at the end of the game.
            display_invalid (bool, optional): Whether to display the invalid move highlight.
                Defaults to True.
        """
        self.screen_height, self.screen_width = stdscr.getmaxyx()

        # calculate minimum terminal size needed to check if the terminal is too small
        min_height = self.game.num_rows + 7
        min_width = 2 * ((self.game.num_cols + 2) * 2 + self.game.num_rows + 2)

        if self.screen_height < min_height or self.screen_width < min_width:
            stdscr.clear()
            stdscr.addstr(
                self.screen_height // 2,
                self.screen_width // 2 - 10,
                "Terminal too small",
                self.color_invalid | curses.A_BOLD,
            )
            stdscr.refresh()
            return

        # Calculate the starting position to center the board
        start_y = (self.screen_height - self.game.num_rows) // 2
        start_x = (self.screen_width - ((2 * self.game.num_cols) + 4 + self.game.num_rows)) // 2

        stdscr.clear()
        # Draw the top row for showing player color
        for col in range(self.game.num_cols):
            pos_y = start_y
            pos_x = start_x + (col + 1) * 2
            stdscr.addstr(pos_y, pos_x, self.cell_filled, self.color_player_1)

        for row in range(self.game.num_rows):
            for col in range(self.game.num_cols):
                pos_y = start_y + (row + 1)
                pos_x = start_x + (col + 1) * 2 + (row + 1)

                # Draw the leftmost column for showing player color
                if col == 0:
                    stdscr.addstr(pos_y, pos_x - 2, self.cell_filled, self.color_player_2)

                cell = self.game.row_col_to_action_index(row, col)
                symbol = self.cell_empty if self.game.is_cell_empty(cell) else self.cell_filled
                cell_state = self.game.state[cell]
                if win_path and (row, col) in win_path:
                    color_pair = self.color_win_path
                elif row == current_row and col == current_col and win_path is None:
                    # Highlight the current cell
                    if cell_state != STATE_EMPTY and display_invalid:
                        color_pair = self.color_invalid
                    else:
                        color_pair = (
                            self.color_player_1
                            if self.game.current_player == STATE_PLAYERS[1]
                            else self.color_player_2
                        )
                elif cell_state == STATE_EMPTY:
                    color_pair = self.color_neutral
                elif cell_state == STATE_PLAYERS[1]:
                    color_pair = self.color_player_1
                elif cell_state == STATE_PLAYERS[2]:
                    color_pair = self.color_player_2
                else:
                    raise ValueError(f"Invalid cell state: {cell_state}")
                stdscr.addstr(pos_y, pos_x, symbol, color_pair)

                # Draw the rightmost column for showing player color
                if col == self.game.num_cols - 1:
                    stdscr.addstr(pos_y, pos_x + 2, self.cell_filled, self.color_player_2)

        # Draw the bottom row for showing player color
        for col in range(self.game.num_cols):
            pos_y = start_y + (self.game.num_rows + 1)
            pos_x = start_x + (col + 1) * 2 + (self.game.num_rows + 1)
            stdscr.addstr(pos_y, pos_x, self.cell_filled, self.color_player_1)

    def run(self, stdscr: Any) -> None:
        """Runs the game loop.

        Args:
            stdscr (curses.window): The window object to draw the game on.
        """
        curses.curs_set(0)
        stdscr.clear()
        stdscr.refresh()

        while True:
            self.current_state.render(stdscr)
            key = stdscr.getch()
            if key == ord("q"):
                break
            if self.current_state.process_input(key):
                self.current_state = self.current_state.next_state
            stdscr.refresh()
            if self.current_state is None:
                break

        stdscr.clear()
        stdscr.refresh()
        curses.endwin()

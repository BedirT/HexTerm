import curses

from hexterm.hex_game import HexGame

WIN_BLINK_DURATION = 200  # Duration for blinking the winning path
WIN_BLINK_AMOUNT = 5  # Number of times to blink the winning path


class GameState:
    def __init__(self, hex_ui):
        self.hex_ui = hex_ui
        self.next_state = None
        self.highlighted = 0

    def process_input(self, key):
        raise NotImplementedError

    def render(self, stdscr):
        raise NotImplementedError

    def _update_screen_dimensions(self, stdscr):
        self.screen_height, self.screen_width = stdscr.getmaxyx()


class MainMenu(GameState):
    def process_input(self, key):
        if key == curses.KEY_UP and self.highlighted > 0:
            self.highlighted -= 1
        elif key == curses.KEY_DOWN and self.highlighted < len(self.menu_items) - 1:
            self.highlighted += 1
        elif key in [curses.KEY_ENTER, ord("\n"), ord(" ")]:
            if self.highlighted == 0:
                self.next_state = GameInitMenu(self.hex_ui)
            elif self.highlighted == 1:
                self.next_state = Instructions(self.hex_ui)
            elif self.highlighted == 2:
                self.next_state = None
            return True
        return False

    def render(self, stdscr):
        self._update_screen_dimensions(stdscr)
        stdscr.clear()

        self.menu_items = ["Start Game", "Instructions", "Quit"]

        for i, item in enumerate(self.menu_items):
            x = self.screen_width // 2 - len(item) // 2
            y = self.screen_height // 2 - len(self.menu_items) // 2 + i
            if i == self.highlighted:
                stdscr.addstr(
                    y, x, item, curses.A_REVERSE | self.hex_ui.color_neutral | curses.A_BOLD
                )
            else:
                stdscr.addstr(y, x, item, self.hex_ui.color_neutral)


class GameInitMenu(GameState):
    def process_input(self, key):
        if key == curses.KEY_UP and self.highlighted > 0:
            self.highlighted -= 1
        elif key == curses.KEY_DOWN and self.highlighted < len(self.menu_items) - 1:
            self.highlighted += 1
        elif key in [curses.KEY_ENTER, ord("\n"), ord(" ")]:
            if self.highlighted == len(self.menu_items) - 1:
                self.next_state = MainMenu(self.hex_ui)
            else:
                size = int(self.menu_items[list(self.menu_items.keys())[self.highlighted]])
                self.hex_ui.game = HexGame(num_cols=size, num_rows=size)
                self.next_state = Gameplay(self.hex_ui)
            return True
        return False

    def render(self, stdscr):
        self._update_screen_dimensions(stdscr)
        stdscr.clear()

        self.menu_items = {
            "4x4": "4",
            "5x5": "5",
            "7x7": "7",
            "9x9": "9",
            "11x11": "11",
            "13x13": "13",
            "15x15": "15",
            "Back": "0",
        }

        for i, item in enumerate(self.menu_items):
            x = self.screen_width // 2 - len(item) // 2
            y = self.screen_height // 2 - len(self.menu_items) // 2 + i
            if i == self.highlighted:
                stdscr.addstr(
                    y, x, item, curses.A_REVERSE | self.hex_ui.color_neutral | curses.A_BOLD
                )
            else:
                stdscr.addstr(y, x, item, self.hex_ui.color_neutral)


class Gameplay(GameState):
    def __init__(self, hex_ui):
        super().__init__(hex_ui)
        if self.hex_ui.game.history:
            self.current_row, self.current_col = self.hex_ui.game.index_to_row_col(
                self.hex_ui.game.history[-1]
            )
        else:
            self.current_row, self.current_col = 0, 0
        self.player = self.hex_ui.game.current_player

    def process_input(self, key: int) -> bool:
        if key == curses.KEY_UP and self.current_row > 0:
            self.current_row -= 1
        elif key == curses.KEY_DOWN and self.current_row < self.hex_ui.game.num_rows - 1:
            self.current_row += 1
        elif key == curses.KEY_LEFT and self.current_col > 0:
            self.current_col -= 1
        elif key == curses.KEY_RIGHT and self.current_col < self.hex_ui.game.num_cols - 1:
            self.current_col += 1
        elif key in [curses.KEY_ENTER, ord("\n"), ord(" ")]:
            action = self.hex_ui.game.row_col_to_action_index(self.current_row, self.current_col)
            _, _, done, extra = self.hex_ui.game.step(action)
            if done == -1:  # Invalid move
                return False
            elif done > 0:
                self.next_state = WinEffect(self.hex_ui, extra['win_path'], done)
                return True
        return False

    def render(self, stdscr):
        self._update_screen_dimensions(stdscr)
        stdscr.clear()

        self.hex_ui.draw_board(stdscr, self.current_row, self.current_col)

        # Add HUD elements
        hud_str_0 = f"Player {self.player}'s turn."
        hud_str_1 = (
            "Use arrow keys to navigate the board. Press spacebar or enter to place a piece. "
            "Press 'q' to quit the game."
        )
        hud_str_2 = "Player 1 Connects Top to Bottom, and plays "
        hud_str_3 = "Player 2 Connects Left to Right, and plays "

        gap_between_hud = 4
        player_info_line_number = self.screen_height - 1

        total_length_hud_2_and_3 = len(hud_str_2) + len(hud_str_3) + gap_between_hud + 4

        side_by_side = self.screen_width >= total_length_hud_2_and_3

        if side_by_side:
            start_pos_hud_2 = (self.screen_width - total_length_hud_2_and_3) // 2
            start_pos_hud_3 = start_pos_hud_2 + len(hud_str_2) + gap_between_hud + 2
            y_pos_hud_2 = y_pos_hud_3 = player_info_line_number
        else:
            start_pos_hud_2 = (self.screen_width - len(hud_str_2)) // 2
            start_pos_hud_3 = (self.screen_width - len(hud_str_3)) // 2
            y_pos_hud_2 = player_info_line_number - 1
            y_pos_hud_3 = player_info_line_number

        stdscr.addstr(y_pos_hud_2, start_pos_hud_2, hud_str_2, self.hex_ui.color_text)
        stdscr.addstr(
            y_pos_hud_2,
            start_pos_hud_2 + len(hud_str_2),
            self.hex_ui.cell_filled,
            self.hex_ui.color_player_1,
        )

        stdscr.addstr(y_pos_hud_3, start_pos_hud_3, hud_str_3, self.hex_ui.color_text)
        stdscr.addstr(
            y_pos_hud_3,
            start_pos_hud_3 + len(hud_str_3),
            self.hex_ui.cell_filled,
            self.hex_ui.color_player_2,
        )

        stdscr.addstr(
            0,
            self.screen_width // 2 - len(hud_str_0) // 2,
            hud_str_0,
            self.hex_ui.color_text | curses.A_BOLD,
        )
        stdscr.addstr(
            1,
            self.screen_width // 2 - len(hud_str_1) // 2,
            hud_str_1,
            self.hex_ui.color_text,
        )


class GameOver(GameState):
    def process_input(self, key):
        if key == curses.KEY_UP and self.highlighted > 0:
            self.highlighted -= 1
        elif key == curses.KEY_DOWN and self.highlighted < len(self.menu_items) - 1:
            self.highlighted += 1
        elif key in [curses.KEY_ENTER, ord("\n"), ord(" ")]:
            if self.highlighted == 0:
                self.next_state = GameInitMenu(self.hex_ui)
            elif self.highlighted == 1:
                self.next_state = MainMenu(self.hex_ui)
            return True
        return False

    def render(self, stdscr):
        self._update_screen_dimensions(stdscr)
        stdscr.clear()

        title = "Do you want to play again?"
        self.menu_items = ["Yes", "No"]

        stdscr.addstr(
            self.screen_height // 2 - 2,
            self.screen_width // 2 - len(title) // 2,
            title,
            self.hex_ui.color_neutral | curses.A_BOLD,
        )
        for i, item in enumerate(self.menu_items):
            x = self.screen_width // 2 - len(item) // 2
            y = self.screen_height // 2 - len(self.menu_items) // 2 + i
            if i == self.highlighted:
                stdscr.addstr(y, x, item, self.hex_ui.color_text | curses.A_BOLD | curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, item, self.hex_ui.color_text)


class WinEffect(GameState):
    def __init__(self, hex_ui, win_path: list, winner: int):
        super().__init__(hex_ui)
        self.path = win_path
        self.player = winner

    def process_input(self, key):
        self.next_state = GameOver(self.hex_ui)
        return True

    def render(self, stdscr):
        stdscr.clear()
        last_cell = self.path[-1]
        for _ in range(WIN_BLINK_AMOUNT):
            self.hex_ui.draw_board(
                stdscr, last_cell[0], last_cell[1], self.path, display_invalid=False
            )
            stdscr.refresh()
            curses.napms(WIN_BLINK_DURATION)
            self.hex_ui.draw_board(stdscr, last_cell[0], last_cell[1], display_invalid=False)
            stdscr.refresh()
            curses.napms(WIN_BLINK_DURATION)

        self._update_screen_dimensions(stdscr)

        # Display the winning message at the bottom of the screen
        messages_to_display = [
            f"Player {self.player} wins!",
            "Press any key to continue",
        ]

        for i, message in enumerate(messages_to_display):
            x = self.screen_width // 2 - len(message) // 2
            y = self.screen_height - 2 + i
            stdscr.addstr(y, x, message, curses.color_pair(3))


class Instructions(GameState):
    def process_input(self, key):
        if key in [curses.KEY_ENTER, ord("\n"), ord(" ")]:
            self.next_state = MainMenu(self.hex_ui)
            return True
        return False

    def render(self, stdscr):
        self._update_screen_dimensions(stdscr)
        stdscr.clear()

        instructions = [
            "Use arrow keys to navigate the board",
            "Press spacebar to place a piece",
            "Press 'q' to quit the game",
            "The first player to connect their sides wins",
            "",
            "Press any key to continue",
        ]

        for i, instruction in enumerate(instructions):
            x = self.screen_width // 2 - len(instruction) // 2
            y = self.screen_height // 2 - len(instructions) // 2 + i
            stdscr.addstr(y, x, instruction, self.hex_ui.color_text)

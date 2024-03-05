# ! Check num_cols and num_rows with different values
from collections import deque
from typing import Tuple
import numpy as np


# BOARD_STATES
STATE_EMPTY = 0 # DO NOT TOUCH THIS VALUE - Numpy dependent for speed
STATE_PLAYERS = {
    1: 1,
    2: 2,
}

class HexGame:
    """HexGame class represents a game of Hex.

    Attributes:
        num_rows (int): The number of rows in the game board.
        num_cols (int): The number of columns in the game board.
        state (np.ndarray): The game state. It's a 1D array of size num_rows * num_cols. Represents
            the board of the game.
        current_player (int): The current player's number.
        history (list): A list of the moves made in the game.
        done (bool): A boolean indicating if the game has ended.
        winner (int): The number of the winning player.
        state (np.ndarray): The current state of the game.

    Methods:
        action_to_key: Converts the row and column indices to a unique string representation.
        key_to_action: Converts the string representation to row and column indices.
        step: Makes a move on the game board at the specified row and column.
        reset: Resets the game.
        get_info_state: Returns the information state.
        history_vector: Returns the vectorized version of the history.
        is_valid: Checks if a move is valid at the specified row and column.
        is_terminal: Checks if the game has reached a terminal state for the specified player using
            BFS.
        _bfs: Performs a breadth-first search to find the shortest path for the specified player.
    """

    def __init__(self, num_rows: int = 0, num_cols: int = 0):
        self.num_cols = num_cols
        self.num_rows = num_rows

        self.reset()

    def action_repr_to_row_col(self, action: str) -> Tuple[int, int]:
        """Converts the string representation to row and column indices.

        Args:
            action (str): String representation of the action.

        Returns:
            tuple: Row and column indices.
        """
        col = ord(action[0].upper()) - 65
        row = int(action[1:]) - 1
        return row, col

    def action_index_to_repr(self, action: int) -> str:
        """Converts the action to a string representation.

        Args:
            action (int): The action to convert.

        Returns:
            str: The string representation of the action.
        """
        row, col = self.action_index_to_row_col(action)
        return f"{chr(col + 65)}{row + 1}"

    def row_col_to_action_index(self, row: int, col: int) -> int:
        """Converts the row and column indices to an action index.

        Args:
            row (int): The row index.
            col (int): The column index.

        Returns:
            int: The action index.
        """
        return row * self.num_cols + col

    def action_index_to_row_col(self, action: int) -> Tuple[int, int]:
        """Converts the action index to row and column indices.

        Args:
            action (int): The action index.

        Returns:
            tuple: Row and column indices.
        """
        return action // self.num_cols, action % self.num_cols

    def is_cell_empty(self, index: int) -> bool:
        """Checks if the cell index is empty.

        Args:
            cell (int): The cell to check.

        Returns:
            bool: True if the cell is empty, False otherwise.
        """
        return self.state[index] == STATE_EMPTY

    def step(self, action: int) -> Tuple[np.ndarray, int, bool, dict]:
        """Takes a step in the environment.

        Args:
            action (int): The action to take.

        Returns:
            Tuple[np.ndarray, float, bool, dict]: The next state, the reward, whether the game is
                done, and additional info.
        """
        action_repr = self.action_index_to_repr(action)
        if self.is_valid(action):
            self._update_game_state(action, action_repr)
            self.done, path = self.is_terminal(self.current_player)
            if self.done:
                self.winner = self.current_player
                return self.get_info_state(), 1, True, {"win_path": path}
            self.update_player()
            return self.get_info_state(), 0, False, {}
        return self.get_info_state(), -1, False, {} # Invalid move

    def reset(self) -> None:
        """Resets the game."""
        self.state = np.zeros(self.num_rows * self.num_cols, dtype=int) # only the board

        self.current_player = 1
        self.history = []

        self.done = False
        self.winner = None

        return self.get_info_state()

    def _update_game_state(self, action: int, action_repr: str) -> None:
        """Updates the game state after a valid move is made.

        Args:
            action (int): The action to take.
            action_repr (str): The string representation of the action.
        """
        self.state[action] = self.current_player
        self.history.append(action_repr)

    def get_opponent(self, player: int) -> int:
        """Returns the opponent of the specified player.

        Args:
            player (int): The player index.

        Returns:
            int: The opponent index.
        """
        return STATE_PLAYERS[3 - player]

    def update_player(self):
        """Updates the current player."""
        self.current_player = self.get_opponent(self.current_player)

    def get_info_state(self, player: int = -1) -> list:
        """Returns the information state."""
        return [list(self.state), self.current_player]

    def history_vector(self) -> list:
        """Returns the vectorized version of the history."""
        v = []
        for a in self.history:
            row, col = self.action_repr_to_row_col(a)
            v.append(self.row_col_to_action_index(row, col))
        return v

    def is_valid(self, action: int) -> bool:
        """Checks if the action is a valid move.

        Args:
            action (int): The action to take.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        row, col = self.action_index_to_row_col(action)
        return 0 <= row < self.num_rows and \
            0 <= col < self.num_cols and self.state[action] == STATE_EMPTY

    def is_terminal(self, player):
        """Checks if the game has reached a terminal state for the specified player using BFS.

        Args:
            player (int): The player number (1 or 2).

        Returns:
            tuple: A tuple containing a boolean value indicating if the game has ended,
                   and the winning path if the game has ended, otherwise returns (False, None).
        """
        path = self._bfs(player)
        return len(path) > 0, path

    def _bfs(self, player):
        """
        Performs a breadth-first search to find the shortest path for the specified player.

        Args:
            player (int): The player. Must be one of the STATE_PLAYERS values.

        Returns:
            list: The shortest path if one exists, otherwise an empty list. The path is a list of
                tuples containing the row and column indices of the path.
        """
        start_cells = (
            [(0, c) for c in range(self.num_cols)]
            if player == 1
            else [(r, 0) for r in range(self.num_rows)]
        )
        target_row = self.num_rows - 1 if player == STATE_PLAYERS[1] else None
        target_col = None if player == STATE_PLAYERS[1] else self.num_cols - 1
        visited = set()
        queue = deque(
            [
                (r, c, [(r, c)])
                for r, c in start_cells
                if self.state[self.row_col_to_action_index(r, c)] == player
            ]
        )

        while queue:
            r, c, path = queue.popleft()
            if (player == STATE_PLAYERS[1] and r == target_row) or \
               (player == STATE_PLAYERS[2] and c == target_col):
                return path  # Found a path to the other side

            for nr, nc in [
                (r - 1, c),
                (r + 1, c),
                (r, c - 1),
                (r, c + 1),
                (r - 1, c + 1),
                (r + 1, c - 1),
            ]:
                if 0 <= nr < self.num_rows and 0 <= nc < self.num_cols and (nr, nc) not in visited:
                    if self.state[self.row_col_to_action_index(nr, nc)] == player:
                        queue.append((nr, nc, path + [(nr, nc)]))
                        visited.add((nr, nc))

        return []  # No path found

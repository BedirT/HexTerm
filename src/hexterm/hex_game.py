# ! Check x_size and y_size with different values
from collections import deque


class HexGame:
    """
    HexGame class represents a game of Hex.

    Attributes:
        x_size (int): The size of the game board in the x-direction.
        y_size (int): The size of the game board in the y-direction.
        board (list): The game board represented as a 2D list.
        player_to_play (int): The player number (1 or 2) who is currently playing.

    Methods:
        make_move(row, col): Makes a move on the game board at the specified row and column.
        is_valid_move(row, col): Checks if a move is valid at the specified row and column.
        is_terminal(player): Checks if the game has reached a terminal state for the specified
            player.
        dfs(r, c, player, visited, win_path): Performs a depth-first search to check for a winning
            path.
    """

    def __init__(self, size=11):
        self.x_size = size
        self.y_size = size
        self.board = [0 for _ in range(self.x_size * self.y_size)]
        self.player_to_play = 1
        self.history = []  # game history

    def row_col_to_index(self, row, col):
        """
        Converts the row and column indices to a single index.

        Args:
            row (int): The row index.
            col (int): The column index.

        Returns:
            int: The single index.
        """
        return row * self.x_size + col

    def index_to_row_col(self, index):
        """
        Converts the single index to row and column indices.

        Args:
            index (int): The single index.

        Returns:
            tuple: A tuple containing the row and column indices.
        """
        return index // self.x_size, index % self.x_size

    def action(self, row, col):
        """
        Makes a move on the game board at the specified row and column.

        Args:
            row (int): The row index of the move.
            col (int): The column index of the move.

        Returns:
            tuple: A tuple containing the winner (1 or 2) and the winning path if the game has
                ended, otherwise returns (0, None).
        """
        move_idx = self.row_col_to_index(row, col)
        if self.is_valid_move(move_idx):
            self.board[move_idx] = self.player_to_play
            if_end, path = self.is_terminal(self.player_to_play)
            if if_end:
                return self.player_to_play, path
            self.player_to_play = 3 - self.player_to_play  # Switch players
            self.history.append(move_idx)
            return 0, None  # No winner yet
        return -1, None  # Invalid move

    def is_valid_move(self, idx):
        """Checks if a move is valid at the specified index.

        Args:
            idx (int): The index of the move.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        row, col = self.index_to_row_col(idx)
        return 0 <= row < self.x_size and 0 <= col < self.y_size and self.board[idx] == 0

    def is_terminal(self, player):
        """Checks if the game has reached a terminal state for the specified player using A*.

        Args:
            player (int): The player number (1 or 2).

        Returns:
            tuple: A tuple containing a boolean value indicating if the game has ended,
                   and the winning path if the game has ended, otherwise returns (False, None).
        """
        path = self.bfs(player)
        return len(path) > 0, path

    def bfs(self, player):
        """
        Performs a breadth-first search to find the shortest path for the specified player.

        Args:
            player (int): The player number (1 or 2).

        Returns:
            list: The shortest path if one exists, otherwise an empty list.
        """
        start_cells = (
            [(0, c) for c in range(self.x_size)]
            if player == 1
            else [(r, 0) for r in range(self.y_size)]
        )
        target_row = self.y_size - 1 if player == 1 else None
        target_col = None if player == 1 else self.x_size - 1
        visited = set()
        queue = deque(
            [
                (r, c, [(r, c)])
                for r, c in start_cells
                if self.board[self.row_col_to_index(r, c)] == player
            ]
        )

        while queue:
            r, c, path = queue.popleft()
            if (player == 1 and r == target_row) or (player == 2 and c == target_col):
                return path  # Found a path to the other side

            for nr, nc in [
                (r - 1, c),
                (r + 1, c),
                (r, c - 1),
                (r, c + 1),
                (r - 1, c + 1),
                (r + 1, c - 1),
            ]:
                if 0 <= nr < self.y_size and 0 <= nc < self.x_size and (nr, nc) not in visited:
                    idx = self.row_col_to_index(nr, nc)
                    if self.board[idx] == player:
                        queue.append((nr, nc, path + [(nr, nc)]))
                        visited.add((nr, nc))

        return []  # No path found

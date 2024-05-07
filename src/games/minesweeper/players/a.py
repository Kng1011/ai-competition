from games.minesweeper.player import MinesweeperPlayer
from games.minesweeper.state import MinesweeperState
from games.state import State


class AMinesweeperPlayer(MinesweeperPlayer):

    def __init__(self, name):
        super().__init__(name)


    def get_action(self, state:MinesweeperState):
        grid = state.get_grid()
        num_rows = state.get_num_rows()
        num_cols = state.get_num_cols()
        possible_actions = list(state.get_possible_actions())

        # First, look for safe reveals
        for action in possible_actions:
            row, col = action.get_row(), action.get_col()
            if AMinesweeperPlayer.is_safe_reveal(grid, row, col, num_rows, num_cols):
                return action

            prob = AMinesweeperPlayer.calculate_probabilities(grid, action, num_rows, num_cols)
            grid[row][col] = prob

        min_probability = float('inf')

        for row in range(num_rows):
            for col in range(num_cols):
                if grid[row][col] < min_probability:
                    min_probability = grid[row][col]

            # Encontrar ação correspondente ao menor valor de probabilidade
        for action in possible_actions:
            row1, col1 = action.get_row(), action.get_col()
            if grid[row1][col1] == min_probability:
                return action



    @staticmethod
    def calculate_probabilities(grid, action, num_rows, num_cols):
        row, col = action.get_row(), action.get_col()
        if grid[row][col] != MinesweeperState.EMPTY_CELL:
            return float('inf')  # Already revealed or marked

        adjacent_mines = 0
        prob = 0
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if grid[r][c] > 0:  # Cell is a number
                    if grid[r][c] == -2:
                        adjacent_mines += 1
                    for rr in range(max(0, r - 1), min(row, r + 2)):
                        for cc in range(max(0, c - 1), min(col, c + 2)):
                            if grid[rr][cc] > 0:
                                if grid[rr][cc] == -2:
                                    adjacent_mines += 1
                    prob = adjacent_mines / 8

        return prob

    def event_action(self, pos: int, action, new_state: State):
        # ignore
        pass

    def event_end_game(self, final_state: State):
        # ignore
        pass

    @staticmethod
    def count_unrevealed_neighbors(grid, row, col, num_rows, num_cols):
        count = 0
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if (r != row or c != col) and grid[r][c] == MinesweeperState.EMPTY_CELL:
                    count += 1
        return count

    @staticmethod
    def is_safe_reveal(grid, row, col, num_rows, num_cols):
        if grid[row][col] != MinesweeperState.EMPTY_CELL:
            return False  # Cell already revealed or marked

        # Check all neighbors for mine indicators
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if grid[r][c] > 0:  # Cell is a number
                    if AMinesweeperPlayer.count_unrevealed_neighbors(grid, r, c, num_rows, num_cols) == grid[r][c]:
                        return True  # Safe to reveal
        return False

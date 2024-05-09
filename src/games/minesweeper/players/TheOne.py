import random
from random import choice

from games.minesweeper.player import MinesweeperPlayer
from games.minesweeper.state import MinesweeperState
from games.minesweeper.action import MinesweeperAction

from games.state import State


class OneMinesweeperPlayer(MinesweeperPlayer):

    def __init__(self, name):
        super().__init__(name)

    def get_action(self, state: MinesweeperState):
        grid = state.get_grid()
        num_rows = state.get_num_rows()
        num_cols = state.get_num_cols()
        possible_actions = list(state.get_possible_actions())

        # Priority: Check for early-game safe reveals (corner/edge cells)
        if len(possible_actions) >= 42:
            for action in possible_actions:
                if (action.get_row() == 0 or action.get_row() == state.get_num_rows() - 1) and (
                        action.get_col() == 0 or action.get_col() == state.get_num_cols() - 1):
                    return action

        # Risk-based selection for non-early-game stages
        risk_groups = {}
        for action in possible_actions:
            row, col = action.get_row(), action.get_col()
            risk = self.calculate_risk(grid, action, num_rows, num_cols)
            if risk not in risk_groups:
                risk_groups[risk] = []
            risk_groups[risk].append(action)

        # Identify minimum risk level
        min_risk = min(risk_groups.keys())

        # If all actions have the same risk, choose randomly
        if len(risk_groups) == 1:
            return random.choice(possible_actions)

        # Select actions from the lowest risk group with probability bias
        low_risk_actions = risk_groups[min_risk]
        weights = [1 + 0.1 * (i - len(low_risk_actions) + 1) for i in range(len(low_risk_actions))]

        min_weight = 1e-6
        weights = [max(w, min_weight) for w in weights]
        action = random.choices(low_risk_actions, weights=weights)[0]
        return action

    @staticmethod
    def is_safe_reveal(grid, row, col, num_rows, num_cols):
        if grid[row][col] != MinesweeperState.EMPTY_CELL:
            return False  # Cell already revealed or marked

        # Check all neighbors for mine indicators
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if grid[r][c] > 0:  # Cell is a number
                    if OneMinesweeperPlayer.count_unrevealed_neighbors(grid, r, c, num_rows, num_cols) == grid[r][c]:
                        return True  # Safe to reveal
        return False

    @staticmethod
    def count_unrevealed_neighbors(grid, row, col, num_rows, num_cols):
        count = 0
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if (r != row or c != col) and grid[r][c] == MinesweeperState.EMPTY_CELL:
                    count += 1
        return count

    @staticmethod
    def calculate_mine_probability(risk: float, total_neighbors: int) -> float:
        return risk / total_neighbors if total_neighbors > 0 else 0

    def event_action(self, pos: int, action, new_state: State):
        # ignore
        pass

    def event_end_game(self, final_state: State):
        # ignore
        pass

    @staticmethod
    def calculate_cell_risk( grid, row, col, num_rows, num_cols):
        """
        Calculates the risk associated with revealing a cell at the given coordinates.

        Args:
            grid: The Minesweeper game grid.
            row: The row index of the cell.
            col: The column index of the cell.
            num_rows: The total number of rows in the grid.
            num_cols: The total number of columns in the grid.

        Returns:
            The calculated risk score (float).
        """

        if grid[row][col] != MinesweeperState.EMPTY_CELL:
            return float('inf')  # Already revealed or marked

        risk = 0
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if grid[r][c] > 0:  # Cell is a number
                    distance = abs(r - row) + abs(c - col)
                    probability = grid[r][c] * (1 / distance)
                    risk += OneMinesweeperPlayer.calculate_mine_probability(probability, 1)
                elif grid[r][c] == MinesweeperState.EMPTY_CELL:
                    distance = abs(r - row) + abs(c - col)
                    risk += 0.1 * (1 / (distance + 1e-9))

        # Fallback risk if no info from neighbors
        if risk == 0:
            risk = OneMinesweeperPlayer.count_unrevealed_neighbors(grid, row, col, num_rows, num_cols)

        return risk

    # Usage in the `calculate_risk` function:
    @staticmethod
    def calculate_risk(grid, action, num_rows, num_cols):
        row, col = action.get_row(), action.get_col()
        return OneMinesweeperPlayer.calculate_cell_risk(grid, row, col, num_rows, num_cols)

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
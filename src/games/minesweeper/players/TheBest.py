import random
from random import choice

from games.minesweeper.player import MinesweeperPlayer
from games.minesweeper.state import MinesweeperState
from games.minesweeper.action import MinesweeperAction
from games.state import State


class BestMinesweeperPlayer(MinesweeperPlayer):

    def __init__(self, name):
        super().__init__(name)

    def get_action(self, state: MinesweeperState):
        grid = state.get_grid()
        num_rows = state.get_num_rows()
        num_cols = state.get_num_cols()
        possible_actions = list(state.get_possible_actions())


        if len(possible_actions) >= 42:
            for action in possible_actions:
                if (action.get_row() == 0 or action.get_row() == state.get_num_rows() - 1) and (
                        action.get_col() == 0 or action.get_col() == state.get_num_cols() - 1):
                    return action

        # If no corner/edge cells or past early game stage, use risk-based selection
        risk_groups = {}
        for action in possible_actions:
            risk = self.calculate_risk(grid, action, num_rows, num_cols)
            if risk not in risk_groups:
                risk_groups[risk] = []
            risk_groups[risk].append(action)

        # Identify the minimum risk level
        min_risk = min(risk_groups.keys())

        # If only one risk level (all actions have the same risk), choose randomly
        if len(risk_groups) == 1:
            return random.choice(possible_actions)

        # Select actions from the lowest risk group
        low_risk_actions = risk_groups[min_risk]

        # Introduce probability bias towards lower risk within the group
        # (Here, a simple linear weighting is used)
        # Introduce probability bias towards lower risk within the group
        # (Here, a steeper linear weighting is used)
        weights = [1 + 0.2 * (i - len(low_risk_actions) + 1) for i in
                   range(len(low_risk_actions))]  # Steeper slope for higher bias

        # OR (exponential weighting for even higher bias)
        # weights = [math.exp(i * 0.5) for i in range(len(low_risk_actions))]

        min_weight = 0.01  # Increased minimum weight for larger weight difference
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
                    if BestMinesweeperPlayer.count_unrevealed_neighbors(grid, r, c, num_rows, num_cols) == grid[r][c]:
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
    def calculate_risk(grid, action, num_rows, num_cols):
        row, col = action.get_row(), action.get_col()
        if grid[row][col] != MinesweeperState.EMPTY_CELL:
            return float('inf')  # Already revealed or marked

        risk = 0
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if grid[r][c] > 0:  # Cell is a number
                    distance = abs(r - row) + abs(c - col)  # Manhattan distance
                    probability = grid[r][c] * (1 / distance)  # Weight based on distance
                    risk += BestMinesweeperPlayer.calculate_mine_probability(probability, 1)
                elif grid[r][c] == MinesweeperState.EMPTY_CELL:
                    distance = abs(r - row) + abs(c - col)  # Manhattan distance
                    risk += 0.1 * (1 / (distance + 1e-9))  # Penalty for unrevealed neighbors

        revealed_neighbors = BestMinesweeperPlayer.get_revealed_neighbors(grid, row, col, num_rows, num_cols)
        risk += BestMinesweeperPlayer.analyze_revealed_cell_distribution(revealed_neighbors, grid)

        num_mines_in_neighborhood = BestMinesweeperPlayer.count_mines_in_neighborhood(grid, row, col, num_rows, num_cols)
        risk += num_mines_in_neighborhood * 0.1

        num_unrevealed_neighbors = BestMinesweeperPlayer.count_unrevealed_neighbors(grid, row, col, num_rows, num_cols)
        risk += num_unrevealed_neighbors * 0.05

        # If no risk indication from neighbors, consider the number of unrevealed neighbors as a fallback risk measure
        if risk == 0:
            risk = BestMinesweeperPlayer.count_unrevealed_neighbors(grid, row, col, num_rows, num_cols)

        return risk

    @staticmethod
    def calculate_mine_probability(risk: float, total_neighbors: int) -> float:
        return risk / total_neighbors if total_neighbors > 0 else 0

    @staticmethod
    def get_revealed_neighbors(grid, row, col, num_rows, num_cols):
        """
        Gets the coordinates of all revealed neighbors of the given cell.

        Args:
            grid: The Minesweeper game grid.
            row: The row index of the target cell.
            col: The column index of the target cell.
            num_rows: The total number of rows in the grid.
            num_cols: The total number of columns in the grid.

        Returns:
            A list of coordinates (tuples) of revealed neighbors.
        """
        revealed_neighbors = []
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if (r != row or c != col) and grid[r][c] != MinesweeperState.EMPTY_CELL:
                    revealed_neighbors.append((r, c))
        return revealed_neighbors

    @staticmethod
    def analyze_revealed_cell_distribution(revealed_neighbors, grid):
        """
        Analyzes the distribution of revealed cell values in the given list.

        Args:
            revealed_neighbors: A list of coordinates (tuples) of revealed neighbors.

        Returns:
            A risk score based on the distribution of revealed cell values.
        """
        if not revealed_neighbors:
            return 0  # No revealed neighbors, no additional risk


        total_value = sum(grid[row][col] for row, col in revealed_neighbors)
        average_value = total_value / len(revealed_neighbors)
        return average_value * 0.2  # Adjust weight as needed (e.g., 0.2 for moderate influence)

    @staticmethod
    def count_mines_in_neighborhood( grid, row, col, num_rows, num_cols):
        count = 0
        for r in range(max(0, row - 1), min(num_rows, row + 2)):
            for c in range(max(0, col - 1), min(num_cols, col + 2)):
                if grid[r][c] == -2:
                    count += 1
        return count

    def event_action(self, pos: int, action, new_state: State):
        # ignore
        pass

    def event_end_game(self, final_state: State):
        # ignore
        pass


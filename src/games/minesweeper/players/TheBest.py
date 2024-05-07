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
                    risk += grid[r][c] * (1 / distance)  # Weight based on distance

        # If no risk indication from neighbors, consider the number of unrevealed neighbors as a fallback risk measure
        if risk == 0:
            risk = BestMinesweeperPlayer.count_unrevealed_neighbors(grid, row, col, num_rows, num_cols)

        return risk


    def event_action(self, pos: int, action, new_state: State):
        # ignore
        pass

    def event_end_game(self, final_state: State):
        # ignore
        pass

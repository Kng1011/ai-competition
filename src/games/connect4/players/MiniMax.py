import math
import random
from random import choice
from games.connect4.result import Connect4Result
from games.connect4.action import Connect4Action
from games.connect4.player import Connect4Player
from games.connect4.state import Connect4State
from games.state import State


class MiniMaxConnect4Player(Connect4Player):

    def __init__(self, name):
        super().__init__(name)
        self.memo = {}  # Initialize the memo attribute

    def minimax(self, state: Connect4State, depth, alpha, beta, maximizingPlayer):
        pos = self.get_current_pos()
        current_player = state.get_acting_player()

        # Check if the result is in memo
        state_key = str(state.get_grid()) + str(depth) + str(alpha) + str(beta) + str(maximizingPlayer)
        if state_key in self.memo:
            return self.memo[state_key]

        if depth == 0 or state.is_finished():
            result = state.get_result(pos)
            if result is not None:
                if result == Connect4Result.WIN:
                    self.event_result(None, Connect4Result.WIN)
                    return None, 100000000000000
                elif result == Connect4Result.LOOSE:
                    self.event_result(None, Connect4Result.LOoSE)
                    return None, -10000000000000
                else:  # Draw
                    self.event_result(None, Connect4Result.DRAW)
                    return None, 0
            else:  # Depth is zero
                return None, MiniMaxConnect4Player.score_position(state.get_grid(), current_player)

        # Order moves: prioritize the center columns
        possible_actions = sorted(state.get_possible_actions(),
                                  key=lambda action: abs(action.get_col() - state.get_num_cols() // 2))

        if maximizingPlayer:
            value = -math.inf
            column = random.choice(range(state.get_num_cols()))
            for action in possible_actions:
                next_state = state.clone()
                next_state.update(action)
                new_score = self.minimax(next_state, depth - 1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = action.get_col()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            result = column, value
        else:  # Minimizing player
            value = math.inf
            column = random.choice(range(state.get_num_cols()))
            for action in possible_actions:
                next_state = state.clone()
                next_state.update(action)
                new_score = self.minimax(next_state, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = action.get_col()
                beta = min(beta, value)
                if alpha >= beta:
                    break
            result = column, value

        # Store the result in memo
        self.memo[state_key] = result

        return result

    def get_action(self, state: Connect4State):
        # Order moves: prioritize the center columns
        possible_actions = sorted(state.get_possible_actions(),
                                  key=lambda action: abs(action.get_col() - state.get_num_cols() // 2))
        for action in possible_actions:
            column, _ = self.minimax(state, depth=2, alpha=-math.inf, beta=math.inf, maximizingPlayer=True)
            if column is not None:
                return Connect4Action(column)

    def event_action(self, pos: int, action, new_state: State):
        # ignore
        pass

    def event_end_game(self, final_state: State):
        # ignore
        pass

    @staticmethod
    def score_position(grid, piece):
        score = 0

        # Score center column
        center_array = [int(row[len(grid[0]) // 2]) for row in grid]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Score Horizontal
        for r in range(len(grid)):
            row_array = [int(i) for i in grid[r]]
            for c in range(len(grid[0]) - 3):
                window = row_array[c:c + 4]
                score += MiniMaxConnect4Player.evaluate_window(window, piece)

        # Score Vertical
        for c in range(len(grid[0])):
            col_array = [int(row[c]) for row in grid]
            for r in range(len(grid) - 3):
                window = col_array[r:r + 4]
                score += MiniMaxConnect4Player.evaluate_window(window, piece)

        # Score positive sloped diagonal
        for r in range(len(grid) - 3):
            for c in range(len(grid[0]) - 3):
                window = [grid[r + i][c + i] for i in range(4)]
                score += MiniMaxConnect4Player.evaluate_window(window, piece)

        # Score negatively sloped diagonal
        for r in range(len(grid) - 3):
            for c in range(len(grid[0]) - 3):
                window = [grid[r + 3 - i][c + i] for i in range(4)]
                score += MiniMaxConnect4Player.evaluate_window(window, piece)

        return score

    @staticmethod
    def evaluate_window(window, piece):
        score = 0
        opponent_piece = 1 if piece == 2 else 2

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            if window.index(0) == 0 or window.index(0) == 3:  # Threat can be completed next turn
                score += 15
            else:
                score += 5
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2

        if window.count(opponent_piece) == 3 and window.count(0) == 1:
            if window.index(0) == 0 or window.index(0) == 3:  # Block opponent's winning threat
                score += 10
            else:
                score -= 4

        return score

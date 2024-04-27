import math
import random
from random import choice
from games.connect4.result import Connect4Result
from games.connect4.action import Connect4Action
from games.connect4.player import Connect4Player
from games.connect4.state import Connect4State
from games.state import State


class MiniMaxConnect4Player(Connect4Player):

    def minimax(self, state: Connect4State, depth, alpha, beta, maximizingPlayer):
        pos = self.get_current_pos()
        current_player = state.get_acting_player()

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
                return None, state.score_position(state.get_grid(), current_player)

        if maximizingPlayer:
            value = -math.inf
            column = random.choice(range(state.get_num_cols()))
            for action in state.get_possible_actions():
                next_state = state.clone()
                next_state.update(action)
                new_score = self.minimax(next_state, depth - 1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = action.get_col()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
        else:  # Minimizing player
            value = math.inf
            column = random.choice(range(state.get_num_cols()))
            for action in state.get_possible_actions():
                next_state = state.clone()
                next_state.update(action)
                new_score = self.minimax(next_state, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = action.get_col()
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def get_action(self, state: Connect4State):
        column, _ = self.minimax(state, depth=3, alpha=-math.inf, beta=math.inf, maximizingPlayer=True)
        return Connect4Action(column)

    def event_action(self, pos: int, action, new_state: State):
        # ignore
        pass

    def event_end_game(self, final_state: State):
        # ignore
        pass




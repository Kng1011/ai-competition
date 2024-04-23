import math
import random
from games.connect4.result import Connect4Result

def minimax(player, state, depth, alpha, beta, maximizingPlayer):
    AI_PIECE = player.piece
    PLAYER_PIECE = "O" if AI_PIECE == "X" else "X"

    if depth == 0 or state.is_finished():
        result = state.get_result(player.get_index())
        if result is not None:
            if result == Connect4Result.WIN:
                player.event_result(None, Connect4Result.WIN)
                return (None, 100000000000000)
            elif result == Connect4Result.LOSS:
                player.event_result(None, Connect4Result.LOSS)
                return (None, -10000000000000)
            else:  # Draw
                player.event_result(None, Connect4Result.DRAW)
                return (None, 0)
        else:  # Depth is zero
                return (None,  state.score_position(state.get_grid(), AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(range(state.get_num_cols()))
        for action in state.get_possible_actions():
            next_state = state.clone()
            next_state.update(action)
            new_score = minimax(player, next_state, depth - 1, alpha, beta, False)[1]
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
            new_score = minimax(player, next_state, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = action.get_col()
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


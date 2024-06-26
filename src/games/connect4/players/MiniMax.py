import math
import random
from games.connect4.result import Connect4Result
from games.connect4.action import Connect4Action
from games.connect4.player import Connect4Player
from games.connect4.state import Connect4State
from games.state import State


class MiniMaxConnect4Player(Connect4Player):

    def __init__(self, name, max_depth=4):
        super().__init__(name)
        self.memo = {}
        self.max_depth = max_depth

    def minimax(self, state: Connect4State, depth, alpha, beta, maximizingPlayer):
        pos = self.get_current_pos()
        current_player = state.get_acting_player()

        # Check if the result is in memo
        state_key = (str(state.get_grid()), depth, alpha, beta, maximizingPlayer)
        if state_key in self.memo:
            return self.memo[state_key]

        if depth == 0 or state.is_finished():
            result = state.get_result(pos)
            if result is not None:
                if result == Connect4Result.WIN:
                    return None, float('inf')
                elif result == Connect4Result.LOOSE:
                    return None, float('-inf')
                else:  # Draw
                    return None, 0
            else:
                return None, self.score_position(state.get_grid(), current_player)

        possible_actions = state.get_possible_actions()
        center_col = state.get_num_cols() // 2

        def action_score(action):
            col = action.get_col()
            next_state = state.clone()
            next_state.update(action)
            if next_state.get_result(pos) == Connect4Result.WIN:
                return float('inf') if maximizingPlayer else float('-inf')
            return abs(col - center_col)

        possible_actions.sort(key=action_score, reverse=maximizingPlayer)

        if maximizingPlayer:
            value = -math.inf
            best_action = random.choice(possible_actions)
            for action in possible_actions:
                next_state = state.clone()
                next_state.update(action)
                new_score = self.minimax(next_state, depth - 1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    best_action = action
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            result = best_action.get_col(), value
        else:
            value = math.inf
            best_action = random.choice(possible_actions)
            for action in possible_actions:
                next_state = state.clone()
                next_state.update(action)
                new_score = self.minimax(next_state, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    best_action = action
                beta = min(beta, value)
                if alpha >= beta:
                    break
            result = best_action.get_col(), value

        self.memo[state_key] = result
        return result

    def get_action(self, state: Connect4State):
        if self.max_depth is None:
            max_depth = self.max_depth

        possible_actions = state.get_possible_actions()
        center_col = state.get_num_cols() // 2

        def action_score(action):
            col = action.get_col()
            next_state = state.clone()
            next_state.update(action)
            if next_state.get_result(self.get_current_pos()) == Connect4Result.WIN:
                return float('inf')
            return abs(col - center_col)

        possible_actions.sort(key=action_score, reverse=True)

        best_action = None
        for depth in range(1, self.max_depth + 1):  # max_depth é a profundidade máxima desejada
            column, _ = self.minimax(state, depth=depth, alpha=-math.inf, beta=math.inf, maximizingPlayer=True)
            if column is not None:
                best_action = Connect4Action(column)
            else:
                break  # Se não houver ação válida para a profundidade atual, pare a iteração
        return best_action

    def event_action(self, pos: int, action, new_state: State):
        pass

    def event_end_game(self, final_state: State):
        pass

    @staticmethod
    def score_position(grid, piece):
        score = 0
        opponent_piece = 1 if piece == 2 else 2
        center_col = len(grid[0]) // 2

        # Score center column
        center_array = [row[center_col] for row in grid]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Padrões de Bloqueio
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] == opponent_piece:
                    # Horizontal
                    if c <= len(grid[0]) - 4:
                        window = grid[r][c:c + 4]
                        if window.count(opponent_piece) == 3 and window.count(0) == 1:
                            score -= 10
                    # Vertical
                    if r <= len(grid) - 4:
                        window = [grid[i][c] for i in range(r, r + 4)]
                        if window.count(opponent_piece) == 3 and window.count(0) == 1:
                            score -= 10
                    # Diagonal (positiva)
                    if c <= len(grid[0]) - 4 and r <= len(grid) - 4:
                        window = [grid[r + i][c + i] for i in range(4)]
                        if window.count(opponent_piece) == 3 and window.count(0) == 1:
                            score -= 10
                    # Diagonal (negativa)
                    if c >= 3 and r <= len(grid) - 4:
                        window = [grid[r + i][c - i] for i in range(4)]
                        if window.count(opponent_piece) == 3 and window.count(0) == 1:
                            score -= 10

        # Padrões de Ataque
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] == piece:
                    # Horizontal
                    if c <= len(grid[0]) - 4:
                        window = grid[r][c:c + 4]
                        score += MiniMaxConnect4Player.evaluate_window(window, piece, opponent_piece)
                    # Vertical
                    if r <= len(grid) - 4:
                        window = [grid[i][c] for i in range(r, r + 4)]
                        score += MiniMaxConnect4Player.evaluate_window(window, piece, opponent_piece)
                    # Diagonal (positiva)
                    if c <= len(grid[0]) - 4 and r <= len(grid) - 4:
                        window = [grid[r + i][c + i] for i in range(4)]
                        score += MiniMaxConnect4Player.evaluate_window(window, piece, opponent_piece)
                    # Diagonal (negativa)
                    if c >= 3 and r <= len(grid) - 4:
                        window = [grid[r + i][c - i] for i in range(4)]
                        score += MiniMaxConnect4Player.evaluate_window(window, piece, opponent_piece)

            # Padrões específicos
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if grid[r][c] == piece:
                        # Verificar padrões horizontais
                        if c <= len(grid[0]) - 4:
                            window = grid[r][c:c + 4]
                            if window.count(piece) == 3 and window.count(0) == 1:
                                score += 10  # Peso extra para padrão de 3 peças com espaço vazio ao lado
                        # Verificar padrões verticais
                        if r <= len(grid) - 4:
                            window = [grid[i][c] for i in range(r, r + 4)]
                            if window.count(piece) == 3 and window.count(0) == 1:
                                score += 10  # Peso extra para padrão de 3 peças com espaço vazio abaixo
                        # Verificar padrões diagonais (positivas)
                        if c <= len(grid[0]) - 4 and r <= len(grid) - 4:
                            window = [grid[r + i][c + i] for i in range(4)]
                            if window.count(piece) == 3 and window.count(0) == 1:
                                score += 10  # Peso extra para padrão de 3 peças com espaço vazio na diagonal (positiva)
                        # Verificar padrões diagonais (negativas)
                        if c >= 3 and r <= len(grid) - 4:
                            window = [grid[r + i][c - i] for i in range(4)]
                            if window.count(piece) == 3 and window.count(0) == 1:
                                score += 10  # Peso extra para padrão de 3 peças com espaço vazio na diagonal (negativa)



        return score

    @staticmethod
    def evaluate_window(window, piece, opponent_piece):
        score = 0
        piece_count = window.count(piece)
        opponent_count = window.count(opponent_piece)

        if piece_count == 4:
            score += 100
        elif piece_count == 3 and window.count(0) == 1:
            score += 5
        elif piece_count == 2 and window.count(0) == 2:
            score += 2

        if opponent_count == 3 and window.count(0) == 1:
            score -= 4

        return score

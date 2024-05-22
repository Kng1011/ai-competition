from collections import Counter
from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.state import HLPokerState
from games.hlpoker.action import HLPokerAction
import random
from games.hlpoker.round import Round
from games.state import State


class Node:
    def __init__(self, num_actions):
        self.regret_sum = [0.0] * num_actions
        self.strategy = [0.0] * num_actions
        self.strategy_sum = [0.0] * num_actions


class ExpectimaxPokerPlayer(HLPokerPlayer):
    def __init__(self, name):
        super().__init__(name)

    def get_action_with_cards(self, state: HLPokerState, private_cards, board_cards):
        possible_actions = list(state.get_possible_actions())
        action_values = {action: self.expectimax(state.clone(), action, float('-inf'), float('inf')) for action in possible_actions}
        best_action = max(action_values, key=action_values.get)
        return best_action

    def expectimax(self, state: HLPokerState, action: HLPokerAction, alpha: float, beta: float):
        next_state = state.clone()
        next_state.update(action)

        if next_state.is_finished():
            return next_state.get_result(self.get_current_pos())

        if next_state.get_acting_player() == self.get_current_pos():
            # Max node
            value = float('-inf')
            for action in next_state.get_possible_actions():
                value = max(value, self.expectimax(next_state.clone(), action, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # beta cut-off
            return value
        else:
            # Chance node
            value = 0
            for action in next_state.get_possible_actions():
                value += self.expectimax(next_state.clone(), action, alpha, beta)
                if value >= beta:
                    break  # alpha cut-off
            return value / len(next_state.get_possible_actions())

    def event_new_round(self, round: Round):
        pass

    def event_end_game(self, final_state: State):
        pass

    def event_my_action(self, action, new_state):
        pass

    def event_opponent_action(self, action, new_state):
        pass

    def event_new_game(self):
        pass

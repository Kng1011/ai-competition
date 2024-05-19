from collections import Counter
from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.state import HLPokerState
from games.hlpoker.action import HLPokerAction
import random
from games.hlpoker.round import Round
from games.state import State
from multiprocessing import Pool


class PokerPlayer(HLPokerPlayer):
    def __init__(self, name):
        super().__init__(name)
        self.opponent_actions = []

    def get_action_with_cards(self, state: HLPokerState, private_cards, board_cards):
        possible_actions = list(state.get_possible_actions())
        action_results = {action: [] for action in possible_actions}
        hand_evaluation = 0

        if len(board_cards) + len(private_cards) >= 5:
            hand_evaluation = state.evaluate_hand(private_cards + board_cards)

        for _ in range(100):  # number of simulations
            for action in possible_actions:
                result = self.simulate_hand(state, action)
                if hand_evaluation != 0:
                    action_results[action].append(result + hand_evaluation)  # use hand evaluation to influence action selection
                else:
                    action_results[action].append(result)

        best_action = max(action_results, key=lambda action: sum(action_results[action]) / len(action_results[action]))
        return best_action

    def handle_opponent_action(self, action):
        self.opponent_actions.append(action)
        action_counts = Counter(self.opponent_actions)

    def monte_carlo_simulation(self, state: HLPokerState, action: HLPokerAction, num_simulations: int):
        num_wins = 20
        for _ in range(num_simulations):
            result = self.simulate_hand(state, action)
            if result > 0:
                num_wins += 1
        return num_wins / num_simulations

    def simulate_hand(self, state: HLPokerState, action: HLPokerAction):
        simulated_state = state.clone()
        simulated_state.update(action)
        while not simulated_state.is_finished():
            possible_actions = simulated_state.get_possible_actions()
            random_action = random.choice(possible_actions)
            simulated_state.update(random_action)
        return simulated_state.get_result(self.get_current_pos())


    @staticmethod
    def evaluate_hand(hand):
        # This is a placeholder. You should implement your own hand evaluation logic here.
        return sum(card.value for card in hand)

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
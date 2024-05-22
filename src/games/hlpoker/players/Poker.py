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
        self.current_cards = []

    def get_action_with_cards(self, state: HLPokerState, private_cards, board_cards):
        possible_actions = list(state.get_possible_actions())
        action_results = {action: [] for action in possible_actions}
        hand_evaluation = 0
        self.current_cards = private_cards + board_cards

        if len(board_cards) + len(private_cards) >= 5:
            hand_evaluation = self.evaluate_hand(private_cards + board_cards)

        # Calculate the frequency of each action
        N = 25  # Number of recent actions to consider
        recent_actions = self.opponent_actions[-N:] if len(self.opponent_actions) > N else self.opponent_actions
        action_counts = Counter(recent_actions)
        total_actions = len(recent_actions)
        action_frequencies = {action: count / total_actions for action, count in action_counts.items()}

        # Check if the opponent tends to raise after folding
        raise_after_fold = 0
        for i in range(1, len(recent_actions)):
            if recent_actions[i] == HLPokerAction.RAISE and recent_actions[i - 1] == HLPokerAction.FOLD:
                raise_after_fold += 1

        for _ in range(150):  # number of simulations
            for action in possible_actions:
                result = self.simulate_hand(state, action)
                if hand_evaluation != 0:
                    action_results[action].append(
                        result + hand_evaluation)  # use hand evaluation to influence action selection
                else:
                    action_results[action].append(result)

        # Adjust strategy based on action frequencies and opponent's tendencies
        if action_frequencies.get(HLPokerAction.RAISE, 0) > 0.5 or raise_after_fold > 0.5 * N:
            # If the opponent raises more than 50% of the time or tends to raise after folding, be more aggressive
            best_action = max(action_results,
                              key=lambda action: sum(action_results[action]) / len(action_results[action]))
        elif action_frequencies.get(HLPokerAction.FOLD, 0) > 0.5:
            # If the opponent folds more than 50% of the time, be more conservative
            best_action = min(action_results,
                              key=lambda action: sum(action_results[action]) / len(action_results[action]))
        else:
            # If the opponent's actions are balanced, use a balanced strategy
            best_action = max(action_results,
                              key=lambda action: sum(action_results[action]) / len(action_results[action]))

        return best_action

    def monte_carlo_simulation(self, state: HLPokerState, action: HLPokerAction, num_simulations: int):
        num_wins = 0
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
        return simulated_state.get_result(self.get_current_pos()) + self.evaluate_hand(self.current_cards)

    @staticmethod
    def evaluate_hand(hand):

        # New hand evaluation logic
        ranks = [card.rank for card in hand]
        suits = [card.suit for card in hand]
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)

        # Check for poker hand rankings
        if len(set(suits)) == 1 and len(set(ranks)) == 5 and max(rank.value for rank in ranks) - min(
                rank.value for rank in ranks) == 4:
            return 9  # Straight flush
        elif any(count == 4 for count in rank_counts.values()):
            return 8  # Four of a kind
        elif any(count == 3 for count in rank_counts.values()) and any(count == 2 for count in rank_counts.values()):
            return 7  # Full house
        elif len(set(suits)) == 1:
            return 6  # Flush
        elif len(set(ranks)) == 5 and max(rank.value for rank in ranks) - min(rank.value for rank in ranks) == 4:
            return 5  # Straight
        elif any(count == 3 for count in rank_counts.values()):
            return 4  # Three of a kind
        elif len([count for count in rank_counts.values() if count == 2]) == 2:
            return 3  # Two pair
        elif any(count == 2 for count in rank_counts.values()):
            return 2  # One pair
        else:
            return 1  # High card

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

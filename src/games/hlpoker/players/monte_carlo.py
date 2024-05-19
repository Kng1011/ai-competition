import math

from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.round import Round
from games.hlpoker.state import HLPokerState
from games.state import State
from games.hlpoker.card import Card
import random
from collections import Counter
from games.hlpoker.action import HLPokerAction


class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0


class MtCHLPokerPlayer(HLPokerPlayer):

    def __init__(self, name):
        super().__init__(name)
        self.num_simulations = 1000  # number of simulations to run for each move
        self.exploration_weight = 1.0  # adjust this value to balance exploration and exploitation

    def get_action_with_cards(self, state: HLPokerState, private_cards, board_cards):
        root_node = Node(state, None, None)
        for _ in range(self.num_simulations):
            node = root_node
            state_copy = state.clone()
            while not state_copy.is_finished():
                if node.children:
                    node = self.select_child(node)
                else:
                    node = self.expand_node(node, state_copy)
                state_copy.update(node.action)
            result = state_copy.get_result(0)  # assuming player 0 is the AI
            self.backpropagate(node, result)
        best_action = self.select_best_action(root_node)

        # Evaluate the hand
        hand_evaluation = self.evaluate_hand(private_cards + board_cards)
        hand_strength = self.get_hand_strength(hand_evaluation)

        # Adjust the best action based on the hand strength
        if hand_strength < 5 and best_action == HLPokerAction.RAISE:
            best_action = HLPokerAction.CALL
        elif hand_strength > 7 and best_action == HLPokerAction.CALL:
            best_action = HLPokerAction.RAISE

        return best_action

    @staticmethod
    def evaluate_hand(hand):
        values = [card.rank for card in hand]
        suits = [card.suit for card in hand]
        value_counts = Counter(values)
        suit_counts = Counter(suits)

        # Check for poker combinations
        if MtCHLPokerPlayer.is_royal_flush(values, suit_counts):
            return "Royal Flush"
        elif MtCHLPokerPlayer.is_straight_flush(values, suit_counts):
            return "Straight Flush"
        elif MtCHLPokerPlayer.is_four_of_a_kind(value_counts):
            return "Four of a Kind"
        elif MtCHLPokerPlayer.is_full_house(value_counts):
            return "Full House"
        elif MtCHLPokerPlayer.is_flush(suit_counts):
            return "Flush"
        elif MtCHLPokerPlayer.is_straight(values):
            return "Straight"
        elif MtCHLPokerPlayer.is_three_of_a_kind(value_counts):
            return "Three of a Kind"
        elif MtCHLPokerPlayer.is_two_pair(value_counts):
            return "Two Pair"
        elif MtCHLPokerPlayer.is_one_pair(value_counts):
            return "One Pair"
        else:
            return "High Card"

    @staticmethod
    def get_hand_strength(hand_evaluation):
        # Assign a numerical value to each possible hand evaluation
        hand_strengths = {
            "Royal Flush": 10,
            "Straight Flush": 9,
            "Four of a Kind": 8,
            "Full House": 7,
            "Flush": 6,
            "Straight": 5,
            "Three of a Kind": 4,
            "Two Pair": 3,
            "One Pair": 2,
            "High Card": 1
        }
        return hand_strengths.get(hand_evaluation, 0)

    @staticmethod
    def is_royal_flush(values, suit_counts):
        int_values = [rank.value for rank in values]
        return MtCHLPokerPlayer.is_flush(suit_counts) and sorted(int_values) == list(range(10, 15))

    @staticmethod
    def is_straight_flush(values, suit_counts):
        return MtCHLPokerPlayer.is_flush(suit_counts) and MtCHLPokerPlayer.is_straight(values)

    @staticmethod
    def is_four_of_a_kind(value_counts):
        return 4 in value_counts.values()

    @staticmethod
    def is_full_house(value_counts):
        return sorted(value_counts.values()) == [2, 3]

    @staticmethod
    def is_flush(suit_counts):
        return max(suit_counts.values()) >= 5

    @staticmethod
    def is_straight(values):
        int_values = [rank.value for rank in values]
        return len(set(int_values)) == 5 and max(int_values) - min(int_values) == 4

    @staticmethod
    def is_three_of_a_kind(value_counts):
        return 3 in value_counts.values()

    @staticmethod
    def is_two_pair(value_counts):
        return list(value_counts.values()).count(2) == 2

    @staticmethod
    def is_one_pair(value_counts):
        return 2 in value_counts.values()

    def select_child(self, node):
        # UCB1 formula to balance exploration and exploitation
        max_ucb = -float('inf')
        best_child = None
        for child in node.children:
            ucb = child.value / child.visits + self.exploration_weight * math.sqrt(
                2 * math.log(node.visits) / child.visits)
            if ucb > max_ucb:
                max_ucb = ucb
                best_child = child
        return best_child

    @staticmethod
    def expand_node(node, state):
        actions = state.get_possible_actions()

        # Filter out clearly bad actions
        actions = MtCHLPokerPlayer.filter_bad_actions(actions, state)

        action = random.choice(actions)
        new_state = state.clone()
        new_state.update(action)

        # Check if the new state is too similar to a previously explored state
        if MtCHLPokerPlayer.is_state_too_similar(new_state):
            return node  # Return the current node without expanding

        new_node = Node(new_state, node, action)
        node.children.append(new_node)
        return new_node

    @staticmethod
    def filter_bad_actions(actions, state):
        # Get the player's hand
        hand = state.get_player_hand(MtCHLPokerPlayer.name)

        # Evaluate the hand
        hand_evaluation = MtCHLPokerPlayer.evaluate_hand(hand)

        # Get the hand strength
        hand_strength = MtCHLPokerPlayer.get_hand_strength(hand_evaluation)

        # If the hand strength is high (e.g., greater than 7), remove FOLD from the actions
        if hand_strength > 7 and HLPokerAction.FOLD in actions:
            actions.remove(HLPokerAction.FOLD)

        return actions

    @staticmethod
    def is_action_bad(action, state):
        # Get the player's hand
        hand = state.get_player_hand(MtCHLPokerPlayer.name)

        # Evaluate the hand
        hand_evaluation = MtCHLPokerPlayer.evaluate_hand(hand)

        # Get the hand strength
        hand_strength = MtCHLPokerPlayer.get_hand_strength(hand_evaluation)

        # If the hand strength is low (e.g., less than 5), and the action is RAISE, then it's a bad action
        if hand_strength < 5 and action == HLPokerAction.RAISE:
            return True

        return False

    def is_state_too_similar(self, new_state):
        # Get the current game state
        current_state = self.state

        # Get the player's hand and board cards in the current state
        current_hand = current_state.get_player_hand(self.name)
        current_board = current_state.get_board_cards()

        # Get the player's hand and board cards in the new state
        new_hand = new_state.get_player_hand(self.name)
        new_board = new_state.get_board_cards()

        # Compare the hands and board cards
        if current_hand == new_hand and current_board == new_board:
            return True  # The states are too similar

        # Check if the current round is the same
        if current_state.get_current_round() != new_state.get_current_round():
            return True  # The states are too similar

        # Check if the number of players is the same
        if current_state.get_num_players() != new_state.get_num_players():
            return True  # The states are too similar

        # Check if the bets are the same
        if current_state.get_spent(self.name) != new_state.get_spent(self.name):
            return True  # The states are too similar

        return False  # The states are not too similar

    def backpropagate(self, node, result):
        while node:
            node.visits += 1
            node.value += result
            node = node.parent

    def select_best_action(self, node):
        best_action = None
        max_value = -float('inf')
        for child in node.children:
            if child.value > max_value:
                max_value = child.value
                best_action = child.action
        return best_action

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

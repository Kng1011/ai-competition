import math

from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.round import Round
from games.hlpoker.state import HLPokerState
from games.state import State
from games.hlpoker.card import Card
import random



class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0


class HeuristicEvaluator:
    @staticmethod
    def evaluate_hand(hand, board):
        hand_cards = hand.cards + board
        hand_rank = 0
        for card in hand_cards:
            hand_rank += Card.rank(card)
        return hand_rank.value

    @staticmethod
    def evaluate_node(node):
        if node.state.is_finished():
            return node.state.get_result(0)
        else:
            return HeuristicEvaluator.evaluate_hand(node.state.get_hand(0), node.state.get_board())


class MtCHLPokerPlayer(HLPokerPlayer):

    def __init__(self, name):
        super().__init__(name)
        self.num_simulations = 10000
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
        return best_action

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

    def expand_node(self, node, state):
        actions = state.get_possible_actions()
        action = random.choice(actions)
        new_state = state.clone()
        new_state.update(action)
        new_node = Node(new_state, node, action)
        node.children.append(new_node)
        return new_node

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

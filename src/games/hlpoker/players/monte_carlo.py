import random

from games.hlpoker.action import HLPokerAction
from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.round import Round
from games.hlpoker.state import HLPokerState
from games.state import State


class MtCHLPokerPlayer(HLPokerPlayer):

    def __init__(self, name):
        super().__init__(name)
        self.num_simulations = 10000

    def get_action_with_cards(self, state: HLPokerState, private_cards, board_cards):
        actions = state.get_possible_actions()
        action_scores = {}

        for action in actions:
            total_score = 0
            for _ in range(self.num_simulations):
                cloned_state = state.clone()
                cloned_state.update(action)
                total_score += self.simulate(cloned_state, private_cards, board_cards)
            action_scores[action] = total_score / self.num_simulations

        # Choose action with highest average score
        best_action = max(action_scores, key=action_scores.get)
        return best_action

    def event_my_action(self, action, new_state):
        pass

    def event_opponent_action(self, action, new_state):
        pass

    def event_new_game(self):
        pass

    def event_end_game(self, final_state: State):
        pass

    def event_result(self, pos: int, result: int):
        pass

    def event_new_round(self, round: Round):
        pass

    def simulate(self, state, private_cards, board_cards):
        # Implemente a lógica de simulação aqui
        # Execute simulações do jogo e retorne os resultados
        # Exemplo simplificado:
        while not state.is_finished():
            # Simule movimentos aleatórios até o final do jogo
            actions = state.get_possible_actions()
            action = random.choice(actions)
            state.update(action)
        return state.get_result(0)  # Supondo avaliação do resultado do ponto de vista do jogador atual

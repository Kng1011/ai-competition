from termcolor import colored

from games.connect4.action import Connect4Action
from games.connect4.player import Connect4Player
from games.connect4.result import Connect4Result
from games.connect4.state import Connect4State


class HumanConnect4Player(Connect4Player):

    def __init__(self, name):
        super().__init__(name)

    def get_color(self):
        pos = self.get_current_pos()
        prompt_color = 'red' if pos == 0 else 'blue'
        char = '●' if pos == 0 else '○'
        return [prompt_color, char]

    def get_action(self, state: Connect4State):
        state.display()
        while True:
            # noinspection PyBroadException
            try:
                [prompt_color, char] = self.get_color()
                return Connect4Action(int(input(colored(f"{self.get_name()} ({char}) > please choose a column: ", prompt_color))))
            except Exception:
                continue

    def event_action(self, pos: int, action, new_state: Connect4State):
        # ignore
        pass

    def event_end_game(self, final_state: Connect4State):
        final_state.display()
        [color, char] = self.get_color()
        if self.__last_result == Connect4Result.LOOSE.value[0]:
            print(colored(f">{self.get_name()} ({char}) > I lost!", color))
        elif self.__last_result == Connect4Result.WIN.value[0]:
            print(colored(f">{self.get_name()} ({char}) > I won!", color))
        else:
            print(colored(f">{self.get_name()} ({char}) > I drawn!", color))



    def event_result(self, pos: int, result: int):
        if self.get_current_pos() == pos:
            self.__last_result = result
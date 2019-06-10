import curses
import random

import game
import action


class Display:
    def __init__(self, current_game):
        self.current_game = current_game
        self.running = True

    def start(self):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.running = True

    def update(self):
        if self.stdscr.getch() == ord('q'):
            self.current_game.running = False
        else:
            game_display = current_game.get_screen()
            for line, row in enumerate(game_display):
                self.stdscr.addstr(line, 0, row)
            self.stdscr.refresh()

    def stop(self):
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
        self.running = False


class Bot:
    def __init__(self):
        pass

    def play(self, current_game, show=False):
        try:
            current_game.start()
            if show:
                display = Display(current_game)
                display.start()
            while current_game.running:
                if show:
                    display.update()
                state = current_game.get_state()
                act = self.choose_action(state)
                current_game.do_action(act)
            return state
        except Exception as e:
            raise e
        finally:
            if show:
                display.stop()

    def choose_action(self, state):
        pass


class RandomBot(Bot):
    def choose_action(self, state):
        if state['message']['is_more']:
            act = action.Action.MORE
        elif state['message']['is_yn']:
            act = action.Action.YES
        else:
            act = random.choice([act for act in action.Action
                                 if act in action.MOVE_ACTIONS])
        return act


class BasicModelBasedBot(Bot):
    def __init__(self):
        self.prev_state = None
        self.prev_act = None
        self.observations = []
        self.exploring = True

    def find_self(self, state_map):
        for y in range(len(state_map)):
            for x in range(len(state_map[0])):
                if state['map'] == '@':
                    return x, y

    def compute_probs(self):
        pass

    def get_neighbors(self, state_map, x, y):
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                neighbors.append[state_map[y][x]]
        return neighbors

    def parse_state(self, state):
        parsed = []
        x, y = self.find_self(state['map'])
        neighbors = self.get_neighbors(state['map'], x, y)
        for patterns in ('abcdefghijklmnopqurstvwxyzABCEFGHIJKLMNOPQRSTUVWXYZ', '+', '>', '$', '-|'):
            for neighbor in neighbors:
                parsed.append(neighbor in pattern)
        return parsed

    def choose_action(self, state):
        if state['message']['is_more']:
            act = Action.MORE
        elif state['message']['is_yn']:
            act = Action.YES
        else:
            parsed_state = self.parse_state(state)
            if self.exploring:
                if self.prev_state is not None:
                    observation = (self.prev_state, self.prev_act,
                                   parsed_state)
                    self.observations.append(observation)
                act = random.choice([act for act in Action
                                     if act not in action.MENU_ACTIONS])
            else:
                pass
            self.prev_state = parsed_state
            self.prev_act = act
        return act


if __name__ == '__main__':
    current_game = game.Game()
    bot = RandomBot()
    print(bot.play(current_game, show=True))

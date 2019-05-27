import curses
import random
import re
import os
import time
from enum import Enum, auto

import pyte
import pexpect
from pexpect.exceptions import TIMEOUT

COMMAND = '/Users/watsonc/quixote/bin/nethack'
OPTIONS_FILE = '/Users/watsonc/quixote/quixote.nethackrc'
WIDTH, HEIGHT = 80, 24
READ_TIMEOUT = 0.05

class Action(Enum):
    NORTH = auto()
    NORTH_EAST = auto()
    EAST = auto()
    SOUTH_EAST = auto()
    SOUTH = auto()
    SOUTH_WEST = auto()
    WEST = auto()
    NORTH_WEST = auto()
    STAIR_UP = auto()
    STAIR_DOWN = auto()
    OPEN = auto()
    CLOSE = auto()
    SEARCH = auto()
    LOOK = auto()
    MORE = auto()
    YES = auto()
    NO = auto()
    LOOT = auto()
    UNTRAP = auto()
    PRAY = auto()

key_actions = {
    Action.NORTH: 'k',
    Action.NORTH_EAST: 'u',
    Action.EAST: 'l',
    Action.SOUTH_EAST: 'n',
    Action.SOUTH: 'j',
    Action.SOUTH_WEST: 'b',
    Action.WEST: 'h',
    Action.NORTH_WEST: 'y',
    Action.STAIR_UP: '<',
    Action.STAIR_DOWN: '>',
    Action.OPEN: 'o',
    Action.CLOSE: 'c',
    Action.SEARCH: 's',
    Action.LOOK: ':',
    Action.MORE: '\n',
    Action.YES: 'y',
    Action.NO: 'n'
}

hash_actions = {
    Action.LOOT: '#loot',
    Action.UNTRAP: '#untrap',
    Action.PRAY: '#pray'
}

menu_actions = [Action.MORE,
                Action.YES,
                Action.NO]


class Game:
    def __init__(self):
        self.running = True
        self.prev_state = {}

    def start(self):
        env = os.environ
        env['NETHACKOPTIONS'] = '@{}'.format(OPTIONS_FILE)
        self.child = pexpect.spawn(COMMAND, env=env)
        self.screen = pyte.Screen(WIDTH, HEIGHT)
        self.stream = pyte.Stream(self.screen)

        index = self.wait_for_texts(['Is this ok?', 'Restoring save file...'])
        if index == 1:
            self.child.sendline()
            self.quit()
            self.child = pexpect.spawn(COMMAND)
            self.wait_for_text('Is this ok?')

        self.child.send('y')
        self.child.sendcontrol('r')  # redraw so we can grab the map
        self.running = True

    def quit(self):
        self.child.sendline('#quit')
        self.child.expect('Really quit?')
        self.child.send('y')
        return self.complete_game()

    def wait_for_text(self, text, timeout=None):
        return self.wait_for_texts([text], timeout=timeout)

    def wait_for_texts(self, texts, timeout=None):
        if timeout is not None:
            start_time = time.time()
        while True:
            display = self.get_screen()
            for index, text in enumerate(texts):
                if any([text in line for line in display]):
                    return index
            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError('Timeout waiting for query')

    def complete_game(self):
        while True:
            self.child.send('n')
            try:
                self.wait_for_text('Do you want', timeout=0.05)
            except TimeoutError:
                break

        end_text = ' '.join(self.get_screen())
        match = re.search('(\d+) point', end_text)
        points = int(match.groups()[0])
        self.running = False
        return points

    def get_screen(self):
        text = ''
        while True:
            try:
                read_bytes = self.child.read_nonblocking(
                    size=self.child.maxread, timeout=READ_TIMEOUT)
                text += read_bytes.decode('ascii')
            except TIMEOUT:
                break
        self.stream.feed(text)
        return self.screen.display

    def get_state(self):
        state = {}
        display = self.get_screen()
        state['map'] = display[1:-2]

        state['message'] = {}
        state['message']['text'] = display[0].strip()
        state['message']['is_more'] = any(
            ['--More--' in line for line in display])
        state['message']['is_yn'] = any(
            ['[yn]' in line for line in display])

        base_stats = {}
        try:
            for stat in ['St', 'Dx', 'Co', 'In', 'Wi', 'Ch']:
                match = re.search('{}:(\d+)'.format(stat), display[-2])
                base_stats[stat] = int(match.groups()[0])
            state['base_stats'] = base_stats
            state['alignment'] = display[-2].split()[-1].strip()
            match = re.search('S:(\d+)', display[-2])
            state['est_score'] = int(match.groups()[0])

            for stat in ['Dlvl', '$', 'HP', 'Pw', 'AC', 'Xp']:
                escaped = re.escape(stat)
                match = re.search(
                    '{}:(\d+)(\(\d+\))?'.format(escaped), display[-1])
                groups = match.groups()
                state[stat] = int(groups[0])
                if groups[1] is not None:
                    state['{}_max'.format(stat)] = int(groups[1][1:-1])
        except AttributeError:
            state = self.prev_state

        try:
            state['reward'] = state['est_score'] - self.prev_state['est_score']
        except KeyError:
            state['reward'] = 0
        if 'Do you want your possessions identified?' in display[0]:
            state['alive'] = True
            state['score'] = self.complete_game()
        else:
            state['alive'] = False
        self.prev_state = state
        return state

    def do_action(self, action):
        if action in key_actions:
            self.child.send(key_actions[action])
        elif action in hash_actions:
            self.child.sendline(hash_actions[action])


class Display:
    def __init__(self, game):
        self.game = game
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
            self.game.running = False
        else:
            game_display = game.get_screen()
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

    def play(self, game, show=False):
        try:
            game.start()
            if show:
                display = Display(game)
                display.start()
            while game.running:
                if show:
                    display.update()
                state = game.get_state()
                action = self.choose_action(state)
                game.do_action(action)
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
            act = Action.MORE
        elif state['message']['is_yn']:
            act = Action.YES
        else:
            act = random.choice([act for act in Action
                                 if act not in menu_actions])
        return act


class BasicQLearningBot(Bot):
    def __init__(self):
        Q = defaultdict(float)

    def parse_state(self, state):
        pass

    def choose_action(self, state):
        if state['message']['is_more']:
            act = Action.MORE
        elif state['message']['is_yn']:
            act = Action.YES
        else:
            parsed_state = parse_state
            # update Q
            # update other stuff


if __name__ == '__main__':
    game = Game()
    bot = RandomBot()
    print(bot.play(game, show=True))

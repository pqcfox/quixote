import curses
import random
import re
import os
import time

import pyte
import pexpect
from pexpect.exceptions import TIMEOUT

import config
import action


class Game:
    def __init__(self):
        self.running = True
        self.prev_state = {}

    def start(self):
        env = os.environ
        env['NETHACKOPTIONS'] = '@{}'.format(config.OPTIONS_FILE)
        self.child = pexpect.spawn(config.COMMAND, env=env)
        self.screen = pyte.Screen(config.WIDTH, config.HEIGHT)
        self.stream = pyte.Stream(self.screen)

        index = self.wait_for_texts(['Is this ok?', 'Restoring save file...'])
        if index == 1:
            self.child.sendline()
            self.quit()
            self.child = pexpect.spawn(config.COMMAND)
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
                    size=self.child.maxread, timeout=config.READ_TIMEOUT)
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

    def do_action(self, act):
        if act in action.KEY_ACTIONS:
            self.child.send(action.KEY_ACTIONS[act])
        elif act in action.HASH_ACTIONS:
            self.child.sendline(action.HASH_ACTIONS[act])


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
                act = self.choose_action(state)
                game.do_action(act)
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
    game = Game()
    bot = RandomBot()
    print(bot.play(game, show=True))

import re
from enum import Enum, auto

import pyte
import pexpect
from pexpect.exceptions import TIMEOUT

COMMAND = 'nethack'
WIDTH, HEIGHT = 80, 24
ROLE = 'v'
RACE = 'h'
ALIGNMENT = 'n'
READ_TIMEOUT = 0.05


class Game:
    class Action(Enum):  # TODO: handle dialogue options
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
        Action.LOOK: ':'
    }

    hash_actions = {
        Action.LOOT: '#loot',
        Action.UNTRAP: '#untrap',
        Action.PRAY: '#pray'
    }

    def __init__(self):
        self.running = True

    def start(self):
        self.child = pexpect.spawn(COMMAND)
        self.screen = pyte.Screen(WIDTH, HEIGHT)
        self.stream = pyte.Stream(self.screen)

        index = self.child.expect(['Shall I pick', 'Restoring save file'])
        if index == 1:
            self.child.sendline()
            self.quit()
            self.child = pexpect.spawn(COMMAND)

        self.child.send('n')
        self.child.expect('Pick a role or profession')
        self.child.send(ROLE)
        self.child.expect('Pick a race or species')
        self.child.send(RACE)
        self.child.expect('Pick an alignment or creed')
        self.child.send(ALIGNMENT)
        self.child.expect('Is this ok?')
        self.child.send('y')
        self.child.expect('--More--')
        self.child.sendline()
        print(self.get_screen())
        self.running = True

    def quit(self):
        self.child.sendline('#quit')
        self.child.expect('Really quit?')
        self.child.send('y')
        self.child.expect('Do you want your possessions identified?')
        self.child.send('n')
        self.child.expect('Do you want to see your attributes?')
        self.child.send('n')
        self.child.expect('Do you want to see your conduct?')
        self.child.send('n')
        self.child.expect('Do you want to see the dungeon overview?')
        self.child.send('n')
        self.child.expect('You quit')
        self.child.sendline()
        self.running = False

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

        state['message'] = display[0].strip()
        base_stats = {}
        for stat in ['St', 'Dx', 'Co', 'In', 'Wi', 'Ch']:
            match = re.search('{}:(\d+)'.format(stat), display[-2])
            base_stats[stat] = int(match.groups()[0])
        state['base_stats'] = base_stats
        state['alignment'] = display[-2].split()[-1].strip()

        for stat in ['Dlvl', '$', 'HP', 'Pw', 'AC', 'Xp']:
            match = re.search('{}:(\d+)(\(\d+\))?'.format(stat), display[-1])
            state[stat] = int(match.groups()[0])
            if len(match.groups()) > 1:
                state['{}_max'.format(stat)] = int(match.groups[1])

        return state

    def do_action(self, action):
        if action in key_actions:
            self.child.send(key_actions[action])
        elif action in hash_actions:
            self.child.sendline(hash_actions[action])


class Bot:
    def __init__(self, game):
        self.game = game

    def play():
        game.start()
        while game.running:
            state = game.get_state()
            action = choose_action(state)
            game.do_action(action)
        return game.get_state()

    def choose_action(state):
        pass


if __name__ == '__main__':
    game = Game()
    game.start()
    # print(game.get_screen())
    # print(game.get_state())

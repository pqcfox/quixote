import random
import string
import collections

import action
import display


class RandomBot:
    def choose_action(self, state):
        if state['message']['is_more']:
            act = action.Action.MORE
        elif state['message']['is_yn']:
            act = action.Action.YES
        else:
            act = random.choice([act for act in action.Action
                                 if act in action.MOVE_ACTIONS])
        return act

    def get_status(self):
        train_string = 'TRAIN' if self.train else 'TEST'
        return '{}\tEPOCH:{}\t{}'.format(train_string, self.epoch, self.prev_act)


class QLearningBot:
    PATTERNS = [string.ascii_letters, '+', '>', '-', '|', ' ']

    def __init__(self, lr=0.1, epsilon=0.1, discount=0.5):
        self.prev_state = None
        self.prev_act = None
        self.prev_reward = None
        self.prev_map = None
        self.beneath = None
        self.lr = lr
        self.epsilon = epsilon
        self.discount = 0.5
        self.Q = collections.defaultdict(float)

    def find_self(self, state_map):
        for y in range(len(state_map)):
            for x in range(len(state_map[0])):
                if state_map[y][x] == '@':
                    return x, y
        return None

    def get_neighbors(self, state_map, x, y):
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                neighbors.append(state_map[y + dy][x + dx])
        return neighbors

    def update_prev_map(self, new_map):
        replaced_map = self.prev_map
        self.prev_map = new_map
        for line, row in enumerate(self.prev_map):
            if '@' in row:
                if replaced_map is None:
                    beneath = '.'
                else:
                    beneath = replaced_map[line][row.index('@')]
                self.prev_map[line] = row.replace('@', beneath)
                break

    def parse_state(self, state):
        pair = self.find_self(state['map'])
        if pair is None or self.prev_map is None:
            parsed = None
        else:
            parsed = []
            x, y = pair
            self.beneath = self.prev_map[y][x]
            neighbors = self.get_neighbors(state['map'], x, y)
            for pattern in self.PATTERNS:
                for neighbor in neighbors:
                    parsed.append(neighbor in pattern)
                parsed.append(self.beneath in pattern)
        self.update_prev_map(state['map'])
        if parsed is None:
            return None
        binary_rep = ''.join(['1' if part else '0' for part in parsed])
        return int(binary_rep, 2)

    def update_Q(self, parsed_state):
        if self.prev_state is not None:
            max_Q = max([self.Q[(parsed_state, act)]
                         for act in action.MOVE_ACTIONS])
            new_Q = (1 - self.lr) * self.Q[(self.prev_state, self.prev_act)]
            new_Q += self.lr * (self.prev_reward + self.discount * max_Q)
            self.Q[(self.prev_state, self.prev_act)] = new_Q

    def choose_action(self, state):
        parsed_state = self.parse_state(state)
        self.update_Q(parsed_state)
        if state['message']['is_more']:
            act = action.Action.MORE
        elif state['message']['is_yn']:
            act = action.Action.YES
        else:
            if random.random() < self.epsilon:
                act = random.choice(action.MOVE_ACTIONS)
            else:
                best_actions = None
                best_Q = None
                for new_act in action.MOVE_ACTIONS:
                    new_Q = self.Q[(parsed_state, new_act)]
                    if best_Q is None or new_Q > best_Q:
                        best_actions = [new_act]
                        best_Q = new_Q
                    elif new_Q == best_Q:
                        best_actions.append(new_act)
                act = random.choice(best_actions)
        self.prev_state = parsed_state
        self.prev_act = act
        self.prev_reward = state['reward']
        return act

    def get_status(self):
        train_string = 'TRAIN' if self.train else 'TEST'
        status = '{}\tEP:{}'.format(train_string, self.epoch)
        if self.prev_state is not None:
            status += '\tST:{:014x}\tQ:{:.3f}'.format(
                self.prev_state, self.Q[(self.prev_state, self.prev_act)])
        if self.beneath is not None:
            status += '\tBN:{}'.format(self.beneath)
        else:
            status += '\tHELP'
        if self.prev_act is not None:
            status += '\t{}'.format(self.prev_act)
        return status

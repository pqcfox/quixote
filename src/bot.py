import random
import string
import collections

import action


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

    def __init__(self, lr=0.2, epsilon=0.1, discount=0.2):
        self.prev_state = None
        self.prev_act = None
        self.prev_reward = None
        self.prev_map = None
        self.prev_poses = []
        self.prev_Q = None
        self.beneath = None
        self.lr = lr
        self.epsilon = epsilon
        self.discount = discount
        self.Q = collections.defaultdict(float)

    def find_self(self, state_map):
        for y in range(len(state_map)):
            for x in range(len(state_map[0])):
                if state_map[y][x] == '@':
                    return x, y
        return None

    def get_neighbors(self, state_map, x, y):
        neighbors = []
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
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
        pos = self.find_self(state['map'])
        if pos is None or self.prev_map is None:
            parsed = None
        else:
            parsed = []
            x, y = pos
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
        return (int(binary_rep, 2), pos)

    def update_Q(self, parsed_state):
        if self.prev_state is not None:
            self.prev_Q = self.Q[(self.prev_state, self.prev_act)]
            max_Q = max([self.Q[(parsed_state, act)]
                         for act in action.MOVE_ACTIONS])
            new_Q = (1 - self.lr) * self.prev_Q
            new_Q += self.lr * (self.prev_reward + self.discount * max_Q)
            self.Q[(self.prev_state, self.prev_act)] = new_Q

    def modify_reward(self, reward, pos):
        if pos in self.prev_poses:
            reward -= 0.5
        return reward - 0.1

    def choose_action(self, state):
        pos = self.find_self(state['map'])
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
        self.prev_reward = self.modify_reward(state['reward'], pos)
        self.prev_poses.append(pos)
        return act

    def get_status(self):
        train_string = 'TRAIN' if self.train else 'TEST'
        status = '{}\tEP:{}'.format(train_string, self.epoch)
        if self.prev_state is not None and self.prev_Q is not None:
            status += '\tQ:{:.3f}\tR:{:.3f}\tST:{:038x}, {}'.format(
                self.Q[(self.prev_state, self.prev_act.name)],
                self.prev_reward, self.prev_state[0], self.prev_state[1])
        status += '\n'
        if self.beneath is not None:
            status += '\tBN:{}'.format(self.beneath)
        if self.prev_act is not None:
            status += '\t{}'.format(self.prev_act)
        status += '\n'
        for act in action.MOVE_ACTIONS:
            status += '\n\t{}:{:.3f}'.format(act.name, self.Q[(self.prev_state, act)])
        return status

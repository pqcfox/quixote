import random
import string

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


class ModelBasedBot:
    def __init__(self):
        self.prev_state = None
        self.prev_act = None
        self.observations = []
        self.exploring = True

    def find_self(self, state_map):
        for y in range(len(state_map)):
            for x in range(len(state_map[0])):
                if state_map[y][x] == '@':
                    return x, y
        return None

    def compute_probs(self):
        pass

    def get_neighbors(self, state_map, x, y):
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                neighbors.append(state_map[y][x])
        return neighbors

    def parse_state(self, state):
        parsed = []
        pair = self.find_self(state['map'])
        if pair is None:
            return None
        x, y = pair
        neighbors = self.get_neighbors(state['map'], x, y)
        for pattern in (string.ascii_letters, '+', '>', '$', '-|'):
            for neighbor in neighbors:
                parsed.append(neighbor in pattern)
        return parsed

    def choose_action(self, state):
        if state['message']['is_more']:
            act = action.Action.MORE
        elif state['message']['is_yn']:
            act = action.Action.YES
        else:
            parsed_state = self.parse_state(state)
            if self.exploring:
                if self.prev_state is not None:
                    observation = (self.prev_state, self.prev_act,
                                   parsed_state)
                    self.observations.append(observation)
                act = random.choice([act for act in action.MOVE_ACTIONS])
            else:
                pass  # TODO: implement
            self.prev_state = parsed_state
            self.prev_act = act
        return act

    def get_status(self):
        exp_string = 'LORE' if self.exploring else 'LOIT'
        train_string = 'TRAIN' if self.train else 'TEST'
        status = '{}\tEP:{}\t{}'.format(train_string, self.epoch, exp_string)
        if (len(self.observations) > 0
                and self.observations[-1][-1] is not None):
            binary_rep = ''.join(['1' if part else '0' for part in
                                  self.observations[-1][-1]])
            status += '\tST:{:05x}'.format(int(binary_rep, 2))
        if self.prev_act is not None:
            status += '\t{}'.format(self.prev_act)
        return status

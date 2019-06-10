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
    PATTERNS = [string.ascii_letters, '+', '>', '$', '-', '|']

    def __init__(self):
        self.prev_state = None
        self.prev_act = None
        self.prev_map = None
        self.beneath = None
        self.observations = []
        self.exploring = True
        # state_size = 
        # self.transition_probs = [[[1.0 / len(MOVE_ACTIONS)
        #                            for _ in range(len(
        self.transition_probs = None
        self.rewards = None

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
        return parsed

    def choose_action(self, state):
        if not self.exploring and self.epoch > self.prob_update_epoch:
            self.update_probs()
        if state['message']['is_more']:
            act = action.Action.MORE
        elif state['message']['is_yn']:
            act = action.Action.YES
        else:
            parsed_state = self.parse_state(state)
            # TODO: unify by initializing probs
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

    def update_probs_and_rewards():
        pass

    def get_status(self):
        exp_string = 'LORE' if self.exploring else 'LOIT'
        train_string = 'TRAIN' if self.train else 'TEST'
        status = '{}\tEP:{}\t{}'.format(train_string, self.epoch, exp_string)
        if (len(self.observations) > 0
                and self.observations[-1][-1] is not None):
            binary_rep = ''.join(['1' if part else '0' for part in
                                  self.observations[-1][-1]])
            status += '\tST:{:012x}'.format(int(binary_rep, 2))
        if self.beneath is not None:
            status += '\tBN:{}'.format(self.beneath)
        else:
            status += '\tHELP'
        if self.prev_act is not None:
            status += '\t{}'.format(self.prev_act)
        return status

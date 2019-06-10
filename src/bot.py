import random

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


class ModelBasedBot:
    def __init__(self):
        self.state = {}
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
                act = random.choice([act for act in action.MOVE_ACTIONS])
            else:
                pass  # TODO: implement
            self.prev_state = parsed_state
            self.prev_act = act
        return act

from enum import Enum, auto

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

KEY_ACTIONS = {
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

HASH_ACTIONS = {
    Action.LOOT: '#loot',
    Action.UNTRAP: '#untrap',
    Action.PRAY: '#pray'
}

MENU_ACTIONS = [
    Action.MORE,
    Action.YES,
    Action.NO
]

MOVE_ACTIONS = [
    Action.NORTH,
    Action.NORTH_EAST,
    Action.EAST,
    Action.SOUTH_EAST,
    Action.SOUTH,
    Action.SOUTH_WEST,
    Action.WEST,
    Action.NORTH_WEST,
    Action.STAIR_UP,
    Action.STAIR_DOWN,
    # Action.SEARCH
]

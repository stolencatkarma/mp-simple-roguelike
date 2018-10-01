# defines base creature in the base. all monsters, players, npcs, and critters derive from this.
from collections import defaultdict
import sys
import os
import json
from .position import Position

class Creature:
    def __init__(self, x, y):
        self.stats = defaultdict(dict)
        self.stats['strength'] = 10
        self.stats['dexterity']['base'] = 10
        self.stats['intelligence']['base'] = 10
        self.stats['perception']['base'] = 10
        self.stats['constitution']['base'] = 10
        self.position = Position(x,y)
        
        self.weapon = None
        self.armor = None
        self.command_queue = [] # what each creature wants to do this turn and the upcoming turns. contains a list of Action(s) that are processed by the server.
        self.name = None # is optional

        self.actions_per_turn = 1 # actions per turn (per second). (moving 5 ft a second is average walking speed)
        self.next_action_available = 0 # how many turns until we can take an action. if this is greater then 0 subtract 1 per turn until 0. add to this per action.

        self.symbol = '?' # base symbol for new creatures. if it doesn't get set it'll be a '?'



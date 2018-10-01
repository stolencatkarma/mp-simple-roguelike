from .creature import Creature
from .position import Position

class Terrain:
    def __init__(self, x, y, impassable=False, blocks_sight=False):
        self.impassable = impassable
        self.blocks_sight = blocks_sight
        self.position = Position(x,y)
        self.symbol = '?' # default symbol
        self.light_level = 0
        # not doing explored. i'd have to save a list for each player.
    
    def on_creature_entered(self, creature):
        pass

    def on_creature_exited(self, creature):
        pass

    
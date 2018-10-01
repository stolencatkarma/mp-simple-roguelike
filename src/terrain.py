from src.creature import Creature
from src.position import Position

class Terrain:
    def __init__(self, ident, position, impassable=False, blocks_sight=False):
        self.ident = ident
        self.position = position
        self.impassable = impassable
        self.blocks_sight = blocks_sight
        self.light_level = 0
        # not doing explored. i'd have to save a list for each player. (could be local I guess.)
    
    def on_creature_entered(self, creature):
        pass

    def on_creature_exited(self, creature):
        pass

    
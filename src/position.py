class Position: 
    # a position relative to the worldmap. 
    # To get the chunk we are in it's for example: Position(162, 164) it returns the modulous of the chunk size so 162 % is worldmap[10][10] remainder 2 and 4 or 
    #                                                                            (worldmap[10][10].pos.x + 2 and .pos.y + 4)
    # that way Positions are related to worldmap and not individual chunks.
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.previous = None # used for pathfinding.

    def __eq__(self, tp): # required to be hashable.
        if(tp.x == self.x):
            if(tp.y == self.y):
                return True
        return False

    def __hash__(self): # so we can use it as a dict object.
        return hash((self.x, self.y))

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'

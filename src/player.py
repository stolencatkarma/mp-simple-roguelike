from .creature import Creature

class Player(Creature):
    def __init__(self, name='JohnDoe'):
        Creature.__init__(self,2,2)
        self.name = name
        self.symbol = '@'
    
    def __str__(self):
        return self.name

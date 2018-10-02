from src.creature import Creature

class Player(Creature):
    def __init__(self, x, y, name='Andrew'):
        Creature.__init__(self,x,y)
        self.name = name
    
    def __str__(self):
        return self.name

from src.creature import Creature

class Player(Creature):
    def __init__(self, x, y, connection_object, name='Andrew'):
        Creature.__init__(self,x,y)
        self.name = name
        self.connection_object = connection_object
    
    def __str__(self):
        return self.name

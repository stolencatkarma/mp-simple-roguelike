class Furniture: # we only need to store the furiture and the items it contains.
    def __init__(self, ident):
        self.ident = ident
        pass
    def __str__(self):
        return str(self.ident)
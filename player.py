from wall import sort_hand


class Player:
    def __init__(self, name:str, wind):
        self.name = name
        self.wind = wind
        self.hand = []
        self.discards = []
        self.score = 25000

    def draw(self, wall):
        if wall:
            tile = wall.pop(0)
            self.hand.append(tile)
            return tile
        return None

    def discard(self, index):
        tile = self.hand.pop(index)
        self.discards.append(tile)
        return tile

    def sort_hand(self):
        self.hand = sort_hand(self.hand)
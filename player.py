from wall import sort_hand
import random


class Player:
    def __init__(self, name:str, wind):
        self.name = name
        self.wind = wind
        self.hand = []
        self.discards = []
        self.melds = []
        self.score = 25000
        self.is_human = False
        self.is_riichi = False
        self.riichi_declared_on_discard_idx = None  # The index in discards where riichi was declared
        self.riichi_declared = False  # Whether riichi was declared in this round

    def draw(self, wall):
        if wall:
            tile = wall.pop(0)
            self.hand.append(tile)
            return tile
        return None

    def discard(self, index):
        tile = self.hand.pop(index)
        self.discards.append(tile)
        if self.riichi_declared:
            self.riichi_declared_on_discard_idx = len(self.discards) - 1  # record the tile discarded when declaring riichi
            self.riichi_declared = False
        return tile

    def decide_discard(self):
        """strategy to discard, by default it randomly discards."""
        if self.is_riichi:
            return len(self.hand) - 1 # discard tiles drew after riichi
        return random.randint(0, len(self.hand) - 1)

    def sort_hand(self):
        self.hand = sort_hand(self.hand)

    def sort_melds(self):
        for i, meld in enumerate(self.melds):
            self.melds[i] = sort_hand(meld)

class AIPlayer(Player):
    def __init__(self, name:str, wind):
        super().__init__(name, wind)
        self.is_human = False
    def decide_discard(self):
        """strategy for AI to discard"""
        return random.randint(0, len(self.hand) - 1)

class HumanPlayer(Player):
    def __init__(self, name:str, wind):
        super().__init__(name, wind)
        self.is_human = True
    def decide_discard(self):
        """discard on human input"""
        if self.is_riichi:
            return super().decide_discard()
        while True:
            formatted_hand = [f"({i}){tile.to_colored_str() }" for i, tile in enumerate(self.hand)]
            print(f"your hand: {' '.join(formatted_hand)} ")
            user_input = input("choose a tile index to discard: ")
            # check the input
            if not user_input.isdigit():
                print("[x] please enter a valid tile index")
                continue
            idx = int(user_input)
            if idx < 0 or idx >= len(self.hand):
                print(f"[x] Invalid index, please choose between 0 and {len(self.hand)-1}.")
            else:
                return idx
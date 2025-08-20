from wall import sort_hand
import random


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

    def decide_discard(self):
        """strategy to discard, by default it randomly discards."""
        return random.randint(0, len(self.hand) - 1)

    def sort_hand(self):
        self.hand = sort_hand(self.hand)

class AIPlayer(Player):
    def decide_discard(self):
        """strategy for AI to discard"""
        return random.randint(0, len(self.hand) - 1)

class HumanPlayer(Player):
    def decide_discard(self):
        """discard on human input"""
        while True:
            formatted_sorted_hand = [f"({i}){tile}" for i, tile in enumerate(self.hand)]
            print(f"your hand: {formatted_sorted_hand}")
            user_input = input("choose a tile index to discard: ")
            # check the input
            if not user_input.isdigit():
                print("[x] please enter a valid tile index")
                continue
            idx = int(user_input)
            if idx < 0 or idx > len(self.hand):
                print(f"[x] Invalid index, please choose between 0 and {len(self.hand)-1}.")
            else:
                return idx
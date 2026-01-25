from collections import Counter
from tiles import Tile
from hand_checker import normalize_red, sort_hand

def all_unique_tiles():
    """
    Return all unique 34 types of tiles
    """
    tiles = []
    for suit in 'mps':
        for v in range(1, 10):
            tiles.append(Tile(suit, v))
    for v in ['E', 'S', 'W', 'N', 'P', 'F', 'C']:
        tiles.append(Tile('z', v))
    return tiles

class ShantenCalculator:
    """
    calculate shanten number for different hand types (standard, chiitoitsu, kokushi musou)
    """
    def __init__(self, hand):
        self.hand = sort_hand(([normalize_red(t) for t in hand]))

    def calculate(self):
        """
        Returns:
            min_shanten: int, minimal shanten across all forms
            best_type: str, 'standard' or 'chiitoitsu' or 'kokushi'
            details: dict, shanten for each type
        """
        s_std = self.shanten_standard(self.hand)
        s_chiitoitsu = self.shanten_chiitoitsu(self.hand)
        s_kokushi = self.shanten_kokushi(self.hand)
        min_shanten = min(s_std, s_chiitoitsu, s_kokushi)
        if min_shanten == s_std:
            shanten_type = 'standard'
        elif min_shanten == s_chiitoitsu:
            shanten_type = 'chiitoitsu'
        else:
            shanten_type = 'kokushi'
        return min_shanten, shanten_type, {'standard': s_std, 'chiitoitsu': s_chiitoitsu, 'kokushi': s_kokushi}

    @staticmethod
    def shanten_kokushi(hand):
        yaochu = {
        Tile('m', 1), Tile('m', 9),
        Tile('p', 1), Tile('p', 9),
        Tile('s', 1), Tile('s', 9),
        Tile('z', 'E'), Tile('z', 'S'),
        Tile('z', 'W'), Tile('z', 'N'),
        Tile('z', 'P'), Tile('z', 'F'),
        Tile('z', 'C')
        }
        unique = set()
        have_pair = False
        counter = Counter(hand)
        for t in yaochu:
            if counter[t]:
                unique.add(t)
                if counter[t] >= 2:
                    have_pair = True
        missing = 13 - len(unique)
        thirteen_wait = True if missing == 0 else False #国士無双１３面待ち
        if thirteen_wait:
            return 0
        return missing if have_pair else missing + 1

    @staticmethod
    def shanten_chiitoitsu(hand):
        counter = Counter(hand)
        pairs = sum(1 for v in counter.values() if v >= 2)
        unique = len(counter)
        return 6 - pairs + max(0, 7 - unique)

    @staticmethod
    def shanten_standard(hand):
        min_shanten = [8] # use list not int to pass the value through the function

        def dfs(tiles, meld=0, pair=0):
            if meld > 4:
                return
            n = len(tiles)
            if n == 0:
                shanten = 8 - meld * 2 - pair
                if shanten < min_shanten[0]:
                    min_shanten[0] = shanten
                return
            counter = Counter(tiles)
            # remove pungs
            for t in set(tiles):
                if counter[t] >= 3:
                    new_tiles = tiles[:]
                    for _ in range(3):
                        new_tiles.remove(t)
                    dfs(new_tiles, meld+1, pair)
            # remove chows
            for t in set(tiles):
                if t.suit in 'mps' and 1 <= t.value <= 7:
                    second_tile = Tile(t.suit, t.value + 1)
                    third_tile = Tile(t.suit, t.value + 2)
                    if second_tile in tiles and third_tile in tiles:
                        new_tiles = tiles[:]
                        new_tiles.remove(t)
                        new_tiles.remove(second_tile)
                        new_tiles.remove(third_tile)
                        dfs(new_tiles, meld+1, pair)
            # remove pair
            for t in set(tiles):
                if counter[t] >= 2 and pair < 1:
                    new_tiles = tiles[:]
                    new_tiles.remove(t)
                    new_tiles.remove(t)
                    dfs(new_tiles, meld, pair+1)
            # no longer removable
            shanten = 8 - meld * 2 - pair
            if shanten < min_shanten[0]:
                min_shanten[0] = shanten

        dfs(hand, 0, 0)
        return min_shanten[0]

    def waiting_tiles(self):
        from wall import create_wall
        all_types = set(create_wall())
        waits = []
        for t in all_types:
            if self.hand.count(t) >= 4:
                continue
            test_hand = self.hand + [t]
            calc = ShantenCalculator(test_hand)
            min_shanten, _, _ = calc.calculate()
            if min_shanten == -1:
                waits.append(t)
        return waits


#test
if __name__ == '__main__':
    # Example: standard tenpai hand
    hand = [
        Tile('p', 3), Tile('p', 2),
        Tile('m', 5), Tile('m', 6), Tile('m', 7),
        Tile('m', 5), Tile('m', 6), Tile('m', 4),
        Tile('m', 7), Tile('m', 8), Tile('m', 9),
        Tile('s', 7), Tile('s', 7),
    ]
    calc = ShantenCalculator(hand)
    min_shanten, typ, detail = calc.calculate()
    print(f"Minimal shanten: {min_shanten}, type: {typ}, detail: {detail}")
    if min_shanten == 0:
        waits = calc.waiting_tiles()
        print("Waits:", waits)
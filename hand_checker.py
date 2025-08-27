from collections import Counter
from wall import sort_hand
from tiles import Tile

def normalize_red(tile: Tile) -> Tile:
    """
    convert red 5 tiles(0m/0p/0s) to normal 5m/5p/5s
    """
    if tile.suit in ("m","p","s") and tile.value == 0:
        return Tile(tile.suit, 5)
    return tile

def is_win_hand(hand:list):
    """
    check if this hand is a winning hand
    winging hands:
    basic: 4 * melds + 1 * pair
    """
    if len(hand) != 14:
        return False

    hand = [normalize_red(tile) for tile in hand]
    hand = sort_hand(hand)

    # check Kokushi Musou
    if is_kokushi(hand):
        return True, "kokushi"

    # check chiitoitsu
    if is_chiitoitsu(hand):
        return True, "chiitoitsu"

    # check standard
    is_standard_winning, head, pungs, chows = try_split_standard_hand(hand)
    if is_standard_winning:
        return True, "standard"

    return False

def is_kokushi(hand:list[Tile]):
    terminals_and_honors = [
        Tile('m', 1), Tile('m', 9),
        Tile('p', 1), Tile('p', 9),
        Tile('s', 1), Tile('s', 9),
        Tile('z', 'E'), Tile('z', 'S'),
        Tile('z', 'W'), Tile('z', 'N'),
        Tile('z', 'P'), Tile('z', 'F'),
        Tile('z', 'C')
    ]
    unique_tiles = set(terminals_and_honors)
    hand_set = set(hand)
    if not unique_tiles.issubset(hand_set):
        return False
    counter = Counter(hand)
    num_pairs = sum(v == 2 for k, v in counter.items() if k in unique_tiles) # one pair in terminals and honors
    if num_pairs == 1:
        return True
    return False

def is_chiitoitsu(hand:list[Tile]):
    counter = Counter(hand)
    if len(counter) == 7 and all(v == 2 for v in counter.values()):
        return True
    return False

def try_split_standard_hand(hand:list[Tile]):
    """
    split hand into head and melds
    """
    hand = [normalize_red(tile) for tile in hand]
    hand = sort_hand(hand)
    for i in range(len(hand) - 1):
        if hand[i] == hand[i + 1]:
            head = [hand[i], hand[i + 1]]
            remaining = hand[:i] + hand[i + 2:]
            flag, pungs, chows = split_melds(remaining)
            if flag:
                return True, head, pungs, chows
    return False, None, [], []


def split_melds(tiles, pung_list=None, chow_lsit=None):
    """
    split hand into melds
    if no remaining tile in the list after split, it is considered as a winning hand
    """
    if pung_list is None:
        pung_list = []
    if chow_lsit is None:
        chow_lsit = []

    if not tiles:
        return True, pung_list[:], chow_lsit[:] # no remaining tile in the list means the original tiles is consisted of melds
    if len(tiles) % 3 != 0:
        return False, [], []

    first_tile = tiles[0]

    # check pung
    if tiles.count(first_tile) >= 3:
        new_tiles = tiles[:]
        meld = []
        for _ in range(3):
            new_tiles.remove(first_tile)
            meld.append(first_tile)
        flag, pungs, chows = split_melds(new_tiles, pung_list + [meld], chow_lsit)
        if flag:
            return True, pungs, chows

    # check chow
    if first_tile.suit in ("m", "p", "s"):
        val = first_tile.value
        if val <= 7:
            second_tile = Tile(first_tile.suit, val+1)
            third_tile = Tile(first_tile.suit, val+2)
            if second_tile in tiles and third_tile in tiles:
                new_tiles = tiles[:]
                meld = [first_tile, second_tile, third_tile]
                new_tiles.remove(first_tile)
                new_tiles.remove(second_tile)
                new_tiles.remove(third_tile)
                flag, pungs, chows = split_melds(new_tiles, pung_list, chow_lsit + [meld])
                if flag:
                    return True, pungs, chows
    return False, [], []


# no longer used
def can_form_melds(tiles:list):
    """
    check if the tiles is consisted of melds
    """
    if not tiles:
        return True # no remaining tile in the list means the original tiles is consisted of melds
    if len(tiles) %3 != 0:
        return False

    first_tile = tiles[0]

    # check pung
    if tiles.count(first_tile) >= 3:
        new_tiles = tiles[:]
        for _ in range(3):
            new_tiles.remove(first_tile)
        return can_form_melds(new_tiles)

    # check chow
    if first_tile.suit in ("m", "p", "s"):
        val = first_tile.value
        if val <= 7:
            # create Tile objects for the next two in sequence
            second_tile = Tile(first_tile.suit, val+1)
            third_tile = Tile(first_tile.suit, val+2)

            if second_tile in tiles and third_tile in tiles:
                new_tiles = tiles[:]
                new_tiles.remove(first_tile)
                new_tiles.remove(second_tile)
                new_tiles.remove(third_tile)
                return can_form_melds(new_tiles)

    return False



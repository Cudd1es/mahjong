from tiles import Tile
from hand_checker import normalize_red

def can_chi(hand, tile):
    # normalize red 5 tiles
    hand = [normalize_red(tile) for tile in hand]
    if tile.suit == 'z':
        return []

    options = []
    values = [t.value for t in hand if t.suit == tile.suit]

    for seq in [
        (tile.value - 2, tile.value - 1),  # e.g.: 4p 5p + 6p
        (tile.value - 1, tile.value + 1),  # e.g.: 5p 7p + 6p
        (tile.value + 1, tile.value + 2)  # e.g.: 7p 8p + 6p
    ]:
        if all(1 <= v <= 9 for v in seq):
            if seq[0] in values and seq[1] in values:
                options.append([Tile(tile.suit, seq[0]), Tile(tile.suit, seq[1])])

    return options

def can_pon(hand, tile):
    # normalize red 5 tiles
    hand = [normalize_red(tile) for tile in hand]
    return sum(1 for t in hand if t == tile) >= 2

def can_kan(hand, tile):
    hand = [normalize_red(tile) for tile in hand]
    return sum(1 for t in hand if t == tile) >= 3

def can_ankan(hand):
    hand = [normalize_red(tile) for tile in hand]
    tiles_count = {}
    for t in hand:
        tiles_count[t] = tiles_count.get(t, 0) + 1
    return [[tile] * 4 for tile, count in tiles_count.items() if count == 4]



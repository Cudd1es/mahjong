import random
from tiles import Tile

def create_wall():
    """create the full wall including red 5 tiles (0m, 0p, 0s)"""
    suits = ['m', 'p', 's']
    honors = ['E', 'S', 'W', 'N', 'P', 'F', 'C']
    wall = []

    for suit in suits:
        for value in range(1, 10):
            wall.extend([Tile(suit, value) for _ in range(4)])

    wall.remove(Tile('m', 5))
    wall.remove(Tile('p', 5))
    wall.remove(Tile('s', 5))
    wall.append(Tile('m', 0))
    wall.append(Tile('p', 0))
    wall.append(Tile('s', 0))


    for honor in honors:
        wall.extend([Tile('z', honor) for _ in range(4)])

    return wall

def shuffle_wall(wall):
    """shuffle tiles randomly"""
    random.shuffle(wall)

def deal_tiles(wall, num_players=4):
    """deal tiles to the players, 13 tiles for each player, dealer has one more tile"""
    hands = [[] for _ in range(num_players)]

    for i in range(num_players):
        hands[i] = wall[i*13:(i+1)*13]

    #dealer
    hands[0].append(wall[num_players*13])

    remaining_wall = wall[num_players*13+1:]

    return hands, remaining_wall

def tile_sort_rule(tile:Tile):
    """define the rule of tile sorting"""

    suit_order = {'m':0, 'p':1, 's':2, 'z':3}

    suit_rank = suit_order[tile.suit]

    if tile.suit in ('m', 'p', 's'):
        value = tile.value
        if value == 0:
            return (suit_rank, 5 - 0.5)
        return (suit_rank, value)

    honor_order = {'E':1, 'S':2, 'W':3, 'N':4, 'P':5, 'F':6, 'C':7}

    return (suit_rank, honor_order[tile.value])

def sort_hand(hand:list):
    return sorted(hand, key=tile_sort_rule)
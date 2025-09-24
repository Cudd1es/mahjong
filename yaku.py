from player import Player, sort_hand
from tiles import Tile
from hand_checker import normalize_red, is_chiitoitsu, is_kokushi, try_split_standard_hand, split_melds
from collections import Counter

def check_yaku(hand:list[Tile], tile:Tile, player:Player, is_tsumo:bool=False)->list[tuple[str, int]]:
    """
    args:
        hand: list of 14 Tile objects (normalized)
        tile: Tile object, the tile for ron or tsumo
        player: Player object, player for yaku calculation
        is_tsumo: bool, is self-draw
        is_riichi: bool, is Riichi declared
    returns:
        list of (yaku name, han_value)
    """
    tmp_hand = hand[:] + [tile]
    dora = 0
    # count aka dora first and then convert all aka dora to normal tiles
    aka_dora = sum(1 for t in tmp_hand if t.value == 0)
    dora += aka_dora

    tmp_hand = [normalize_red(tile) for tile in tmp_hand]
    result = []

    tmp_meld = []
    if player.melds:
        for m in player.melds:
            tmp_meld += m
    tmp_meld = [normalize_red(tile) for tile in tmp_meld]

    _, head, pungs, chows = try_split_standard_hand(tmp_hand)
    tmp_lable, m_pungs, m_chows = split_melds(tmp_meld)

    all_pungs = pungs + m_pungs
    all_chows = chows + m_chows

    print(f"head: {head}, pungs: {all_pungs}, chows: {all_chows}")

    # dora
    if dora > 0:
        result.append(('dora', dora))
    # menzenchin tsumo
    if is_menzen(player) and is_tsumo:
        result.append(('menzen', 1))
    # riichi
    if is_menzen(player) and player.is_riichi:
        result.append(('riichi', 1))
    # pinfu
    if is_pinfu(hand, tile, player):
        result.append(('pinfu', 1))
    # tanyao
    if is_tanyao(tmp_hand, player):
        result.append(('tanyao', 1))
    # chiitoitsu
    if is_chiitoitsu(tmp_hand):
        result.append(('chiitoitsu', 2))
    # honitsu
    flag, factor = is_honitsu(tmp_hand, player)
    if flag:
        result.append(('honitsu', 3+factor))
    # chinitsu
    flag, factor = is_chinitsu(tmp_hand, player)
    if flag:
        result.append(('chinitsu', 6+factor))
    # toitoi
    if is_toitoi(all_pungs, all_chows):
        result.append(('toitoi', 2))
    # sanshouku doujun
    flag, factor = is_sanshouku_doujun(all_chows, player)
    if flag:
        result.append(('sanshouku_doujun', 2+factor))
    # sanshouku doukou
    flag, factor = is_sanshouku_doukou(all_pungs, player)
    if flag:
        result.append(('sanshouku_doukou', 2+factor))
    # ittsu 一気通貫

    # yakuhai
    flag, yaku_result = yakuhai(all_pungs, player)
    if flag:
        result += yaku_result

    # iipeikou
    if is_iipeikou(chows, player):
        result.append(('iipeikou', 2))
    # ryanpeikou
    if is_ryanpeikou(chows, player):
        result.append(('ryanpeikou', 3))
    # ippatsu

    # haitei
    # houtei
    # rinshan
    # double riichi
    # chantaiyao
    # junchan
    # sanankou
    # sankangtsu
    # honroutou
    # shousangen
    # kokushi


    return result

def is_honor(tile: Tile) -> bool:
    if tile.suit == 'z':
        return True
    return False

def is_terminal(tile: Tile) -> bool:
    if tile.value in [1, 9]:
        return True
    return False

def is_menzen(player) -> bool:
    if player.melds:
        return False
    else: return True

def is_tanyao(hand:list[Tile], player):
    for tile in hand:
        if is_terminal(tile) or is_honor(tile):
            return False
    if player.melds:
        for meld in player.melds:
            for tile in meld:
                if is_terminal(tile) or is_honor(tile):
                    return False
    return True

def is_honitsu(hand, player):
    factor = -1 if player.melds else 0
    tmp_hand = hand[:]
    if player.melds:
        for m in player.melds:
            tmp_hand += m
    suits = [t.suit for t in tmp_hand]
    suits = set(suits)
    if len(suits) == 2 and 'z' in suits:
        return True, factor
    return False, 0

def is_chinitsu(hand, player):
    factor = -1 if player.melds else 0
    tmp_hand = hand[:]
    if player.melds:
        for m in player.melds:
            tmp_hand += m
    suits = [t.suit for t in tmp_hand]
    suits = set(suits)
    if len(suits) == 1 and 'z' not in suits:
        return True, factor
    return False, 0

def is_toitoi(pungs, chows):
    if not chows and len(pungs) == 4:
        return True
    return False

def yakuhai(pungs, player):
    result = []
    for p in pungs:
        if p[0].suit == 'z':
            if p[0].value in ["P", "F", "C"]:
                result.append((p[0].value, 1))
            if p[0].value == player.wind:
                result.append(("seat wind", 1))
            if p[0].value == "E":
                result.append(("round wind", 1))
    if result:
        return True, result
    return False, []

def is_pinfu(hand:list[Tile], tile, player):
    tmp_hand = hand[:] + [tile]
    if len(tmp_hand) != 14:
        return False
    tmp_hand = [normalize_red(tile) for tile in tmp_hand]
    tmp_hand = sort_hand(tmp_hand)

    # WIP
    return False

def is_iipeikou(chows, player):
    if player.melds:
        return False
    elif is_ryanpeikou(chows, player):
        return False
    chows_counter = Counter(tuple(sorted(meld, key=lambda t: (t.suit, t.value))) for meld in chows)
    return sum(1 for c in chows_counter.values() if c == 2) == 1


def is_ryanpeikou(chows, player):
    if player.melds:
        return False
    chows_counter = Counter(tuple(sorted(meld, key=lambda t: (t.suit, t.value))) for meld in chows)
    return sum(1 for c in chows_counter.values() if c == 2) == 2

def is_sanshouku_doujun(all_chows, player):
    factor = -1 if player.melds else 0
    chows = set([tuple(sorted(meld, key=lambda t: (t.suit, t.value))) for meld in all_chows])
    for chow in chows:
        s, v = chow[0].suit, chow[0].value
        tmp1 = tuple([Tile('m', v), Tile('m', v + 1), Tile('m', v + 2)])
        tmp2 = tuple([Tile('p', v), Tile('p', v + 1), Tile('p', v + 2)])
        tmp3 = tuple([Tile('s', v), Tile('s', v + 1), Tile('s', v + 2)])
        if tmp1 in chows and tmp2 in chows and tmp3 in chows:
            return True, factor
    return False, 0

def is_sanshouku_doukou(all_pungs, player):
    factor = -1 if player.melds else 0
    pungs = set([tuple(sorted(meld, key=lambda t: (t.suit, t.value))) for meld in all_pungs])
    for pung in pungs:
        s, v = pung[0].suit, pung[0].value
        tmp1 = tuple([Tile('m', v), Tile('m', v), Tile('m', v)])
        tmp2 = tuple([Tile('p', v), Tile('p', v), Tile('p', v)])
        tmp3 = tuple([Tile('s', v), Tile('s', v), Tile('s', v)])
        if tmp1 in pungs and tmp2 in pungs and tmp3 in pungs:
            return True, factor
    return False, 0
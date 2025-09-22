from tiles import Tile
from player import Player
from yaku import *
def test_sanshouku_doujun_menzen():
    # 门清三色同顺，234m,234p,234s
    all_chows = [
        [Tile('m',2), Tile('m',3), Tile('m',4)],
        [Tile('p',2), Tile('p',3), Tile('p',4)],
        [Tile('s',2), Tile('s',3), Tile('s',4)]
    ]
    player = Player("Test", "E")
    player.melds = []
    result, factor = is_sanshouku_doujun(all_chows, player)
    assert result and factor == 0

def test_sanshouku_doujun_open():
    all_chows = [
        [Tile('m',2), Tile('m',3), Tile('m',4)],
        [Tile('p',2), Tile('p',3), Tile('p',4)],
        [Tile('s',2), Tile('s',3), Tile('s',4)]
    ]
    player = Player("Test", "E")
    player.melds = [[Tile('p',2), Tile('p',3), Tile('p',4)]]
    result, factor = is_sanshouku_doujun(all_chows, player)
    assert result and factor == -1

def test_not_sanshouku_doujun():
    all_chows = [
        [Tile('m',2), Tile('m',3), Tile('m',4)],
        [Tile('p',2), Tile('p',3), Tile('p',4)],
        [Tile('s',3), Tile('s',4), Tile('s',5)]
    ]
    player = Player("Test", "E")
    result, factor = is_sanshouku_doujun(all_chows, player)
    assert not result

def test_sanshouku_doukou_menzen():
    all_pungs = [
        [Tile('m',7), Tile('m',7), Tile('m',7)],
        [Tile('p',7), Tile('p',7), Tile('p',7)],
        [Tile('s',7), Tile('s',7), Tile('s',7)]
    ]
    player = Player("Test", "E")
    player.melds = []
    result, factor = is_sanshouku_doukou(all_pungs, player)
    assert result and factor == 0

def test_not_sanshouku_doukou():
    all_pungs = [
        [Tile('m',7), Tile('m',7), Tile('m',7)],
        [Tile('p',7), Tile('p',7), Tile('p',7)],
        [Tile('s',8), Tile('s',8), Tile('s',8)]
    ]
    player = Player("Test", "E")
    result, factor = is_sanshouku_doukou(all_pungs, player)
    assert not result


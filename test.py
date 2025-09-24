from player import Player
from hand_converter import hand_converter
from tiles import Tile
from yaku import check_yaku

test_player = Player("p1", "E")

str_hand1 = "13m12663p123345s"
str_hand2 = "22m222p222789s44z"
hand = hand_converter(str_hand1)
print(hand)

test_tile = Tile("m", 2)
yaku = check_yaku(hand, test_tile, test_player)

print(f"yaku: {yaku}")


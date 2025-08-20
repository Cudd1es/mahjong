from tiles import Tile
from hand_checker import is_win_hand
from tiles import Tile


def parse_hand(hand_str_list: list[str]) -> list[Tile]:
    """
    Convert a list of string tiles into a list of Tile objects.

    Examples of input:
        "1m", "0p", "5s", "E", "F", "C"
    """
    tile_list = []
    for t in hand_str_list:
        if t[-1] in ("m", "p", "s"):  # 数牌
            value = int(t[:-1])
            suit = t[-1]
            tile_list.append(Tile(suit, value))
        else:  # 字牌
            tile_list.append(Tile("z", t))
    return tile_list



hand1 = ["1m","2m","3m","4p","5p","6p","7s","8s","9s","E","E","E","0m","5m"]
# True : 1m2m3m | 4p5p6p | 7s8s9s | EEE | 5m5m(赤5当5m)

hand2 = ["1m","2m","3m","0p","5p","6p","9s","8s","9s","E","E","E","5m","5m"]
# True : 1m2m3m | 0p5p6p (即 4p5p6p) | 7s8s9s | EEE | 5m5m


print(parse_hand(hand1))  # 会自动调用 __repr__，输出类似 [1m, 2m, 3m, ...]
hand1 = parse_hand(hand1)
hand2 = parse_hand(hand2)
print(is_win_hand(hand2))

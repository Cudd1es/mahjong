from tiles import Tile
from wall import sort_hand

def hand_converter(hand_str):
    """
    convert the hand like "123456m456p777s22z" to list of Tile objects
    """

    # string checker here

    # convert
    result = []
    z_dict = {
        '1': 'E',
        '2': 'S',
        '3': 'W',
        '4': 'N',
        '5': 'P',
        '6': 'F',
        '7': 'C'
    }
    tmp_suit = None

    for i in range(len(hand_str)-1, -1, -1):
        if hand_str[i].lower() in "mpsz":
            tmp_suit = hand_str[i].lower()
        else:
            if tmp_suit == 'z':
                result.append(Tile(tmp_suit, z_dict[hand_str[i]]))
            else:
                result.append(Tile(tmp_suit, hand_str[i]))
    result = sort_hand(result)
    return result


case = "123456m456p777s22z"
ret = hand_converter(case)
print(ret)
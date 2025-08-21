from wall import *
from player import *
import random
from hand_checker import is_win_hand
from melds import can_chi, can_pon, can_kan


def check_win(player, hand, source, tile=None):
    """
    Check if a player wants to declare a win (Ron or Tsumo).
    :param player: The player object.
    :param hand: The player's hand.
    :param source: "draw" for Tsumo, "discard" for Ron, "tenhou" for Tenhou.
    :param tile: The tile that allows Ron (if source == "discard").
    :return: True if player declares win, False otherwise.
    """

    if not is_win_hand(hand):
        return False

    if source == "draw":
        msg = f"{player.name}, you can Tsumo! Do you want to win? ([Y]/n): "
        win_type = "Tsumo"
    elif source == "discard":
        msg = f"{player.name}, you can Ron with {tile}! Do you want to win? ([Y]/n): "
        win_type = "Ron"
    elif source == "tenhou":
        msg = f"{player.name}, you have Tenhou! Do you want to win? ([Y]/n): "
        win_type = "Tenhou"
    else:
        raise ValueError(f"Invalid source type: {source}")

    if player.is_human:
        while True:
            choice = input(msg).strip().lower()
            if choice in ['y', '']:
                print(f"{player.name} declared {win_type}!")
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid input, please choose from y or n.")
    else:
        print(f"{player.name} declared {win_type}!")
        return True



def play_round():
    wall = create_wall()
    shuffle_wall(wall)

    # set human player as P1 and rest player are AI
    players = [
        HumanPlayer("P1", "E"),
        AIPlayer("P2", "S"),
        AIPlayer("P3", "W"),
        AIPlayer("P4", "N")
    ]

    hands, wall = deal_tiles(wall, 4)
    for i, p in enumerate(players):
        p.hand = hands[i]
        p.sort_hand()

    # separate dead wall (14 tiles)
    dead_wall = wall[14:]
    live_wall = wall[:-14]

    for p in players:
        print(f"{p.name} ({p.wind}) hand: {p.hand}")

    # check Tenhou
    for p in players:
        if check_win(p, p.hand, "tenhou"):
            return

    turn = 0
    while len(live_wall) > 0:
        current_player = players[turn%4]
        print(f"\nround {turn} {current_player.name} ({current_player.wind})'s turn---")

        current_player.sort_hand()

        if turn != 0:
            drawn_tile = current_player.draw(live_wall)
            if drawn_tile is None:
                print("No more tiles to draw, game ends in draw")
                break
            print(f"{current_player.name} ({current_player.wind}) drew {drawn_tile}")

            # check Tsumo
            if check_win(current_player, current_player.hand, "draw"):
                return

        print(f"Hand: {current_player.hand}")

        discard_index = current_player.decide_discard()
        #print(f"Discard index {discard_index} out of {len(current_player.hand) - 1}--")
        discarded = current_player.discard(discard_index)
        print(f"{current_player.name} discarded {discarded}")

        # Check if other players can Ron (win by discard)
        for other_player in players:
            if other_player != current_player:
                if check_win(other_player, other_player.hand, "discard", tile=discarded):
                    return


        if len(live_wall) == 0:
            print("\nNo more tiles in live wall. The game ends in draw")
            break
        turn += 1


if __name__ == "__main__":
    play_round()


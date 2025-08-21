from wall import *
from player import *
import random
from hand_checker import is_win_hand
from melds import can_chi, can_pon, can_kan


def check_win(player, source, tile=None):
    """
    Check if a player wants to declare a win (Ron or Tsumo or Tenhou).
    This function now supports a unified interaction style as the meld checker.

    Args:
        player: the Player object (AI or Human).
        hand: the current hand (list of Tile).
        source: "draw" (Tsumo), "discard" (Ron), or "tenhou".
        tile: the winning tile if Ron.

    Returns:
        True if the player declares win, False otherwise.
    """
    new_hand = player.hand[:]
    if player.melds:
        for m in player.melds:
            new_hand += m
    if tile:
        new_hand = new_hand + [tile]
    if not is_win_hand(new_hand):
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
            if choice.strip().lower() in ["y", ""]:
                print(f"{player.name} declared {win_type}!")
                return True
            elif choice.strip().lower() == 'n':
                return False
            else:
                print("Invalid input, please choose from y or n.")
    else:
        print(f"{player.name} declared {win_type}!")
        return True

def check_melds(players, discarder_idx, discarded_tile):
    """
    Checks if any human player wants to claim the discarded tile for Kan, Pon, or Chi.
    Returns (meld_made: bool, claiming_player_idx: int, meld_type: int, meld_tiles: list of Tile objects)
    meld_type: 0: Skipped 1: Kan, 2: Pon, 3: Chi.
    """
    meld_made = False
    claiming_player_idx = discarder_idx
    meld_type = 0
    meld_tiles = []

    # Kan
    for i in range(1, 4):
        idx = (discarder_idx + i) % 4 # other 3 players in order
        p = players[idx]
        if not p.is_human:
            continue  # AI players skip melds
        if can_kan(p.hand, discarded_tile):
            while True:
                print(f"Your hand: {sort_hand(p.hand)}")
                choice = input(f"{p.name}, do you want to Kan {discarded_tile}? ([Y]/n): ")
                if choice.strip().lower() in ["y", ""]:
                    meld_type = 1  # kan
                    meld_tiles = [discarded_tile]  # add discarded tile to meld tiles
                    print(f"{p.name} claims Kan with {discarded_tile}!")
                    removed = 0
                    new_hand = []
                    for t in p.hand:
                        if t == discarded_tile and removed < 3:
                            removed += 1
                            meld_tiles.append(t) # add hand tiles
                        else:
                            new_hand.append(t)
                    p.hand = new_hand
                    p.melds.append([discarded_tile] * 4)
                    meld_made = True
                    claiming_player_idx = idx
                    return meld_made, claiming_player_idx, meld_type, meld_tiles
                elif choice.strip().lower() == 'n':
                    meld_made = False
                    meld_type = 0
                    return meld_made, claiming_player_idx, meld_type, meld_tiles
                else:
                    print("Invalid input, please choose from y or n.")

    # Pon
    for i in range(1, 4):
        idx = (discarder_idx + i) % 4
        p = players[idx]
        if not p.is_human:
            continue  # AI players skip melds
        if can_pon(p.hand, discarded_tile):
            while True:
                print(f"Your hand: {sort_hand(p.hand)}")
                choice = input(f"{p.name}, do you want to Pon {discarded_tile}? ([Y]/n): ")
                if choice.strip().lower() in ["y", ""]:
                    meld_type = 2  # pon
                    meld_tiles = [discarded_tile]  # add discarded tile to meld tiles
                    print(f"{p.name} claims Pon with {discarded_tile}!")
                    removed = 0
                    new_hand = []
                    for t in p.hand:
                        if t == discarded_tile and removed < 2:
                            removed += 1
                            meld_tiles.append(t) # add hand tiles
                        else:
                            new_hand.append(t)
                    p.hand = new_hand
                    p.melds.append([discarded_tile] * 3)
                    meld_made = True
                    claiming_player_idx = idx
                    return meld_made, claiming_player_idx, meld_type, meld_tiles
                elif choice.strip().lower() == 'n':
                    meld_made = False
                    meld_type = 0
                    return meld_made, claiming_player_idx, meld_type, meld_tiles
                else:
                    print("Invalid input, please choose from y or n.")

    # Chi
    chi_player_idx = (discarder_idx + 1) % 4
    chi_player = players[chi_player_idx]
    if chi_player.is_human:
        chi_options= can_chi(chi_player.hand, discarded_tile)
        if chi_options:
            chosen_option = None
            while True:
                print(f"Your hand: {sort_hand(chi_player.hand)}")
                choice = input(f"{chi_player.name}, do you want to Chi {discarded_tile}? ([Y]/n): ")
                if choice.strip().lower() in ["y", ""]:
                    meld_type = 3 # chi
                    meld_tiles = [discarded_tile]  # add discarded tile to meld tiles
                    while True:
                        print(f"{chi_player.name}, you can Chi {discarded_tile} with:")
                        for idx, opt in enumerate(chi_options):
                            print(f"  {idx}: {opt} + {discarded_tile}")
                        sel = input("Choose option (number) or n to skip: ").strip()
                        if sel.isdigit() and int(sel) in range(len(chi_options)):
                            chosen_option = chi_options[int(sel)]
                            break
                        elif sel.strip().lower() == "n":
                            meld_made = False
                            return meld_made, claiming_player_idx, meld_type, meld_tiles
                        else:
                            print("Invalid input, please choose option (number) or n.")
                    if chosen_option:
                        print(f"{chi_player.name} claims Chi {discarded_tile} with {chosen_option}!")
                        for chi_tile in chosen_option:
                            chi_player.hand.remove(chi_tile)
                            meld_tiles.append(chi_tile) # add hand tile to meld tiles
                        chi_player.melds.append(sort_hand(list(chosen_option) + [discarded_tile]))
                        meld_made = True
                        claiming_player_idx = chi_player_idx
                        return meld_made, claiming_player_idx, meld_type, meld_tiles
                elif choice.strip().lower() == 'n':
                    meld_made = False
                    return meld_made, claiming_player_idx, meld_type, meld_tiles
                else:
                    print("Invalid input, please choose from y or n.")

    # No meld was claimed
    return meld_made, claiming_player_idx, meld_type, meld_tiles

def play_round():
    wall = create_wall()
    shuffle_wall(wall)

    kan_counter = 0 # game ends with 4 kans 四槓散了（スーカンサンラ）


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
        if check_win(p, "tenhou"):
            return

    turn = 0
    while len(live_wall) > 0:
        current_player_idx = turn % 4
        current_player = players[current_player_idx]
        print(f"\nround {turn} {current_player.name} ({current_player.wind})'s turn---")
        current_player.sort_hand()

        if turn != 0:
            drawn_tile = current_player.draw(live_wall)
            if drawn_tile is None:
                print("No more tiles to draw, game ends in draw")
                break
            print(f"{current_player.name} ({current_player.wind}) drew {drawn_tile}")

            # check Tsumo
            if check_win(current_player, "draw"):
                return

        print(f"Melds: {current_player.melds}")
        print(f"Hand: {current_player.hand}")

        discard_index = current_player.decide_discard()
        discarded = current_player.discard(discard_index)
        print(f"{current_player.name} discarded {discarded}")

        # check if other players can Ron (win by discard)
        for other_player in players:
            if other_player != current_player:
                if check_win(other_player, "discard", tile=discarded):
                    return
        # check Chi Pon Kan
        meld_made, meld_player_idx, meld_type, meld_tiles = check_melds(players, current_player_idx, discarded)
        if meld_made:
            # update player melds, draw (for kan), discard, and change order
            meld_player = players[meld_player_idx]
            meld_player.sort_hand()
            if meld_type == 1: # for kan, player needs draw a new tile from dead wall
                kan_counter += 1
                if kan_counter > 3: # 四槓散了（スーカンサンラ）
                    print("四槓散了（スーカンサンラ）")
                    return
                drawn_tile2 = (meld_player.draw(dead_wall.pop())) # draw the last one from the wall
                print(f"{meld_player.name} ({meld_player.wind}) drew {drawn_tile2}")
                # Tsumo check
                if check_win(meld_player, "draw"):
                    return

            # discard the tile after claiming the meld
            print(f"Hand after meld: {meld_player.hand}")
            discard_index = meld_player.decide_discard()
            discarded2 = meld_player.discard(discard_index)
            print(f"{meld_player.name} discarded {discarded2} after meld")

            # Ron check again
            for other_player in players:
                if other_player != meld_player:
                    if check_win(other_player, "discard", tile=discarded2):
                        return

            # continue from the next player to the meld claimer
            turn = meld_player_idx + 1
            continue

        if len(live_wall) == 0:
            print("\nNo more tiles in live wall. The game ends in draw")
            break
        turn += 1


if __name__ == "__main__":
    play_round()


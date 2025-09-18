from wall import *
from player import *
import random
from hand_checker import is_win_hand, is_waiting_hand, discard_to_wait
from melds import can_chi, can_pon, can_kan
from yaku import check_yaku

def colored(tiles):
    return " ".join([t.to_colored_str() for t in tiles])

def ask_win(win_type, player):
    if not player.is_human:
        return True
    else:
        if win_type == "tsumo":
            msg = f"{player.name}, you can Tsumo! Do you want to win? ([Y]/n): "
        elif win_type == "tenhou":
            msg = f"{player.name}, you have Tenhou! Do you want to win? ([Y]/n): "
        else:
            raise ValueError(f"Invalid source type: {win_type}")
        while True:
            choice = input(msg).strip().lower()
            if choice.strip().lower() in ["y", ""]:
                #print(f"{player.name} declared {win_type}!")
                return True
            elif choice.strip().lower() == 'n':
                return False
            else:
                print("Invalid input, please choose from y or n.")

def ask_riichi(player):
    if not player.is_human:
        player.is_riichi = True
        return True
    msg = f"{player.name}, You can riichi, do you want to riichi? ([Y]/n): "
    while True:
        choice = input(msg).strip().lower()
        if choice.strip().lower() in ["y", ""]:
            return True
        elif choice.strip().lower() == 'n':
            return False
        else:
            print("Invalid input, please choose from y or n.")

def player_hand_check(player):
    return_val = "None"
    if not player.is_human:
        return return_val
    full_hand = player.hand[:] + [t for meld in player.melds for t in meld]
    # check Tsumo
    if is_win_hand(full_hand):
        if ask_win("tsumo", player):
            print(f"{player.name} wins by Tsumo!")
            # test
            yaku = check_yaku(player.hand[:-1], player.hand[-1], player, is_tsumo=True)
            yaku_list = []
            han = 0
            for y, h in yaku:
                yaku_list.append(y)
                han += h
            print(f"{yaku}")
            print(f"{han}")
            # !test
            return_val = "tsumo"
            return return_val
    # check waiting hand
    discard_tiles = discard_to_wait(player.hand[:], player.melds)
    if discard_tiles and len(discard_tiles) > 0:
        print("you can discard the following to Tenpai:")
        for tile, waiting in discard_tiles:
            print(f"{tile}: waiting: {waiting}")

    # check riichi
    if not player.is_riichi and discard_tiles and not player.melds:
        is_riichi = ask_riichi(player)
        if is_riichi:
            return_val = "riichi"
    return return_val

def check_responses(players, discarder_idx, discarded_tile):
    """
    Check if any human player wants to declare Ron, Kan, Pon, or Chi.
    Only one player can respond; priority: Ron > Kan > Pon > Chi.
    Returns ('ron'/'kan'/'pon'/'chi'/None, player_idx, details)
    """
    for i in range(1, 4):
        idx = (discarder_idx + i) % 4
        p = players[idx]
        if not p.is_human:
            continue
        options = []
        # Ron
        tmp_hand = (p.hand[:])
        if discarded_tile:
            tmp_hand += [discarded_tile]
        if p.melds:
            for m in p.melds:
                tmp_hand += m
        if is_win_hand(tmp_hand):
            options.append('ron')
        # Kan
        if can_kan(p.hand, discarded_tile):
            options.append('kan')
        # Pon
        if can_pon(p.hand, discarded_tile) and not p.is_riichi:
            options.append('pon')
        # Chi
        chi_options = []
        if i == 1: # only next player can chi
            chi_options = can_chi(p.hand, discarded_tile)
            if chi_options and not p.is_riichi:
                options.append('chi')
        if not options:
            continue
        while True:
            print(f"{p.name}, you can: {', '.join(options)} on {discarded_tile}")
            print(f"your hand: {colored(sort_hand(p.hand))}")
            choice = input("Type [1]ron, [2]kan, [3]pon, [4]chi or 'n' to skip: ").strip().lower()
            if choice == '1' and 'ron' in options:
                print(f"{p.name} declares Ron and wins!")
                return 'ron', idx, None
            elif choice == '2' and 'kan' in options:
                print(f"{p.name} claims Kan with {discarded_tile}!")
                tiles = [discarded_tile]
                removed = 0
                new_hand = []
                for t in p.hand:
                    if t == discarded_tile and removed < 3:
                        tiles.append(t)
                        removed += 1
                    else:
                        new_hand.append(t)
                p.hand = new_hand
                p.melds.append([discarded_tile]*4)
                return 'kan', idx, tiles
            elif choice == '3' and 'pon' in options:
                print(f"{p.name} claims Pon with {discarded_tile}!")
                tiles = [discarded_tile]
                removed = 0
                new_hand = []
                for t in p.hand:
                    if t == discarded_tile and removed < 2:
                        tiles.append(t)
                        removed += 1
                    else:
                        new_hand.append(t)
                p.hand = new_hand
                p.melds.append([discarded_tile]*3)
                return 'pon', idx, tiles
            elif choice == '4' and 'chi' in options:
                print(f"{p.name}, you can Chi {discarded_tile} with:")
                for chi_idx, opt in enumerate(chi_options):
                    print(f" {chi_idx+1}: {opt} + {discarded_tile}")
                sel = input("choose option (number) or 'n' to skip: ").strip().lower()
                if sel.isdigit() and int(sel) in range(1, len(chi_options)+1):
                    chosen = chi_options[int(sel)-1]
                    print(f"{p.name} claims Chi {discarded_tile} with {chosen}!")
                    for chi_tile in chosen:
                        remove_tile_from_hand(p.hand, chi_tile)
                    p.melds.append(sort_hand(list(chosen) + [discarded_tile]))
                    return 'chi', idx, chosen + [discarded_tile]
                elif sel == 'n':
                    continue
            elif choice == 'n':
                break
            print("invalid input, please try again")
    return None, discarder_idx, None

def remove_tile_from_hand(hand, tile):
    """
    Remove one tile from hand, treat red five(0) and normal five(5) as equivalent
    """
    for idx, t in enumerate(hand):
        if t.suit == tile.suit:
            if t.value == tile.value:
                hand.pop(idx)
                return
            # remove aka5 when looking for 5
            if tile.value == 5 and t.value == 0:
                hand.pop(idx)
                return
            # remove 5 when looking for aka5
            if tile.value == 0 and t.value == 5:
                hand.pop(idx)
                return

def play_round():
    wall = create_wall()
    shuffle_wall(wall)
    kan_counter = 0 # game ends with 4 kans 四槓散了（スーカンサンラ）

    # set human player as P1 and rest player are AI
    players = [
        HumanPlayer("P1", "E"),
        #AIPlayer("P1", "E"),
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
        if is_win_hand(p.hand):
            if ask_win("tenhou", p):
                print(f"{p.name} wins by Tenhou!")
                return

    turn = 0
    while len(live_wall) > 0:
        current_player_idx = turn % 4
        current_player = players[current_player_idx]
        print(f"\nround {turn} {current_player.name} ({current_player.wind})'s turn---")
        current_player.sort_hand()

        if turn != 0:

            # draw
            drawn_tile = current_player.draw(live_wall)
            if drawn_tile is None:
                print("No more tiles to draw, game ends in draw")
                break
            print(f"{current_player.name} ({current_player.wind}) drew {drawn_tile}")

            """
            # check Tsumo
            if is_win_hand(current_player.hand + [drawn_tile]):
                if ask_win("tsumo", current_player):
                    print(f"{current_player.name} wins by Tsumo!")
                    # test
                    yaku, han = check_yaku(current_player.hand, drawn_tile, current_player, is_tsumo=True, is_riichi=False)
                    print(f"{yaku}")
                    # !test
                    return
            """

        print(f"Melds: {current_player.melds}")
        print(f"Hand: {colored(current_player.hand)}")

        return_val = player_hand_check(current_player)
        if return_val == "tsumo":
            return
        discard_index = current_player.decide_discard()
        discarded = current_player.discard(discard_index)
        print(f"{current_player.name} discarded {discarded}")

        # check response
        response, responder_idx, response_details = check_responses(players, current_player_idx, discarded)
        if response == 'ron':
            print(f"{players[responder_idx].name} wins by Ron!")
            # test
            yaku = check_yaku(players[responder_idx].hand, discarded, players[responder_idx], False)
            yaku_list = []
            han = 0
            for y, h in yaku:
                yaku_list.append(y)
                han += h
            print(f"{han}")
            print(f"{yaku}")
            # !test
            return
        elif response == 'kan':
            kan_counter += 1
            if kan_counter > 3: # 四槓散了（スーカンサンラ）
                print("四槓散了（スーカンサンラ）")
                return
            kan_player = players[responder_idx]
            drawn_tile2 = kan_player.draw(dead_wall)
            print(f"{kan_player.name} drew {drawn_tile2}")
            # Tsumo check
            if is_win_hand(kan_player.hand + [drawn_tile2]):
                if ask_win("tsumo", kan_player):
                    print(f"{kan_player.name} wins by Tsumo!")
                    return
            # discard the tile after claiming the meld
            print(f"Hand after meld: {colored(kan_player.hand)}")
            discard_index = kan_player.decide_discard()
            discarded2 = kan_player.discard(discard_index)
            print(f"{kan_player.name} discarded {discarded2} after meld")
            # Ron check again
            response2, responder_idx2, _ = check_responses(players, responder_idx, discarded2)
            if response2 == 'ron':
                print(f"{players[responder_idx2].name} wins by Ron!")
                return
            turn = responder_idx + 1
            continue

        elif response in ['pon', 'chi']:
            meld_player = players[responder_idx]
            print(f"Hand after meld: {colored(meld_player.hand)}")
            discard_index = meld_player.decide_discard()
            discarded2 = meld_player.discard(discard_index)
            print(f"{meld_player.name} discarded {discarded2} after meld")

            # Ron check again
            response2, responder_idx2, _ = check_responses(players, responder_idx, discarded2)
            if response2 == 'ron':
                print(f"{players[responder_idx2].name} wins by Ron!")
                return
            turn = responder_idx + 1
            continue

        if len(live_wall) == 0:
            print("\nNo more tiles in live wall. The game ends in draw")
            break

        if return_val == "riichi":
            print(f"{current_player.name}Riichi!")
            current_player.is_riichi = True
        turn += 1


if __name__ == "__main__":
    play_round()


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


def initialize_game():
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
        
    dead_wall = wall[14:]
    live_wall = wall[:-14]
    
    return live_wall, dead_wall, players

def check_self_win_or_riichi(player):
    """
    Check for Tsumo, Tenpai (discard suggestions), and Riichi opportunities.
    Returns: "tsumo", "riichi", or "None"
    """
    return_val = "None"
    if not player.is_human:
        return return_val
        
    full_hand = player.hand[:] + [t for meld in player.melds for t in meld]
    
    # check Tsumo
    if is_win_hand(full_hand):
        if ask_win("tsumo", player):
            print(f"{player.name} wins by Tsumo!")
            # Calculate and display score (WIP)
            yaku = check_yaku(player.hand[:-1], player.hand[-1], player, is_tsumo=True)
            yaku_list = []
            han = 0
            for y, h in yaku:
                yaku_list.append(y)
                han += h
            print(f"Yaku: {yaku_list}")
            print(f"Han: {han}")
            return "tsumo"

    # check waiting hand
    try:
        discard_tiles = discard_to_wait(player.hand[:], player.melds)
    except ValueError as e:
        print(f"Warning: Hand check failed: {e}")
        discard_tiles = []

    if discard_tiles and len(discard_tiles) > 0:
        print("you can discard the following to Tenpai:")
        for tile, waiting in discard_tiles:
            print(f"{tile}: waiting: {waiting}")

    # check riichi
    if not player.is_riichi and discard_tiles and not player.melds:
        is_riichi = ask_riichi(player)
        if is_riichi:
            player.riichi_declared = True # declare riichi in this round
            return "riichi"
            
    return "None"

def process_responses(players, discarder_idx, discarded_tile, dead_wall):
    """
    Check if any player (currently only Human) wants to declare Ron/Kan/Pon/Chi.
    Returns: 
        action_type (str or None): 'ron', 'kan', 'pon', 'chi'
        responder_idx (int): index of the player who responded
        new_discarded (Tile or None): if meld happened, the new tile discarded by responder
    """
    # Uses existing check_responses logic but returns structured data
    # We use the existing function `check_responses` which is actually quite complex
    # handling the input loop and meld execution.
    # To avoid changing too much, we will reuse it but wrap its result.
    
    # `check_responses` signature: (players, discarder_idx, discarded_tile)
    # returns: ('ron'/'kan'/'pon'/'chi'/None, player_idx, details_or_tiles)
    
    # However, existing check_responses ALREADY handles the meld execution (removing tiles, adding meld).
    # It DOES NOT handle the "discard after meld" part for Melds (Pon/Chi), 
    # BUT looking at the original code (lines 120-162), it DOES handle updating the hand.
    # Wait, the original `play_round` code (lines 300+) handled the "discard after meld". 
    # `check_responses` only returns WHO did WHAT.
    # Exception: For Kan, `check_responses` returns 'kan' but doesn't handle the draw/discard cycle fully?
    # Let's check original line 123 for Kan: it claims Kan and returns.
    
    action, idx, details = check_responses(players, discarder_idx, discarded_tile)
    
    if action == 'ron':
        return 'ron', idx, None
        
    elif action == 'kan':
        # Kan requires drawing from dead wall and discarding
        kan_player = players[idx]
        drawn_tile = kan_player.draw(dead_wall)
        print(f"{kan_player.name} drew {drawn_tile} (Rinshan)")
        
        # Check Rinshan Kaihou (Tsumo on Kan)
        if is_win_hand(kan_player.hand + [t for meld in kan_player.melds for t in meld]):
            if ask_win("tsumo", kan_player):
                print(f"{kan_player.name} wins by Tsumo (Rinshan Kaihou)!")
                return 'tsumo', idx, None
        
        # Discard after Kan
        print(f"Hand after meld: {colored(kan_player.hand)}")
        d_idx = kan_player.decide_discard()
        new_discarded = kan_player.discard(d_idx)
        print(f"{kan_player.name} discarded {new_discarded} after meld")
        return 'kan', idx, new_discarded

    elif action in ['pon', 'chi']:
        meld_player = players[idx]
        # Meld is already processed in check_responses (hand updated)
        print(f"Hand after meld: {colored(meld_player.hand)}")
        d_idx = meld_player.decide_discard()
        new_discarded = meld_player.discard(d_idx)
        print(f"{meld_player.name} discarded {new_discarded} after meld")
        return 'meld', idx, new_discarded
        
    return None, -1, None

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
    live_wall, dead_wall, players = initialize_game()
    kan_counter = 0

    for p in players:
        print(f"{p.name} ({p.wind}) hand: {p.hand}")

    turn = 0
    while len(live_wall) > 0:
        current_player_idx = turn % 4
        current_player = players[current_player_idx]
        
        print(f"\nround {turn} {current_player.name} ({current_player.wind})'s turn---")
        current_player.sort_hand()

        # 1. Draw (except first turn)
        drawn_tile = None
        if turn != 0:
            drawn_tile = current_player.draw(live_wall)
            if drawn_tile is None:
                print("No more tiles to draw, game ends in draw")
                break
            print(f"{current_player.name} ({current_player.wind}) drew {drawn_tile}")

        # 2. Self Action Check (Tsumo / Riichi)
        print(f"Melds: {current_player.melds}")
        print(f"Hand: {colored(current_player.hand)}")
        
        status = check_self_win_or_riichi(current_player)
        if status == "tsumo":
            return
        if status == "riichi":
            print(f"{current_player.name} declared Riichi!")
            current_player.is_riichi = True

        # 3. Discard
        discard_index = current_player.decide_discard()
        discarded_tile = current_player.discard(discard_index)
        print(f"{current_player.name} discarded {discarded_tile}")

        # 4. Responses Loop (Handling Ron/Kan/Pon/Chi and subsequent discards recursively-ish)
        # We need a loop here because a Kan/Pon/Chi results in a new discard which might trigger another Ron.
        
        active_discard = discarded_tile
        active_discarder = current_player_idx
        
        while True:
            action, responder_idx, new_discard = process_responses(players, active_discarder, active_discard, dead_wall)
            
            if action == 'ron' or action == 'tsumo':
                # Win detected
                if action == 'ron':
                    print(f"{players[responder_idx].name} wins by Ron!")
                    # Check yaku for winner (WIP logging)
                    winner = players[responder_idx]
                    yaku = check_yaku(winner.hand, active_discard, winner, False)
                    print(f"Yaku: {[y[0] for y in yaku]}, Han: {sum(y[1] for y in yaku)}")
                return
            
            elif action == 'kan':
                kan_counter += 1
                if kan_counter > 3: # 四槓散了
                     print("四槓散了（スーカンサンラ）")
                     return
                # Kan continues the loop with the NEW discarded tile from the Kan player
                active_discard = new_discard
                active_discarder = responder_idx
                turn = responder_idx # Update turn to the kan player so next ++ increments correctly?
                # Actually, after a Kan/Melds, the turn shifts to that player.
                # If we continue the outer loop, `turn += 1` will happen.
                # If responder is P3 (idx 2), we want next main loop to be P4 (idx 3). 
                # So setting turn = 2 is correct, then turn++ => 3.
                continue 

            elif action == 'meld': # Pon or Chi
                # Turn shifts to meld player
                # New discard is active_discard
                # Check if anyone Rons this NEW discard
                active_discard = new_discard
                active_discarder = responder_idx
                turn = responder_idx 
                continue
            
            else:
                # No response, turn ends normally
                break
        
        turn += 1 # Next player

    print("\nNo more tiles in live wall. The game ends in draw")


if __name__ == "__main__":
    play_round()


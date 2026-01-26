from src.core.hand_checker import is_win_hand, try_split_standard_hand
from src.core.scoring import FuCalculator, ScoreTable
from src.core.yaku import check_yaku

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

def handle_win(player, win_tile, win_type, is_rinshan=False):
    """
    Handle winning logic: Calculate Yaku, Fu, Score and Print details.
    """
    print(f"{player.name} wins by {win_type}!")
    
    is_tsumo = (win_type == 'tsumo')
    
    # Calculate Yaku
    if is_tsumo:
        hand_for_yaku = player.hand[:-1]
        win_tile_for_yaku = player.hand[-1]
    else:
        hand_for_yaku = player.hand
        win_tile_for_yaku = win_tile
        
    yaku = check_yaku(hand_for_yaku, win_tile_for_yaku, player, is_tsumo=is_tsumo)
    
    # Add Rinshan Kaihou if applicable
    if is_rinshan:
        yaku.append(('rinshan kaihou', 1))

    yaku_names = [y[0] for y in yaku]
    han = sum(h for y, h in yaku)
    
    # Calculate Fu
    full_hand = player.hand[:] + [t for m in player.melds for t in m]
    if not is_tsumo:
        full_hand += [win_tile]
        
    is_win, type_str = is_win_hand(full_hand)
    
    fu_calc = FuCalculator()
    fu = 0
    
    if type_str == 'chiitoitsu':
        fu = 25
    else:
        _, head, pungs, chows = try_split_standard_hand(full_hand)
        fu = fu_calc.calculate_fu(player.hand, player.melds, win_tile, win_type, player, pungs, chows, head)
        
    # Pinfu Tsumo Exception (20 Fu)
    if 'pinfu' in yaku_names and is_tsumo:
        fu = 20
        
    print(f"Yaku: {yaku_names}")
    print(f"{han} Han, {fu} Fu")
    
    score = ScoreTable.calculate_points(han, fu, player.wind == 'E', is_tsumo)
    print(f"Score: {score}")
    
    return {
        "score": score,
        "han": han,
        "fu": fu,
        "yaku": yaku_names
    }

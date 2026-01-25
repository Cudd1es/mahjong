from hand_checker import is_win_hand, try_split_standard_hand
from scoring import FuCalculator, ScoreTable
from yaku import check_yaku

def handle_win(player, win_tile, win_type, is_rinshan=False):
    """
    Handle winning logic: Calculate Yaku, Fu, Score and Print details.
    """
    print(f"{player.name} wins by {win_type}!")
    
    is_tsumo = (win_type == 'tsumo')
    
    # Calculate Yaku
    # Note: check_yaku requires the hand WITHOUT the winning tile for Tsumo? 
    # check_yaku signature: (hand, tile, player, is_tsumo)
    # The `hand` argument in check_yaku:
    # "hand: list of 14 Tile objects (normalized)" -> docstring says 14?
    # Let's check yaku.py docstring: "hand: list of 14 Tile objects"
    # But lines 6-14 in game_loop.py passed `player.hand[:-1]` and `player.hand[-1]` for Tsumo.
    # Meaning (13 tiles, 1 win_tile).
    # For Ron: passed `winner.hand` (13 tiles) and `active_discard` (1 tile).
    
    # So we prepare the 13-tile hand + win tile.
    if is_tsumo:
        hand_for_yaku = player.hand[:-1]
        win_tile_for_yaku = player.hand[-1]
    else:
        hand_for_yaku = player.hand
        win_tile_for_yaku = win_tile
        
    yaku = check_yaku(hand_for_yaku, win_tile_for_yaku, player, is_tsumo=is_tsumo)
    
    # Add Rinshan Kaihou if applicable
    # Currently check_yaku might not detect Rinshan automatically unless we pass a flag specific to it
    # or if we fake the yaku addition here.
    # Standard Yaku list append
    if is_rinshan:
        # Check if 'rinshan kaihou' is already in yaku (unlikely if not passed)
        # We manually add it.
        # But 'rinshan kaihou' is 1 han.
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
    return score

from src.models.tiles import Tile
import math

class FuCalculator:
    def __init__(self):
        pass

    def calculate_fu(self, hand, melds, win_tile, win_type, player, pungs=None, chows=None, head=None):
        """
        Calculate total Fu.
        args:
            hand: list[Tile], unmelded tiles (including win_tile)
            melds: list[list[Tile]], open melds (Pung/Chow/Kan)
            win_tile: Tile, the tile won on
            win_type: str, 'ron' or 'tsumo'
            player: Player object
            pungs: list, pungs from split (includes Hand-only pungs and Melds)
            chows: list, chows from split
            head: list, pair tiles
        """
        
        # 1. Base Fu
        if win_type == 'chiitoitsu':
            return 25
        
        fu = 20 # Fukutei

        # 2. Winning Type Fu
        is_menzen = len(melds) == 0 # Note: checks OPEN melds only
        # Strict menzen check: if any open meld exists, not menzen.
        # But wait, player.melds includes Ankan (Closed Kan)?
        # Usually Ankan is treated as closed for Yaku, but open for Fu? 
        # No, Ankan is closed.
        # Standard: If player has OPENED hand (Chi/Pon/Min-Kan), Menzen=False.
        # We need to know if melds are open or closed.
        # Current system: melds storage doesn't clearly distinguish Open/Closed except by context?
        # Actually `player.melds` stores all melds. 
        # AI/Game implementation usually treats all `player.melds` as Open Melds (claimed from others) 
        # except Ankan (declared from hand). 
        # In this simple implementation, let's assume all melds in `player.melds` are Open, 
        # UNLESS we specifically track Ankans. 
        # For now, let's assume `player.melds` = Open.
        
        if win_type == 'ron':
            if is_menzen:
                fu += 10 # Menzen-Ron
            else:
                pass # No fu for non-menzen ron
        elif win_type == 'tsumo':
            # Pinfu Tsumo Exception: if Pinfu, Fu=20 (no +2).
            # We need to rely on external explicit check for Pinfu, or detect it here.
            # For Safety: Add 2, if Pinfu detection later overrides it to 20, handled there.
            fu += 2

        # 3. Pung/Kan Fu
        # We need to classify 'pungs' argument into:
        # - Open Pung
        # - Closed Pung
        # - Open Kan
        # - Closed Kan
        
        # This is tricky because `pungs` argument passed from `try_split_standard_hand` 
        # contains BOTH hand-pungs (Closed) and meld-pungs (Open/Kan).
        # We need to separate them.
        
        # Strategy: Iterate `pungs`. If the exact tile set exists in `player.melds`, it's Open/Kan.
        # Otherwise, if it's from `hand`, it's Closed.
        
        # Normalize melds for comparison
        open_melds_normalized = []
        for m in melds:
            open_melds_normalized.append(sorted([str(t) for t in m]))
            
        for group in (pungs or []):
            # Check if this group is a Kan (len 4)
            is_kan = len(group) == 4
            
            # Check uniqueness: Is this group in open_melds?
            # We use string matching for simplicity
            group_strs = sorted([str(t) for t in group])
            
            is_open = False
            # Find and remove from open_melds_normalized to handle duplicate sets
            if group_strs in open_melds_normalized:
                is_open = True
                open_melds_normalized.remove(group_strs)
            
            base = 2
            if is_kan: base = 8
            
            # Check terminal/honor
            tile = group[0]
            is_yao = (tile.value in [1, 9]) or (tile.suit == 'z')
            
            if is_yao: base *= 2
            
            if not is_open: base *= 2 # Closed doubles the value
            
            fu += base

        # 4. Head Fu
        if head:
            tile = head[0]
            # Dragons get 2 fu
            if tile.suit == 'z' and tile.value in ['P', 'F', 'C']:
                fu += 2
            # Seat Wind
            elif tile.suit == 'z' and tile.value == player.wind:
                fu += 2
            # Round Wind (Assume E for East round always for MVP)
            elif tile.suit == 'z' and tile.value == 'E':
                fu += 2
        
        # 5. Wait Fu (Kanchan, Penchan, Tanki)
        # This requires knowing WHICH tile completed the hand and HOW.
        # This is hard to deduce just from the final split.
        # Examples: 
        # Hand: 12m + 3m(win). Side wait (Ryanmen). 0 Fu.
        # Hand: 13m + 2m(win). Closed wait (Kanchan). +2 Fu.
        # Hand: 89m + 7m(win). Side wait. 0 Fu.
        # Hand: 12m + 3m(win) -> Wait was 1-2.
        # Hand: 89m + 7m(win) -> Wait was 8-9. (Penchan) -> Wait: 7m completes 89? No, 89 waits for 7.
        #   Strictly: 89 waits for 7. This is Penchan (Edge). +2 Fu.
        #   12 waits for 3. Penchan. +2 Fu.
        #   23 waits for 1/4. Ryanmen. 0 Fu.
        
        # Heuristic:
        # Check if `win_tile` is part of the `head` -> Tanki (Pair Wait) -> +2
        # Check if `win_tile` is part of a `chow` -> Check wait type.
        
        # Limitation: If win_tile is in multiple sets (e.g. 444 56), we don't know which one completed.
        # Standard rule: High payout takes precedence. 
        # Since Wait Fuj is +2, we assume +2 if ANY interpretation allows it? 
        # Usually we assume standard Pinfu (0 fu) if possible.
        
        wait_fu = 0
        if head and win_tile in head: 
            # Tanki
            wait_fu = 2
        else:
            # Check chows
            for chow in (chows or []):
                if win_tile in chow:
                    # Interpret wait
                    # Sort chow
                    c = sorted(chow, key=lambda x: x.value)
                    # Values
                    vals = [t.value for t in c]
                    idx = -1
                    # Find index of win_tile in this chow
                    # Note: we must match exact object or value. simple value match:
                    for i, v in enumerate(vals):
                        if v == win_tile.value and chow[i].suit == win_tile.suit:
                            idx = i
                            break
                    
                    if idx == 1: # Middle tile -> Kanchan (Closed)
                        wait_fu = 2
                    elif idx == 0 and vals[0] == 7: # 7-8-9, waiting on 7 -> Penchan? No 89 waits 7.
                        # If I have 789, did I have 89 waiting for 7? Yes.
                        # Wait, Penchan is 12->3 or 89->7.
                        wait_fu = 2
                    elif idx == 2 and vals[2] == 3: # 1-2-3, waiting on 3 -> Penchan.
                        wait_fu = 2
                    # Else Ryanmen (0 Fu)
                    
                    # If we found a 0 Fu interpretation (Ryanmen), that is usually preferred for Pinfu?
                    # But Pinfu requires NO Fu. 
                    # If we aren't Pinfu, we technically want Max Fu? 
                    # Actually standard is: take interpretation that gives highest score.
                    # Since Pinfu (1 Han) > 2 Fu usually, we prefer Pinfu.
                    # But if Pinfu is impossible (e.g. other conditions fail), we stick to +2 Fu.
                    
                    if wait_fu == 0: 
                        break # Found a good wait, assume this is used
        
        fu += wait_fu

        # Round up to nearest 10
        if fu == 25: # Chiitoitsu exception
            return 25
            
        return math.ceil(fu / 10) * 10 

class ScoreTable:
    @staticmethod
    def calculate_points(han, fu, is_dealer, is_tsumo):
        if han == 0: return {}
        
        # Check Yakuman
        if han >= 13:
            basic_points = 8000
        else:
            # Basic calculation
            basic_points = fu * (2 ** (2 + han))
            
            # Limits
            if basic_points > 2000: # Mangan limit check logic from raw formula
                # Mangan: 2000 basic -> 8000 dealer / 12000 ron?
                # Actually, limit applies if score exceeds Mangan fixed values
                pass
            
            # Kiriage Mangan etc.
            # Simplified Logic based on Han/Fu standard table:
            if han >= 5: # Mangan+
                if han == 5: basic_points = 2000
                elif 6 <= han <= 7: basic_points = 3000 # Haneman
                elif 8 <= han <= 10: basic_points = 4000 # Baiman
                elif 11 <= han <= 12: basic_points = 6000 # Sanbaiman
            elif basic_points > 2000:
                basic_points = 2000 # Mangan cap

        # Calculate payments
        if is_dealer:
            if is_tsumo:
                # All pay 2 * basic
                pay = math.ceil(basic_points * 2 / 100) * 100
                return {"all": pay}
            else:
                # Ron: payer pays 6 * basic
                pay = math.ceil(basic_points * 6 / 100) * 100
                return {"single": pay}
        else:
            if is_tsumo:
                # Dealer pays 2 * basic, other 1 * basic
                pay_dealer = math.ceil(basic_points * 2 / 100) * 100
                pay_other = math.ceil(basic_points / 100) * 100
                return {"dealer": pay_dealer, "other": pay_other}
            else:
                # Ron: payer pays 4 * basic
                pay = math.ceil(basic_points * 4 / 100) * 100
                return {"single": pay}

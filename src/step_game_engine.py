from src.game_state import GameState
from src.core.hand_checker import is_win_hand, normalize_red, try_split_standard_hand
from src.core.melds import can_chi, can_pon, can_kan, can_ankan, can_kakan
from src.core.game_utils import handle_win, remove_tile_from_hand
from src.core.yaku import check_yaku
from src.core.shanten import ShantenCalculator
from src.core.scoring import FuCalculator, ScoreTable
from src.models.wall import create_wall, shuffle_wall

class StepGameEngine:
    def __init__(self):
        self.state = GameState()
        self.phase = "IDLE" # IDLE, WAIT_DISCARD, WAIT_RESPONSE, GAME_OVER
        self.last_discard = None
        self.last_discard_idx = -1
        self.pending_responses = {} # player_idx -> action_list
        self.turn_result = None # store win info etc

    def start_game(self):
        self.state.initialize()
        # Ensure fresh wall
        self.state.live_wall = create_wall()
        shuffle_wall(self.state.live_wall)
        self.state.dead_wall = [self.state.live_wall.pop() for _ in range(14)]
        for p in self.state.players:
            p.hand = [self.state.live_wall.pop() for _ in range(13)]
            p.melds = []
            p.score = 25000
            p.sort_hand()
            
        self.phase = "DRAW" 
        return self.next_step()

    def check_furiten(self, player):
        """
        Check if player is in Furiten.
        """
        calc = ShantenCalculator(player.hand)
        waiting = calc.waiting_tiles(len(player.melds))
        
        waits_norm = set([str(normalize_red(t)) for t in waiting])
        discards_norm = set([str(normalize_red(t)) for t in player.discards])
        
        intersection = waits_norm.intersection(discards_norm)
        if intersection:
            return True, waiting
        return False, waiting

    def next_step(self):
        """
        Execute next logical step based on phase.
        Return: dict describing current required action or event.
        """
        if self.phase == "DRAW":
            return self._phase_draw()
        elif self.phase == "WAIT_DISCARD":
            return {"type": "input_required", "action": "discard", "player_idx": self.state.current_player_idx}
        elif self.phase == "WAIT_RESPONSE":
            return {"type": "input_required", "action": "response", "candidates": list(self.pending_responses.keys())}
        elif self.phase == "GAME_OVER":
            return {"type": "game_over", "result": self.turn_result}
            
        return {"type": "error", "message": f"Unknown phase {self.phase}"}

    def _phase_draw(self):
        if not self.state.live_wall:
            self.phase = "GAME_OVER"
            self.turn_result = {"type": "draw", "reason": "exhausted_wall"}
            return self.next_step()

        player = self.state.get_current_player()
        tile = self.state.draw_live(player)
        
        # Check Tsumo
        if is_win_hand(player.hand, player.melds):
            yakus = check_yaku(player.hand[:-1], tile, player, is_tsumo=True)
            valid = [y for y, h in yakus if y != 'dora']
            if valid:
                # Tsumo!
                # If AI, take it.
                if not player.name.startswith("Player"): # Heuristic, or use is_human flag
                     res = handle_win(player, tile, 'tsumo')
                     self.phase = "GAME_OVER"
                     self.turn_result = {"type": "tsumo", "winner": self.state.current_player_idx, "tile": str(tile), "result": res}
                     return self.next_step()
                # If Human, we should really offer Tsumo button. 
                # For MVP, let's keep it simple: Human Tsumo is a 'response' or special event?
                # We can set phase to "WAIT_DISCARD" but add a flag "can_tsumo"?
                
        # Move to DISCARD phase
        self.phase = "WAIT_DISCARD"
        
        # AI Auto-Play
        # Assuming Player 0 is Human (set in state init? or name based?)
        # Let's check player.name or index. 
        # In main.py/state, all are Players? 
        # We need to ensure Bot objects are used or `is_human` attr.
        # GameState relies on `Player` class.
        # Let's assume index 0 is Human.
        # Move to DISCARD phase
        self.phase = "WAIT_DISCARD"
        
        # PURE ENGINE: Always return input_required
        # Drivers (CLI/Sim) must decide what to do.
        return {"type": "input_required", "action": "discard", "player_idx": self.state.current_player_idx}

    def action_discard(self, player_idx, tile_idx):
        if self.phase != "WAIT_DISCARD":
             return {"error": "Not discard phase"}
             
        if player_idx != self.state.current_player_idx:
             return {"error": "Not your turn"}
             
        player = self.state.players[player_idx]
        if tile_idx < 0 or tile_idx >= len(player.hand):
             return {"error": "Invalid tile index"}
             
        tile = player.discard(tile_idx)
        player.sort_hand() # Keep hand sorted
        
        self.last_discard = tile
        self.last_discard_idx = player_idx
        
        # Check Responses (Ron/Pon/Chi/Kan)
        self.pending_responses = self._check_responses(player_idx, tile)
        
        if self.pending_responses:
            self.phase = "WAIT_RESPONSE"
            
            # Auto-resolve if everyone (e.g. only Bots) already responded
            if hasattr(self, 'received_responses') and len(self.received_responses) == len(self.pending_responses):
                print("[Engine] All pending players auto-responded. Resolving immediately.")
                return self._resolve_responses()
                
            return {"type": "event", "event": "discard", "player_idx": player_idx, "tile": str(tile), "wait_response": True}
        else:
            # No responses, next turn
            self.state.current_player_idx = (player_idx + 1) % 4
            self.phase = "DRAW"
            return self.next_step()

    def _check_responses(self, discarder_idx, tile):
        self.received_responses = {} # Ensure fresh buffer for new discard
        responses = {} # player_idx -> [allowed_action_strings]
        for i in range(1, 4):
            idx = (discarder_idx + i) % 4
            p = self.state.players[idx]
            
            allowed = []
            
            # Ron Check
            # Check standing hand + discard
            # Note: is_win_hand takes full hand (standing + winning tile)
            tmp_standing = p.hand[:] + [tile]
            if is_win_hand(tmp_standing, p.melds):
                # Yaku Check
                yakus = check_yaku(p.hand, tile, p, is_tsumo=False)
                valid_yakus = [y for y, h in yakus if y != 'dora']
                if valid_yakus:
                    # Check Furiten
                    is_furiten, waits = self.check_furiten(p)
                    if not is_furiten:
                         allowed.append('ron')
                    # else: print(f"DEBUG: {p.name} in Furiten, cannot Ron on {tile}")
            
            if can_pon(p.hand, tile) and not p.is_riichi: allowed.append('pon')
            if can_kan(p.hand, tile) and not p.is_riichi: allowed.append('kan') # Daiminkan
            
            # Chi only from left player (i=1 means next player)
            # Correct logic: "Left" of ME is the Discarder.
            # If I (idx) am the next player (i=1), then Discarder is my Left (Previous).
            # So i=1 is CORRECT for Chi eligibility.
            if i == 1 and not p.is_riichi:
                if can_chi(p.hand, tile): allowed.append('chi')
                
            if allowed:
                responses[idx] = allowed
                # AI Auto-Resolution buffer removed.
                # Engine is pure state machine now.
                pass
                
        if responses:
             print(f"[Engine] Pending Responses: {responses}")
             if hasattr(self, 'received_responses'):
                 print(f"[Engine] Buffered Responses: {self.received_responses.keys()}")
                 
        return responses

    def action_response(self, player_idx, action, extra_data=None):
        """
        Handle response from player (ron, pon, chi, kan, skip).
        extra_data: needed for Chi (which combination)
        """
        if self.phase != "WAIT_RESPONSE": return {"error": "Not response phase"}
        if player_idx not in self.pending_responses: return {"error": "Not eligible to respond"}
        
        # Store response
        if not hasattr(self, 'received_responses'): self.received_responses = {}
        self.received_responses[player_idx] = {"action": action, "extra": extra_data}
        
        # Check if all responded
        if len(self.received_responses) == len(self.pending_responses):
            return self._resolve_responses()
            
        return {"status": "waiting_others"}

    def _resolve_responses(self):
        # Priority: Ron > Kan/Pon > Chi
        # 1. Check Ron
        ronners = [pid for pid, r in self.received_responses.items() if r['action'] == 'ron']
        if ronners:
            # Handle Ron (Multiple Ron allowed? MVP: First one closest to turn?)
            # Standard: Head bump (Atamahane) or Double Ron.
            # MVP: First closest (Head Bump)
            current = self.state.current_player_idx
            # Sort by turn order distance
            ronners.sort(key=lambda x: (x - current) % 4)
            winner_idx = ronners[0]
            
            # Execute Ron
            res = handle_win(self.state.players[winner_idx], self.last_discard, 'ron')
            self.phase = "GAME_OVER"
            self.turn_result = {"type": "ron", "winner": winner_idx, "loser": self.last_discard_idx, "tile": str(self.last_discard), "result": res}
            return self.next_step()
            
        # 2. Check Kan/Pon (Excluding 'skip')
        ponners = [pid for pid, r in self.received_responses.items() if r['action'] in ['pon', 'kan']]
        if ponners:
            # Pon priority over Chi
            winner_idx = ponners[0] # Should only be one valid ponner usually (Wait, can multiple pon? No only 3 copies left)
            resp = self.received_responses[winner_idx]
            
            # Execute Pon/Kan
            self._execute_meld(winner_idx, resp['action'], resp['extra'])
            # After meld, it is winner's turn to discard
            self.state.current_player_idx = winner_idx
            self.phase = "WAIT_DISCARD"
            return {"type": "event", "event": "meld", "player": winner_idx, "action": resp['action']}
            
        # 3. Check Chi
        chiers = [pid for pid, r in self.received_responses.items() if r['action'] == 'chi']
        if chiers:
            winner_idx = chiers[0]
            resp = self.received_responses[winner_idx]
            self._execute_meld(winner_idx, 'chi', resp['extra'])
            self.state.current_player_idx = winner_idx
            self.phase = "WAIT_DISCARD"
            return {"type": "event", "event": "meld", "player": winner_idx, "action": "chi"}
            
        # 4. All skipped
        self.received_responses = {}
        self.pending_responses = {}
        # Next turn
        self.state.current_player_idx = (self.state.current_player_idx + 1) % 4
        self.phase = "DRAW"
        return self.next_step()

    def _execute_meld(self, player_idx, action, extra):
        from src.core.game_utils import remove_tile_from_hand
        from src.core.hand_checker import normalize_red, sort_hand
        p = self.state.players[player_idx]
        tile = self.last_discard
        
        if action == 'pon':
             # Remove 2 matching tiles
             found_tiles = []
             new_hand = []
             removed = 0
             for t in p.hand:
                 if removed < 2 and normalize_red(t) == normalize_red(tile):
                     found_tiles.append(t)
                     removed += 1
                 else:
                     new_hand.append(t)
             p.hand = new_hand
             p.melds.append([tile] + found_tiles)
             
        elif action == 'kan':
             # Daiminkan
             found_tiles = []
             new_hand = []
             removed = 0
             for t in p.hand:
                 if removed < 3 and normalize_red(t) == normalize_red(tile):
                     found_tiles.append(t)
                     removed += 1
                 else:
                     new_hand.append(t)
             p.hand = new_hand
             p.melds.append([tile] + found_tiles)
             # Draw Rinshan? 
             # Logic is complex: Kan -> Rinshan -> Discard.
             # MVP: Simplified Kan (No Rinshan step-by-step yet, just add tile)
             # Ideally draw a tile here immediately?
             rinshan = self.state.draw_dead(p)
             p.hand.append(rinshan)
             
        elif action == 'chi':
             # Valid Chi options
             options = can_chi(p.hand, tile)
             if not options:
                 # Should not happen if pre-checked, but safe parsing
                 return 
                 
             chosen = None
             if extra:
                 # extra should be list of 2 tiles e.g. ['3m', '4m']
                 # Try to match with options
                 # Simplified: Just grab first option for MVP or if no extra
                 pass
             
             # Auto-select first option for MVP (User button sends no extra)
             chosen = options[0]
             
             # Execute
             for t in chosen: remove_tile_from_hand(p.hand, t)
             p.melds.append(sort_hand(list(chosen) + [tile]))

from src.game_engine import GameEngine
from src.models.player import AIPlayer, Player
from src.models.tiles import Tile
from src.core.melds import can_pon, can_chi, can_kan, can_kakan, can_ankan
from src.core.hand_checker import is_win_hand, sort_hand, normalize_red
from src.core.game_utils import colored, handle_win, remove_tile_from_hand
from src.core.yaku import check_yaku
from src.core.shanten import ShantenCalculator
import sys
import os
import random

# Suppress stdout to speed up simulation and reduce noise
class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

class SimulationPlayer(AIPlayer):
    def __init__(self, name, wind):
        super().__init__(name, wind)
        self.can_respond_to_discard = True
        
    def decide_response(self, options, discarded_tile, hand):
        """
        Randomly decide to take an action if available.
        options: list of strings ['ron', 'pon', 'kan', 'chi']
        """
        # 20% chance to claim if available, to avoid constant interruptions?
        # Or higher to stress test. Let's say 50%.
        if not options: return 'n', None
        
        # Priority: Ron > Kan > Pon > Chi
        if 'ron' in options: return '1', 'ron'
        
        if random.random() < 0.5: # 50% chance to skip
            return 'n', None
            
        if 'kan' in options: return '2', 'kan'
        if 'pon' in options: return '3', 'pon'
        if 'chi' in options: return '4', 'chi'
        
        return 'n', None

    def decide_chi_option(self, chi_options):
        # random choice
        return random.randint(1, len(chi_options))

class SimulationGameEngine(GameEngine):
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

    def process_responses(self, discarder_idx, discarded_tile):
        """
        Overridden to allow AI response handling without Input.
        Based strictly on src/game_engine.py logic.
        """
        players = self.state.players
        for i in range(1, 4):
            idx = (discarder_idx + i) % 4
            p = players[idx]
            # ENABLE AI RESPONSE
            # if not p.is_human: continue 
            
            options = []
            
            # Ron Check
            # Check standing hand + discard, keeping melds logic separate
            tmp_standing = p.hand[:] + [discarded_tile]
            if is_win_hand(tmp_standing, p.melds):
                # Calculate Yaku
                yakus = check_yaku(p.hand, discarded_tile, p, is_tsumo=False)
                valid_yakus = [y for y, h in yakus if y != 'dora']
                if valid_yakus:
                    # Check Furiten
                    is_furiten, waits = self.check_furiten(p)
                    if is_furiten:
                        # Log or Debug print?
                        # print(f"Bot {p.name} Furiten. Cannot Ron.")
                        pass
                    else:
                        options.append('ron')
            
            if can_kan(p.hand, discarded_tile): options.append('kan')
            if can_pon(p.hand, discarded_tile) and not p.is_riichi: options.append('pon')
            
            chi_options = []
            if i == 1: # Next player
                chi_options = can_chi(p.hand, discarded_tile)
                if chi_options and not p.is_riichi: options.append('chi')
                
            if not options: continue
            
            # AI Decision
            # We assume p is SimulationPlayer
            if isinstance(p, SimulationPlayer):
                choice_code, choice_str = p.decide_response(options, discarded_tile, p.hand)
            else:
                choice_str = 'n'
                
            if choice_str == 'ron':
                handle_win(p, discarded_tile, 'ron')
                return 'ron', idx, None
                
            elif choice_str == 'kan':
                # Execute Kan (Daiminkan)
                # Copied from game_engine.py logic (fixed version)
                from src.core.hand_checker import normalize_red
                
                found_tiles = []
                final_hand = []
                removed = 0
                
                for t in p.hand:
                     if removed < 3 and normalize_red(t) == normalize_red(discarded_tile):
                         found_tiles.append(t)
                         removed += 1
                     else:
                         final_hand.append(t)
                         
                p.hand = final_hand
                p.melds.append([discarded_tile] + found_tiles) # 4 tiles
                
                rinshan = self.state.draw_dead(p)
                status, _ = self.check_self_actions(p)
                if status == 'tsumo':
                    return 'tsumo', idx, None
                    
                d_idx = p.decide_discard()
                new_discard = p.discard(d_idx)
                return 'kan', idx, new_discard
                
            elif choice_str == 'pon':
                 # Execute Pon
                 from src.core.hand_checker import normalize_red
                 found_tiles = []
                 final_hand = []
                 removed_count = 0
                 
                 for t in p.hand:
                     if removed_count < 2 and normalize_red(t) == normalize_red(discarded_tile):
                         found_tiles.append(t)
                         removed_count += 1
                     else:
                         final_hand.append(t)
                         
                 p.hand = final_hand
                 p.melds.append([discarded_tile] + found_tiles)
                 
                 d_idx = p.decide_discard()
                 new_discard = p.discard(d_idx)
                 return 'meld', idx, new_discard
                 
            elif choice_str == 'chi':
                # Handle Chi
                # Need to pick option
                sel_idx = p.decide_chi_option(chi_options) - 1 # 0-indexed
                chosen = chi_options[sel_idx]
                
                for t in chosen: remove_tile_from_hand(p.hand, t)
                # Sort meld: discarded + chosen
                # sort_hand returns a list
                p.melds.append(sort_hand(list(chosen) + [discarded_tile]))
                
                d_idx = p.decide_discard()
                new_discard = p.discard(d_idx)
                return 'meld', idx, new_discard
                
        return None, -1, None

    def check_self_actions(self, player):
        # Override to avoid Input for Tsumo/Riichi/Kan
        # For AI, always auto-win (Tsumo)
        # Always auto-kan/ankan if safe?
        # Random Riichi?
        
        if is_win_hand(player.hand, player.melds):
            # Enforce Yaku Ari in Simulation too
            tsumo_tile = player.hand[-1]
            hand_13 = player.hand[:-1]
            yakus = check_yaku(hand_13, tsumo_tile, player, is_tsumo=True)
            valid_yakus = [y for y, h in yakus if y != 'dora']
            if valid_yakus:
                handle_win(player, player.hand[-1], 'tsumo')
                return "tsumo", None
            # Else ignored (Chicken Hand)
            
        # Kan Check
        if len(self.state.dead_wall) > 0:
            ankan_opts = can_ankan(player.hand)
            valid_kakans = []
            for t in player.hand:
                if can_kakan(player.hand, player.melds, t):
                     valid_kakans.append(t)
            
            if ankan_opts or valid_kakans:
                # 50% chance to Kan
                if random.random() < 0.5:
                    if ankan_opts:
                        tiles = ankan_opts[0] # Just pick first
                        for t in tiles: remove_tile_from_hand(player.hand, t)
                        player.melds.append(tiles)
                        rinshan = self.state.draw_dead(player)
                        return self.check_self_actions(player) # Recursion check
                    elif valid_kakans:
                        t = valid_kakans[0]
                        kakan_opts = can_kakan(player.hand, player.melds, t)
                        m = kakan_opts[0]
                        remove_tile_from_hand(player.hand, t)
                        player.melds.remove(m)
                        player.melds.append(m + [t])
                        rinshan = self.state.draw_dead(player)
                        return self.check_self_actions(player)
        
        # Riichi Check
        # AI Logic: if tenpai and !riichi -> Riichi?
        # random choice
        from src.core.hand_checker import discard_to_wait
        try:
            discard_tiles = discard_to_wait(player.hand[:], player.melds)
            if discard_tiles and not player.is_riichi and not player.melds:
                 if random.random() < 0.3: # 30% Riichi
                     return "riichi", [dt[0] for dt in discard_tiles]
        except:
            pass
            
        return "None", None


def log_game_result(game_idx, ended_by, state, winner_idx=None, winning_tile=None, loser_idx=None):
    with open("simulation_log.txt", "a") as f:
        f.write(f"=== Game {game_idx+1} Result: {ended_by} ===\n")
        if winner_idx is not None:
            w_name = state.players[winner_idx].name
            if ended_by == 'ron':
                loser_name = state.players[loser_idx].name if loser_idx is not None else "Unknown"
                f.write(f"Winner: {w_name} (Ron on {winning_tile} from {loser_name})\n")
            else:
                f.write(f"Winner: {w_name} (Tsumo {winning_tile})\n")
        
        for idx, p in enumerate(state.players):
            hand_str = " ".join([str(t) for t in p.hand])
            if idx == winner_idx and ended_by == 'ron' and winning_tile:
                 # Add the winning tile to the display for clarity
                 hand_str += f" + {winning_tile}"
            
            melds_str = str(p.melds)
            f.write(f"{p.name}: Hand=[{hand_str}], Melds={melds_str}\n")
        f.write("\n")

def run_simulation(num_games=100):
    errors = []
    stats = {'pon': 0, 'chi': 0, 'kan': 0, 'ron': 0, 'tsumo': 0, 'draw': 0}
    
    # Clear log file
    with open("simulation_log.txt", "w") as f:
        f.write("Simulation Started\n\n")

    print(f"Starting simulation of {num_games} games...")
    
    for game_idx in range(num_games):
        if (game_idx + 1) % 10 == 0:
            print(f"Simulating game {game_idx + 1}/{num_games}... Stats: {stats}")
            
        engine = SimulationGameEngine()
        engine.state.initialize()
        # Override with SimulationPlayers
        engine.state.players = [
            SimulationPlayer(f'Bot{i+1}', w) 
            for i, w in enumerate(['E', 'S', 'W', 'N'])
        ]
        
        # Redeal
        from src.models.wall import create_wall, shuffle_wall
        engine.state.live_wall = create_wall()
        shuffle_wall(engine.state.live_wall)
        
        engine.state.dead_wall = [engine.state.live_wall.pop() for _ in range(14)]
        for p in engine.state.players:
            p.hand = [engine.state.live_wall.pop() for _ in range(13)]
            p.melds = []
            p.score = 25000
            
        try:
            with SuppressOutput():
                state = engine.state
                game_ended_by = 'draw'
                winner_idx = None
                winning_tile = None
                loser_idx = None
                
                while len(state.live_wall) > 0:
                    current_player = state.get_current_player()
                    current_player.sort_hand()
                    
                    check_invariants(state)
                    
                    # 1. Draw
                    if state.round_count != 0:
                        drawn = state.draw_live(current_player)
                        if not drawn: break
                    
                    # 2. Self Actions
                    status, data = engine.check_self_actions(current_player)
                    if status == "tsumo": 
                        stats['tsumo'] += 1
                        game_ended_by = 'tsumo'
                        winner_idx = state.current_player_idx
                        winning_tile = current_player.hand[-1]
                        break
                    
                    pending_riichi = False
                    if status == "riichi":
                        pending_riichi = True
                        valid_riichi_discards = data
                        current_player.is_riichi = True # Auto confirm logic for sim
                        # Filter hand for discard?
                        # For simplicity, AI just discards.
                        # Ideally we verify the discard is valid.
                        
                    # 3. Discard
                    d_idx = current_player.decide_discard()
                    # Ensure discard is valid for Riichi if just declared
                    if pending_riichi:
                        candidate = current_player.hand[d_idx]
                        if not any(normalize_red(candidate) == normalize_red(v) for v in valid_riichi_discards):
                            # Force pick valid
                            for i, c in enumerate(current_player.hand):
                                if any(normalize_red(c) == normalize_red(v) for v in valid_riichi_discards):
                                    d_idx = i; break
                                    
                    discarded = current_player.discard(d_idx)
                    
                    # 4. Responses
                    active_discard = discarded
                    active_idx = state.current_player_idx
                    
                    # Simulation loop doesn't restart cleanly for responses unless we loop here
                    # But process_responses in SimEngine handles the 'meld' response by returning 'meld'.
                    # We need to LOOP `process_responses` in case of chain (Kan -> Rinshan -> Discard -> Ron?).
                    # Wait, our `process_responses` implementation:
                    # If `meld`, it does `decide_discard`. So it returns `new_discard`.
                    # We should loop until response is None.
                    
                    while True:
                         action, responder_idx, new_discard = engine.process_responses(active_idx, active_discard)
                         if action == 'ron':
                             stats['ron'] += 1
                             game_ended_by = 'ron'
                             winner_idx = responder_idx
                             winning_tile = active_discard
                             loser_idx = active_idx
                             break # Game End
                         elif action == 'tsumo':
                             stats['tsumo'] += 1
                             game_ended_by = 'tsumo'
                             winner_idx = responder_idx
                             break
                         elif action == 'kan':
                             stats['kan'] += 1
                             state.kan_counter += 1
                             if state.kan_counter > 3: 
                                game_ended_by = 'draw'
                                break # 4 kans
                             active_discard = new_discard
                             active_idx = responder_idx
                             state.current_player_idx = responder_idx
                             continue
                         elif action == 'meld':
                             # Identify type (pon/chi are both 'meld' return code, but decide_response knows)
                             # We can infer from hand diff or just count generic melds for now to be safe.
                             # But let's upgrade process_responses to return type?
                             # Or just inspecting melds?
                             # Let's count generic 'meld' (Chi/Pon)
                             # Or better, check the last meld of the responder?
                             responder = state.players[responder_idx]
                             last_meld = responder.melds[-1]
                             if len(last_meld) == 4: stats['kan'] += 1 # Daiminkan
                             elif len(last_meld) == 3:
                                 # Chi or Pon
                                 if last_meld[0] == last_meld[1]: stats['pon'] += 1
                                 else: stats['chi'] += 1
                                 
                             active_discard = new_discard
                             active_idx = responder_idx
                             state.current_player_idx = responder_idx
                             continue
                         else:
                             break
                             
                    # Determine if game ended
                    # If action was ron/tsumo, break outer loop
                    if action in ['ron', 'tsumo']: break
                    if state.kan_counter > 3: break
                    
                    state.current_player_idx = (state.current_player_idx + 1) % 4
                    state.round_count += 1
                
                if game_ended_by == 'draw':
                    stats['draw'] += 1
                    
                log_game_result(game_idx, game_ended_by, state, winner_idx, winning_tile, loser_idx)
                    
        except Exception as e:
            msg = f"Game {game_idx} CRASH: {e}"
            print(msg)
            errors.append(msg)
            # import traceback; traceback.print_exc()
            break
            
    if not errors:
        print("Simulation passed with no crashes.")
        print(f"Final Stats: {stats}")
    else:
        print(f"Found {len(errors)} errors.")

def check_invariants(state):
    for idx, p in enumerate(state.players):
        # Counts
        total = len(p.hand) + len(p.melds)*3
        # Adjust for Kan (4 tiles but counts as 3)
        # Each Kan in melds adds 4 to length, but we want it to count as 3.
        # But `len(p.melds)*3` assumes 3 per meld.
        # If Kan, len(m)==4.
        # So we don't need to adjust `len(p.melds)*3` if we assume 3.
        # But we do need to verify hand+melds consistency.
        # Base is 13.
        # If turn, 14.
        
        # Just check upper bound to catch explosion
        if total > 18: # Generous bound
             raise ValueError(f"Player {p.name} hand explosion! {total} tiles.")

if __name__ == "__main__":
    run_simulation(100)

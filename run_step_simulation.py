from src.game_engine import GameEngine
from src.models.player import AIPlayer, Player
from src.models.tiles import Tile
from src.core.melds import can_pon, can_chi, can_kan, can_kakan, can_ankan
from src.core.hand_checker import is_win_hand, sort_hand, normalize_red, try_split_standard_hand
from src.core.game_utils import colored, handle_win, remove_tile_from_hand
from src.core.yaku import check_yaku
from src.core.shanten import ShantenCalculator
from src.core.scoring import FuCalculator, ScoreTable
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

# SimulationGameEngine removed


def log_game_result(game_idx, ended_by, state, winner_idx=None, winning_tile=None, loser_idx=None, points=None):
    with open("step_simulation_log.txt", "a") as f:
        f.write(f"=== Game {game_idx} Result: {ended_by} ===\n")
        if winner_idx is not None:
            w_name = state.players[winner_idx].name
            score_str = f" Points: {points}" if points else ""
            if isinstance(points, dict):
                 # New format compatibility
                 score_str = f" Score: {points.get('score')} ({points.get('han')} Han, {points.get('fu')} Fu)"
                 
            if ended_by == 'ron':
                loser_name = state.players[loser_idx].name if loser_idx is not None else "Unknown"
                f.write(f"Winner: {w_name} (Ron on {winning_tile} from {loser_name}){score_str}\n")
            else:
                f.write(f"Winner: {w_name} (Tsumo {winning_tile}){score_str}\n")
        
        for idx, p in enumerate(state.players):
            hand_str = " ".join([str(t) for t in p.hand])
            if idx == winner_idx and ended_by == 'ron' and winning_tile:
                 # Add the winning tile to the display for clarity
                 hand_str += f" + {winning_tile}"
            
            melds_str = str(p.melds)
            f.write(f"{p.name}: Hand=[{hand_str}], Melds={melds_str}\n")
        f.write("\n")

def run_single_game(game_idx, state_players, state_log=False, stats=None):
    from src.step_game_engine import StepGameEngine
    
    engine = StepGameEngine()
    engine.start_game()
    
    # ... (SimPlayers setup omitted for brevity in diff, but preserved in file) ...
    # Wait, I cannot omit lines in replace_file_content if I want to keep them.
    # I should target the function definition line and the event handling block separately if they are far apart.
    # But start_game to event loop is long.
    # Let me do this in two chunks.
    
    # Chunk 1: Function signature
    
    # We need to inject our SimulationPlayers into the engine state
    # But StepGameEngine inits its own state and players.
    # We must replace them or init engine with them.
    # StepGameEngine doesn't accept players in init or start_game.
    # We have to hackily replace them AFTER start_game (which deals tiles).
    # Wait, start_game calls state.initialize() which creates new players and deals.
    # If we replace players, we lose the hands?
    # NO. We should copy hands/winds to our SimPlayers OR inject SimPlayers into State.initialize.
    # Better: Inspect engine.state.players and UPGRADE them to SimulationPlayer or wrapper?
    # Or just let SimulationPlayer be a separate logic controller that WE use
    # to decide actions for the corresponding index.
    
    # Let's use the Controller approach. 
    # The `engine.state.players` are standard `Player` objects (or whatever GameState makes).
    # We use `sim_players` list to hold our AI logic instances.
    
    sim_players = [
        SimulationPlayer(f'Bot{i}', w) 
        for i, w in enumerate(['E', 'S', 'W', 'N'])
    ]
    
    # Sync winds/names just in case
    for i, p in enumerate(engine.state.players):
        p.name = sim_players[i].name # Sync Name
        sim_players[i].hand = p.hand # Share reference or copy? 
        # Actually AI decision needs to see the hand.
        # If we pass `p.hand` to decide_*, it's fine.
        pass
        
    step = engine.next_step() # Initial step
    
    game_ended_by = 'draw'
    winner_idx = None
    winning_tile = None
    loser_idx = None
    points = None
    
    steps = 0
    max_steps = 3000
    
    while steps < max_steps:
        steps += 1
        stype = step['type']
        
        if steps % 100 == 0:
             # print(f"Step {steps}: Wall {len(engine.state.live_wall)}, Phase {engine.phase}", file=sys.stderr)
             pass
        
        if stype == "game_over":
            res = step['result']
            rtype = res['type']
            game_ended_by = rtype
            
            if rtype in ['ron', 'tsumo']:
                winner_idx = res['winner']
                winning_tile = res.get('tile')
                loser_idx = res.get('loser') # Extract loser index
                if 'result' in res:
                    points = res['result']
            
            # Log result
            log_game_result(game_idx, game_ended_by, engine.state, winner_idx, winning_tile, loser_idx, points)
            return rtype
            
        elif stype == "input_required":
            act = step['action']
            pid = step.get('player_idx')
            
            if act == 'discard':
                # Ask SimPlayer to decide
                # We need to give it the hand (from engine state, current truth)
                current_p = engine.state.players[pid]
                sim_p = sim_players[pid]
                
                # SimPlayer needs hand to decide.
                # decide_discard() usually looks at self.hand.
                # So we must sync hand.
                sim_p.hand = current_p.hand
                sim_p.melds = current_p.melds
                
                d_idx = sim_p.decide_discard()
                step = engine.action_discard(pid, d_idx)
                
            elif act == 'response':
                candidates = step['candidates']
                # Loop through candidates
                # NOTE: StepGameEngine waits for all, or until one resolves it?
                # We should iterate.
                
                # Copy candidates as we might modify or break
                current_cands = list(candidates)
                
                # We need to pass valid options to SimPlayer.
                # StepGameEngine stores them in `pending_responses`.
                
                for c_pid in current_cands:
                    allowed = engine.pending_responses[c_pid]
                    sim_p = sim_players[c_pid]
                    current_p = engine.state.players[c_pid]
                    
                    # Sync
                    sim_p.hand = current_p.hand
                    sim_p.melds = current_p.melds
                    
                    # Retrieve discard info?
                    # decide_response(options, discarded_tile, hand)
                    # We need discarded_tile. StepGameEngine has `last_discard`.
                    discarded_tile = engine.last_discard
                    
                    # SimPlayer expects options as list of strings
                    # allowed is list of strings
                    
                    # DECIDE
                    code, choice_str = sim_p.decide_response(allowed, discarded_tile, current_p.hand)
                    
                    # Convert choice to engine API
                    # Engine: action_response(pid, action, extra)
                    # choice_str is 'ron', 'pon', 'kan', 'chi', 'n'
                    
                    action = 'skip'
                    if choice_str in ['ron', 'pon', 'kan', 'chi']:
                        action = choice_str
                    
                    extra = None
                    # If chi, we might need extra?
                    # SimPlayer decide_response doesn't return which chi option.
                    # It just says 'chi'.
                    # StepEngine needs to know WHICH chi if multiple.
                    # For MVP SimPlayer just picks random Chi?
                    # The `decide_response` in SimPlayer (inherited or here?)
                    # calls `decide_chi_option`.
                    # But here we only got `choice_str`.
                    
                    if action == 'chi':
                        # We need to pick one.
                        # `can_chi` logic is inside engine `check_responses`, not exposed easily?
                        # Wait, engine only told us 'chi' is allowed.
                        # We don't know the sets.
                        # We can re-calc `can_chi` here or assume engine picks first if extra=None?
                        # StepGameEngine code: 
                        #  `options = can_chi(...)`
                        #  `if not extra: chosen = options[0]` (MVP auto-select first)
                        # So passing None is safe for now.
                        pass
                        
                    res = engine.action_response(c_pid, action, extra)
                    
                    # Check result
                    if res.get('status') != 'waiting_others':
                        # Resolution!
                        step = res
                        # Break candidate loop?
                        # Yes, phase changed.
                        # If Ron happened, step is GAME_OVER or next step.
                        # If Kan happened, step is next step.
                        break
                    
                # If we finished loop and still waiting?
                # Should not happen if we covered all candidates 
                # AND engine auto-resolves when all responded.
                # (We verified this logic in previous turns).
                # But just in case, if we didn't break (all skipped?), 
                # the last action_response should return the Next Step (Draw).
                if res.get('status') == 'waiting_others':
                     # This implies we missed someone or didn't finish?
                     # Candidates len(engine.received) == len(pending) triggers resolve.
                     # So last one MUST return non-waiting.
                     pass
        
        elif stype == "event":
            # events like 'draw', 'meld', 'discard' (info only)
            if step.get('event') == 'meld':
                action = step.get('action') # 'pon', 'chi', 'kan'
                if stats is not None and action in stats:
                    stats[action] += 1
            
            # We must proceed.
            step = engine.next_step()
            
        elif stype == "error":
            print(f"Engine Error: {step['message']}")
            break
            
    # Timeout reached
    log_game_result(game_idx, 'timeout', engine.state, None, None, None, None)
    return 'draw'

def run_simulation(num_games=100):
    stats = {'pon': 0, 'chi': 0, 'kan': 0, 'ron': 0, 'tsumo': 0, 'draw': 0}
    
    # Clear log file
    with open("step_simulation_log.txt", "w") as f:
        f.write("Simulation Started\n\n")

    print(f"Starting simulation of {num_games} games...")
    
    for i in range(num_games):
        if (i + 1) % 10 == 0:
            print(f"Simulating game {i + 1}/{num_games}... Stats: {stats}")
            
        try:
             with SuppressOutput():
                 res_type = run_single_game(i+1, None, stats=stats) # SimulationPlayers created inside
                 if res_type in stats:
                     stats[res_type] += 1
                 else:
                     # Maybe meld variations or something?
                     pass
        except Exception as e:
            print(f"Game {i+1} Crash: {e}")
            import traceback
            traceback.print_exc()
            
    print(f"Final Stats: {stats}")

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
    n = 100
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except:
            pass
    run_simulation(n)

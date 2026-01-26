
import sys
import time
import random
from src.step_game_engine import StepGameEngine
from src.models.player import AIPlayer
from src.core.game_utils import colored
from src.core.hand_checker import sort_hand

class SimulationPlayer(AIPlayer):
    def __init__(self, name, wind):
        super().__init__(name, wind)
        self.can_respond_to_discard = True
        
    def decide_response(self, options, discarded_tile, hand):
        # Priority: Ron > Kan > Pon > Chi
        if not options: return 'n', None
        if 'ron' in options: return '1', 'ron'
        
        if random.random() < 0.5: # 50% chance to skip
            return 'n', None
            
        if 'kan' in options: return '2', 'kan'
        if 'pon' in options: return '3', 'pon'
        if 'chi' in options: return '4', 'chi'
        
        return 'n', None

    def decide_chi_option(self, chi_options):
        return random.randint(1, len(chi_options))

def print_hand_status(player, is_my_turn=False):
    print(f"Melds: {player.melds}")
    if is_my_turn:
        # Show indices for user
        hand_str = ""
        sorted_hand = sorted(player.hand, key=lambda t: (t.suit, t.value))
        for i, t in enumerate(sorted_hand):
            hand_str += f"({i}){t} "
        print(f"your hand: {hand_str}") # Using Colored implicitly via __str__? No, wait.
        # The original game_engine used: print(f"Hand: {colored(current_player.hand)}")
        # And input prompt used: print(f"your hand: {colored_with_indices...}") ??
        # Let's verify game_engine.py logic for input prompt.
        # It printed: "your hand: (0)2m (1)2m ..."
        # I'll replicate that style manually or check if `colored` handles indices.
        # `src/core/game_utils.py` colored just joins to_colored_str.
        # So I need to build the string with indices myself but use colored str for tiles.
    else:
        print(f"Hand: {colored(player.hand)}")

def print_hand_with_indices(player):
    # Do not sort! Engine hand structure is [sorted_tiles, drawn_tile]
    # We must match that structure for indices to be correct.
    res = ""
    for i, t in enumerate(player.hand):
        res += f"({i}){t.to_colored_str()} "
    print(f"your hand: {res}")

def get_user_discard(player):
    # Round info printed by event loop
    print_hand_with_indices(player)
    while True:
        try:
            choice = input("choose a tile index to discard: ")
            idx = int(choice)
            if 0 <= idx < len(player.hand):
                return idx
            else:
                print("please enter a valid tile index")
        except ValueError:
            print("please enter a valid tile index")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)

def get_user_response(player, options, tile):
    print(f"{player.name}, you can: {', '.join(options)} on {tile}")
    # Also do not sort here to keep visual consistency, although indices aren't used for Melds.
    # But usually Melds happen on OP turn, so 'hand' is just your standing hand.
    # Sorted is probably nicer for reading, but consistency is key.
    # Let's keep it sorted for readability since we don't select index? 
    # NO, if we sort here, user might get confused about their hand structure.
    # Let's match print_hand_with_indices style but without indices.
    print(f"your hand: {colored(player.hand)}") 
    
    while True:
        try:
            choice = input("Type [1]ron, [2]kan, [3]pon, [4]chi or 'n' to skip: ").strip().lower()
            if choice == 'n': return 'skip', None
            
            if choice == '1' and 'ron' in options: return 'ron', None
            if choice == '2' and 'kan' in options: return 'kan', None
            if choice == '3' and 'pon' in options: return 'pon', None
            if choice == '4' and 'chi' in options:
                # Need Chi logic
                # For MVP CLI, just pick first or return 'chi'
                return 'chi', None
                
            print("Invalid choice.")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)

def play_cli():
    # Setup
    engine = StepGameEngine()
    engine.start_game()
    
    # Setup players (0 is Human P1)
    sim_players = [
        None, 
        SimulationPlayer("P2", "S"),
        SimulationPlayer("P3", "W"),
        SimulationPlayer("P4", "N")
    ]
    
    # Sync names and winds to match GameEngine default
    # GameEngine uses P1(E), P2(S), P3(W), P4(N)
    engine.state.players[0].name = "P1"
    engine.state.players[0].wind = "E"
    
    for i in range(1, 4):
        engine.state.players[i].name = sim_players[i].name
        engine.state.players[i].wind = sim_players[i].wind
        
    # Initial print
    for p in engine.state.players:
        print(f"{p.name} ({p.wind}) hand: {p.hand}") # Uses __repr__ list format
        
    step = engine.next_step()
    
    while True:
        stype = step['type']
        
        if stype == "game_over":
            print("\n=== GAME OVER ===")
            if step['result']:
                print(f"Result: {step['result']}")
            else:
                 print("Game Ended.")
            break
            
        elif stype == "event":
            evt = step.get('event')
            p_idx = step.get('player_idx')
            if p_idx is None and 'player' in step: p_idx = step['player']
            
            p_obj = engine.state.players[p_idx] if p_idx is not None else None
            p_name = p_obj.name if p_obj else "Unknown"
            
            if evt == 'draw':
                # GameEngine: "round X P1 (E)'s turn---" then "P1 (E) drew 8s"
                # StepEngine sends draw event. We can print round info here if it's the start of turn (draw).
                
                # Check if we should print round header
                # We can track last round count?
                print(f"\nround {engine.state.round_count} {p_name} ({p_obj.wind})'s turn---")
                print(f"{p_name} ({p_obj.wind}) drew {step['tile']}")
                print(f"Melds: {p_obj.melds}")
                # print(f"Hand: {colored(p_obj.hand)}") # Only print hand for others? 
                # GameEngine prints hand for current player always.
                # But for Human, we print it in get_tile.
                if p_idx != 0:
                     print(f"Hand: {colored(p_obj.hand)}")
                else:
                     # For human, we will print in input phase usually.
                     # But consistency...
                     print(f"Hand: {colored(p_obj.hand)}")

            elif evt == 'discard':
                print(f"{p_name} discarded {step['tile']}")
                
            elif evt == 'meld':
                # "P1 calls pon"
                # GameEngine: "P1 claims Pon!" or "P1 Chi!"
                # We can map action
                action = step.get('action')
                if action == 'chi': 
                    print(f"{p_name} Chi!")
                elif action == 'pon':
                    print(f"{p_name} claims Pon!")
                elif action == 'kan':
                    print(f"{p_name} declares Kan!")
                else:
                    print(f"{p_name} called {action}")
                
            step = engine.next_step()
            
        elif stype == "input_required":
            act = step['action']
            pid = step.get('player_idx')
            
            p_obj = None
            if pid is not None:
                p_obj = engine.state.players[pid]
            
            if pid == 0:
                # HUMAN
                if act == 'discard':
                    # get_user_discard prints prompt
                    d_idx = get_user_discard(p_obj)
                    step = engine.action_discard(pid, d_idx)
                elif act == 'response':
                     # Handled below in common response block
                     pass
                     
            
            if act == 'response':
                candidates = step['candidates']
                pending = engine.pending_responses
                new_step = None
                
                for c_pid in candidates:
                    opts = pending[c_pid]
                    
                    if c_pid == 0:
                        # Human
                        # "P1, you can: pon, chi on 8m"
                        action, extra = get_user_response(engine.state.players[0], opts, engine.last_discard)
                        res = engine.action_response(c_pid, action, extra)
                    else:
                        # Bot
                        sim_p = sim_players[c_pid]
                        current_b = engine.state.players[c_pid]
                        sim_p.hand = current_b.hand
                        sim_p.melds = current_b.melds
                        
                        code, choice = sim_p.decide_response(opts, engine.last_discard, sim_p.hand)
                        action = choice if choice in ['ron', 'pon', 'kan', 'chi'] else 'skip'
                        res = engine.action_response(c_pid, action, None)
                        
                        if action != 'skip':
                             # Simulate bot delay/thought if it did something?
                             pass
                        
                    if res.get('status') != 'waiting_others':
                        new_step = res
                        break
                        
                if new_step:
                    step = new_step
                else:
                    pass

            elif pid != 0 and act == 'discard':
                # Bot Discard
                sim_p = sim_players[pid]
                sim_p.hand = p_obj.hand
                sim_p.melds = p_obj.melds
                d_idx = sim_p.decide_discard()
                step = engine.action_discard(pid, d_idx)
                # print(f"{sim_players[pid].name} thinks...") # Removed to match GameEngine clean output
                time.sleep(0.1) # Small delay

        elif stype == "error":
            print(f"Error: {step['message']}")
            break

if __name__ == "__main__":
    play_cli()

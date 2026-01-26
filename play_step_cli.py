
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

import argparse

def play_cli():
    parser = argparse.ArgumentParser(description="Step Mahjong CLI")
    parser.add_argument("--humans", type=int, default=1, help="Number of human players (0-4)")
    args = parser.parse_args()
    num_humans = args.humans

    print(f"Starting Mahjong Step CLI with {num_humans} Human(s)...")
    engine = StepGameEngine()
    engine.start_game()
    
    # Setup players
    # indices < num_humans -> None (Human)
    # indices >= num_humans -> Bot
    sim_players = []
    
    for i in range(4):
        if i < num_humans:
            sim_players.append(None) # Human placeholder
            engine.state.players[i].name = f"You(P{i})"
            engine.state.players[i].wind = ['E','S','W','N'][i]
        else:
            bot = SimulationPlayer(f"Bot{i}", ['E','S','W','N'][i])
            sim_players.append(bot)
            engine.state.players[i].name = bot.name
            engine.state.players[i].wind = bot.wind
        
    # Initial print
    for p in engine.state.players:
        print(f"{p.name} ({p.wind}) hand: {p.hand}") 
        
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
                # Check if we should print round header
                print(f"\nround {engine.state.round_count} {p_name} ({p_obj.wind})'s turn---")
                
                # If Hand is Human (any human), show it? 
                # Or only if it's "Me"?
                # With multiple humans, we probably want to assume hot-seat.
                # Just print drawing info.
                
                # If Human, print "You drew..."
                if sim_players[p_idx] is None:
                    print(f"{p_name} drew {step['tile']}")
                    print(f"Melds: {p_obj.melds}")
                    # Print hand for active human?
                    print(f"Hand: {colored(p_obj.hand)}")
                else:
                    print(f"{p_name} drew {step['tile']}")
                    print(f"Melds: {p_obj.melds}")

            elif evt == 'discard':
                print(f"{p_name} discarded {step['tile']}")
                
            elif evt == 'meld':
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
            
            # Check if current required player is Human
            is_human = False
            if pid is not None:
                 is_human = (sim_players[pid] is None)
            
            if is_human:
                # HUMAN
                if act == 'discard':
                    d_idx = get_user_discard(p_obj)
                    step = engine.action_discard(pid, d_idx)
                elif act == 'response':
                     pass

            elif pid is not None and act == 'discard':
                # BOT Discard
                sim_p = sim_players[pid]
                sim_p.hand = p_obj.hand
                sim_p.melds = p_obj.melds
                d_idx = sim_p.decide_discard()
                step = engine.action_discard(pid, d_idx)
                time.sleep(0.1)
            
            if act == 'response':
                candidates = step['candidates']
                pending = engine.pending_responses
                new_step = None
                
                for c_pid in candidates:
                    opts = pending[c_pid]
                    
                    if sim_players[c_pid] is None:
                        # Human
                        action, extra = get_user_response(engine.state.players[c_pid], opts, engine.last_discard)
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
                             pass
                        
                    if res.get('status') != 'waiting_others':
                        new_step = res
                        break
                        
                if new_step:
                    step = new_step
                else:
                    pass

        elif stype == "error":
            print(f"Error: {step['message']}")
            break

if __name__ == "__main__":
    play_cli()

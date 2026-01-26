from src.step_game_engine import StepGameEngine
from src.models.tiles import Tile
from src.core.game_utils import colored

def test_chi_crash():
    print("Initializing Engine...")
    engine = StepGameEngine()
    engine.start_game()
    
    # Force Player 0 Logic
    p = engine.state.players[0]
    p.hand = [
        Tile('m', 3), Tile('m', 4), Tile('m', 6), 
        Tile('p', 1), Tile('p', 1), Tile('p', 1),
        Tile('s', 9), Tile('s', 9), Tile('s', 9),
        Tile('z', 1), Tile('z', 1), Tile('z', 2), Tile('z', 2)
    ]
    p.melds = []
    
    print(f"P0 Hand: {colored(p.hand)}")
    
    # Set Discarder as P3 (Left)
    discarder = engine.state.players[3]
    tile = Tile('m', 2) # 2m -> fits 3m, 4m for Chi
    engine.last_discard = tile
    engine.last_discard_idx = 3
    engine.phase = "WAIT_RESPONSE"
    engine.pending_responses = {0: ['chi', 'pon', 'ron']} # Fake it
    
    print(f"Discard: {tile}")
    print("Attempting Chi...")
    
    # Try action
    try:
        res = engine.action_response(0, 'chi', extra_data=None)
        print("Result:", res)
        print(f"New Hand: {colored(p.hand)}")
        print(f"Melds: {p.melds}")
    except Exception as e:
        print("CRASHED!")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chi_crash()

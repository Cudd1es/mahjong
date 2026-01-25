from src.models.tiles import Tile
from src.core.hand_checker import is_win_hand
from src.core.game_utils import colored

def test_invalid_hand():
    # Hand from log: 
    # Bot3: Hand=[3p 1s 4s 1p + 2p], Melds=[[2s, 3s, 4s], [5m, 6m, 7m], [1s, 2s, 3s]]
    # Melds are ignored by is_win_hand(hand) if we pass the full hand?
    # No, is_win_hand expects "standing hand". 
    # Wait, the logic in game_engine uses "full_hand = hand + melds" for checking?
    # Let's check game_engine.py Check Self Actions logic.
    
    # But usually is_win_hand checks the 14 tiles provided.
    # If 3 melds are open (9 tiles), then input hand is 14 tiles (5 standing + 9 melds).
    
    # Constructing the 14 tile hand
    standing = [
        Tile('p', 3), Tile('s', 1), Tile('s', 4), Tile('p', 1), Tile('p', 2)
    ]
    melds = [
        [Tile('s', 2), Tile('s', 3), Tile('s', 4)],
        [Tile('m', 5), Tile('m', 6), Tile('m', 7)],
        [Tile('s', 1), Tile('s', 2), Tile('s', 3)]
    ]
    
    full_hand = standing + [t for m in melds for t in m]
    print(f"Testing Hand (Combined length check): {len(full_hand)}")
    print(f"Standing Hand: {standing}")
    print(f"Melds: {melds}")
    
    # New API: is_win_hand(standing, melds)
    result = is_win_hand(standing, melds)
    print(f"Is Win: {result}")
    
    if result:
        print("FAIL: Invalid hand identified as Win!")
    else:
        print("PASS: Invalid hand correctly rejected.")

if __name__ == "__main__":
    test_invalid_hand()

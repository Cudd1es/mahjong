import unittest
from tiles import Tile
from hand_checker import discard_to_wait, is_win_hand

class TestKanIssues(unittest.TestCase):
    def test_discard_to_wait_with_kan(self):
        print("\nTesting discard_to_wait with Kan...")
        # Kan: 8p (4 tiles)
        kan_meld = [Tile('p', 8), Tile('p', 8), Tile('p', 8), Tile('p', 8)]
        melds = [kan_meld]
        
        # Standing hand (10 tiles) - Just needs one more pair or sequence for tenpai/win logic, 
        # but here we just test the length validation in discard_to_wait.
        # Logical count: 10 (hand) + 3 (Kan) = 13.
        # We draw 1 tile -> 14 logical.
        # Physical count: 10 (hand) + 4 (Kan) + 1 (drawn) = 15.
        
        hand = [
            Tile('m', 1), Tile('m', 1), Tile('m', 1),
            Tile('s', 2), Tile('s', 3), Tile('s', 4),
            Tile('z', 'E'), Tile('z', 'E'),
            Tile('p', 1), Tile('p', 1) 
        ]
        
        # Simulate drawing a tile
        hand.append(Tile('z', 'W'))
        
        try:
            # This previously raised ValueError: Hand must contain 14 tiles
            results = discard_to_wait(hand, melds)
            print(f"Success: discard_to_wait processed hand with {len(hand) + 4} physical tiles.")
        except ValueError as e:
            self.fail(f"discard_to_wait raised ValueError with Kan: {e}")

    def test_win_hand_with_kan(self):
        print("\nTesting is_win_hand with Kan...")
        # A valid winning hand with 1 Kan
        # Kan: 8p (4 tiles)
        # Meld 2: 1m 1m 1m (3 tiles)
        # Meld 3: 2s 3s 4s (3 tiles)
        # Pair: E E (2 tiles)
        # Total Physical: 4 + 3 + 3 + 3 + 2 = 15.
        # Logical: 3 + 3 + 3 + 3 + 2 = 14.
        
        full_hand_tiles = [
            Tile('p', 8), Tile('p', 8), Tile('p', 8), Tile('p', 8), # Kan
            Tile('m', 1), Tile('m', 1), Tile('m', 1),               # Pung
            Tile('s', 2), Tile('s', 3), Tile('s', 4),               # Chow
            Tile('p', 2), Tile('p', 2), Tile('p', 2),               # Pung
            Tile('z', 'E'), Tile('z', 'E')                          # Pair
        ]
        
        try:
            result = is_win_hand(full_hand_tiles)
            if isinstance(result, tuple):
                is_win = result[0]
            else:
                is_win = result
                
            if not is_win:
                print(f"Failure: is_win_hand returned False for valid Kan hand (Size: {len(full_hand_tiles)})")
            else:
                print("Success: is_win_hand detected win with Kan.")
                
            self.assertTrue(is_win, "Should detect valid win with Kan")
        except Exception as e:
            self.fail(f"is_win_hand raised exception: {e}")

if __name__ == '__main__':
    unittest.main()

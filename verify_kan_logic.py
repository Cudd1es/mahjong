import unittest
from unittest.mock import patch, MagicMock
from player import HumanPlayer
from tiles import Tile
from game_loop import check_self_actions, process_responses
from wall import create_wall

class TestKanLogic(unittest.TestCase):
    @patch('builtins.input', side_effect=['1', 'n']) # 1 to Kan, n to skip Riichi/Kan
    @patch('game_loop.ask_win', return_value=False)
    @patch('game_loop.ask_riichi', return_value=False)
    def test_ankan_flow(self, mock_riichi, mock_ask_win, mock_input):
        print("\nTesting Ankan Logic...")
        p = HumanPlayer("Tester", "E")
        # Hand: 1m 1m 1m 1m 2p 3p 4p 5s 5s 6s 7s 8s 9s + 9s (14 tiles)
        p.hand = [
            Tile('m', 1), Tile('m', 1), Tile('m', 1), Tile('m', 1),
            Tile('p', 2), Tile('p', 3), Tile('p', 4),
            Tile('s', 5), Tile('s', 5), Tile('s', 6), 
            Tile('s', 7), Tile('s', 8), Tile('s', 9),
            Tile('s', 9) 
        ]
        p.sort_hand()
        
        dead_wall = [Tile('z', 'W')] * 14
        live_wall = [] 
        
        # Expectation: 
        # 1. Detect Ankan 1m. User selects it.
        # 2. Remove 4x 1m. Add meld [1m, 1m, 1m, 1m].
        # 3. Draw Rinshan (W).
        # 4. Loop again. No Tsumo, No Kan. Return None.
        
        status, _ = check_self_actions(p, dead_wall, live_wall)
        
        print(f"Status: {status}")
        print(f"Hand: {p.hand}")
        print(f"Melds: {p.melds}")
        
        # Verify
        self.assertEqual(len(p.melds), 1)
        self.assertEqual(len(p.melds[0]), 4) # 1m kan
        self.assertEqual(p.melds[0][0], Tile('m', 1))
        
        # Check hand size: 
        # Initial 14. Removed 4. Added Rinshan 1. Total 11.
        self.assertEqual(len(p.hand), 11)
        self.assertIn(Tile('z', 'W'), p.hand)
        
    @patch('builtins.input', side_effect=['1', 'n'])
    @patch('game_loop.ask_win', return_value=False)
    @patch('game_loop.ask_riichi', return_value=False)
    def test_kakan_flow(self, mock_riichi, mock_ask_win, mock_input):
        print("\nTesting Kakan Logic...")
        p = HumanPlayer("Tester", "E")
        # Meld: Pon 1m
        p.melds = [[Tile('m', 1), Tile('m', 1), Tile('m', 1)]]
        
        # Hand: 1m + others (13 tiles + 1 draw? No, 10 tiles + 1 draw = 11 tiles)
        # Because we have 1 Pon (3 tiles). Full hand size logic: 3 (meld) + 11 (hand) = 14.
        p.hand = [
            Tile('m', 1), # The Kakan tile
            Tile('p', 2), Tile('p', 3), Tile('p', 4),
            Tile('s', 5), Tile('s', 5), Tile('s', 6), 
            Tile('s', 7), Tile('s', 8), Tile('s', 9),
            Tile('s', 9) 
        ]
        p.sort_hand()
        
        dead_wall = [Tile('z', 'N')] * 14
        live_wall = []
        
        # User selects 1 to Kakan
        status, _ = check_self_actions(p, dead_wall, live_wall)
        
        # Verify
        self.assertEqual(len(p.melds), 1)
        self.assertEqual(len(p.melds[0]), 4) # Upgraded to Kan
        
        # Check hand:
        # Initial 11. Removed 1 (1m). Added Rinshan (N). Total 11.
        self.assertEqual(len(p.hand), 11)
        self.assertIn(Tile('z', 'N'), p.hand)

        self.assertEqual(len(p.hand), 11)
        self.assertIn(Tile('z', 'N'), p.hand)

    @patch('game_loop.check_responses')
    @patch('game_loop.check_self_actions', return_value=("None", None))
    @patch('builtins.input', return_value='0') # discard index 0
    def test_daiminkan_flow(self, mock_input, mock_self_actions, mock_check_responses):
        print("\nTesting Daiminkan Flow in process_responses...")
        p1 = HumanPlayer("P1", "E")
        p2 = HumanPlayer("P2", "S") # The Kan player
        p3 = HumanPlayer("P3", "W")
        p4 = HumanPlayer("P4", "N")
        players = [p1, p2, p3, p4]
        
        # Setup P2 hand
        p2.hand = [Tile('m',1)] * 3 + [Tile('p',1)] * 10 
        p2.melds = []
        
        # Mock check_responses to return 'kan' for P2
        # return: (action, responder_idx, details)
        # details for Kan is the tiles used (e.g. 1m 1m 1m)
        mock_check_responses.return_value = ('kan', 1, [Tile('m',1)]*3)
        
        dead_wall = [Tile('z', 'P')] * 14
        
        # Act
        # Discarder P1 (idx 0), Discarded 1m
        action, idx, new_discard = process_responses(players, 0, Tile('m',1), dead_wall)
        
        # Verify
        self.assertEqual(action, 'kan')
        self.assertEqual(idx, 1) # P2
        # Check if drawn Rinshan (P) was handled
        # `process_responses` calls `p2.draw(dead_wall)`.
        self.assertIn(Tile('z', 'P'), p2.hand)
        
        # Check check_self_actions called
        mock_self_actions.assert_called_once()
        
        # Check discard happened
        self.assertIsNotNone(new_discard)


if __name__ == '__main__':
    unittest.main()

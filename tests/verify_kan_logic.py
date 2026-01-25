import unittest
from unittest.mock import patch, MagicMock
from src.models.player import HumanPlayer
from src.models.tiles import Tile
from src.game_engine import GameEngine
from src.models.wall import create_wall

class TestKanLogic(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.state.initialize() # initializes players and wall

    @patch('builtins.input', side_effect=['1', 'n']) # 1 to Kan, n to skip Riichi/Kan
    @patch('src.core.game_utils.ask_win', return_value=False)
    @patch('src.core.game_utils.ask_riichi', return_value=False)
    def test_ankan_flow(self, mock_riichi, mock_ask_win, mock_input):
        print("\nTesting Ankan Logic...")
        p = self.engine.state.players[0] # HumanPlayer P1
        p.hand = [
            Tile('m', 1), Tile('m', 1), Tile('m', 1), Tile('m', 1),
            Tile('p', 2), Tile('p', 3), Tile('p', 4),
            Tile('s', 5), Tile('s', 5), Tile('s', 6), 
            Tile('s', 7), Tile('s', 8), Tile('s', 9),
            Tile('s', 9) 
        ]
        p.sort_hand()
        p.melds = []
        
        self.engine.state.dead_wall = [Tile('z', 'W')] * 14
        
        # Test engine.check_self_actions
        status, _ = self.engine.check_self_actions(p)
        
        print(f"Status: {status}")
        print(f"Hand: {p.hand}")
        print(f"Melds: {p.melds}")
        
        self.assertEqual(len(p.melds), 1)
        self.assertEqual(len(p.melds[0]), 4) # 1m kan
        
        # Initial 14 - 4 + 1 = 11 tiles
        self.assertEqual(len(p.hand), 11)
        self.assertIn(Tile('z', 'W'), p.hand)
        
    @patch('builtins.input', side_effect=['1', 'n'])
    @patch('src.core.game_utils.ask_win', return_value=False)
    @patch('src.core.game_utils.ask_riichi', return_value=False)
    def test_kakan_flow(self, mock_riichi, mock_ask_win, mock_input):
        print("\nTesting Kakan Logic...")
        p = self.engine.state.players[0]
        p.melds = [[Tile('m', 1), Tile('m', 1), Tile('m', 1)]]
        
        p.hand = [
            Tile('m', 1), 
            Tile('p', 2), Tile('p', 3), Tile('p', 4),
            Tile('s', 5), Tile('s', 5), Tile('s', 6), 
            Tile('s', 7), Tile('s', 8), Tile('s', 9),
            Tile('s', 9) 
        ]
        p.sort_hand()
        
        self.engine.state.dead_wall = [Tile('z', 'N')] * 14
        
        status, _ = self.engine.check_self_actions(p)
        
        self.assertEqual(len(p.melds), 1)
        self.assertEqual(len(p.melds[0]), 4) 
        self.assertEqual(len(p.hand), 11)
        self.assertIn(Tile('z', 'N'), p.hand)

    @patch('src.game_engine.GameEngine.check_self_actions', return_value=("None", None))
    @patch('builtins.input', return_value='0') 
    @patch('src.models.player.AIPlayer.decide_discard', return_value=0)
    def test_daiminkan_flow(self, mock_decide, mock_input, mock_self_actions):
        print("\nTesting Daiminkan Flow in process_responses...")
        # Responder is self.engine.state.players[1] (P2)
        p2 = self.engine.state.players[1]
        p2.hand = [Tile('m',1)] * 3 + [Tile('p',1)] * 10 
        p2.melds = []
        p2.is_human = True 
        
        # Mock input for "Type [1]ron, [2]kan...": '2' (Kan)
        mock_input.side_effect = ['2', '0'] # 2 to Kan, then 0 to discard
        
        self.engine.state.dead_wall = [Tile('z', 'P')] * 14
        
        # Act
        # Discarder P1 (idx 0), Discarded 1m
        # process_responses(discarder_idx, discarded_tile)
        action, idx, new_discard = self.engine.process_responses(0, Tile('m',1))
        
        # Verify
        self.assertEqual(action, 'kan')
        self.assertEqual(idx, 1) # P2
        self.assertIn(Tile('z', 'P'), p2.hand)
        
    @patch('src.game_engine.GameEngine.check_self_actions', return_value=("None", None))
    @patch('src.models.player.AIPlayer.decide_discard', return_value=0)
    def test_kakan_on_chi_fail(self, mock_decide, mock_self_actions):
        print("\nTesting Kakan Failure on Chi...")
        p = self.engine.state.players[0]
        # Player has a Chi open: 4p 5p 6p
        p.melds = [[Tile('p', 4), Tile('p', 5), Tile('p', 6)]]
        
        # Player draws ANY tile, let's say 4p. 
        # Code incorrectly matched 4p with m[0] before.
        drawn_tile = Tile('p', 4)  
        p.hand = [drawn_tile] + [Tile('s', 1)] * 10
        
        # Test usage of can_kakan
        from src.core.melds import can_kakan
        options = can_kakan(p.hand, p.melds, drawn_tile)
        
        # Should be empty because [4p,5p,6p] is not a Pon
        self.assertEqual(options, [], f"Should not find Kakan options for Chi meld: {options}")

    @patch('src.game_engine.GameEngine.check_self_actions', return_value=("None", None))
    @patch('src.models.player.AIPlayer.decide_discard', return_value=0)
    def test_pon_with_three_tiles(self, mock_decide, mock_self_actions):
        print("\nTesting Pon with 3 matching tiles in hand...")
        from src.models.tiles import Tile
        p = self.engine.state.players[0]
        # Player has THREE 8s in hand
        # Hand: 2m 3m 4m 2s 2s 3s 7s 8s 8s 8s S S S
        p.hand = [
            Tile('m', 2), Tile('m', 3), Tile('m', 4),
            Tile('s', 2), Tile('s', 2), Tile('s', 3), Tile('s', 7),
            Tile('s', 8), Tile('s', 8), Tile('s', 8),
            Tile('z', 'S'), Tile('z', 'S'), Tile('z', 'S')
        ]
        p.melds = []
        
        # Discarded 8s
        discarded_tile = Tile('s', 8)
        
        # Mock input '3' (Pon) then '0' (Discard)
        with patch('builtins.input', side_effect=['3', '0']):
            # Discarder must be NOT 0, so P0 can respond
            action, idx, new_discard = self.engine.process_responses(1, discarded_tile)
            
        print(f"Hand after Pon: {p.hand}")
        print(f"Melds after Pon: {p.melds}")
        
        # Verify
        self.assertEqual(action, 'meld', "Action should be meld")
        # Check melds: Should be [8s, 8s, 8s] (len 3)
        self.assertEqual(len(p.melds), 1, "Should have 1 meld")
        self.assertEqual(len(p.melds[0]), 3, f"Meld size should be 3, got: {p.melds[0]}")
        
        # Check hand size: 13 - 2 = 11 tiles (plus draw/discard cycle not happening here)
        # Wait, process_responses reduces hand by 2, then discards 1. Total hand size = 13-2-1 = 10.
        self.assertEqual(len(p.hand), 10, f"Hand size mismatch. Hand: {p.hand}")
        
        # Check if one 8s remains in hand
        remaining_8s = [t for t in p.hand if t == Tile('s', 8)]
        self.assertEqual(len(remaining_8s), 1, "Should have one 8s remaining in hand. Got 0.")

if __name__ == '__main__':
    unittest.main()

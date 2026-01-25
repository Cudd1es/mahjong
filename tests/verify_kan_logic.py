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
    def test_daiminkan_flow(self, mock_input, mock_self_actions):
        print("\nTesting Daiminkan Flow in process_responses...")
        # Responder is self.engine.state.players[1] (P2)
        p2 = self.engine.state.players[1]
        p2.hand = [Tile('m',1)] * 3 + [Tile('p',1)] * 10 
        p2.melds = []
        # P2 needs to be human for process_responses logic?
        # GameEngine.process_responses checks `if not p.is_human: continue`.
        # So we must convert P2 to human or mock it.
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
        
        mock_self_actions.assert_called_once()
        self.assertIsNotNone(new_discard)


if __name__ == '__main__':
    unittest.main()

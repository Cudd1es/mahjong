
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
            action, idx, new_discard = self.engine.process_responses(0, discarded_tile)
            
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
        self.assertEqual(len(remaining_8s), 1, "Should have one 8s remaining in hand")

from scoring import FuCalculator, ScoreTable
from tiles import Tile
from player import Player
import unittest

class TestScoring(unittest.TestCase):
    def test_chiitoitsu_fu(self):
        # Chiitoitsu is always 25 Fu
        calc = FuCalculator()
        fu = calc.calculate_fu(
            hand=[], melds=[], win_tile=Tile('m',1), win_type='ron', 
            player=Player("Test", "E"), pungs=[], chows=[], head=[]
        )
        # Note: In our implementation, we need to Pass 'chiitoitsu' as win_type logic inside
        # Actually our calculate_fu checks `win_type == 'chiitoitsu'`?
        # Let's check logic: `if win_type == 'chiitoitsu': return 25`
        # So we hijack `win_type` arg to pass this info.
        fu = calc.calculate_fu(
            hand=[], melds=[], win_tile=Tile('m',1), win_type='chiitoitsu', 
            player=Player("Test", "E")
        )
        self.assertEqual(fu, 25)

    def test_pinfu_tsumo(self):
        # Pinfu Tsumo = 20 Fu (Usually hand_checker override this, but let's see base logic)
        # Base 20 + Tsumo 2 = 22 -> 30.
        # UNLESS override.
        # Our game_loop applies override.
        # This test checks NON-Override behavior first.
        calc = FuCalculator()
        
        # Hand: 234m 234p 234s 678s 99p (Head)
        hand = [
            Tile('m',2), Tile('m',3), Tile('m',4),
            Tile('p',2), Tile('p',3), Tile('p',4),
            Tile('s',2), Tile('s',3), Tile('s',4), 
            Tile('s',6), Tile('s',7), Tile('s',8),
            Tile('p',9), Tile('p',9)
        ]
        win_tile = Tile('m', 2) # Low wait?
        # Chows
        chows = [
            [Tile('m',2), Tile('m',3), Tile('m',4)],
            [Tile('p',2), Tile('p',3), Tile('p',4)],
            [Tile('s',2), Tile('s',3), Tile('s',4)],
            [Tile('s',6), Tile('s',7), Tile('s',8)]
        ]
        head = [Tile('p',9), Tile('p',9)]
        
        fu = calc.calculate_fu(
            hand=hand, melds=[], win_tile=win_tile, win_type='tsumo',
            player=Player("Test", "E"), pungs=[], chows=chows, head=head
        )
        # Base 20 + Tsumo 2 = 22 -> Roundup 30.
        self.assertEqual(fu, 30)

    def test_open_hand_ron_fu(self):
        # 1 Open Pung (Simple), 1 Closed Pung (Simple).
        # Win Ron (Base 30).
        # Open Pung: +2.
        # Closed Pung: +4.
        # Total = 20 + 2 + 4 = 26 -> 30.
        
        calc = FuCalculator()
        p1 = Player("Test", "S")
        
        # 222m (Open), 444s (Closed), 678p, 789p, 11z
        m_pung = [Tile('m',2), Tile('m',2), Tile('m',2)]
        p1.melds = [m_pung]
        
        c_pung = [Tile('s',4), Tile('s',4), Tile('s',4)]
        
        # pungs list passed from hand checker (contains both)
        pungs = [m_pung, c_pung]
        chows = [
            [Tile('p',6), Tile('p',7), Tile('p',8)],
            [Tile('p',7), Tile('p',8), Tile('p',9)]
        ]
        head = [Tile('z',1), Tile('z',1)] # East wind (Not seat, Not round)
        
        fu = calc.calculate_fu(
            hand=[], melds=[m_pung], win_tile=Tile('s',4), win_type='ron',
            player=p1, pungs=pungs, chows=chows, head=head
        )
        
        # Base 20
        # Menzen Ron: No (Open meld) -> 0
        # Open Pung (2m): +2
        # Closed Pung (4s): +4
        # Total: 26 -> 30.
        self.assertEqual(fu, 30)
        
    def test_kan_fu(self):
        # Open Kan (Terminals) -> 16 Fu
        calc = FuCalculator()
        p1 = Player("Test", "S")
        
        # 1111m (Open Kan)
        kan = [Tile('m',1)] * 4
        p1.melds = [kan]
        
        pungs = [kan]
        fu = calc.calculate_fu(
            hand=[], melds=[kan], win_tile=Tile('m',5), win_type='ron',
            player=p1, pungs=pungs, chows=[], head=[Tile('z',2), Tile('z',2)]
        )
        
        # Base 20
        # Menzen: No
        # Open Kan (1m): +16
        # Total: 36 -> 40.
        self.assertEqual(fu, 40)

if __name__ == '__main__':
    unittest.main()

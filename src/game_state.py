from src.models.wall import create_wall, shuffle_wall, deal_tiles
from src.models.player import HumanPlayer, AIPlayer

class GameState:
    def __init__(self):
        self.live_wall = []
        self.dead_wall = []
        self.players = []
        self.current_player_idx = 0
        self.round_count = 0
        self.kan_counter = 0
        
    def initialize(self):
        wall = create_wall()
        shuffle_wall(wall)
        
        # set human player as P1 and rest player are AI
        self.players = [
            HumanPlayer("P1", "E"),
            AIPlayer("P2", "S"),
            AIPlayer("P3", "W"),
            AIPlayer("P4", "N")
        ]
        
        hands, wall = deal_tiles(wall, 4)
        for i, p in enumerate(self.players):
            p.hand = hands[i]
            p.sort_hand()
            
        self.dead_wall = wall[14:]
        self.live_wall = wall[:-14]
        self.current_player_idx = 0
        self.round_count = 0
        self.kan_counter = 0

    def get_current_player(self):
        return self.players[self.current_player_idx]
        
    def draw_live(self, player):
        return player.draw(self.live_wall)
        
    def draw_dead(self, player):
        return player.draw(self.dead_wall)

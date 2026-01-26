from pydantic import BaseModel
from typing import List, Optional, Union, Dict

class TileModel(BaseModel):
    suit: str
    value: Union[int, str]
    
    def __str__(self):
        return f"{self.value}{self.suit}"

class PlayerModel(BaseModel):
    name: str
    wind: str
    score: int
    hand: List[str] # List of tile strings e.g. "1m", "5p"
    melds: List[List[str]]
    discards: List[str]
    is_riichi: bool

class GameStateModel(BaseModel):
    players: List[PlayerModel]
    current_player_idx: int
    round_count: int
    kan_counter: int
    live_wall_count: int
    dead_wall_count: int
    phase: str # DRAW, WAIT_DISCARD, WAIT_RESPONSE, GAME_OVER
    last_discard: Optional[str]
    
class ActionRequest(BaseModel):
    type: str # discard, ron, pon, kan, chi, skip
    player_idx: int
    tile_index: Optional[int] = None # for discard
    extra: Optional[List[str]] = None # for chi/pon choices

class StepResponse(BaseModel):
    type: str # event, input_required, game_over, error
    action: Optional[str] = None
    player_idx: Optional[int] = None
    tile: Optional[str] = None
    candidates: Optional[List[int]] = None
    result: Optional[Dict] = None
    message: Optional[str] = None

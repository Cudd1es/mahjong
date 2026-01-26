from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.step_game_engine import StepGameEngine
from server.schemas import GameStateModel, PlayerModel, ActionRequest, StepResponse
from typing import List

app = FastAPI()

# Allow CORS for React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = StepGameEngine()

def serialize_state(e: StepGameEngine) -> GameStateModel:
    players = []
    for p in e.state.players:
        hand_strs = [str(t) for t in p.hand]
        meld_strs = [[str(t) for t in m] for m in p.melds]
        discard_strs = [str(t) for t in p.discards]
        players.append(PlayerModel(
            name=p.name,
            wind=p.wind,
            score=p.score,
            hand=hand_strs,
            melds=meld_strs,
            discards=discard_strs,
            is_riichi=p.is_riichi
        ))
        
    return GameStateModel(
        players=players,
        current_player_idx=e.state.current_player_idx,
        round_count=e.state.round_count,
        kan_counter=e.state.kan_counter,
        live_wall_count=len(e.state.live_wall),
        dead_wall_count=len(e.state.dead_wall),
        phase=e.phase,
        last_discard=str(e.last_discard) if e.last_discard else None
    )

@app.post("/start", response_model=StepResponse)
def start_game():
    res = engine.start_game()
    return res

@app.get("/state", response_model=GameStateModel)
def get_state():
    return serialize_state(engine)

@app.post("/action", response_model=StepResponse)
def handle_action(req: ActionRequest):
    if req.type == "discard":
        if req.tile_index is None:
            raise HTTPException(status_code=400, detail="tile_index required for discard")
        res = engine.action_discard(req.player_idx, req.tile_index)
        if "error" in res:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
        
    elif req.type in ["ron", "pon", "kan", "chi", "skip"]:
        res = engine.action_response(req.player_idx, req.type, req.extra)
        if "error" in res:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
        
    raise HTTPException(status_code=400, detail="Unknown action type")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Mahjong API is running"}

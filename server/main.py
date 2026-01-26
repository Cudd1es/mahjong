from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.step_game_engine import StepGameEngine
from server.schemas import GameStateModel, PlayerModel, ActionRequest, StepResponse
from typing import List
import random
from src.models.player import AIPlayer

# --- Mini SimulationPlayer (could import from files if organized, but inline for now ensures compat) ---
class SimulationPlayer(AIPlayer):
    def __init__(self, name, wind):
        super().__init__(name, wind)
        self.can_respond_to_discard = True
        
    def decide_response(self, options, discarded_tile, hand):
        if not options: return 'n', None
        if 'ron' in options: return '1', 'ron'
        if random.random() < 0.5: return 'n', None
        if 'kan' in options: return '2', 'kan'
        if 'pon' in options: return '3', 'pon'
        if 'chi' in options: return '4', 'chi'
        return 'n', None

    def decide_chi_option(self, chi_options):
        return random.randint(1, len(chi_options))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = StepGameEngine()

# Setup Bots
bots = [
    None, # P0 is Human
    SimulationPlayer("Bot1", "S"),
    SimulationPlayer("Bot2", "W"),
    SimulationPlayer("Bot3", "N")
]

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
        last_discard=str(e.last_discard) if e.last_discard else None,
        last_discard_player_idx=e.last_discard_idx,
        valid_actions=list(e.pending_responses.get(0, [])) + (['skip'] if 0 in e.pending_responses else []) if e.phase == "WAIT_RESPONSE" else []
    )

def process_ai_turns(current_step):
    """
    Loop until input is required from Player 0 (Human) or Game Over.
    """
    step = current_step
    
    while True:
        # Check safety break
        # (Could add max loop count if needed)
        
        stype = step['type']
        
        if stype == 'game_over':
            return step
            
        elif stype == 'input_required':
            action = step['action']
            pid = step.get('player_idx')
            
            # If it's P0's turn to discard, stop and let frontend handle it
            if action == 'discard' and pid == 0:
                return step
                
            # If it's P0's turn to respond, stop
            if action == 'response':
                candidates = step['candidates']
                if 0 in candidates:
                    # P0 needs to respond. Even if bots also need to respond, 
                    # we return step so frontend can prompt P0.
                    # BUT we must process Bot responses too if any.
                    # Currently StepGameEngine waits for ALL.
                    # So we should process Bots here, then return step for P0.
                    pass
                else:
                    # Only bots responding?
                    # Engine returns 'candidates' list.
                    # If P0 not in candidates, we should resolve all bots and continue loop.
                    pass
                    
                # Handle Responses
                pending = engine.pending_responses
                new_step = None
                p0_needs_input = False
                
                for c_pid in candidates:
                    opts = pending[c_pid]
                    
                    if c_pid == 0:
                        p0_needs_input = True
                        continue # Skip P0 logic
                        
                    # Bot Logic
                    bot = bots[c_pid]
                    current_p = engine.state.players[c_pid]
                    bot.hand = current_p.hand
                    bot.melds = current_p.melds
                    
                    code, choice = bot.decide_response(opts, engine.last_discard, bot.hand)
                    act_str = choice if choice in ['ron', 'pon', 'kan', 'chi'] else 'skip'
                    
                    res = engine.action_response(c_pid, act_str, None)
                    if res.get('status') != 'waiting_others':
                        new_step = res
                        break
                
                if new_step:
                    step = new_step
                    continue # Loop again with new step
                    
                if p0_needs_input:
                    return step # Return control to P0
                    
                # If we are here, P0 not needed, but no new step? 
                # Means waiting for others? But we processed all Bots.
                # Must be some logic error if we didn't get new step and P0 not involved.
                # But logicaly if P0 not involved, we processed all bots.
                # So engine should have resolved.
                # If engine didn't resolve, maybe bug?
                # Assume continue if new_step generated.
                if not new_step:
                     # This effectively means we are waiting but consumed all bot turns?
                     # Should not happen if StepGameEngine is correct.
                     return step 

            elif action == 'discard' and pid != 0:
                # Bot Discard
                bot = bots[pid]
                current_p = engine.state.players[pid]
                bot.hand = current_p.hand
                bot.melds = current_p.melds
                
                d_idx = bot.decide_discard()
                step = engine.action_discard(pid, d_idx)
                continue # Execute next step immediately
                
        elif stype == 'event':
            # Draw, Meld, Discard events
            # Just ack and get next
            step = engine.next_step()
            continue
            
        elif stype == 'error':
            return step
            
    return step

@app.post("/start", response_model=StepResponse)
def start_game():
    # Reset bots state if needed?
    # engine.start_game() resets State.
    res = engine.start_game()
    final_res = process_ai_turns(res)
    return final_res

@app.get("/state", response_model=GameStateModel)
def get_state():
    return serialize_state(engine)

@app.post("/action", response_model=StepResponse)
def handle_action(req: ActionRequest):
    res = None
    if req.type == "discard":
        if req.tile_index is None:
            raise HTTPException(status_code=400, detail="tile_index required for discard")
        res = engine.action_discard(req.player_idx, req.tile_index)
        if "error" in res:
            raise HTTPException(status_code=400, detail=res["error"])
        
    elif req.type in ["ron", "pon", "kan", "chi", "skip"]:
        res = engine.action_response(req.player_idx, req.type, req.extra)
        if "error" in res:
            raise HTTPException(status_code=400, detail=res["error"])
    else:
        raise HTTPException(status_code=400, detail="Unknown action type")
        
    # After human action, auto-advance bots
    final_res = process_ai_turns(res)
    return final_res

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Mahjong API is running"}

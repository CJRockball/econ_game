from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
from core.game_engine import GameEngine

app = FastAPI(title="Economic Simulation Game")

# Static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# Global game instance
game = GameEngine()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "game_state": game.get_state(),
        "players": game.get_all_players()
    })

@app.post("/api/game/start")
async def start_game():
    game.start_new_game()
    return {"status": "Game started", "turn": game.current_turn}

@app.post("/api/game/advance_turn") 
async def advance_turn():
    game.advance_turn()
    return {"status": "Turn advanced", "turn": game.current_turn}

@app.get("/api/game/state")
async def get_game_state():
    return game.get_state()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Send game state updates
        await websocket.send_text(json.dumps(game.get_state()))
        await asyncio.sleep(1)

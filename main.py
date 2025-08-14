# main.py - REPLACE ENTIRELY
import asyncio
import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from core.game_engine import GameEngine

app = FastAPI(title="Economic Simulation Game")

# Static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# Global game instance
game = GameEngine()

# Store active WebSocket connections
active_connections: list[WebSocket] = []

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
    await broadcast_game_state()
    return {"status": "Game started", "turn": game.current_turn}

@app.post("/api/game/advance_turn") 
async def advance_turn():
    game.advance_turn()
    await broadcast_game_state()
    return {"status": "Turn advanced", "turn": game.current_turn}

@app.get("/api/game/state")
async def get_game_state():
    return game.get_state()

async def broadcast_game_state():
    """Send game state to all connected WebSocket clients"""
    if active_connections:
        game_state = game.get_state()
        message = json.dumps(game_state)
        
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            active_connections.remove(connection)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_text(json.dumps(game.get_state()))
        
        # Keep connection alive with periodic heartbeat
        while True:
            try:
                # Wait for any message or timeout after 30 seconds
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send periodic heartbeat
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

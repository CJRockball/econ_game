import asyncio
import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.game_engine import GameEngine

app = FastAPI(title="Economic Simulation Game")

# Templates
templates = Jinja2Templates(directory="web/templates")

# Global game instance
game = GameEngine()

# Store active WebSocket connections
active_connections: list[WebSocket] = []

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "game_state": game.get_state()
    })

@app.post("/api/game/start")
async def start_game():
    """Start a new game and broadcast to all clients."""
    game.start_new_game()
    await broadcast_game_state()
    return {"status": "Game started", "turn": game.current_turn}

@app.post("/api/game/advance_turn") 
async def advance_turn():
    """Advance the game by one turn and broadcast to all clients."""
    game.advance_turn()
    await broadcast_game_state()
    return {"status": "Turn advanced", "turn": game.current_turn}

@app.get("/api/game/state")
async def get_game_state():
    """Get current game state."""
    return game.get_state()

async def broadcast_game_state():
    """Send game state to all connected WebSocket clients."""
    if active_connections:
        game_state = game.economic_state.get_state()
        message = json.dumps(game_state)
        
        # Remove disconnected clients
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
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send updated state on connect
        await websocket.send_text(json.dumps(game.economic_state.get_state()))
        
        # Keep connection alive
        while True:
            try:
                # Wait for client ping or timeout
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

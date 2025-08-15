import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Safe import with error handling
try:
    from core.game_engine import GameEngine
except ImportError as e:
    print(f"Error importing GameEngine: {e}")
    # Create a fallback class if needed
    class GameEngine:
        def __init__(self):
            self.current_turn = 0
        def get_state(self):
            return {"error": "GameEngine not available"}

app = FastAPI(title="Enhanced Economic Simulation Game")

# Templates and static files
templates = Jinja2Templates(directory="web/templates")
try:
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
except:
    print("Warning: Static files directory not found")

# Global game instance
game = GameEngine()

# Store active WebSocket connections
active_connections: list[WebSocket] = []

# Request models for API endpoints
class ModeRequest(BaseModel):
    mode: str

class VoteRequest(BaseModel):
    votes: Dict[str, float]

class InvestmentRequest(BaseModel):
    amount: float

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard page - SAFE ACCESS."""
    try:
        game_state = game.get_state() if hasattr(game, 'get_state') else {}
    except Exception as e:
        game_state = {"error": str(e)}
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "game_state": game_state
    })

@app.post("/api/game/start")
async def start_game():
    """Start a new game with safe method calls."""
    try:
        if hasattr(game, 'start_new_game'):
            game.start_new_game()
            await broadcast_game_state()
            
            return {
                "status": "Game started", 
                "turn": getattr(game, 'current_turn', 0),
                "central_bank_mode": getattr(game, 'central_bank_mode', 'ai')
            }
        else:
            raise HTTPException(status_code=500, detail="Game engine not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting game: {e}")

@app.post("/api/game/advance_turn") 
async def advance_turn():
    """Advance the game by one turn with safe processing."""
    try:
        if hasattr(game, 'advance_turn'):
            game.advance_turn()
            await broadcast_game_state()
            
            # Get economic indicators safely
            economic_indicators = {}
            if (hasattr(game, 'economic_state') and 
                hasattr(game.economic_state, 'get_economic_indicators')):
                economic_indicators = game.economic_state.get_economic_indicators()
            
            return {
                "status": "Turn advanced", 
                "turn": getattr(game, 'current_turn', 0),
                "economic_indicators": economic_indicators,
                "recent_events": getattr(game, 'recent_events', [])
            }
        else:
            raise HTTPException(status_code=500, detail="Game engine not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error advancing turn: {e}")

@app.get("/api/game/state")
async def get_game_state():
    """Get current game state with safe access."""
    try:
        if hasattr(game, 'get_state'):
            return game.get_state()
        else:
            return {"error": "Game state not available"}
    except Exception as e:
        return {"error": f"Error getting game state: {e}"}

@app.post("/api/central_bank/set_mode")
async def set_central_bank_mode(request: ModeRequest):
    """Set central bank governance mode with validation."""
    try:
        mode = request.mode
        if mode not in ["ai", "democratic"]:
            raise HTTPException(status_code=400, detail="Invalid mode. Must be 'ai' or 'democratic'")
        
        if hasattr(game, 'set_central_bank_mode'):
            game.set_central_bank_mode(mode)
            await broadcast_game_state()
            return {
                "status": f"Central bank mode set to {mode}",
                "mode": mode
            }
        else:
            raise HTTPException(status_code=500, detail="Central bank mode setting not available")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting central bank mode: {e}")

@app.get("/api/central_bank/policy_options")
async def get_policy_options():
    """Get Fed Funds Rate policy options for voting."""
    try:
        if hasattr(game, 'get_central_bank_policy_options'):
            return game.get_central_bank_policy_options()
        else:
            return {
                "current_rate": 0.025,
                "taylor_rule_rate": 0.025,
                "options": [{"rate": 0.025, "description": "2.5% (Default)"}],
                "policy_explanation": "Policy options not available"
            }
    except Exception as e:
        return {
            "error": f"Error getting policy options: {e}",
            "current_rate": 0.025,
            "options": [{"rate": 0.025, "description": "2.5% (Error)"}]
        }

@app.post("/api/central_bank/vote")
async def vote_fed_funds_rate(request: VoteRequest):
    """Process democratic vote on Fed Funds Rate."""
    try:
        player_votes = request.votes
        
        if getattr(game, 'central_bank_mode', 'ai') != "democratic":
            raise HTTPException(status_code=400, detail="Central bank is not in democratic mode")
        
        if not player_votes:
            raise HTTPException(status_code=400, detail="No votes provided")
        
        voted_rate = 0.025  # Default
        if hasattr(game, 'vote_on_fed_funds_rate'):
            voted_rate = game.vote_on_fed_funds_rate(player_votes)
        
        await broadcast_game_state()
        
        return {
            "status": "Vote processed",
            "new_fed_funds_rate": voted_rate,
            "votes": player_votes
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing vote: {e}")

@app.get("/api/players/{player_name}/status")
async def get_player_status(player_name: str):
    """Get detailed status for specific player."""
    try:
        if not hasattr(game, 'players'):
            raise HTTPException(status_code=500, detail="Game players not available")
        
        player = game.players.get(player_name)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        if hasattr(player, 'get_status'):
            return player.get_status()
        else:
            return {"name": player_name, "error": "Player status not available"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting player status: {e}")

@app.post("/api/players/{player_name}/invest_technology")
async def invest_in_technology(player_name: str, request: InvestmentRequest):
    """Player invests in technology with safe method calls."""
    try:
        if not hasattr(game, 'players'):
            raise HTTPException(status_code=500, detail="Game players not available")
        
        player = game.players.get(player_name)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        amount = request.amount
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Investment amount must be positive")
        
        if hasattr(player, 'invest_in_technology'):
            # Check if player has enough money
            if hasattr(player, 'money') and getattr(player, 'money', 0) >= amount:
                player.invest_in_technology(amount)
                await broadcast_game_state()
                
                return {
                    "status": f"{player_name} invested {amount} in technology",
                    "new_tech_level": getattr(player, 'technology_level', 1.0)
                }
            else:
                raise HTTPException(status_code=400, detail="Insufficient funds for technology investment")
        else:
            raise HTTPException(status_code=400, detail="Technology investment not available for this player")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing technology investment: {e}")

@app.get("/api/economic/indicators")
async def get_economic_indicators():
    """Get comprehensive economic indicators."""
    try:
        if (hasattr(game, 'economic_state') and 
            hasattr(game.economic_state, 'get_economic_indicators')):
            return game.economic_state.get_economic_indicators()
        else:
            return {"error": "Economic indicators not available"}
    except Exception as e:
        return {"error": f"Error getting economic indicators: {e}"}

@app.get("/api/economic/history")
async def get_economic_history():
    """Get economic time series data for charts."""
    try:
        if not hasattr(game, 'economic_state'):
            return {"error": "Economic state not available"}
        
        economic_state = game.economic_state
        return {
            "gdp_history": getattr(economic_state, 'gdp_history', []),
            "inflation_history": getattr(economic_state, 'inflation_history', []),
            "money_supply_history": getattr(economic_state, 'm2_history', []),
            "employment_history": getattr(economic_state, 'employment_history', []),
            "velocity_history": getattr(economic_state, 'velocity_history', []),
            "interest_rate_history": getattr(economic_state, 'interest_rate_history', [])
        }
    except Exception as e:
        return {"error": f"Error getting economic history: {e}"}

@app.get("/api/financial/metrics")
async def get_financial_metrics():
    """Get detailed financial sector metrics."""
    try:
        if not hasattr(game, 'players'):
            return {"error": "Game players not available"}
        
        financial_player = game.players.get('financial')
        if not financial_player:
            return {"error": "Financial player not found"}
        
        return {
            "commercial_rate": getattr(financial_player, 'commercial_rate', 0.05),
            "fed_funds_rate": getattr(financial_player, 'fed_funds_rate', 0.025),
            "loans_outstanding": getattr(financial_player, 'loans_outstanding', 0.0),
            "deposits": getattr(financial_player, 'deposits', 0.0),
            "lending_capacity": (financial_player.calculate_lending_capacity() 
                               if hasattr(financial_player, 'calculate_lending_capacity') else 0.0),
            "new_money_created": getattr(financial_player, 'new_loans_this_turn', 0.0)
        }
    except Exception as e:
        return {"error": f"Error getting financial metrics: {e}"}

async def broadcast_game_state():
    """Send game state to all connected WebSocket clients with error handling."""
    if not active_connections:
        return
    
    try:
        game_state = game.get_state() if hasattr(game, 'get_state') else {"error": "Game state unavailable"}
        message = json.dumps(game_state, default=str)  # Handle non-serializable objects
        
        # Remove disconnected clients
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"WebSocket send error: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            active_connections.remove(connection)
    except Exception as e:
        print(f"Broadcast error: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates with error handling."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial state on connect
        try:
            initial_state = game.get_state() if hasattr(game, 'get_state') else {"error": "Game unavailable"}
            await websocket.send_text(json.dumps(initial_state, default=str))
        except Exception as e:
            await websocket.send_text(json.dumps({"error": f"Initial state error: {e}"}))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages or timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle client messages
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except json.JSONDecodeError:
                    pass  # Ignore invalid JSON
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "game_available": hasattr(game, 'get_state'),
        "current_turn": getattr(game, 'current_turn', 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
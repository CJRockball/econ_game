# core/game_engine.py

from typing import Dict, List
from .economic_state import EconomicState
from .turn_manager import TurnManager
from players.raw_materials import RawMaterialsPlayer
from players.manufacturing import ManufacturingPlayer
from players.services import ServicesPlayer
from players.consumer import ConsumerPlayer
from players.financial import FinancialPlayer
from players.government import GovernmentPlayer

class GameEngine:
    """
    Main game engine coordinating all players and game systems.
    """
    
    def __init__(self):
        self.economic_state = EconomicState()
        self.turn_manager = TurnManager()
        self.players = self._create_players()
        self.current_turn = 0
        
    def _create_players(self) -> Dict[str, object]:
        """Create all 6 player types."""
        return {
            'raw_materials': RawMaterialsPlayer("Raw Materials Co."),
            'manufacturing': ManufacturingPlayer("Manufacturing Corp."),
            'services': ServicesPlayer("Services Inc."),
            'consumer': ConsumerPlayer("Households"),
            'financial': FinancialPlayer("National Bank"),
            'government': GovernmentPlayer("Government")
        }
    
    def start_new_game(self):
        """Initialize a new game."""
        self.current_turn = 0
        self.economic_state.reset()
        for player in self.players.values():
            player.reset()
    
    def advance_turn(self):
        """Execute one complete turn."""
        # Execute all turn phases
        self.turn_manager.execute_turn(self.players)
        
        # Calculate total GDP for tax collection
        total_gdp = sum(player.production_value for player in self.players.values())
        
        # Government collects taxes
        self.players['government'].collect_taxes(total_gdp)
        
        # Update economic state
        self.economic_state.update(self.players)
        
        # Increment turn counter
        self.current_turn += 1
        
    def get_state(self) -> Dict:
        """Get current game state for API/UI."""
        return {
            'turn': self.current_turn,
            'gdp': self.economic_state.gdp,
            'inflation': self.economic_state.inflation_rate,
            'employment': self.economic_state.employment_rate,
            'players': {name: player.get_status() for name, player in self.players.items()}
        }
    
    def get_all_players(self) -> Dict:
        """Get all players for template rendering."""
        return {name: player.get_status() for name, player in self.players.items()}

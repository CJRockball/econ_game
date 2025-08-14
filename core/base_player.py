# core/base_player.py

from typing import Dict, Any

class BasePlayer:
    """
    Base class for all economic players with common attributes and methods.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.money = 10000.0  # Starting capital
        self.labor = 100.0    # Labor units available
        self.inventory = {}   # Goods inventory {good_type: quantity}
        self.production_value = 0.0  # Value of production this turn
        self.operating_costs = 0.0   # Costs incurred this turn
        
    def reset(self):
        """Reset player to initial state for new game."""
        self.money = 10000.0
        self.labor = 100.0
        self.inventory = {}
        self.production_value = 0.0
        self.operating_costs = 0.0
        
    def produce(self):
        """Override in subclasses - production logic."""
        pass
        
    def update_after_market(self):
        """Update state after market clearing."""
        # Apply operating costs
        self.money -= self.operating_costs
        self.operating_costs = 0.0
        
    def get_status(self) -> Dict[str, Any]:
        """Return current player status for UI."""
        return {
            'name': self.name,
            'money': self.money,
            'labor': self.labor,
            'inventory': self.inventory.copy(),
            'production_value': self.production_value
        }

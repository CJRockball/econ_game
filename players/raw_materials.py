# players/raw_materials.py

from core.base_player import BasePlayer

class RawMaterialsPlayer(BasePlayer):
    """
    Simplified Raw Materials Player - extracts basic resources.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.extraction_capacity = 100  # Maximum extraction per turn
        self.extraction_cost = 2.0      # Cost per unit extracted
        self.resource_price = 10.0      # Base price per unit
        
    def produce(self):
        """Extract raw materials based on capacity and labor."""
        # Production limited by labor and capacity
        production_amount = min(
            self.labor * 0.8,  # Labor efficiency factor
            self.extraction_capacity
        )
        
        # Only produce if we can afford operating costs
        total_cost = production_amount * self.extraction_cost
        if self.money >= total_cost:
            # Add to inventory
            self.inventory['raw_materials'] = self.inventory.get('raw_materials', 0) + production_amount
            
            # Calculate production value
            self.production_value = production_amount * self.resource_price
            self.operating_costs = total_cost
        else:
            # Can't afford full production
            affordable_production = self.money / self.extraction_cost
            self.inventory['raw_materials'] = self.inventory.get('raw_materials', 0) + affordable_production
            self.production_value = affordable_production * self.resource_price
            self.operating_costs = self.money  # Use all available money

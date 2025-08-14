# players/manufacturing.py

from core.base_player import BasePlayer

class ManufacturingPlayer(BasePlayer):
    """
    Simplified Manufacturing Player - converts raw materials to finished goods.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.production_capacity = 80
        self.raw_material_ratio = 1.2  # Raw materials needed per finished good
        self.production_cost = 3.0     # Labor/energy cost per unit
        self.finished_good_price = 20.0
        
    def produce(self):
        """Convert raw materials to finished goods."""
        # Check available raw materials (default to 0)
        available_raw = self.inventory.get('raw_materials', 0)
        
        # Production limited by raw materials, capacity, and labor
        max_production = min(
            available_raw / self.raw_material_ratio,
            self.production_capacity,
            self.labor * 0.6
        )
        
        # Calculate costs
        raw_material_used = max_production * self.raw_material_ratio
        total_cost = max_production * self.production_cost
        
        if self.money >= total_cost and available_raw > 0:
            # Only consume up to what's available
            actual_used = min(raw_material_used, available_raw)
            self.inventory['raw_materials'] = available_raw - actual_used
            
            # Produce finished goods
            self.inventory['finished_goods'] = self.inventory.get('finished_goods', 0) + max_production
            
            # Set costs and value
            self.production_value = max_production * self.finished_good_price
            self.operating_costs = total_cost
        else:
             # Cannot produce due to lack of money or raw materials
             self.production_value = 0.0
             self.operating_costs = 0.0

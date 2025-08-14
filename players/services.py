# players/services.py

from core.base_player import BasePlayer

class ServicesPlayer(BasePlayer):
    """
    Simplified Services Player - provides business and consumer services.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.service_capacity = 120
        self.service_cost = 1.5      # Cost per service unit
        self.service_price = 15.0    # Revenue per service unit
        
    def produce(self):
        """Provide services based on labor and capacity."""
        # Services production limited by labor and capacity
        service_production = min(
            self.labor * 1.0,  # Services are labor-intensive
            self.service_capacity
        )
        
        total_cost = service_production * self.service_cost
        
        if self.money >= total_cost:
            # Services are produced and consumed immediately (no inventory)
            self.production_value = service_production * self.service_price
            self.operating_costs = total_cost
        else:
            # Reduced service level
            affordable_services = self.money / self.service_cost
            self.production_value = affordable_services * self.service_price
            self.operating_costs = self.money

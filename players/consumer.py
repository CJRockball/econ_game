# players/consumer.py

from core.base_player import BasePlayer

class ConsumerPlayer(BasePlayer):
    """
    Simplified Consumer Player - represents household consumption demand.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.income_rate = 50.0      # Income per labor unit
        self.consumption_rate = 0.8  # Fraction of income consumed
        self.savings = 0.0           # Accumulated savings
        
    def produce(self):
        """Generate income from labor and determine consumption demand."""
        # Generate income from providing labor to other sectors
        labor_income = self.labor * self.income_rate
        total_income = labor_income + (self.savings * 0.02)  # 2% return on savings
        
        # Determine consumption spending
        consumption_spending = total_income * self.consumption_rate
        new_savings = total_income * (1 - self.consumption_rate)
        
        # Update money and savings
        self.money += labor_income
        self.savings += new_savings
        
        # Production value represents consumption demand in the economy
        self.production_value = consumption_spending
        
        # Consumers don't have operating costs in traditional sense
        self.operating_costs = 0.0
        
    def update_after_market(self):
        """Update after consuming goods and services."""
        # Consumers spend money on goods/services (simplified)
        consumption_amount = min(self.money * 0.7, self.production_value)
        self.money -= consumption_amount
        
        # Update inventory with consumed goods (for tracking)
        self.inventory['consumed_goods'] = self.inventory.get('consumed_goods', 0) + consumption_amount

# players/government.py

from core.base_player import BasePlayer

class GovernmentPlayer(BasePlayer):
    """
    Simplified Government Player - provides public services and regulation.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.tax_rate = 0.15         # 15% tax rate
        self.government_spending = 0.0
        self.public_debt = 0.0
        self.tax_revenue = 0.0
        
    def produce(self):
        """Provide government services and collect taxes."""
        # Government services based on spending capacity
        service_level = min(self.money * 0.8, self.labor * 20.0)
        
        # Government production value represents public services
        self.production_value = service_level
        self.operating_costs = service_level * 0.9  # 90% of service value as cost
        
    def collect_taxes(self, players_gdp: float):
        """Collect taxes based on total economic activity."""
        self.tax_revenue = players_gdp * self.tax_rate
        self.money += self.tax_revenue
        
    def government_spend(self, amount: float):
        """Government spending on public goods."""
        if self.money >= amount:
            self.money -= amount
            self.government_spending = amount
        else:
            # Deficit spending - increase debt
            deficit = amount - self.money
            self.public_debt += deficit
            self.money = 0
            self.government_spending = amount

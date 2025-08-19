from core.base_player import BasePlayer

class GovernmentPlayer(BasePlayer):
    """
    Enhanced Government Player with dynamic tax policy and public spending.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.tax_rate = 0.15  # 15% tax rate
        self.government_spending = 5000.0  # Base spending
        self.public_debt = 0.0
        self.budget_deficit = 0.0
        
        # Enhanced government capabilities
        self.infrastructure_investment = 0.0
        self.social_programs = 0.0
        self.defense_spending = 0.0
        
    def reset(self):
        """Reset to initial state."""
        super().reset()
        self.tax_rate = 0.15
        self.government_spending = 5000.0
        self.public_debt = 0.0
        self.budget_deficit = 0.0
        self.infrastructure_investment = 0.0
        self.social_programs = 0.0
        self.defense_spending = 0.0
        
    def collect_taxes(self, total_gdp: float):
        """Collect taxes based on economic activity."""
        tax_revenue = total_gdp * self.tax_rate
        self.money += tax_revenue
        
        # Track tax collection
        self.inventory['tax_revenue'] = self.inventory.get('tax_revenue', 0) + tax_revenue
        
    def produce(self):
        """Government production represents public goods and services."""
        # Government spending on various categories
        infrastructure_spend = min(self.money * 0.3, 1500)
        social_spend = min(self.money * 0.4, 2000) 
        defense_spend = min(self.money * 0.2, 1000)
        
        total_spending = infrastructure_spend + social_spend + defense_spend
        
        if self.money >= total_spending:
            self.money -= total_spending
            
            # Allocate spending
            self.infrastructure_investment += infrastructure_spend
            self.social_programs += social_spend
            self.defense_spending += defense_spend
            
            # Production value represents public goods provision
            self.production_value = total_spending
            self.operating_costs = total_spending
            
            # Government spending boosts productivity across economy
            infrastructure_effect = infrastructure_spend * 0.0001
            # This effect would be applied to other players in a full implementation
            
        else:
            self.production_value = self.money  # Spend whatever is available
            self.operating_costs = self.money
            self.money = 0
            
    def adjust_tax_rate(self, new_rate: float):
        """Adjust tax rate within reasonable bounds."""
        self.tax_rate = max(0.05, min(0.40, new_rate))  # 5% to 40% range
        
    def get_status(self) -> dict:
        """Enhanced status with government metrics."""
        status = super().get_status()
        status.update({
            'tax_rate': round(self.tax_rate * 100, 1),  # NEW: Show as percentage
            'government_spending': round(self.government_spending, 2),
            'public_debt': round(self.public_debt, 2),
            'budget_deficit': round(self.budget_deficit, 2),
            'infrastructure_investment': round(self.infrastructure_investment, 2),
            'social_programs': round(self.social_programs, 2),
            'defense_spending': round(self.defense_spending, 2),
            'tax_revenue_collected': round(self.inventory.get('tax_revenue', 0), 2)
        })
        return status
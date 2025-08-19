class BasePlayer:
    """
    Base class for all economic players with enhanced capabilities.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.money = 1000.0
        self.labor = 100.0
        self.technology_level = 1.0
        self.productivity_factor = 1.0
        self.production_value = 0.0
        self.operating_costs = 0.0
        self.inventory = {}
        self.borrowing_demand = 0.0
        self.loans_outstanding = 0.0
        self.credit_rating = 1.0
        self.rd_budget = 0.0
        self.investment_budget = 0.0
        
    def reset(self):
        """Reset player to initial state."""
        self.money = 1000.0
        self.labor = 100.0
        self.technology_level = 1.0
        self.productivity_factor = 1.0
        self.production_value = 0.0
        self.operating_costs = 0.0
        self.inventory.clear()
        self.borrowing_demand = 0.0
        self.loans_outstanding = 0.0
        self.credit_rating = 1.0
        self.rd_budget = 0.0
        self.investment_budget = 0.0
        
    def calculate_borrowing_need(self):
        """Calculate how much money player needs to borrow."""
        # Players borrow when money falls below operational threshold
        if self.money < 500:
            self.borrowing_demand = max(1000 - self.money, 0)
        else:
            self.borrowing_demand = 0
            
    def service_debt(self, interest_rate: float):
        """Service debt by paying interest and principal."""
        if self.loans_outstanding > 0:
            # Monthly payment: 5% principal + interest
            principal_payment = self.loans_outstanding * 0.05
            interest_payment = self.loans_outstanding * interest_rate
            total_payment = principal_payment + interest_payment
            
            if self.money >= total_payment:
                self.money -= total_payment
                self.loans_outstanding -= principal_payment
                # Update credit rating based on payment history
                self.credit_rating = min(1.0, self.credit_rating + 0.01)
            else:
                # Missed payment - credit rating deteriorates
                self.credit_rating *= 0.95
                
    def invest_in_technology(self, amount: float):
        """Invest in technology improvements."""
        if self.money >= amount:
            self.money -= amount
            tech_gain = amount * 0.0001  # Small but cumulative gains
            self.technology_level += tech_gain
            self.productivity_factor = self.technology_level
            self.rd_budget += amount
            
    def update_after_market(self):
        """Override in subclasses for post-market updates."""
        pass
        
    def get_status(self) -> dict:
        """FIXED: Get player status with properly formatted inventory."""
        # Format inventory with 0 decimal places
        formatted_inventory = {}
        for item, amount in self.inventory.items():
            if isinstance(amount, (int, float)) and item not in ['spent_last_turn', 'actual_purchases', 'forced_savings', 'wages_received', 'services_provided']:
                formatted_inventory[item] = int(amount)  # Round to 0 decimal places
            else:
                formatted_inventory[item] = round(amount, 2) if isinstance(amount, (int, float)) else amount
        
        return {
            'name': self.name,
            'money': round(self.money, 2),
            'labor': round(self.labor, 1),
            'technology_level': round(self.technology_level, 3),
            'productivity_factor': round(self.productivity_factor, 3),
            'production_value': round(self.production_value, 2),
            'operating_costs': round(self.operating_costs, 2),
            'inventory': formatted_inventory,
            'borrowing_demand': round(self.borrowing_demand, 2),
            'loans_outstanding': round(self.loans_outstanding, 2),
            'credit_rating': round(self.credit_rating, 3)
        }
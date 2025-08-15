from typing import Dict, Any
import random

class BasePlayer:
    """
    Enhanced base class for all economic players with all required methods.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.money = 10000.0  # Starting capital
        self.labor = 100.0    # Labor units available
        self.inventory = {}   # Goods inventory {good_type: quantity}
        self.production_value = 0.0  # Value of production this turn
        self.operating_costs = 0.0   # Costs incurred this turn
        
        # Enhanced economic attributes - ALL players have these
        self.technology_level = 1.0   # Technology productivity multiplier
        self.rd_budget = 0.0         # R&D spending this turn
        self.loans_outstanding = 0.0  # Money owed to banks
        self.debt_service = 0.0      # Interest payments this turn
        self.productivity_factor = 1.0  # Overall productivity
        
        # Financial attributes - ALL players have these
        self.credit_rating = 1.0     # Creditworthiness (0.5 to 1.5)
        self.borrowing_demand = 0.0  # Desired borrowing amount
        self.investment_budget = 0.0 # Capital investment spending
        
    def reset(self):
        """Reset player to initial state for new game."""
        self.money = 10000.0
        self.labor = 100.0
        self.inventory = {}
        self.production_value = 0.0
        self.operating_costs = 0.0
        self.technology_level = 1.0
        self.rd_budget = 0.0
        self.loans_outstanding = 0.0
        self.debt_service = 0.0
        self.productivity_factor = 1.0
        self.credit_rating = 1.0
        self.borrowing_demand = 0.0
        self.investment_budget = 0.0
        
    def invest_in_technology(self, amount: float):
        """Invest in R&D to improve technology level - REQUIRED METHOD."""
        if self.money >= amount and amount > 0:
            self.money -= amount
            self.rd_budget += amount
            # Technology improvement with diminishing returns
            tech_gain = amount * 0.001 * (2.0 - self.technology_level)
            self.technology_level += tech_gain
            self.productivity_factor = self.technology_level
            
    def calculate_borrowing_need(self):
        """Calculate how much the player wants to borrow - REQUIRED METHOD."""
        # Base borrowing on investment opportunities vs. available cash
        investment_opportunity = self.production_value * 0.5
        cash_available = max(0, self.money - 2000)  # Keep minimum cash buffer
        
        if investment_opportunity > cash_available:
            self.borrowing_demand = min(5000, investment_opportunity - cash_available)
        else:
            self.borrowing_demand = 0.0
            
    def service_debt(self, commercial_interest_rate: float):
        """Pay interest on outstanding loans - REQUIRED METHOD."""
        if self.loans_outstanding > 0:
            self.debt_service = self.loans_outstanding * commercial_interest_rate
            if self.money >= self.debt_service:
                self.money -= self.debt_service
            else:
                # Default risk - affects credit rating
                self.credit_rating = max(0.5, self.credit_rating * 0.9)
                self.debt_service = self.money
                self.money = 0.0
    
    def produce(self):
        """Override in subclasses - production logic."""
        pass
    
    def update_after_market(self):
        """Update state after market clearing - REQUIRED METHOD."""
        # Apply operating costs
        self.money = max(0, self.money - self.operating_costs)
        self.operating_costs = 0.0
        
        # Update credit rating based on financial health
        if self.production_value > 0:
            debt_to_income_ratio = self.loans_outstanding / self.production_value
            if debt_to_income_ratio < 1.0:
                self.credit_rating = min(1.5, self.credit_rating * 1.01)
            elif debt_to_income_ratio > 2.0:
                self.credit_rating = max(0.5, self.credit_rating * 0.99)
    
    def get_status(self) -> Dict[str, Any]:
        """Return current player status for UI - REQUIRED METHOD."""
        return {
            'name': self.name,
            'money': round(self.money, 2),
            'labor': self.labor,
            'inventory': self.inventory.copy(),
            'production_value': round(self.production_value, 2),
            'technology_level': round(self.technology_level, 3),
            'loans_outstanding': round(self.loans_outstanding, 2),
            'credit_rating': round(self.credit_rating, 3),
            'borrowing_demand': round(self.borrowing_demand, 2),
            'productivity_factor': round(self.productivity_factor, 3)
        }
from core.base_player import BasePlayer

class ConsumerPlayer(BasePlayer):
    """
    Enhanced Consumer Player with employment-responsive consumption.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.income_rate = 50.0  # Income per labor unit
        self.consumption_rate = 0.85  # INCREASED: Basic necessities require 85% of income
        self.savings = 0.0  # Accumulated savings
        self.consumption_confidence = 1.0  # Employment-based confidence factor
        
    def reset(self):
        """Reset player to initial state for new game."""
        super().reset()
        self.savings = 0.0
        self.consumption_confidence = 1.0
        
    def produce(self):
        """Generate income and determine consumption demand - Employment responsive."""
        # Generate income from providing labor to other sectors  
        labor_income = self.labor * self.income_rate
        savings_return = self.savings * 0.02  # 2% return on savings
        total_income = labor_income + savings_return
        
        # AI smooths consumption over turns to avoid wild spending swings
        # Employment confidence affects consumption propensity
        effective_consumption_rate = self.consumption_rate * self.consumption_confidence
        target_consume = total_income * effective_consumption_rate
        
        last_turn_spending = self.inventory.get('spent_last_turn', target_consume)
        
        # Smooth consumption: 70% weight on target, 30% on last turn
        consumption_demand = (target_consume * 0.7 + last_turn_spending * 0.3)
        
        # Update money with income only - NO SPENDING IN PRODUCE()
        self.money += labor_income
        
        # Update savings with unspent income
        self.savings += savings_return
        
        # Production value represents consumption DEMAND (not actual spending)
        self.production_value = consumption_demand
        
        # Consumers don't have operating costs in traditional sense  
        self.operating_costs = 0.0

    def update_after_market(self):
        """FIXED: Track actual spending from markets, no double-spending."""
        # Get actual spending from market transactions
        actual_spending = self.inventory.get('actual_purchases', 0)
        
        # Update spending tracking for next turn's smoothing
        self.inventory['spent_last_turn'] = actual_spending
        
        # Reset the purchase counter for next turn
        self.inventory['actual_purchases'] = 0
        
        # Update savings based on actual spending vs planned
        if actual_spending < self.production_value:
            # Consumer spent less than planned - increase savings
            forced_savings = self.production_value - actual_spending  
            self.savings += forced_savings
            self.inventory['forced_savings'] = self.inventory.get('forced_savings', 0) + forced_savings
        
        # NO MONEY DEDUCTION HERE - spending already happened in markets
        
    def get_status(self) -> dict:
        """Return enhanced consumer status including confidence."""
        status = super().get_status()
        
        # FIXED: Format inventory with 0 decimal places
        formatted_inventory = {}
        for item, amount in status.get('inventory', {}).items():
            if isinstance(amount, (int, float)):
                formatted_inventory[item] = int(amount)  # Round to 0 decimal places
            else:
                formatted_inventory[item] = amount
        
        status.update({
            'inventory': formatted_inventory,  # Override with formatted version
            'savings': round(self.savings, 2),
            'consumption_rate': self.consumption_rate,
            'consumption_confidence': round(self.consumption_confidence, 3),
            'effective_consumption_rate': round(self.consumption_rate * self.consumption_confidence, 3),
            'last_turn_spending': round(self.inventory.get('spent_last_turn', 0), 2),
            'planned_consumption': round(self.production_value, 2),
            'current_unit_wage': round(self.income_rate, 2)  # NEW: Show unit wage
        })
        return status
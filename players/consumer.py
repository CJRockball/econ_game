from core.base_player import BasePlayer

class ConsumerPlayer(BasePlayer):
    """
    FIXED Consumer Player - eliminates double-spending, uses actual market purchases.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.income_rate = 50.0  # Income per labor unit
        self.consumption_rate = 0.7  # Fraction of income consumed
        self.savings = 0.0  # Accumulated savings
        
    def reset(self):
        """Reset player to initial state for new game."""
        super().reset()
        self.savings = 0.0
        
    def produce(self):
        """Generate income and determine consumption demand - NO SPENDING HERE."""
        # Generate income from providing labor to other sectors  
        labor_income = self.labor * self.income_rate
        savings_return = self.savings * 0.02  # 2% return on savings
        total_income = labor_income + savings_return
        
        # AI smooths consumption over turns to avoid wild spending swings
        target_consume = total_income * self.consumption_rate
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
        
        # Update savings based on actual spending vs income
        if actual_spending < self.production_value:
            # Consumer spent less than planned - increase savings
            forced_savings = self.production_value - actual_spending  
            self.savings += forced_savings
            self.inventory['forced_savings'] = self.inventory.get('forced_savings', 0) + forced_savings
        
        # NO MONEY DEDUCTION HERE - spending already happened in markets
        
    def get_status(self) -> dict:
        """Return enhanced consumer status including savings."""
        status = super().get_status()
        status.update({
            'savings': round(self.savings, 2),
            'consumption_rate': self.consumption_rate,
            'last_turn_spending': round(self.inventory.get('spent_last_turn', 0), 2),
            'planned_consumption': round(self.production_value, 2)
        })
        return status
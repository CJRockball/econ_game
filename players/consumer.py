# players/consumer.py

from core.base_player import BasePlayer

class ConsumerPlayer(BasePlayer):
    """
    Enhanced Consumer Player with improved AI for more realistic spending behavior.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.income_rate = 50.0      # Income per labor unit
        self.consumption_rate = 0.7  # Fraction of income consumed (reduced from 0.8)
        self.savings = 0.0           # Accumulated savings
        
    def reset(self):
        """Reset player to initial state for new game."""
        super().reset()
        self.savings = 0.0
        
    def produce(self):
        """Generate income from labor and determine consumption demand with AI smoothing."""
        # Generate income from providing labor to other sectors
        labor_income = self.labor * self.income_rate
        total_income = labor_income + (self.savings * 0.02)  # 2% return on savings
        
        # AI smooths consumption over 3 turns to avoid wild spending swings
        target_consume = total_income * self.consumption_rate
        last_turn_spending = self.inventory.get('spent_last_turn', target_consume)
        
        # Smooth consumption: 2/3 weight on last turn, 1/3 on target
        consumption_spending = (last_turn_spending * 2 + target_consume) / 3
        
        # Calculate new savings
        new_savings = total_income - consumption_spending
        
        # Update money and savings
        self.money += labor_income
        self.savings += new_savings
        
        # Production value represents consumption demand in the economy
        self.production_value = consumption_spending
        
        # Consumers don't have operating costs in traditional sense
        self.operating_costs = 0.0
        
    def update_after_market(self):
        """Update after consuming goods and services with AI spending buffer."""
        # AI spends up to 80% of planned consumption but buffers 20% for stability
        max_affordable = self.money * 0.8
        planned_consumption = self.production_value
        
        # Actual consumption is limited by both affordability and planning
        consumption_amount = min(max_affordable, planned_consumption)
        
        # Execute spending
        self.money -= consumption_amount
        
        # Track spending for next turn's AI smoothing
        self.inventory['spent_last_turn'] = consumption_amount
        
        # Update inventory with consumed goods (for tracking)
        self.inventory['consumed_goods'] = self.inventory.get('consumed_goods', 0) + consumption_amount
        
        # Track cumulative savings for economic indicators
        if consumption_amount < planned_consumption:
            # Consumer saved more than planned due to liquidity constraints
            forced_savings = planned_consumption - consumption_amount
            self.savings += forced_savings
            self.inventory['forced_savings'] = self.inventory.get('forced_savings', 0) + forced_savings
    
    def get_status(self) -> dict:
        """Return enhanced consumer status including savings."""
        status = super().get_status()
        status['savings'] = self.savings
        status['consumption_rate'] = self.consumption_rate
        return status

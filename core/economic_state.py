# core/economic_state.py

class EconomicState:
    def __init__(self):
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 100.0
        self.money_supply = 1000000.0
        self.previous_gdp = 0.0
        self.turn_count = 0
        
    def reset(self):
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 100.0
        self.previous_gdp = 0.0
        self.turn_count = 0
        
    def update(self, players):
        self.turn_count += 1
        
        # Store previous GDP
        self.previous_gdp = self.gdp
        
        # Calculate new GDP as sum of all production values
        self.gdp = sum(player.production_value for player in players.values())
        
        # Calculate inflation based on GDP growth and money supply changes
        if self.previous_gdp > 0:
            gdp_growth = (self.gdp - self.previous_gdp) / self.previous_gdp
            
            # Simple inflation model: faster growth = higher inflation
            base_inflation = gdp_growth * 0.3
            
            # Add some randomness and economic cycle effects
            import random
            cycle_effect = random.uniform(-0.02, 0.02)
            
            self.inflation_rate = max(0, min(0.1, base_inflation + cycle_effect))
        else:
            self.inflation_rate = 0.0
            
        # Employment based on economic activity (simplified)
        if self.gdp > 0:
            activity_factor = min(1.0, self.gdp / 10000)  # Normalize to reasonable range
            self.employment_rate = 85 + (activity_factor * 15)  # 85-100% employment
        else:
            self.employment_rate = 85.0

# core/economic_state.py - REPLACE ENTIRELY
import random

class EconomicState:
    def __init__(self):
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 95.0
        self.money_supply = 1000000.0
        self.previous_gdp = 0.0
        self.turn_count = 0
        self.gdp_history = []
        self.inflation_history = []
        
    def reset(self):
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 95.0
        self.previous_gdp = 0.0
        self.turn_count = 0
        self.gdp_history = []
        self.inflation_history = []
        
    def update(self, players):
        self.turn_count += 1
        
        # Store previous GDP
        self.previous_gdp = self.gdp
        
        # Calculate new GDP as sum of all production values
        self.gdp = sum(player.production_value for player in players.values())
        
        # Store GDP history
        self.gdp_history.append(self.gdp)
        
        # Calculate inflation based on GDP growth
        if self.previous_gdp > 0 and self.gdp > 0:
            gdp_growth = (self.gdp - self.previous_gdp) / self.previous_gdp
            # Inflation responds to growth with some lag and randomness
            base_inflation = gdp_growth * 0.4
            cycle_effect = random.uniform(-0.015, 0.015)
            self.inflation_rate = max(-0.02, min(0.08, base_inflation + cycle_effect))
        else:
            self.inflation_rate = random.uniform(-0.005, 0.005)  # Small random variation
            
        self.inflation_history.append(self.inflation_rate)
        
        # Employment based on economic activity
        if self.gdp > 0:
            activity_factor = min(1.0, self.gdp / 15000)
            self.employment_rate = 80 + (activity_factor * 20)  # 80-100% employment
        else:
            self.employment_rate = max(75, self.employment_rate - 2)  # Gradual decline

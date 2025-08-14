class EconomicState:
    def __init__(self):
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 100.0  # Simplified - no unemployment
        self.money_supply = 1000000.0  # Fixed money supply initially
        self.previous_gdp = 0.0
        
    def reset(self):
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 100.0
        
    def update(self, players):
        # Calculate GDP as sum of all production
        self.previous_gdp = self.gdp
        self.gdp = sum(player.production_value for player in players.values())
        
        # Simple inflation calculation
        if self.previous_gdp > 0:
            gdp_growth = (self.gdp - self.previous_gdp) / self.previous_gdp
            self.inflation_rate = max(0, gdp_growth * 0.5)  # Simplified relationship

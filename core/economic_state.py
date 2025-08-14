# core/economic_state.py

import random

class EconomicState:
    def __init__(self):
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 95.0
        self.money_supply = 1_000_000.0
        self.previous_gdp = 0.0
        self.turn_count = 0
        self.gdp_history = []
        self.m2_history = []
        self.inflation_history = []

    def reset(self):
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 95.0
        self.money_supply = 1_000_000.0
        self.previous_gdp = 0.0
        self.turn_count = 0
        self.gdp_history.clear()
        self.m2_history.clear()
        self.inflation_history.clear()

    def update(self, players):
        self.turn_count += 1
        self.previous_gdp = self.gdp
        self.gdp = sum(p.production_value for p in players.values())
        self.gdp_history.append(self.gdp)

        total_loans = sum(getattr(p, 'loans_outstanding', 0) for p in players.values())
        m2_growth = total_loans * 0.01
        self.money_supply += m2_growth
        self.m2_history.append(self.money_supply)

        if self.previous_gdp > 0:
            gdp_growth = (self.gdp - self.previous_gdp) / self.previous_gdp
            base_inflation = gdp_growth * 0.4
            cycle = random.uniform(-0.015, 0.015)
            self.inflation_rate = max(-0.02, min(0.08, base_inflation + cycle))
        else:
            self.inflation_rate = random.uniform(-0.005, 0.005)
        self.inflation_history.append(self.inflation_rate)

        if self.gdp > 0:
            factor = min(1.0, self.gdp / 15000)
            self.employment_rate = 80 + factor * 20
        else:
            self.employment_rate = max(75, self.employment_rate - 2)

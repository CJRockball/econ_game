from core.base_player import BasePlayer
import random

class RawMaterialsPlayer(BasePlayer):
    """
    Enhanced Raw Materials Player with dynamic pricing, technology investment,
    and resource management.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.extraction_capacity = 100
        self.extraction_cost = 2.0
        self.resource_price = 10.0  # Base price for production value calculation
        
        # Dynamic market pricing (set by market clearing)
        self.current_price = 8.0  # Current market price
        
        # Enhanced attributes
        self.resource_reserves = 10000.0  # Finite resource base
        self.depletion_rate = 0.001  # Resource depletion per unit extracted
        self.environmental_cost = 0.0  # Environmental compliance costs
        self.exploration_budget = 0.0  # Investment in finding new reserves
        
        # Extraction efficiency factors
        self.extraction_efficiency = 1.0
        self.environmental_compliance = 1.0
        
    def reset(self):
        """Reset to enhanced initial state."""
        super().reset()
        self.current_price = 8.0
        self.resource_reserves = 10000.0
        self.depletion_rate = 0.001
        self.environmental_cost = 0.0
        self.exploration_budget = 0.0
        self.extraction_efficiency = 1.0
        self.environmental_compliance = 1.0
        
    def invest_in_exploration(self, amount: float):
        """Invest in finding new resource reserves."""
        if self.money >= amount:
            self.money -= amount
            self.exploration_budget += amount
            # Exploration success with diminishing returns
            new_reserves = amount * random.uniform(0.5, 2.0)  # Uncertain returns
            self.resource_reserves += new_reserves
            
    def invest_in_extraction_efficiency(self, amount: float):
        """Invest in extraction technology."""
        if self.money >= amount:
            self.money -= amount
            efficiency_gain = amount * 0.0006
            self.extraction_efficiency += efficiency_gain
            self.productivity_factor = self.extraction_efficiency * self.technology_level

    def produce(self):
        """Enhanced resource extraction with technology and depletion."""
        # Production affected by technology, efficiency, and depletion
        tech_efficiency = self.technology_level * self.extraction_efficiency
        depletion_factor = max(0.5, 1.0 - (10000.0 - self.resource_reserves) * 0.00005)
        
        # Effective capacity considering all factors
        effective_capacity = (self.extraction_capacity * tech_efficiency * 
                            depletion_factor * self.productivity_factor)
        
        # Production limited by labor, capacity, and reserves
        max_production = min(
            self.labor * 0.8,
            effective_capacity,
            self.resource_reserves * 0.1  # Can't extract more than 10% of reserves per turn
        )
        
        # Variable extraction cost based on technology and depletion
        unit_cost = self.extraction_cost / (tech_efficiency * depletion_factor)
        
        # Environmental compliance costs
        self.environmental_cost = max_production * 0.5 * self.environmental_compliance
        total_unit_cost = unit_cost + (self.environmental_cost / max_production if max_production > 0 else 0)
        total_cost = max_production * total_unit_cost
        
        if self.money >= total_cost and max_production > 0:
            # Successful production
            production_amount = max_production
            self.inventory['raw_materials'] = self.inventory.get('raw_materials', 0) + production_amount
            
            # Deplete reserves
            self.resource_reserves -= production_amount * self.depletion_rate
            
            # Production value calculation using expected market price
            expected_price = (self.resource_price + self.current_price) / 2
            quality_premium = 1.0 + (self.technology_level - 1.0) * 0.2
            efficiency_premium = 1.0 + (self.extraction_efficiency - 1.0) * 0.15
            
            unit_value = expected_price * quality_premium * efficiency_premium
            self.production_value = production_amount * unit_value
            self.operating_costs = total_cost
            
            # Automatic exploration investment if reserves are low
            if self.resource_reserves < 5000 and self.money > 1000:
                exploration_investment = min(self.money * 0.1, 500)
                self.invest_in_exploration(exploration_investment)
                
            # Automatic efficiency investment if profitable
            if self.production_value > self.operating_costs * 1.4:  # 40% margin
                profit = self.production_value - self.operating_costs
                efficiency_investment = min(profit * 0.12, self.money * 0.06)
                if efficiency_investment > 100:
                    self.invest_in_extraction_efficiency(efficiency_investment)
                    
        else:
            # Constrained production
            affordable_production = min(max_production, self.money / total_unit_cost) if total_unit_cost > 0 else 0
            if affordable_production > 0:
                self.inventory['raw_materials'] = self.inventory.get('raw_materials', 0) + affordable_production
                self.resource_reserves -= affordable_production * self.depletion_rate
                self.production_value = affordable_production * self.resource_price
                self.operating_costs = self.money
            else:
                self.production_value = 0.0
                self.operating_costs = 0.0
    
    def get_status(self):
        """Enhanced status with resource management data."""
        status = super().get_status()
        status.update({
            'resource_reserves': round(self.resource_reserves, 2),
            'depletion_rate': self.depletion_rate,
            'environmental_cost': round(self.environmental_cost, 2),
            'exploration_budget': round(self.exploration_budget, 2),
            'extraction_efficiency': round(self.extraction_efficiency, 3),
            'overall_efficiency': round(self.technology_level * self.extraction_efficiency, 3),
            'current_price': round(getattr(self, 'current_price', 8.0), 2)
        })
        return status
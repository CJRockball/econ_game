from core.base_player import BasePlayer
import random

class RawMaterialsPlayer(BasePlayer):
    """
    Enhanced Raw Materials Player with technology investment,
    productivity improvements, and economic cycles.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.extraction_capacity = 100
        self.extraction_cost = 2.0
        self.resource_price = 10.0
        
        # Enhanced attributes
        self.resource_reserves = 10000.0  # Finite resource base
        self.depletion_rate = 0.001      # Resource depletion per unit extracted
        self.environmental_cost = 0.0    # Environmental compliance costs
        self.exploration_budget = 0.0    # Investment in finding new reserves
        
    def reset(self):
        """Reset to enhanced initial state."""
        super().reset()
        self.resource_reserves = 10000.0
        self.depletion_rate = 0.001
        self.environmental_cost = 0.0
        self.exploration_budget = 0.0
    
    def invest_in_exploration(self, amount: float):
        """Invest in finding new resource reserves."""
        if self.money >= amount:
            self.money -= amount
            self.exploration_budget += amount
            # Exploration success with diminishing returns
            new_reserves = amount * random.uniform(0.5, 2.0)  # Uncertain returns
            self.resource_reserves += new_reserves
            
    def produce(self):
        """Enhanced resource extraction with technology and depletion."""
        # Production affected by technology and depletion
        tech_efficiency = self.technology_level
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
        total_cost = max_production * unit_cost
        
        # Environmental compliance costs
        self.environmental_cost = max_production * 0.5
        total_cost += self.environmental_cost
        
        if self.money >= total_cost and max_production > 0:
            # Successful production
            production_amount = max_production
            self.inventory['raw_materials'] = self.inventory.get('raw_materials', 0) + production_amount
            
            # Deplete reserves
            self.resource_reserves -= production_amount * self.depletion_rate
            
            # Variable pricing based on market conditions and quality
            quality_premium = 1.0 + (self.technology_level - 1.0) * 0.2
            self.production_value = production_amount * self.resource_price * quality_premium
            self.operating_costs = total_cost
            
            # Automatic exploration investment if reserves are low
            if self.resource_reserves < 5000 and self.money > 1000:
                exploration_investment = min(self.money * 0.1, 500)
                self.invest_in_exploration(exploration_investment)
                
        else:
            # Constrained production
            affordable_production = min(max_production, self.money / (unit_cost + 0.5))
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
            'extraction_efficiency': round(self.technology_level * self.productivity_factor, 3)
        })
        return status
'''

# Enhanced Manufacturing Player
manufacturing_enhanced = '''# players/manufacturing.py

from core.base_player import BasePlayer
import random

class ManufacturingPlayer(BasePlayer):
    """
    Enhanced Manufacturing Player with supply chain management,
    quality control, and technology integration.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.production_capacity = 80
        self.raw_material_ratio = 1.2
        self.production_cost = 3.0
        self.finished_good_price = 20.0
        
        # Enhanced manufacturing capabilities
        self.quality_level = 1.0         # Product quality multiplier
        self.automation_level = 1.0      # Automation reduces labor needs
        self.supply_chain_efficiency = 1.0  # Raw material usage efficiency
        self.inventory_management = 1.0   # Reduces holding costs
        self.product_innovation = 0.0    # New product development
        
    def reset(self):
        """Reset to enhanced initial state."""
        super().reset()
        self.quality_level = 1.0
        self.automation_level = 1.0
        self.supply_chain_efficiency = 1.0
        self.inventory_management = 1.0
        self.product_innovation = 0.0
    
    def invest_in_automation(self, amount: float):
        """Invest in automation technology."""
        if self.money >= amount:
            self.money -= amount
            automation_gain = amount * 0.0005
            self.automation_level += automation_gain
            self.productivity_factor = self.automation_level * self.technology_level
            
    def invest_in_quality(self, amount: float):
        """Invest in quality improvements."""
        if self.money >= amount:
            self.money -= amount
            quality_gain = amount * 0.0008
            self.quality_level += quality_gain
    
    def produce(self):
        """Enhanced manufacturing with quality and efficiency considerations."""
        available_raw = self.inventory.get('raw_materials', 0)
        
        if available_raw <= 0:
            self.production_value = 0.0
            self.operating_costs = 0.0
            return
        
        # Enhanced production calculation
        # Technology reduces raw material needs and labor requirements
        effective_ratio = self.raw_material_ratio / (self.supply_chain_efficiency * self.technology_level)
        labor_efficiency = self.automation_level * self.productivity_factor
        
        # Production constraints
        raw_material_constraint = available_raw / effective_ratio
        capacity_constraint = self.production_capacity * self.technology_level
        labor_constraint = self.labor * 0.6 * labor_efficiency
        
        max_production = min(raw_material_constraint, capacity_constraint, labor_constraint)
        
        # Variable production costs
        base_cost = self.production_cost / self.automation_level  # Automation reduces costs
        quality_cost = self.quality_level * 0.5  # Higher quality costs more
        total_unit_cost = base_cost + quality_cost
        
        total_cost = max_production * total_unit_cost
        
        if self.money >= total_cost and max_production > 0:
            # Successful production
            raw_used = max_production * effective_ratio
            self.inventory['raw_materials'] -= raw_used
            
            production_amount = max_production
            self.inventory['finished_goods'] = self.inventory.get('finished_goods', 0) + production_amount
            
            # Enhanced pricing with quality premium
            quality_premium = 1.0 + (self.quality_level - 1.0) * 0.3
            tech_premium = 1.0 + (self.technology_level - 1.0) * 0.1
            
            unit_price = self.finished_good_price * quality_premium * tech_premium
            self.production_value = production_amount * unit_price
            self.operating_costs = total_cost
            
            # Automatic quality investments if profitable
            if self.production_value > self.operating_costs * 1.2:  # 20% margin
                profit = self.production_value - self.operating_costs
                quality_investment = min(profit * 0.1, self.money * 0.05)
                if quality_investment > 100:
                    self.invest_in_quality(quality_investment)
                    
        else:
            # Constrained production
            affordable_production = min(max_production, self.money / total_unit_cost)
            if affordable_production > 0:
                raw_used = affordable_production * effective_ratio
                self.inventory['raw_materials'] -= raw_used
                self.inventory['finished_goods'] = self.inventory.get('finished_goods', 0) + affordable_production
                
                self.production_value = affordable_production * self.finished_good_price
                self.operating_costs = self.money
            else:
                self.production_value = 0.0
                self.operating_costs = 0.0
    
    def get_status(self):
        """Enhanced status with manufacturing metrics."""
        status = super().get_status()
        status.update({
            'quality_level': round(self.quality_level, 3),
            'automation_level': round(self.automation_level, 3),
            'supply_chain_efficiency': round(self.supply_chain_efficiency, 3),
            'manufacturing_efficiency': round(self.automation_level * self.technology_level, 3)
        })
        return status
from core.base_player import BasePlayer

class ManufacturingPlayer(BasePlayer):
    """
    Enhanced Manufacturing Player with persistent pricing and improved production.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.production_capacity = 80
        self.raw_material_ratio = 1.2  # Raw materials needed per finished good
        self.production_cost = 3.0  # Labor/energy cost per unit
        self.finished_good_price = 20.0  # Base price for production value calculation
        
        # Dynamic market pricing (set by market clearing)
        self.current_price = 18.0  # Current market price
        
        # Enhanced manufacturing capabilities
        self.quality_level = 1.0  # Product quality multiplier
        self.automation_level = 1.0  # Automation reduces labor needs
        self.supply_chain_efficiency = 1.0  # Raw material usage efficiency
        
    def reset(self):
        """Reset to enhanced initial state."""
        super().reset()
        self.current_price = 18.0
        self.quality_level = 1.0
        self.automation_level = 1.0
        self.supply_chain_efficiency = 1.0
        
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
        # Check available raw materials
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
            
            # Production value calculation using current market expectations
            # Use expected price (combination of base price and current market price)
            expected_price = (self.finished_good_price + self.current_price) / 2
            quality_premium = 1.0 + (self.quality_level - 1.0) * 0.3
            tech_premium = 1.0 + (self.technology_level - 1.0) * 0.1
            
            unit_value = expected_price * quality_premium * tech_premium
            self.production_value = production_amount * unit_value
            self.operating_costs = total_cost
            
            # Automatic quality investments if profitable
            if self.production_value > self.operating_costs * 1.3:  # 30% margin
                profit = self.production_value - self.operating_costs
                quality_investment = min(profit * 0.1, self.money * 0.05)
                if quality_investment > 100:
                    self.invest_in_quality(quality_investment)
                    
        else:
            # Constrained production
            affordable_production = min(max_production, self.money / total_unit_cost) if total_unit_cost > 0 else 0
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
            'manufacturing_efficiency': round(self.automation_level * self.technology_level, 3),
            'current_price': round(getattr(self, 'current_price', 18.0), 2)
        })
        return status
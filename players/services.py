from core.base_player import BasePlayer

class ServicesPlayer(BasePlayer):
    """
    Enhanced Services Player with dynamic pricing and improved service delivery.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.service_capacity = 120
        self.service_cost = 1.5  # Cost per service unit
        self.service_price = 15.0  # Base price for production value calculation
        
        # Dynamic market pricing (set by market clearing)
        self.current_price = 15.0  # Current market price
        
        # Service quality and efficiency
        self.service_quality = 1.0
        self.digital_efficiency = 1.0  # Technology factor for services
        
    def reset(self):
        """Reset to initial state."""
        super().reset()
        self.current_price = 15.0
        self.service_quality = 1.0
        self.digital_efficiency = 1.0
        
    def invest_in_digital_systems(self, amount: float):
        """Invest in digital systems to improve efficiency."""
        if self.money >= amount:
            self.money -= amount
            efficiency_gain = amount * 0.0008
            self.digital_efficiency += efficiency_gain
            self.productivity_factor = self.digital_efficiency * self.technology_level

    def produce(self):
        """Enhanced service production with technology and quality factors."""
        # Services production limited by labor, capacity, and technology
        tech_capacity_multiplier = self.technology_level * self.digital_efficiency
        effective_capacity = self.service_capacity * tech_capacity_multiplier
        
        service_production = min(
            self.labor * 1.2 * self.productivity_factor,  # Services are labor-intensive
            effective_capacity
        )
        
        # Variable costs based on quality and efficiency
        unit_cost = self.service_cost / self.digital_efficiency  # Technology reduces costs
        quality_cost = self.service_quality * 0.3  # Higher quality services cost more
        total_unit_cost = unit_cost + quality_cost
        
        total_cost = service_production * total_unit_cost
        
        if self.money >= total_cost and service_production > 0:
            # Services are produced and ready for market
            # Production value calculation using expected market price
            expected_price = (self.service_price + self.current_price) / 2
            quality_premium = 1.0 + (self.service_quality - 1.0) * 0.25
            tech_premium = 1.0 + (self.technology_level - 1.0) * 0.15
            
            unit_value = expected_price * quality_premium * tech_premium
            self.production_value = service_production * unit_value
            self.operating_costs = total_cost
            
            # Store service capacity for market clearing
            self.inventory['service_capacity'] = service_production
            
            # Automatic digital investments if profitable
            if self.production_value > self.operating_costs * 1.25:  # 25% margin
                profit = self.production_value - self.operating_costs
                digital_investment = min(profit * 0.08, self.money * 0.04)
                if digital_investment > 100:
                    self.invest_in_digital_systems(digital_investment)
                    
        else:
            # Reduced service level due to budget constraints
            affordable_services = self.money / total_unit_cost if total_unit_cost > 0 else 0
            if affordable_services > 0:
                self.production_value = affordable_services * self.service_price
                self.operating_costs = self.money
                self.inventory['service_capacity'] = affordable_services
            else:
                self.production_value = 0.0
                self.operating_costs = 0.0
                self.inventory['service_capacity'] = 0.0
    
    def get_status(self):
        """Enhanced status with service metrics."""
        status = super().get_status()
        status.update({
            'service_quality': round(self.service_quality, 3),
            'digital_efficiency': round(self.digital_efficiency, 3),
            'service_efficiency': round(self.digital_efficiency * self.technology_level, 3),
            'current_price': round(getattr(self, 'current_price', 15.0), 2),
            'service_capacity': round(self.inventory.get('service_capacity', 0), 1)
        })
        return status
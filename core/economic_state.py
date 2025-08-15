import random
from typing import Dict

class EconomicState:
    """
    Enhanced Economic State with transaction-based inflation calculation.
    """
    
    def __init__(self):
        # Core economic indicators
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 95.0
        self.money_supply = 100_000.0  # M2 money supply
        self.previous_gdp = 0.0
        self.turn_count = 0
        
        # Velocity of money (MV = PY)
        self.money_velocity = 2.0  # How many times money changes hands
        self.previous_money_supply = 100_000.0
        
        # Historical tracking - ALL these arrays exist
        self.gdp_history = []
        self.m2_history = []
        self.inflation_history = []
        self.employment_history = []
        self.velocity_history = []
        self.interest_rate_history = []
        
        # Economic components
        self.consumption = 0.0
        self.investment = 0.0
        self.government_spending = 0.0
        self.net_exports = 0.0
        
        # PRICE LEVEL TRACKING - Key for inflation
        self.price_level = 100.0  # Base price index = 100
        self.previous_price_level = 100.0
        self.price_history = []
        
        # Consumer Price Index components
        self.cpi_basket = {
            'finished_goods': 0.6,    # 60% weight
            'services': 0.3,          # 30% weight  
            'raw_materials': 0.1      # 10% weight
        }
        self.last_prices = {
            'finished_goods': 18.0,
            'services': 15.0,
            'raw_materials': 8.0
        }
        
        # New money created this turn
        self.new_money_created = 0.0
        
    def reset(self):
        """Reset economic state to initial conditions."""
        self.gdp = 0.0
        self.inflation_rate = 0.0
        self.employment_rate = 95.0
        self.money_supply = 100_000.0
        self.previous_gdp = 0.0
        self.turn_count = 0
        self.money_velocity = 2.0
        self.previous_money_supply = 100_000.0
        self.price_level = 100.0
        self.previous_price_level = 100.0
        self.new_money_created = 0.0
        
        # Reset last prices to defaults
        self.last_prices = {
            'finished_goods': 18.0,
            'services': 15.0,
            'raw_materials': 8.0
        }
        
        # Clear all histories
        self.gdp_history.clear()
        self.m2_history.clear()
        self.inflation_history.clear()
        self.employment_history.clear()
        self.velocity_history.clear()
        self.interest_rate_history.clear()
        self.price_history.clear()
        
    def calculate_money_velocity(self) -> float:
        """Calculate velocity of money: V = GDP / M2"""
        if self.money_supply > 0:
            return self.gdp / self.money_supply
        return 2.0  # Default velocity
    
    def update_money_supply(self, players: Dict):
        """Update money supply based on new loan creation - SAFE ACCESS."""
        # Track new money created through bank lending
        financial_player = players.get('financial')
        if financial_player:
            self.new_money_created = getattr(financial_player, 'new_loans_this_turn', 0.0)
            
            # Money supply grows by new loans created
            self.previous_money_supply = self.money_supply
            self.money_supply += self.new_money_created
            
            # Money supply also affected by loan repayments (simplified)
            loans_outstanding = getattr(financial_player, 'loans_outstanding', 0.0)
            loan_repayments = loans_outstanding * 0.05  # 5% repayment rate
            self.money_supply = max(50000, self.money_supply - loan_repayments)
        else:
            self.previous_money_supply = self.money_supply
    
    def calculate_transaction_based_inflation(self, turn_manager):
        """Calculate inflation using actual transaction prices (CPI approach)."""
        # Get transaction prices from turn manager
        if hasattr(turn_manager, 'get_transaction_prices'):
            transaction_prices = turn_manager.get_transaction_prices()
        else:
            transaction_prices = {}
        
        # Update last known prices with actual transactions
        for good_type, price in transaction_prices.items():
            if good_type in self.last_prices:
                self.last_prices[good_type] = price
        
        # Calculate weighted price index (CPI)
        self.previous_price_level = self.price_level
        
        current_index = 0.0
        for good_type, weight in self.cpi_basket.items():
            if good_type in self.last_prices:
                # Normalize to base price for index calculation
                base_price = {'finished_goods': 18.0, 'services': 15.0, 'raw_materials': 8.0}[good_type]
                price_ratio = self.last_prices[good_type] / base_price
                current_index += weight * price_ratio * 100
        
        # Update price level
        if current_index > 0:
            # Smooth price level adjustment to avoid volatility
            adjustment_speed = 0.6
            self.price_level = (self.price_level * (1 - adjustment_speed) + 
                              current_index * adjustment_speed)
        
        # Calculate inflation rate
        if self.previous_price_level > 0:
            self.inflation_rate = (self.price_level - self.previous_price_level) / self.previous_price_level
        else:
            self.inflation_rate = 0.0
        
        # Add small economic noise but keep bounded
        noise = random.uniform(-0.002, 0.002)
        self.inflation_rate = max(-0.05, min(0.15, self.inflation_rate + noise))
    
    def calculate_inflation_mv_py_fallback(self):
        """Fallback inflation calculation using MV = PY if no transactions."""
        # Calculate money velocity
        self.money_velocity = self.calculate_money_velocity()
        
        # MV = PY, so P = MV/Y
        if self.gdp > 0:
            # Theoretical price level from quantity equation  
            theoretical_price_level = (self.money_supply * self.money_velocity) / self.gdp * 10  # Scale factor
            
            # Smooth price level adjustment
            adjustment_speed = 0.3
            self.previous_price_level = self.price_level
            self.price_level = (self.price_level * (1 - adjustment_speed) + 
                              theoretical_price_level * adjustment_speed)
            
            # Inflation is the rate of change in price level
            if self.previous_price_level > 0:
                self.inflation_rate = (self.price_level - self.previous_price_level) / self.previous_price_level
            else:
                self.inflation_rate = 0.0
        else:
            self.inflation_rate = 0.0
            
        # Add some economic noise and bounded inflation
        noise = random.uniform(-0.005, 0.005)
        self.inflation_rate = max(-0.03, min(0.10, self.inflation_rate + noise))
    
    def update_gdp_components(self, players: Dict):
        """Calculate GDP components: C + I + G + (X-M) - SAFE ACCESS."""
        # Consumption (from consumer player)
        consumer_player = players.get('consumer')
        self.consumption = getattr(consumer_player, 'production_value', 0.0) if consumer_player else 0.0
        
        # Investment (R&D and capital investment from all players)
        self.investment = 0.0
        for player in players.values():
            self.investment += getattr(player, 'rd_budget', 0.0)
            self.investment += getattr(player, 'investment_budget', 0.0)
        
        # Government spending
        government_player = players.get('government')
        self.government_spending = getattr(government_player, 'production_value', 0.0) if government_player else 0.0
        
        # Net exports (simplified - assume zero for closed economy)
        self.net_exports = 0.0
        
        # GDP = C + I + G + (X-M)
        self.previous_gdp = self.gdp
        self.gdp = self.consumption + self.investment + self.government_spending + self.net_exports
    
    def update_employment(self, players: Dict):
        """Update employment rate based on economic activity and productivity."""
        # Employment depends on GDP growth and productivity
        if self.previous_gdp > 0:
            gdp_growth = (self.gdp - self.previous_gdp) / self.previous_gdp
        else:
            gdp_growth = 0.0
            
        # Average productivity across sectors - SAFE ACCESS
        total_productivity = 0.0
        count = 0
        for player in players.values():
            productivity = getattr(player, 'productivity_factor', 1.0)
            total_productivity += productivity
            count += 1
            
        avg_productivity = total_productivity / max(count, 1)
        
        # Employment rate formula considering productivity
        base_employment = 85.0
        gdp_effect = gdp_growth * 500  # GDP growth effect
        productivity_effect = (avg_productivity - 1.0) * 10  # Productivity can reduce employment need
        
        target_employment = base_employment + gdp_effect - productivity_effect
        
        # Smooth employment adjustment
        adjustment_speed = 0.2
        self.employment_rate = (self.employment_rate * (1 - adjustment_speed) + 
                              target_employment * adjustment_speed)
        
        # Keep employment within reasonable bounds
        self.employment_rate = max(75.0, min(98.0, self.employment_rate))
    
    def update(self, players: Dict, turn_manager=None):
        """Comprehensive economic state update with transaction-based inflation."""
        self.turn_count += 1
        
        # Update GDP components
        self.update_gdp_components(players)
        
        # Update money supply from bank lending
        self.update_money_supply(players)
        
        # Calculate money velocity
        self.money_velocity = self.calculate_money_velocity()
        
        # Calculate inflation using transaction prices if available
        if turn_manager and hasattr(turn_manager, 'get_transaction_prices'):
            self.calculate_transaction_based_inflation(turn_manager)
        else:
            # Fallback to MV = PY approach
            self.calculate_inflation_mv_py_fallback()
        
        # Update employment
        self.update_employment(players)
        
        # Store histories - ALL these arrays are guaranteed to exist
        self.gdp_history.append(self.gdp)
        self.m2_history.append(self.money_supply)
        self.inflation_history.append(self.inflation_rate)
        self.employment_history.append(self.employment_rate)
        self.velocity_history.append(self.money_velocity)
        self.price_history.append(self.price_level)
        
        # Store interest rates if available
        financial_player = players.get('financial')
        if financial_player:
            commercial_rate = getattr(financial_player, 'commercial_rate', 0.05)
            self.interest_rate_history.append(commercial_rate)
        else:
            self.interest_rate_history.append(0.05)  # Default rate
        
    def get_economic_indicators(self) -> Dict:
        """FIXED: Get comprehensive economic indicators with inflation as PERCENTAGE."""
        gdp_growth = 0.0
        if self.previous_gdp > 0:
            gdp_growth = ((self.gdp - self.previous_gdp) / self.previous_gdp) * 100
            
        return {
            'gdp': round(self.gdp, 2),
            'inflation_rate': round(self.inflation_rate * 100, 2),  # FIXED: Convert to percentage
            'employment_rate': round(self.employment_rate, 2),
            'money_supply': round(self.money_supply, 2),
            'money_velocity': round(self.money_velocity, 3),
            'price_level': round(self.price_level, 3),
            'new_money_created': round(self.new_money_created, 2),
            'consumption': round(self.consumption, 2),
            'investment': round(self.investment, 2),
            'government_spending': round(self.government_spending, 2),
            'gdp_growth': round(gdp_growth, 2),
            'last_prices': {k: round(v, 2) for k, v in self.last_prices.items()}
        }
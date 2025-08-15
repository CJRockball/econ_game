from core.base_player import BasePlayer
from typing import Dict

class CentralBankPlayer(BasePlayer):
    """
    Central Bank Player - Controls monetary policy through Fed Funds Rate.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        # Central bank specific attributes
        self.fed_funds_rate = 0.025    # Starting at 2.5%
        self.discount_rate = 0.035     # Emergency lending rate
        self.inflation_target = 0.02   # 2% inflation target
        self.neutral_rate = 0.025      # Long-term neutral rate
        self.governance_mode = "ai"    # "ai" or "democratic"
        
        # Policy tracking
        self.policy_history = []
        self.emergency_lending = 0.0
        
        # Economic indicators for decision making
        self.current_inflation = 0.0
        self.current_unemployment = 0.05
        self.output_gap = 0.0
        
    def reset(self):
        """Reset central bank to initial state."""
        super().reset()
        self.fed_funds_rate = 0.025
        self.discount_rate = 0.035
        self.policy_history.clear()
        self.emergency_lending = 0.0
        self.current_inflation = 0.0
        self.current_unemployment = 0.05
        self.output_gap = 0.0
        
    def update_economic_indicators(self, economic_state):
        """Update economic indicators for policy decisions - REQUIRED METHOD."""
        self.current_inflation = getattr(economic_state, 'inflation_rate', 0.0)
        self.current_unemployment = 1.0 - (getattr(economic_state, 'employment_rate', 95.0) / 100.0)
        
        # Calculate output gap safely
        gdp_history = getattr(economic_state, 'gdp_history', [])
        current_gdp = getattr(economic_state, 'gdp', 0.0)
        
        if gdp_history and len(gdp_history) > 0 and gdp_history[0] > 0:
            potential_gdp = gdp_history[0]
            self.output_gap = (current_gdp - potential_gdp) / potential_gdp
        else:
            self.output_gap = 0.0
    
    def taylor_rule_recommendation(self) -> float:
        """Calculate Fed Funds Rate using Taylor Rule - REQUIRED METHOD."""
        # Taylor Rule: r = r_neutral + 1.5*(inflation - target) + 0.5*output_gap
        recommended_rate = (self.neutral_rate + 
                          1.5 * (self.current_inflation - self.inflation_target) +
                          0.5 * self.output_gap)
        
        # Keep rate within reasonable bounds (0% to 8%)
        return max(0.0, min(0.08, recommended_rate))
    
    def set_ai_policy(self):
        """AI-controlled monetary policy using Taylor Rule."""
        if self.governance_mode == "ai":
            target_rate = self.taylor_rule_recommendation()
            
            # Gradual adjustment (central banks don't make dramatic changes)
            max_change = 0.005  # 0.5% maximum change per turn
            if abs(target_rate - self.fed_funds_rate) > max_change:
                if target_rate > self.fed_funds_rate:
                    self.fed_funds_rate += max_change
                else:
                    self.fed_funds_rate -= max_change
            else:
                self.fed_funds_rate = target_rate
                
            # Round to nearest 0.25%
            self.fed_funds_rate = round(self.fed_funds_rate * 400) / 400
            
    def set_democratic_policy(self, voted_rate: float):
        """Set policy based on democratic vote - REQUIRED METHOD."""
        if self.governance_mode == "democratic":
            # Validate rate is reasonable
            self.fed_funds_rate = max(0.0, min(0.08, voted_rate))
            
    def provide_emergency_lending(self, amount: float) -> float:
        """Provide emergency lending at discount rate."""
        # Central bank can create money for emergency lending
        self.emergency_lending += amount
        return amount  # Always available (central bank creates money)
    
    def produce(self):
        """Central bank operations - REQUIRED METHOD."""
        # Set monetary policy if AI mode
        if self.governance_mode == "ai":
            self.set_ai_policy()
            
        # Calculate operational costs
        self.operating_costs = self.labor * 50.0  # Central bank operations
        self.production_value = self.operating_costs  # Services to economy
        
        # Track policy changes
        if not self.policy_history or self.policy_history[-1] != self.fed_funds_rate:
            self.policy_history.append(self.fed_funds_rate)
    
    def calculate_borrowing_need(self):
        """Central bank doesn't need to borrow - override."""
        self.borrowing_demand = 0.0
            
    def get_policy_explanation(self) -> str:
        """Explain current policy decision for educational purposes."""
        taylor_rate = self.taylor_rule_recommendation()
        
        explanation = f"Fed Funds Rate: {self.fed_funds_rate:.2%}\\n"
        explanation += f"Taylor Rule suggests: {taylor_rate:.2%}\\n"
        explanation += f"Inflation: {self.current_inflation:.2%} (Target: {self.inflation_target:.2%})\\n"
        explanation += f"Unemployment: {self.current_unemployment:.2%}\\n"
        explanation += f"Output Gap: {self.output_gap:.2%}\\n"
        
        if self.current_inflation > self.inflation_target + 0.005:
            explanation += "Policy stance: Fighting inflation"
        elif self.current_unemployment > 0.06:
            explanation += "Policy stance: Supporting employment"
        else:
            explanation += "Policy stance: Neutral"
            
        return explanation
    
    def get_status(self) -> Dict:
        """Return central bank status for UI - REQUIRED METHOD."""
        status = super().get_status()
        status.update({
            'fed_funds_rate': round(self.fed_funds_rate, 4),
            'discount_rate': round(self.discount_rate, 4),
            'inflation_target': self.inflation_target,
            'governance_mode': self.governance_mode,
            'policy_explanation': self.get_policy_explanation(),
            'emergency_lending': round(self.emergency_lending, 2),
            'taylor_rule_rate': round(self.taylor_rule_recommendation(), 4)
        })
        return status
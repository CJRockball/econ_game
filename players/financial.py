from core.base_player import BasePlayer
from typing import Dict

class FinancialPlayer(BasePlayer):
    """
    Enhanced Financial Player with proper fractional reserve banking.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.deposits = 0.0              # Customer deposits
        self.reserves = 0.0              # Bank reserves
        self.reserve_ratio = 0.1         # 10% reserve requirement
        self.commercial_rate = 0.055     # Commercial lending rate
        self.deposit_rate = 0.015        # Rate paid on deposits
        self.fed_funds_rate = 0.025      # Current Fed Funds Rate
        self.risk_premium = 0.025        # Base risk premium over Fed Funds
        self.pass_through_coefficient = 0.8  # Interest rate pass-through
        
        # Banking metrics
        self.new_loans_this_turn = 0.0
        self.loan_defaults = 0.0
        self.net_interest_margin = 0.0
        self.banking_capacity = 200000.0
        
    def reset(self):
        """Reset financial player to initial state."""
        super().reset()
        self.deposits = 0.0
        self.reserves = 10000.0  # Initial reserves
        self.commercial_rate = 0.055
        self.deposit_rate = 0.015
        self.fed_funds_rate = 0.025
        self.new_loans_this_turn = 0.0
        self.loan_defaults = 0.0
        self.net_interest_margin = 0.0
        
    def update_fed_funds_rate(self, new_fed_funds_rate: float):
        """Update Fed Funds Rate and adjust commercial rates - REQUIRED METHOD."""
        self.fed_funds_rate = new_fed_funds_rate
        
        # Commercial rate pass-through with incomplete transmission
        target_commercial_rate = (self.fed_funds_rate * self.pass_through_coefficient + 
                                self.risk_premium + 0.015)  # Bank markup
        
        # Gradual adjustment of commercial rates
        adjustment_speed = 0.3
        self.commercial_rate = (self.commercial_rate * (1 - adjustment_speed) + 
                              target_commercial_rate * adjustment_speed)
        
        # Update deposit rate (lower than commercial rate)
        self.deposit_rate = max(0.001, self.commercial_rate * 0.4)
        
    def calculate_lending_capacity(self) -> float:
        """Calculate maximum new lending capacity - REQUIRED METHOD."""
        # Fractional reserve banking: can lend based on excess reserves
        required_reserves = self.deposits * self.reserve_ratio
        excess_reserves = max(0, self.reserves - required_reserves)
        
        # Money multiplier effect: new loans can create deposits
        max_lending_capacity = excess_reserves / self.reserve_ratio if self.reserve_ratio > 0 else 0
        
        # Also limited by bank capital and regulatory limits
        capital_constraint = max(0, self.banking_capacity - self.loans_outstanding)
        
        return min(max_lending_capacity, capital_constraint, 10000)  # Max loan size limit
    
    def make_loan(self, borrower, requested_amount: float) -> float:
        """Make a loan - creates new money through fractional reserve banking - REQUIRED METHOD."""
        if not hasattr(borrower, 'money') or not hasattr(borrower, 'credit_rating'):
            return 0.0
            
        lending_capacity = self.calculate_lending_capacity()
        
        # Adjust loan amount based on credit rating and capacity
        credit_adjusted_amount = requested_amount * getattr(borrower, 'credit_rating', 1.0)
        loan_amount = min(credit_adjusted_amount, lending_capacity)
        
        if loan_amount > 100:  # Minimum loan size
            # CRITICAL: This creates new money in the economy
            borrower.money += loan_amount
            borrower.loans_outstanding += loan_amount
            
            # Bank records the loan as an asset
            self.loans_outstanding += loan_amount
            self.new_loans_this_turn += loan_amount
            
            # Create corresponding deposit (money creation)
            self.deposits += loan_amount
            
            # Loan fee income
            origination_fee = loan_amount * 0.01
            self.money += origination_fee
            
            return loan_amount
        
        return 0.0
    
    def accept_deposit(self, depositor, amount: float):
        """Accept customer deposits - REQUIRED METHOD."""
        if (hasattr(depositor, 'money') and 
            amount > 0 and depositor.money >= amount):
            depositor.money -= amount
            self.deposits += amount
            self.reserves += amount  # Simplified - assume all deposits become reserves
            
    def handle_loan_defaults(self):
        """Handle loan defaults - safe internal calculation."""
        # Simple default model based on interest rate spread
        base_default_rate = 0.005
        stress_factor = max(0, (self.commercial_rate - self.deposit_rate - 0.03) * 2)
        default_rate = base_default_rate + stress_factor
        
        defaults = self.loans_outstanding * default_rate
        self.loan_defaults += defaults
        self.loans_outstanding = max(0, self.loans_outstanding - defaults)
        self.money = max(0, self.money - defaults)  # Bank absorbs the loss
        
    def produce(self):
        """Banking operations - REQUIRED METHOD."""
        # Reset turn counters
        self.new_loans_this_turn = 0.0
        
        # Calculate interest income and expenses
        interest_income = self.loans_outstanding * self.commercial_rate
        interest_expense = self.deposits * self.deposit_rate
        self.net_interest_margin = interest_income - interest_expense
        
        # Operating costs
        operating_costs = self.banking_capacity * 0.015  # 1.5% of capacity
        
        # Net income
        net_income = self.net_interest_margin - operating_costs
        self.money += net_income
        
        # Production value represents financial services provided
        self.production_value = interest_income + (self.deposits * 0.005)  # Service fees
        self.operating_costs = operating_costs
        
        # Handle defaults
        self.handle_loan_defaults()
        
    def calculate_borrowing_need(self):
        """Banks don't typically borrow for investment - override."""
        self.borrowing_demand = 0.0  # Banks manage liquidity differently
        
    def get_lending_rate_for_borrower(self, borrower) -> float:
        """Calculate lending rate for specific borrower."""
        # Base rate + risk adjustment based on credit rating
        credit_rating = getattr(borrower, 'credit_rating', 1.0)
        risk_adjustment = (2.0 - credit_rating) * 0.02
        return self.commercial_rate + risk_adjustment
    
    def get_status(self) -> Dict:
        """Return enhanced financial player status - REQUIRED METHOD."""
        status = super().get_status()
        status.update({
            'deposits': round(self.deposits, 2),
            'reserves': round(self.reserves, 2),
            'commercial_rate': round(self.commercial_rate, 4),
            'deposit_rate': round(self.deposit_rate, 4),
            'fed_funds_rate': round(self.fed_funds_rate, 4),
            'lending_capacity': round(self.calculate_lending_capacity(), 2),
            'new_loans_this_turn': round(self.new_loans_this_turn, 2),
            'net_interest_margin': round(self.net_interest_margin, 2),
            'loan_defaults': round(self.loan_defaults, 2)
        })
        return status
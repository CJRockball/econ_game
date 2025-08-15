# players/financial.py

from core.base_player import BasePlayer

class FinancialPlayer(BasePlayer):
    """
    Simplified Financial Player - provides banking and credit services.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.deposits = 0.0          # Customer deposits
        self.loans_outstanding = 0.0 # Loans made to other players
        self.interest_rate = 0.05    # 5% interest rate
        self.banking_capacity = 200000.0  # Maximum banking operations
        
    def produce(self):
        """Provide financial services - lending and deposit taking."""
        # Collect interest & service fees then decide deposit vs lending
        interest_income = self.loans_outstanding * self.interest_rate
        interest_expense = self.deposits * (self.interest_rate * 0.6)
        net_interest = interest_income - interest_expense
        
        # Pay interest on deposits (lower rate)
        interest_expense = self.deposits * (self.interest_rate * 0.6)
        
        # Net interest income
        net_interest = interest_income - interest_expense
        
        # Operating costs for banking operations
        operating_cost = self.banking_capacity * 0.01  # 1% of capacity
        
        # Banking service fees
        service_fees = min(self.labor * 5.0, self.banking_capacity * 0.01)
        self.production_value = net_interest + service_fees
        self.operating_costs = self.banking_capacity * 0.01
        self.money += net_interest
        
        # Total revenue
        self.production_value = net_interest + service_fees
        self.operating_costs = operating_cost
        
        # Update money
        self.money += net_interest
        
    def make_loan(self, amount: float) -> bool:
        """Make a loan if sufficient funds available."""
        # AI only lends if solvency ratio OK
        if (self.loans_outstanding + amount) <= self.banking_capacity * 0.8 and self.money >= amount:
            self.money -= amount
            self.loans_outstanding += amount
            return True
        return False
        
    def accept_deposit(self, amount: float):
        """Accept customer deposit."""
        # AI limits deposits to avoid hoarding
        cap = self.banking_capacity * 0.5
        accepted = min(amount, cap - self.deposits)
        self.money += accepted
        self.deposits += accepted

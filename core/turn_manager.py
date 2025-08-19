from typing import Dict
import random

class TurnManager:
    """
    Enhanced turn manager with demand-responsive production and labor tracking.
    """

    def __init__(self):
        # CRITICAL FIX: Goods markets BEFORE financial markets
        self.phases = [
            self.monetary_policy_phase,
            self.production_phase,
            self.goods_markets_phase,     # MOVED: Markets before deposits/loans
            self.financial_market_phase,  # MOVED: After goods are traded
            self.update_phase,
        ]
        # Track transaction prices for inflation calculation
        self.transaction_prices = {}
        self.transaction_volumes = {}
        
        # NEW: Track realized sales and labor demand for adaptive behavior
        self.realized_sales = {'raw_materials': 0.0, 'finished_goods': 0.0, 'services_units': 0.0}
        self.labor_demand_log = 0.0

    def execute_turn(self, players: Dict[str, object]):
        """Execute all phases in sequence for one turn - SAFE EXECUTION."""
        # Reset transaction tracking each turn
        self.transaction_prices.clear()
        self.transaction_volumes.clear()
        self.realized_sales = {'raw_materials': 0.0, 'finished_goods': 0.0, 'services_units': 0.0}
        self.labor_demand_log = 0.0
        
        for phase in self.phases:
            try:
                phase(players)
            except Exception as e:
                print(f"Warning: Error in {phase.__name__}: {e}")
                continue

    def monetary_policy_phase(self, players: Dict[str, object]):
        """Central bank sets monetary policy first - SAFE ACCESS."""
        central_bank = players.get('central_bank')
        financial_player = players.get('financial')
        
        if central_bank and hasattr(central_bank, 'produce'):
            central_bank.produce()  # Sets Fed Funds Rate in AI mode
            
            # Transmit Fed Funds Rate to commercial banks
            if (financial_player and 
                hasattr(financial_player, 'update_fed_funds_rate') and
                hasattr(central_bank, 'fed_funds_rate')):
                financial_player.update_fed_funds_rate(central_bank.fed_funds_rate)

    def production_phase(self, players: Dict[str, object]):
        """Each player produces goods or services - SAFE ACCESS."""
        # Calculate borrowing needs first
        for player_name, player in players.items():
            if (player_name not in ['financial', 'central_bank'] and 
                hasattr(player, 'calculate_borrowing_need')):
                player.calculate_borrowing_need()
        
        # NEW: Aggregate labor demand from all producers
        for name, player in players.items():
            if hasattr(player, 'get_intended_labor'):
                self.labor_demand_log += max(0.0, player.get_intended_labor())
        
        # Then produce
        for player in players.values():
            if hasattr(player, 'produce'):
                player.produce()

    def goods_markets_phase(self, players: Dict[str, object]):
        """Clear goods and services markets BEFORE financial operations - CRITICAL FIX."""
        self.clear_labor_market(players)
        self.clear_raw_materials_market(players)
        self.clear_finished_goods_market(players)
        self.clear_services_market(players)
        
        # NEW: Write realized sales back to players for next-turn adaptation
        rm = players.get('raw_materials')
        mf = players.get('manufacturing')
        sv = players.get('services')

        if rm: setattr(rm, 'last_realized_sales', self.realized_sales['raw_materials'])
        if mf: setattr(mf, 'last_realized_sales', self.realized_sales['finished_goods'])
        if sv: setattr(sv, 'last_realized_sales', self.realized_sales['services_units'])

    def financial_market_phase(self, players: Dict[str, object]):
        """Financial markets AFTER goods markets - players can deposit surplus cash."""
        financial_player = players.get('financial')
        if not (financial_player and hasattr(financial_player, 'make_loan')):
            return
            
        # Process loan applications from all sectors
        borrowers = []
        for name, player in players.items():
            if (name not in ['financial', 'central_bank'] and 
                hasattr(player, 'borrowing_demand') and 
                getattr(player, 'borrowing_demand', 0) > 0):
                borrowers.append(player)
        
        # Sort by credit rating (best borrowers first)
        borrowers.sort(key=lambda x: getattr(x, 'credit_rating', 1.0), reverse=True)
        
        # Process loans
        for borrower in borrowers:
            borrowing_demand = getattr(borrower, 'borrowing_demand', 0)
            if borrowing_demand > 0:
                loan_amount = financial_player.make_loan(borrower, borrowing_demand)
                # Reduce borrowing demand by loan amount
                borrower.borrowing_demand = max(0, borrowing_demand - loan_amount)
        
        # Handle deposits from excess cash AFTER purchases
        self.process_deposits(players, financial_player)
        
        # Service existing debt
        if hasattr(financial_player, 'commercial_rate'):
            commercial_rate = financial_player.commercial_rate
            for player_name, player in players.items():
                if (player_name not in ['financial', 'central_bank'] and 
                    hasattr(player, 'service_debt') and
                    hasattr(player, 'loans_outstanding') and
                    getattr(player, 'loans_outstanding', 0) > 0):
                    player.service_debt(commercial_rate)

    def process_deposits(self, players: Dict[str, object], financial_player):
        """Process deposits ONLY from excess cash after purchases - SAFE ACCESS."""
        if not hasattr(financial_player, 'accept_deposit'):
            return
            
        for player_name, player in players.items():
            if (player_name not in ['financial', 'central_bank'] and 
                hasattr(player, 'money') and 
                getattr(player, 'money', 0) > 5000):  # Higher threshold after purchases
                
                # Special handling for consumer - even more conservative
                if player_name == 'consumer':
                    if player.money > 8000:
                        excess = player.money - 8000
                        deposit_amount = excess * 0.2
                        if deposit_amount > 200:
                            financial_player.accept_deposit(player, deposit_amount)
                    continue
                
                # More conservative deposit strategy - keep more operating cash
                excess_cash = player.money - 5000  # Increased buffer
                deposit_amount = excess_cash * 0.3  # Reduced from 0.4 to 0.3
                
                if deposit_amount > 200:  # Higher minimum deposit
                    financial_player.accept_deposit(player, deposit_amount)

    def clear_labor_market(self, players: Dict[str, object]):
        """Enhanced labor market with productivity effects - SAFE ACCESS."""
        consumer_player = players.get('consumer')
        if not (consumer_player and hasattr(consumer_player, 'money')):
            return
        
        total_wages = 0
        for player_name, player in players.items():
            if (player_name not in ['consumer', 'central_bank'] and 
                hasattr(player, 'money') and hasattr(player, 'production_value') and
                getattr(player, 'money', 0) > 500):
                
                # Wage payments affected by productivity and technology
                base_wage_budget = getattr(player, 'production_value', 0) * 0.3
                productivity_multiplier = getattr(player, 'productivity_factor', 1.0)
                
                # Higher productivity means higher wages
                wage_budget = min(player.money * 0.25, base_wage_budget * productivity_multiplier)
                
                if wage_budget > 0:
                    total_wages += wage_budget
                    player.money -= wage_budget
        
        # Consumer receives wages
        consumer_player.money += total_wages
        if hasattr(consumer_player, 'inventory'):
            consumer_player.inventory['wages_received'] = consumer_player.inventory.get('wages_received', 0) + total_wages

    def clear_raw_materials_market(self, players: Dict[str, object]):
        """Raw Materials → Manufacturing with DYNAMIC PRICING - SAFE ACCESS."""
        raw_materials_player = players.get('raw_materials')
        manufacturing_player = players.get('manufacturing')
        
        if not (raw_materials_player and manufacturing_player and 
                hasattr(raw_materials_player, 'inventory') and
                hasattr(manufacturing_player, 'money')):
            return
            
        supply = raw_materials_player.inventory.get('raw_materials', 0)
        
        if supply > 0 and getattr(manufacturing_player, 'money', 0) > 100:
            # Initialize price if not set
            if not hasattr(raw_materials_player, 'current_price'):
                raw_materials_player.current_price = 8.0
            
            # Dynamic pricing based on supply and previous sales
            base_price = raw_materials_player.current_price
            tech_factor = getattr(raw_materials_player, 'technology_level', 1.0)
            supply_factor = max(0.5, min(2.0, 50 / max(supply, 1)))
            
            # Price per unit considering technology
            price_per_unit = (base_price * supply_factor) / tech_factor
            
            # Manufacturing demand
            max_affordable = manufacturing_player.money / price_per_unit
            demand = min(max_affordable, 40, supply)
            
            if demand > 0:
                total_cost = demand * price_per_unit
                
                # Execute trade - CRITICAL: All three operations
                raw_materials_player.inventory['raw_materials'] -= demand
                raw_materials_player.money += total_cost
                manufacturing_player.money -= total_cost
                manufacturing_player.inventory['raw_materials'] = manufacturing_player.inventory.get('raw_materials', 0) + demand
                
                # NEW: Track realized sales
                self.realized_sales['raw_materials'] += float(demand)
                
                # Track transaction for inflation calculation
                self.transaction_prices['raw_materials'] = price_per_unit
                self.transaction_volumes['raw_materials'] = demand
                
                # Adjust price for next turn based on demand/supply ratio
                if demand >= supply:  # Sold out - raise price
                    raw_materials_player.current_price *= 1.05
                elif demand < supply * 0.5:  # Low demand - lower price
                    raw_materials_player.current_price *= 0.95
                else:  # Normal demand - small adjustment
                    raw_materials_player.current_price *= 1.01
            else:
                # No sales - lower price more aggressively
                raw_materials_player.current_price *= 0.92

    def clear_finished_goods_market(self, players: Dict[str, object]):
        """Manufacturing → Consumer with AGGRESSIVE NECESSITY SPENDING - SAFE ACCESS."""
        manufacturing_player = players.get('manufacturing')
        consumer_player = players.get('consumer')
        
        if not (manufacturing_player and consumer_player and 
                hasattr(manufacturing_player, 'inventory') and
                hasattr(consumer_player, 'money')):
            return
            
        supply = manufacturing_player.inventory.get('finished_goods', 0)
        
        if supply > 0 and getattr(consumer_player, 'money', 0) > 50:
            # Initialize price if not set
            if not hasattr(manufacturing_player, 'current_price'):
                manufacturing_player.current_price = 18.0
            
            # Dynamic pricing
            base_price = manufacturing_player.current_price
            tech_factor = getattr(manufacturing_player, 'technology_level', 1.0)
            supply_factor = max(0.7, min(1.8, 30 / max(supply, 1)))
            
            # Price considering technology and quality
            price_per_unit = base_price * supply_factor * (0.8 + 0.4 * tech_factor)
            
            # AGGRESSIVE SPENDING ON BASIC NECESSITIES - Consumer must buy food/essentials
            confidence = getattr(consumer_player, 'consumption_confidence', 1.0)
            max_affordable = consumer_player.money / price_per_unit
            
            # INCREASED: Consumer spends much more aggressively on basic necessities (food, clothing, etc.)
            # Use 95% of affordable amount since these are necessities, not luxuries
            necessity_multiplier = 0.95  # Increased from 0.8 to 0.95
            demand = min(max_affordable * necessity_multiplier * confidence, 30, supply)
            
            if demand > 0:
                total_cost = demand * price_per_unit
                
                # Execute trade - CRITICAL: All operations
                manufacturing_player.inventory['finished_goods'] -= demand
                manufacturing_player.money += total_cost
                consumer_player.money -= total_cost
                consumer_player.inventory['finished_goods'] = consumer_player.inventory.get('finished_goods', 0) + demand
                
                # Track actual spending for consumer smoothing
                consumer_player.inventory['actual_purchases'] = consumer_player.inventory.get('actual_purchases', 0) + total_cost
                
                # NEW: Track realized sales
                self.realized_sales['finished_goods'] += float(demand)
                
                # Track transaction for inflation calculation
                self.transaction_prices['finished_goods'] = price_per_unit
                self.transaction_volumes['finished_goods'] = demand
                
                # Adjust price for next turn
                if demand >= supply:  # Sold out - raise price
                    manufacturing_player.current_price *= 1.05
                elif demand < supply * 0.5:  # Low demand - lower price
                    manufacturing_player.current_price *= 0.95
                else:  # Normal demand
                    manufacturing_player.current_price *= 1.01
            else:
                # No sales - lower price
                manufacturing_player.current_price *= 0.92
            
            
    def clear_services_market(self, players: Dict[str, object]):
        """Services market with DYNAMIC PRICING - SAFE ACCESS."""
        services_player = players.get('services')
        if not (services_player and hasattr(services_player, 'money')):
            return
        
        # Initialize service price if not set
        if not hasattr(services_player, 'current_price'):
            services_player.current_price = 15.0
            
        total_service_revenue = 0
        total_service_units = 0
        
        for player_name, player in players.items():
            if (player_name not in ['services', 'central_bank'] and 
                hasattr(player, 'money') and getattr(player, 'money', 0) > 80):
                
                # Service demand varies by player type and productivity
                # Service demand varies by player type and productivity
                if player_name == 'consumer':
                    confidence = getattr(player, 'consumption_confidence', 1.0)
                    # INCREASED: Consumers need more services (healthcare, utilities, transport, etc.)
                    service_necessity_rate = 0.35  # Increased from 0.2 to 0.35
                    desired_units = min(player.money / services_player.current_price * service_necessity_rate * confidence, 15)  # Increased cap to 15
                elif player_name == 'financial':
                    desired_units = min(player.money / services_player.current_price * 0.1, 8)
                else:
                    # Business services scale with production and technology
                    tech_factor = getattr(player, 'technology_level', 1.0)
                    desired_units = min(player.money / services_player.current_price * 0.15 * tech_factor, 10)
                
                if desired_units > 0:
                    service_cost = desired_units * services_player.current_price
                    if player.money >= service_cost:
                        # Execute trade - CRITICAL: Both operations
                        player.money -= service_cost
                        services_player.money += service_cost
                        total_service_revenue += service_cost
                        total_service_units += desired_units
                        
                        # Track consumer spending
                        if player_name == 'consumer':
                            player.inventory['actual_purchases'] = player.inventory.get('actual_purchases', 0) + service_cost
        
        if hasattr(services_player, 'inventory'):
            services_player.inventory['services_provided'] = services_player.inventory.get('services_provided', 0) + total_service_revenue
        
        # NEW: Track realized sales units
        self.realized_sales['services_units'] += float(total_service_units)
        
        # Track transaction for inflation calculation
        if total_service_units > 0:
            avg_service_price = total_service_revenue / total_service_units
            self.transaction_prices['services'] = avg_service_price
            self.transaction_volumes['services'] = total_service_units
            
            # Adjust service price for next turn based on demand
            capacity_utilization = total_service_units / 60  # Increased capacity assumption
            if capacity_utilization > 0.9:  # High demand
                services_player.current_price *= 1.04
            elif capacity_utilization < 0.5:  # Low demand
                services_player.current_price *= 0.96
            else:  # Normal demand
                services_player.current_price *= 1.01
        else:
            # No demand - lower price
            services_player.current_price *= 0.93

    def update_phase(self, players: Dict[str, object]):
        """Update player states - SAFE ACCESS."""
        for player in players.values():
            if hasattr(player, 'update_after_market'):
                player.update_after_market()
        
        # Technology investment phase
        self.process_technology_investments(players)
        
        # Apply economic volatility
        if random.random() < 0.08:  # 8% chance each turn
            self.apply_economic_shock(players)

    def process_technology_investments(self, players: Dict[str, object]):
        """Process R&D investments - SAFE ACCESS."""
        for player_name, player in players.items():
            if (player_name not in ['consumer', 'financial', 'central_bank'] and
                hasattr(player, 'production_value') and hasattr(player, 'operating_costs') and
                hasattr(player, 'money') and hasattr(player, 'invest_in_technology')):
                
                # Automatic R&D investment based on profits
                production_value = getattr(player, 'production_value', 0)
                operating_costs = getattr(player, 'operating_costs', 0)
                
                if production_value > operating_costs:
                    profit = production_value - operating_costs
                    rd_investment = min(profit * 0.1, player.money * 0.05)  # 10% of profit or 5% of cash
                    
                    if rd_investment > 50:  # Minimum R&D investment
                        player.invest_in_technology(rd_investment)

    def apply_economic_shock(self, players: Dict[str, object]):
        """Apply economic shocks - SAFE ACCESS."""
        shock_type = random.choice([
            'demand_surge', 'supply_shortage', 'tech_breakthrough', 
            'financial_crisis', 'productivity_boom'
        ])
        
        if shock_type == 'demand_surge':
            consumer = players.get('consumer')
            if consumer and hasattr(consumer, 'money') and hasattr(consumer, 'borrowing_demand'):
                consumer.money += 800
                consumer.borrowing_demand += 500
                
        elif shock_type == 'supply_shortage':
            raw_player = players.get('raw_materials')
            if raw_player and hasattr(raw_player, 'inventory'):
                current_materials = raw_player.inventory.get('raw_materials', 0)
                shortage = current_materials * 0.3
                raw_player.inventory['raw_materials'] = max(0, current_materials - shortage)
                
        elif shock_type == 'tech_breakthrough':
            eligible_players = [p for name, p in players.items() 
                             if (name not in ['consumer', 'financial', 'central_bank'] and
                                 hasattr(p, 'technology_level') and hasattr(p, 'productivity_factor'))]
            if eligible_players:
                lucky_player = random.choice(eligible_players)
                lucky_player.technology_level += 0.1
                lucky_player.productivity_factor = lucky_player.technology_level
                
        elif shock_type == 'financial_crisis':
            financial = players.get('financial')
            if financial and hasattr(financial, 'banking_capacity'):
                financial.banking_capacity *= 0.9
                for player in players.values():
                    if hasattr(player, 'credit_rating'):
                        player.credit_rating *= 0.95
                        
        elif shock_type == 'productivity_boom':
            for player_name, player in players.items():
                if (player_name not in ['consumer', 'central_bank'] and
                    hasattr(player, 'productivity_factor')):
                    player.productivity_factor *= 1.05

    def get_transaction_prices(self) -> Dict[str, float]:
        """Get current turn's transaction prices for inflation calculation."""
        return self.transaction_prices.copy()
    
    def get_transaction_volumes(self) -> Dict[str, float]:
        """Get current turn's transaction volumes."""
        return self.transaction_volumes.copy()
    
    # NEW: Helper methods for economic state
    def get_realized_sales(self) -> Dict[str, float]:
        """Get current turn's realized sales for demand tracking."""
        return dict(self.realized_sales)

    def get_total_labor_demand(self) -> float:
        """Get total labor demand for employment calculation."""
        return float(self.labor_demand_log)
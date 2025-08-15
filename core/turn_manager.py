from typing import Dict
import random

class TurnManager:
    """
    Enhanced turn manager with safe method calls and proper error handling.
    """

    def __init__(self):
        self.phases = [
            self.monetary_policy_phase,
            self.production_phase,
            self.financial_market_phase,
            self.goods_markets_phase,
            self.update_phase,
        ]

    def execute_turn(self, players: Dict[str, object]):
        """Execute all phases in sequence for one turn - SAFE EXECUTION."""
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
        
        # Then produce
        for player in players.values():
            if hasattr(player, 'produce'):
                player.produce()

    def financial_market_phase(self, players: Dict[str, object]):
        """Enhanced financial market with safe lending - SAFE ACCESS."""
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
        
        # Handle deposits from excess cash
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
        """Process deposits from players with excess cash - SAFE ACCESS."""
        if not hasattr(financial_player, 'accept_deposit'):
            return
            
        for player_name, player in players.items():
            if (player_name not in ['financial', 'central_bank'] and 
                hasattr(player, 'money') and 
                getattr(player, 'money', 0) > 3000):
                # Deposit excess cash above operating buffer
                excess_cash = player.money - 3000
                deposit_amount = excess_cash * 0.4  # Deposit 40% of excess
                if deposit_amount > 100:
                    financial_player.accept_deposit(player, deposit_amount)

    def goods_markets_phase(self, players: Dict[str, object]):
        """Clear goods and services markets - SAFE ACCESS."""
        self.clear_labor_market(players)
        self.clear_raw_materials_market(players)
        self.clear_finished_goods_market(players)
        self.clear_services_market(players)

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
        """Raw Materials → Manufacturing - SAFE ACCESS."""
        raw_materials_player = players.get('raw_materials')
        manufacturing_player = players.get('manufacturing')
        
        if not (raw_materials_player and manufacturing_player and 
                hasattr(raw_materials_player, 'inventory') and
                hasattr(manufacturing_player, 'money')):
            return
            
        supply = raw_materials_player.inventory.get('raw_materials', 0)
        
        if supply > 0 and getattr(manufacturing_player, 'money', 0) > 100:
            # Enhanced pricing with technology effects
            base_price = 8.0
            tech_factor = getattr(raw_materials_player, 'technology_level', 1.0)
            supply_factor = max(0.5, min(2.0, 50 / max(supply, 1)))
            
            # Higher tech reduces costs, lower prices
            price_per_unit = (base_price * supply_factor) / tech_factor
            
            # Manufacturing demand
            max_affordable = manufacturing_player.money / price_per_unit
            demand = min(max_affordable, 40, supply)
            
            if demand > 0:
                total_cost = demand * price_per_unit
                
                # Execute trade
                raw_materials_player.inventory['raw_materials'] -= demand
                raw_materials_player.money += total_cost
                
                manufacturing_player.inventory['raw_materials'] = manufacturing_player.inventory.get('raw_materials', 0) + demand
                manufacturing_player.money -= total_cost

    def clear_finished_goods_market(self, players: Dict[str, object]):
        """Manufacturing → Consumer - SAFE ACCESS."""
        manufacturing_player = players.get('manufacturing')
        consumer_player = players.get('consumer')
        
        if not (manufacturing_player and consumer_player and 
                hasattr(manufacturing_player, 'inventory') and
                hasattr(consumer_player, 'money')):
            return
            
        supply = manufacturing_player.inventory.get('finished_goods', 0)
        
        if supply > 0 and getattr(consumer_player, 'money', 0) > 50:
            # Quality and technology affect pricing
            base_price = 18.0
            tech_factor = getattr(manufacturing_player, 'technology_level', 1.0)
            supply_factor = max(0.7, min(1.8, 30 / max(supply, 1)))
            
            # Higher tech enables premium pricing
            price_per_unit = base_price * supply_factor * (0.8 + 0.4 * tech_factor)
            
            # Consumer demand affected by income and prices
            max_affordable = consumer_player.money / price_per_unit
            demand = min(max_affordable * 0.4, 25, supply)
            
            if demand > 0:
                total_cost = demand * price_per_unit
                
                # Execute trade
                manufacturing_player.inventory['finished_goods'] -= demand
                manufacturing_player.money += total_cost
                
                consumer_player.inventory['finished_goods'] = consumer_player.inventory.get('finished_goods', 0) + demand
                consumer_player.money -= total_cost

    def clear_services_market(self, players: Dict[str, object]):
        """Services market - SAFE ACCESS."""
        services_player = players.get('services')
        if not (services_player and hasattr(services_player, 'money')):
            return
            
        total_service_revenue = 0
        
        for player_name, player in players.items():
            if (player_name not in ['services', 'central_bank'] and 
                hasattr(player, 'money') and getattr(player, 'money', 0) > 80):
                
                # Service demand varies by player type and productivity
                base_spending = 0.0
                
                if player_name == 'consumer':
                    base_spending = min(player.money * 0.15, 150)
                elif player_name == 'financial':
                    base_spending = min(player.money * 0.08, 100)
                else:
                    # Business services scale with production and technology
                    tech_factor = getattr(player, 'technology_level', 1.0)
                    base_spending = min(player.money * 0.12 * tech_factor, 120)
                
                if base_spending > 0:
                    player.money -= base_spending
                    total_service_revenue += base_spending
        
        services_player.money += total_service_revenue
        if hasattr(services_player, 'inventory'):
            services_player.inventory['services_provided'] = services_player.inventory.get('services_provided', 0) + total_service_revenue

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
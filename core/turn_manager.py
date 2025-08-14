# core/turn_manager.py - REPLACE ENTIRELY
from typing import Dict
from core.base_player import BasePlayer
import random

class TurnManager:
    """
    Enhanced turn manager with more realistic economic interactions.
    """

    def __init__(self):
        self.phases = [
            self.production_phase,
            self.market_phase,
            self.update_phase,
        ]

    def execute_turn(self, players: Dict[str, BasePlayer]):
        """Execute all phases in sequence for one turn."""
        for phase in self.phases:
            phase(players)

    def production_phase(self, players: Dict[str, BasePlayer]):
        """Each player produces goods or services."""
        for player in players.values():
            player.produce()

    def market_phase(self, players: Dict[str, BasePlayer]):
        """Enhanced market clearing with more interactions."""
        self.clear_labor_market(players)
        self.clear_raw_materials_market(players)
        self.clear_finished_goods_market(players)
        self.clear_services_market(players)
        self.clear_financial_market(players)

    def clear_labor_market(self, players: Dict[str, BasePlayer]):
        """Consumer provides labor to all sectors"""
        consumer_player = players['consumer']
        
        total_wages = 0
        for player_name, player in players.items():
            if player_name != 'consumer' and player.money > 200:
                # Each sector pays wages based on their production value
                wage_budget = min(player.money * 0.25, player.production_value * 0.3)
                total_wages += wage_budget
                player.money -= wage_budget
        
        # Consumer receives wages
        consumer_player.money += total_wages
        consumer_player.inventory['wages_received'] = consumer_player.inventory.get('wages_received', 0) + total_wages

    def clear_raw_materials_market(self, players: Dict[str, BasePlayer]):
        """Raw Materials → Manufacturing with variable pricing"""
        raw_materials_player = players['raw_materials']
        manufacturing_player = players['manufacturing']
        
        supply = raw_materials_player.inventory.get('raw_materials', 0)
        
        if supply > 0 and manufacturing_player.money > 100:
            # Dynamic pricing based on supply/demand
            base_price = 8.0
            supply_factor = max(0.5, min(2.0, 50 / max(supply, 1)))  # Price varies with supply
            price_per_unit = base_price * supply_factor
            
            # Manufacturing demand based on money and price
            max_affordable = manufacturing_player.money / price_per_unit
            demand = min(max_affordable, 40, supply)
            
            if demand > 0:
                total_cost = demand * price_per_unit
                
                # Execute trade
                raw_materials_player.inventory['raw_materials'] -= demand
                raw_materials_player.money += total_cost
                
                manufacturing_player.inventory['raw_materials'] = manufacturing_player.inventory.get('raw_materials', 0) + demand
                manufacturing_player.money -= total_cost

    def clear_finished_goods_market(self, players: Dict[str, BasePlayer]):
        """Manufacturing → Consumer with dynamic pricing"""
        manufacturing_player = players['manufacturing']
        consumer_player = players['consumer']
        
        supply = manufacturing_player.inventory.get('finished_goods', 0)
        
        if supply > 0 and consumer_player.money > 50:
            # Dynamic pricing
            base_price = 18.0
            supply_factor = max(0.7, min(1.8, 30 / max(supply, 1)))
            price_per_unit = base_price * supply_factor
            
            # Consumer demand based on money and preferences
            max_affordable = consumer_player.money / price_per_unit
            demand = min(max_affordable * 0.4, 25, supply)  # Consumer buys 40% of what they can afford
            
            if demand > 0:
                total_cost = demand * price_per_unit
                
                # Execute trade
                manufacturing_player.inventory['finished_goods'] -= demand
                manufacturing_player.money += total_cost
                
                consumer_player.inventory['finished_goods'] = consumer_player.inventory.get('finished_goods', 0) + demand
                consumer_player.money -= total_cost

    def clear_services_market(self, players: Dict[str, BasePlayer]):
        """Services → All other players"""
        services_player = players['services']
        
        total_service_revenue = 0
        for player_name, player in players.items():
            if player_name != 'services' and player.money > 80:
                # Service demand varies by player type
                if player_name == 'consumer':
                    service_spending = min(player.money * 0.15, 150)
                elif player_name == 'financial':
                    service_spending = min(player.money * 0.08, 100)
                else:
                    service_spending = min(player.money * 0.12, 120)
                
                if service_spending > 0:
                    player.money -= service_spending
                    total_service_revenue += service_spending
        
        services_player.money += total_service_revenue
        services_player.inventory['services_provided'] = services_player.inventory.get('services_provided', 0) + total_service_revenue

    def clear_financial_market(self, players: Dict[str, BasePlayer]):
        """Financial services and credit"""
        financial_player = players['financial']
        
        # Collect deposits from players with excess money
        total_deposits = 0
        for player_name, player in players.items():
            if player_name != 'financial' and player.money > 500:
                deposit_amount = (player.money - 500) * 0.3  # 30% of excess money
                player.money -= deposit_amount
                total_deposits += deposit_amount
        
        financial_player.money += total_deposits
        
        # Provide loans to players who need money
        total_loans = 0
        for player_name, player in players.items():
            if player_name != 'financial' and player.money < 200 and total_deposits > 100:
                loan_amount = min(200, total_deposits * 0.4)
                player.money += loan_amount
                financial_player.money -= loan_amount
                total_loans += loan_amount
                total_deposits -= loan_amount
        
        # Financial player earns interest
        interest_income = total_deposits * 0.02 + total_loans * 0.05
        financial_player.money += interest_income
        financial_player.production_value += interest_income

    def update_phase(self, players: Dict[str, BasePlayer]):
        """Update inventories and apply economic effects."""
        for player in players.values():
            player.update_after_market()
            
        # Apply some economic volatility
        if random.random() < 0.1:  # 10% chance each turn
            self.apply_economic_shock(players)

    def apply_economic_shock(self, players: Dict[str, BasePlayer]):
        """Apply random economic events"""
        shock_type = random.choice(['demand_surge', 'supply_shortage', 'tech_breakthrough'])
        
        if shock_type == 'demand_surge':
            # Increase consumer spending
            players['consumer'].money += 500
            
        elif shock_type == 'supply_shortage':
            # Reduce raw materials inventory
            raw_player = players['raw_materials']
            shortage = raw_player.inventory.get('raw_materials', 0) * 0.2
            raw_player.inventory['raw_materials'] = max(0, raw_player.inventory.get('raw_materials', 0) - shortage)
            
        elif shock_type == 'tech_breakthrough':
            # Boost manufacturing efficiency
            players['manufacturing'].money += 300
            players['services'].money += 200

# core/turn_manager.py

from typing import Dict
from core.base_player import BasePlayer

class TurnManager:
    """
    Manages the sequence of phases in each game turn with actual market clearing.
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
        """Clear markets: facilitate trade between players."""
        self.clear_raw_materials_market(players)
        self.clear_finished_goods_market(players)
        self.clear_services_market(players)
        self.clear_labor_market(players)

    def clear_raw_materials_market(self, players: Dict[str, BasePlayer]):
        """Raw Materials → Manufacturing trade"""
        raw_materials_player = players['raw_materials']
        manufacturing_player = players['manufacturing']
        
        # Raw materials supply
        supply = raw_materials_player.inventory.get('raw_materials', 0)
        
        # Manufacturing demand (needs raw materials to produce)
        demand = min(manufacturing_player.money / 10, 50)  # Can afford at $10/unit
        
        if supply > 0 and demand > 0:
            # Trade quantity
            trade_quantity = min(supply, demand)
            price_per_unit = 10.0
            total_cost = trade_quantity * price_per_unit
            
            # Execute trade
            raw_materials_player.inventory['raw_materials'] -= trade_quantity
            raw_materials_player.money += total_cost
            
            manufacturing_player.inventory['raw_materials'] = manufacturing_player.inventory.get('raw_materials', 0) + trade_quantity
            manufacturing_player.money -= total_cost

    def clear_finished_goods_market(self, players: Dict[str, BasePlayer]):
        """Manufacturing → Consumer trade"""
        manufacturing_player = players['manufacturing']
        consumer_player = players['consumer']
        
        # Finished goods supply
        supply = manufacturing_player.inventory.get('finished_goods', 0)
        
        # Consumer demand
        demand = min(consumer_player.money / 20, 30)  # Can afford at $20/unit
        
        if supply > 0 and demand > 0:
            # Trade quantity
            trade_quantity = min(supply, demand)
            price_per_unit = 20.0
            total_cost = trade_quantity * price_per_unit
            
            # Execute trade
            manufacturing_player.inventory['finished_goods'] -= trade_quantity
            manufacturing_player.money += total_cost
            
            consumer_player.inventory['finished_goods'] = consumer_player.inventory.get('finished_goods', 0) + trade_quantity
            consumer_player.money -= total_cost

    def clear_services_market(self, players: Dict[str, BasePlayer]):
        """Services → All other players"""
        services_player = players['services']
        
        # All other players buy some services
        for player_name, player in players.items():
            if player_name != 'services' and player.money > 50:
                service_demand = min(player.money * 0.1, 30)  # 10% of money on services
                
                if service_demand > 0:
                    # Simple service transaction
                    player.money -= service_demand
                    services_player.money += service_demand

    def clear_labor_market(self, players: Dict[str, BasePlayer]):
        """Consumer provides labor to other sectors"""
        consumer_player = players['consumer']
        
        # Each sector pays for labor
        total_wages = 0
        for player_name, player in players.items():
            if player_name != 'consumer' and player.money > 100:
                wages = min(player.money * 0.2, 200)  # 20% goes to wages
                total_wages += wages
                player.money -= wages
        
        # Consumer receives wages
        consumer_player.money += total_wages

    def update_phase(self, players: Dict[str, BasePlayer]):
        """Update inventories, track macro indicators, reset temporary flags."""
        for player in players.values():
            player.update_after_market()

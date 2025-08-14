# core/turn_manager.py

from typing import Dict
from .base_player import BasePlayer

class TurnManager:
    """
    Manages the sequence of phases in each game turn.
    For MVP: 3-phase turn (Production, Market, Update).
    Extendable to 5-phase as per full design.
    """

    def __init__(self):
        # List of phase methods in order
        self.phases = [
            self.production_phase,
            self.market_phase,
            self.update_phase,
        ]
        # For full 5-phase, uncomment the next lines:
        # self.phases = [
        #     self.planning_phase,
        #     self.production_phase,
        #     self.market_phase,
        #     self.consumption_phase,
        #     self.end_of_turn_phase,
        # ]

    def clear_markets(self, players: Dict[str, BasePlayer]):
        """
        Placeholder for simple market clearing logic.
        In full version, this invokes MarketSystem for each market.
        """
        # Example: collect all supply/demand, compute prices, execute trades
        pass

    def execute_turn(self, players: Dict[str, BasePlayer]):
        """
        Execute all phases in sequence for one turn.
        """
        for phase in self.phases:
            phase(players)

    # MVP Phases

    def production_phase(self, players: Dict[str, BasePlayer]):
        """
        Each player produces goods or services.
        """
        for player in players.values():
            player.produce()

    def market_phase(self, players: Dict[str, BasePlayer]):
        """
        Clear markets: match supply and demand at uniform prices.
        """
        self.clear_markets(players)

    def update_phase(self, players: Dict[str, BasePlayer]):
        """
        Update inventories, track macro indicators, reset temporary flags.
        """
        for player in players.values():
            player.update_after_market()

    # Full 5-phase placeholders

    def planning_phase(self, players: Dict[str, BasePlayer]):
        """
        Phase 1: Players plan investments, R&D, budgets.
        """
        for player in players.values():
            player.plan()

    def consumption_phase(self, players: Dict[str, BasePlayer]):
        """
        Phase 4: Consumers decide spending; other players consume inputs.
        """
        for player in players.values():
            player.consume()

    def end_of_turn_phase(self, players: Dict[str, BasePlayer]):
        """
        Phase 5: Handle events, shocks, and turn-based clean-up.
        """
        # e.g., advance event scheduler, apply seasonal cycles
        pass

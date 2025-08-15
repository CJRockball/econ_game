from typing import Dict, List
from .economic_state import EconomicState
from .turn_manager import TurnManager

# Safe imports with error handling
try:
    from players.raw_materials import RawMaterialsPlayer
    from players.manufacturing import ManufacturingPlayer
    from players.services import ServicesPlayer
    from players.consumer import ConsumerPlayer
    from players.financial import FinancialPlayer
    from players.government import GovernmentPlayer
    from players.central_bank import CentralBankPlayer
except ImportError as e:
    print(f"Warning: Could not import player: {e}")

class GameEngine:
    """
    Enhanced game engine with transaction-based inflation tracking.
    """
    
    def __init__(self):
        self.economic_state = EconomicState()
        self.turn_manager = TurnManager()
        self.players = self._create_players()
        self.current_turn = 0
        
        # Game configuration
        self.central_bank_mode = "ai"  # "ai" or "democratic"
        self.max_turns = 100
        self.recent_events = []  # Initialize events list
        
    def _create_players(self) -> Dict[str, object]:
        """Create all player types with safe instantiation."""
        players = {}
        
        # Create players with error handling
        try:
            players['raw_materials'] = RawMaterialsPlayer("Raw Materials Co.")
        except:
            print("Warning: Could not create raw materials player")
            
        try:
            players['manufacturing'] = ManufacturingPlayer("Manufacturing Corp.")
        except:
            print("Warning: Could not create manufacturing player")
            
        try:
            players['services'] = ServicesPlayer("Services Inc.")
        except:
            print("Warning: Could not create services player")
            
        try:
            players['consumer'] = ConsumerPlayer("Households")
        except:
            print("Warning: Could not create consumer player")
            
        try:
            players['financial'] = FinancialPlayer("National Bank")
        except:
            print("Warning: Could not create financial player")
            
        try:
            players['government'] = GovernmentPlayer("Government")
        except:
            print("Warning: Could not create government player")
            
        try:
            players['central_bank'] = CentralBankPlayer("Federal Reserve")
            # Set central bank governance mode
            if hasattr(players['central_bank'], 'governance_mode'):
                players['central_bank'].governance_mode = self.central_bank_mode
        except:
            print("Warning: Could not create central bank player")
        
        return players
    
    def set_central_bank_mode(self, mode: str):
        """Set central bank governance mode - SAFE ACCESS."""
        if mode in ["ai", "democratic"]:
            self.central_bank_mode = mode
            central_bank = self.players.get('central_bank')
            if central_bank and hasattr(central_bank, 'governance_mode'):
                central_bank.governance_mode = mode
    
    def vote_on_fed_funds_rate(self, player_votes: Dict[str, float]) -> float:
        """Process democratic vote on Fed Funds Rate - SAFE ACCESS."""
        central_bank = self.players.get('central_bank')
        
        if (self.central_bank_mode == "democratic" and 
            player_votes and central_bank and 
            hasattr(central_bank, 'set_democratic_policy')):
            
            # Simple majority vote - average for now
            rates = list(player_votes.values())
            voted_rate = sum(rates) / len(rates) if rates else 0.025
            
            # Set the rate
            central_bank.set_democratic_policy(voted_rate)
            return voted_rate
        
        # Return current rate if voting failed
        if central_bank and hasattr(central_bank, 'fed_funds_rate'):
            return central_bank.fed_funds_rate
        return 0.025
    
    def start_new_game(self):
        """Initialize a new game with safe setup."""
        self.current_turn = 0
        self.economic_state.reset()
        self.recent_events.clear()
        
        # Reset all players safely
        for player in self.players.values():
            if hasattr(player, 'reset'):
                player.reset()
            
        # Initialize financial relationships safely
        financial_player = self.players.get('financial')
        central_bank = self.players.get('central_bank')
        
        if (central_bank and financial_player and 
            hasattr(central_bank, 'fed_funds_rate') and
            hasattr(financial_player, 'update_fed_funds_rate')):
            # Set initial Fed Funds Rate
            financial_player.update_fed_funds_rate(central_bank.fed_funds_rate)
        
        # Give financial player initial reserves
        if financial_player and hasattr(financial_player, 'reserves'):
            financial_player.reserves = 10000.0
        
    def advance_turn(self):
        """Execute one complete turn with transaction-based economic tracking."""
        # Update central bank with current economic conditions
        central_bank = self.players.get('central_bank')
        if (central_bank and 
            hasattr(central_bank, 'update_economic_indicators')):
            central_bank.update_economic_indicators(self.economic_state)
        
        # Execute all turn phases
        self.turn_manager.execute_turn(self.players)
        
        # Calculate total GDP for tax collection (exclude central bank)
        total_gdp = 0.0
        for player_name, player in self.players.items():
            if (player_name != 'central_bank' and 
                hasattr(player, 'production_value')):
                total_gdp += getattr(player, 'production_value', 0.0)
        
        # Government collects taxes
        government_player = self.players.get('government')
        if government_player and hasattr(government_player, 'collect_taxes'):
            government_player.collect_taxes(total_gdp)
        
        # Update economic state with turn manager for transaction prices
        self.economic_state.update(self.players, self.turn_manager)
        
        # Increment turn counter
        self.current_turn += 1
        
        # Log significant economic events
        self._log_economic_events()
    
    def _log_economic_events(self):
        """Log significant economic events for educational purposes."""
        events = []
        
        # Check for significant changes safely
        if len(self.economic_state.inflation_history) > 1:
            current_inflation = self.economic_state.inflation_rate
            previous_inflation = self.economic_state.inflation_history[-2]
            inflation_change = current_inflation - previous_inflation
            
            if abs(inflation_change) > 0.01:  # 1% change
                direction = 'surged' if inflation_change > 0 else 'dropped'
                events.append(f"Inflation {direction} by {inflation_change:.2%}")
        
        if len(self.economic_state.m2_history) > 1:
            current_money = self.economic_state.money_supply
            previous_money = self.economic_state.m2_history[-2]
            if previous_money > 0:
                money_growth = (current_money - previous_money) / previous_money
                if abs(money_growth) > 0.05:  # 5% change
                    direction = 'expanded' if money_growth > 0 else 'contracted'
                    events.append(f"Money supply {direction} by {money_growth:.1%}")
        
        # Check for significant price level changes
        if len(self.economic_state.price_history) > 1:
            current_prices = self.economic_state.price_level
            previous_prices = self.economic_state.price_history[-2]
            if previous_prices > 0:
                price_change = (current_prices - previous_prices) / previous_prices
                if abs(price_change) > 0.02:  # 2% change in price level
                    direction = 'rose' if price_change > 0 else 'fell'
                    events.append(f"Price level {direction} by {price_change:.1%}")
        
        # Store events for UI display (keep last 5 events)
        self.recent_events.extend(events)
        self.recent_events = self.recent_events[-5:]
    
    def get_state(self) -> Dict:
        """Get comprehensive game state for API/UI - SAFE ACCESS."""
        try:
            economic_indicators = self.economic_state.get_economic_indicators()
        except:
            economic_indicators = {}
        
        # Get player statuses safely
        players_status = {}
        for name, player in self.players.items():
            try:
                if hasattr(player, 'get_status'):
                    players_status[name] = player.get_status()
                else:
                    players_status[name] = {'name': getattr(player, 'name', name), 'error': 'No status method'}
            except Exception as e:
                players_status[name] = {'name': name, 'error': str(e)}
        
        # Add current market prices to player status
        try:
            raw_materials_player = self.players.get('raw_materials')
            if raw_materials_player and hasattr(raw_materials_player, 'current_price'):
                players_status['raw_materials']['current_price'] = round(raw_materials_player.current_price, 2)
                
            manufacturing_player = self.players.get('manufacturing')  
            if manufacturing_player and hasattr(manufacturing_player, 'current_price'):
                players_status['manufacturing']['current_price'] = round(manufacturing_player.current_price, 2)
                
            services_player = self.players.get('services')
            if services_player and hasattr(services_player, 'current_price'):
                players_status['services']['current_price'] = round(services_player.current_price, 2)
        except:
            pass  # Price info is optional
        
        state = {
            'turn': self.current_turn,
            'central_bank_mode': self.central_bank_mode,
            'economic_indicators': economic_indicators,
            'players': players_status,
            'recent_events': getattr(self, 'recent_events', [])
        }
        
        # Add historical data for charts - with safe access
        try:
            state.update({
                'gdp_history': getattr(self.economic_state, 'gdp_history', []),
                'm2_history': getattr(self.economic_state, 'm2_history', []),
                'inflation_history': getattr(self.economic_state, 'inflation_history', []),
                'employment_history': getattr(self.economic_state, 'employment_history', []),
                'velocity_history': getattr(self.economic_state, 'velocity_history', []),
                'interest_rate_history': getattr(self.economic_state, 'interest_rate_history', []),
                'price_history': getattr(self.economic_state, 'price_history', [])
            })
        except:
            pass  # History data is optional
        
        return state
    
    def get_all_players(self) -> Dict:
        """Get all players for template rendering - SAFE ACCESS."""
        result = {}
        for name, player in self.players.items():
            try:
                if hasattr(player, 'get_status'):
                    result[name] = player.get_status()
                else:
                    result[name] = {'name': getattr(player, 'name', name)}
            except Exception as e:
                result[name] = {'name': name, 'error': str(e)}
        return result
    
    def get_central_bank_policy_options(self) -> Dict:
        """Get policy options for central bank voting - SAFE ACCESS."""
        central_bank = self.players.get('central_bank')
        if not (central_bank and hasattr(central_bank, 'taylor_rule_recommendation')):
            return {
                'current_rate': 0.025,
                'taylor_rule_rate': 0.025,
                'options': [{'rate': 0.025, 'description': '2.5% (Default)'}],
                'policy_explanation': 'Central bank not available'
            }
        
        try:
            taylor_rate = central_bank.taylor_rule_recommendation()
            current_rate = getattr(central_bank, 'fed_funds_rate', 0.025)
            
            # Suggest rate options around Taylor Rule recommendation
            options = []
            for adjustment in [-0.0050, -0.0025, 0.0000, 0.0025, 0.0050]:
                rate = max(0.0, min(0.08, taylor_rate + adjustment))
                description = f"{rate:.2%}"
                if adjustment < 0:
                    description += " (Lower)"
                elif adjustment > 0:
                    description += " (Higher)"
                else:
                    description += " (Taylor Rule)"
                options.append({'rate': rate, 'description': description})
            
            policy_explanation = "Policy options available"
            if hasattr(central_bank, 'get_policy_explanation'):
                policy_explanation = central_bank.get_policy_explanation()
            
            return {
                'current_rate': current_rate,
                'taylor_rule_rate': taylor_rate,
                'options': options,
                'policy_explanation': policy_explanation
            }
        except Exception as e:
            return {
                'current_rate': 0.025,
                'taylor_rule_rate': 0.025,
                'options': [{'rate': 0.025, 'description': '2.5% (Error)'}],
                'policy_explanation': f'Error getting policy options: {e}'
            }
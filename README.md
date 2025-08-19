# Economic Simulation Game

A comprehensive economic simulation game built in Python that models a complex market economy with multiple interacting players. The simulation features monetary policy through central bank operations, banking systems with fractional reserve lending, and various economic sectors competing in dynamic markets.

## Features

### Economic Players
- **Raw Materials Player**: Extracts and supplies base materials to manufacturing
- **Manufacturing Player**: Converts raw materials into finished goods with adaptive production
- **Services Player**: Provides service-based economic activities
- **Consumer Player**: Represents household consumption with employment-responsive behavior
- **Financial Player**: Implements fractional reserve banking with money creation through lending
- **Government Player**: Collects taxes and provides government services
- **Central Bank Player**: Controls monetary policy using the Taylor Rule for interest rate setting

### Key Economic Mechanics

#### Monetary Policy
- **Taylor Rule Implementation**: Central bank adjusts Fed Funds Rate based on inflation target and output gap
- **Dual Governance Modes**: 
  - AI-controlled: Automatic policy using Taylor Rule calculations
  - Democratic: Player voting on interest rate decisions
- **Interest Rate Transmission**: Commercial bank rates adjust based on Fed Funds Rate with realistic pass-through coefficients

#### Banking System
- **Fractional Reserve Banking**: Banks create money through lending with 10% reserve requirements
- **Dynamic Money Supply**: M2 money supply expands and contracts based on loan creation and repayments
- **Credit Risk Assessment**: Lending decisions based on borrower credit ratings
- **Interest Rate Spreads**: Commercial rates include risk premiums over Fed Funds Rate

#### Market Dynamics
- **Price Discovery**: Market clearing mechanisms determine transaction prices
- **Employment Feedback**: Employment rates influence consumer spending confidence
- **Demand-Adaptive Production**: Firms adjust output based on realized sales
- **Investment in Technology**: Players can invest in R&D to improve productivity

#### Economic Indicators
- **GDP Calculation**: C + I + G + (X-M) components with detailed tracking
- **Inflation Measurement**: Consumer Price Index based on actual transaction prices
- **Employment Modeling**: Labor demand-based employment calculation
- **Money Velocity**: Tracks velocity of money circulation (MV = PY)

## Technology Stack

- **Backend**: FastAPI web framework with WebSocket support
- **Frontend**: HTML/CSS/JavaScript with real-time dashboard
- **Dependencies**: 
  - FastAPI 0.104.1
  - Uvicorn 0.24.0 (ASGI server)
  - Pydantic 2.5.0 (data validation)
  - Jinja2 3.1.2 (templating)
  - WebSockets 12.0 (real-time communication)
  - Python-SocketIO 5.10.0 (real-time features)

## Project Structure

```
econ_game/
├── core/                    # Core game mechanics
│   ├── game_engine.py      # Main game orchestration
│   ├── economic_state.py   # Economic indicators and state management
│   ├── turn_manager.py     # Turn execution and market clearing
│   └── base_player.py      # Base player class with common functionality
├── players/                # Economic player implementations
│   ├── raw_materials.py   # Raw materials extraction
│   ├── manufacturing.py   # Manufacturing with adaptive production
│   ├── services.py        # Service sector player
│   ├── consumer.py        # Household consumption
│   ├── financial.py       # Banking and lending
│   ├── government.py      # Government operations
│   └── central_bank.py    # Monetary policy implementation
├── markets/               # Market mechanisms (if implemented)
├── api/                   # API endpoints
├── utils/                 # Utility functions
├── web/                   # Web interface
│   └── templates/
│       └── dashboard.html # Real-time economic dashboard
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CJRockball/econ_game.git
   cd econ_game
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the dashboard**:
   - Open your browser to `http://localhost:8000`
   - The dashboard provides real-time monitoring of economic indicators

## How to Use

### Basic Gameplay
1. **Start a New Game**: Initialize the economy with default parameters
2. **Advance Turns**: Each turn represents one economic period where:
   - Players produce goods/services based on available resources
   - Markets clear and prices are determined
   - Economic indicators are updated
   - Policy decisions may be made

### Central Bank Operations
- **AI Mode**: Central bank automatically adjusts rates using Taylor Rule
- **Democratic Mode**: Players can vote on Fed Funds Rate decisions
- Policy changes affect commercial bank rates and overall economic activity

### Monitoring the Economy
The dashboard displays:
- **Key Indicators**: GDP, inflation, employment, money supply
- **Central Bank Policy**: Current rates and policy stance
- **Financial Sector**: Banking capacity, loan creation, interest rates
- **Player Status**: Individual player performance and resources
- **Historical Charts**: Track economic trends over time

## Educational Value

This simulation demonstrates:
- **Monetary Policy Transmission**: How central bank decisions affect the broader economy
- **Banking Operations**: Money creation through fractional reserve lending
- **Market Interactions**: Price discovery and resource allocation
- **Economic Feedback Loops**: Employment affects consumption affects production
- **Policy Trade-offs**: Inflation vs. employment considerations in monetary policy

## Technical Highlights

### Advanced Economic Modeling
- **Taylor Rule**: `rate = neutral_rate + 1.5*(inflation - target) + 0.5*output_gap`
- **Money Multiplier**: `max_lending = excess_reserves / reserve_ratio`
- **CPI Calculation**: Weighted basket of goods with transaction-based pricing
- **Employment Model**: Labor demand-driven with smooth adjustment mechanisms

### Real-time Web Interface
- WebSocket connections for live economic data streaming
- Interactive charts showing historical trends
- Policy voting interface for democratic central bank mode
- Comprehensive player status monitoring

### Robust Error Handling
- Safe attribute access patterns throughout codebase
- Graceful degradation when optional features unavailable
- Comprehensive status reporting with error tracking

## Development Notes

The codebase demonstrates sophisticated software engineering practices:
- **Modular Architecture**: Clear separation between game logic, players, and presentation
- **Safe Programming**: Extensive use of `getattr()` and `hasattr()` for robust attribute access
- **Extensible Design**: Easy to add new player types or economic mechanisms
- **Real-time Features**: WebSocket integration for dynamic dashboard updates

## Contributing

This project provides an excellent foundation for:
- Economic education and simulation
- Game theory research
- Monetary policy experimentation
- Full-stack web development with real-time features

The modular design makes it easy to extend with new economic sectors, policy tools, or market mechanisms.

## License

This project appears to be a educational/research tool for understanding economic principles through interactive simulation. The comprehensive implementation covers fundamental macroeconomic concepts while providing an engaging user experience through modern web technologies.
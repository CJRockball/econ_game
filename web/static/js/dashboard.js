class EconomicDashboard {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        
        this.initializeWebSocket();
        this.setupEventListeners();
    }
    
    initializeWebSocket() {
        try {
            this.socket = new WebSocket(`ws://${window.location.host}/ws`);
            
            this.socket.onopen = () => {
                console.log('WebSocket connected');
                document.getElementById('ws-status').textContent = 'connected';
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.updateDashboard(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.socket.onclose = () => {
                console.log('WebSocket disconnected');
                document.getElementById('ws-status').textContent = 'disconnected';
                this.attemptReconnect();
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                document.getElementById('ws-status').textContent = 'error';
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            document.getElementById('ws-status').textContent = 'failed';
            this.attemptReconnect();
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${this.reconnectDelay}ms`);
            
            setTimeout(() => {
                this.initializeWebSocket();
            }, this.reconnectDelay);
            
            // Exponential backoff
            this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 10000);
        } else {
            console.log('Max reconnection attempts reached');
            document.getElementById('ws-status').textContent = 'failed';
        }
    }
    
    setupEventListeners() {
        // Central bank mode switching
        document.getElementById('ai-mode')?.addEventListener('click', () => {
            this.setCentralBankMode('ai');
        });
        
        document.getElementById('democratic-mode')?.addEventListener('click', () => {
            this.setCentralBankMode('democratic');
        });
    }
    
    setCentralBankMode(mode) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action: 'set_mode',
                mode: mode
            }));
        }
    }
    
    updateDashboard(data) {
        try {
            // Update turn and mode
            this.updateElement('current-turn', data.turn || 0);
            this.updateElement('bank-mode', data.central_bank_mode || 'ai');
            
            // Update economic indicators
            const indicators = data.economic_indicators || {};
            this.updateElement('gdp', this.formatNumber(indicators.gdp || 0));
            this.updateElement('inflation', `${indicators.inflation_rate || 0}%`);
            this.updateElement('employment', `${indicators.employment_rate || 0}%`);
            this.updateElement('money-supply', this.formatNumber(indicators.money_supply || 0));
            this.updateElement('velocity', indicators.money_velocity || 0);
            this.updateElement('price-level', indicators.price_level || 1.00);
            this.updateElement('new-money', this.formatNumber(indicators.new_money_created || 0));
            
            // Update central bank info
            const centralBank = data.players?.central_bank || {};
            this.updateElement('cb-fed-funds', this.formatPercentage(centralBank.fed_funds_rate));
            this.updateElement('taylor-rule', this.formatPercentage(centralBank.taylor_rule_rate));
            this.updateElement('discount-rate', this.formatPercentage(centralBank.discount_rate));
            this.updateElement('governance', centralBank.governance_mode || 'ai');
            this.updateElement('policy-explanation', centralBank.policy_explanation || '—');
            
            // Update financial sector
            const financial = data.players?.financial || {};
            this.updateElement('commercial-rate', this.formatPercentage(financial.commercial_rate));
            this.updateElement('deposit-rate', this.formatPercentage(financial.deposit_rate));
            this.updateElement('lending-capacity', this.formatNumber(financial.banking_capacity));
            this.updateElement('deposits', this.formatNumber(financial.total_deposits));
            this.updateElement('loans-outstanding', this.formatNumber(financial.loans_outstanding));
            this.updateElement('new-loans', this.formatNumber(financial.new_loans_this_turn));
            
            // NEW: Update labor market and government info
            const consumer = data.players?.consumer || {};
            const government = data.players?.government || {};
            this.updateElement('unit-wage', this.formatNumber(consumer.current_unit_wage || consumer.income_rate || 0));
            this.updateElement('employment-confidence', (consumer.consumption_confidence || 1.0).toFixed(3));
            this.updateElement('tax-rate', `${government.tax_rate || 0}%`);
            this.updateElement('tax-revenue', this.formatNumber(government.tax_revenue_collected || 0));
            this.updateElement('gov-spending', this.formatNumber(government.government_spending || 0));
            this.updateElement('public-debt', this.formatNumber(government.public_debt || 0));
            
            // Update fed funds rate in main indicators
            this.updateElement('fed-funds-rate', this.formatPercentage(centralBank.fed_funds_rate));
            
            // Update events
            this.updateEvents(data.recent_events || []);
            
            // Update players
            this.updatePlayers(data.players || {});
            
            // Update histories
            this.updateHistories(data);
            
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }
    
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    formatNumber(num) {
        if (num === null || num === undefined || num === '—') return '—';
        if (typeof num !== 'number') return num;
        
        if (Math.abs(num) >= 1000) {
            return num.toLocaleString('en-US', { maximumFractionDigits: 0 });
        }
        return num.toFixed(1);
    }
    
    formatPercentage(num) {
        if (num === null || num === undefined || num === '—') return '—';
        if (typeof num !== 'number') return num;
        return `${(num * 100).toFixed(2)}%`;
    }
    
    updateEvents(events) {
        const eventsList = document.getElementById('events-list');
        if (eventsList) {
            eventsList.innerHTML = events.length > 0 
                ? events.map(event => `<div class="event">${event}</div>`).join('')
                : '<div class="event">No recent events</div>';
        }
    }
    
    updatePlayers(players) {
        const playersGrid = document.getElementById('players-grid');
        if (!playersGrid) return;
        
        playersGrid.innerHTML = '';
        
        Object.entries(players).forEach(([name, player]) => {
            const playerCard = document.createElement('div');
            playerCard.className = 'player-card';
            
            // Format inventory with 0 decimal places
            const inventoryHtml = Object.entries(player.inventory || {})
                .map(([item, amount]) => {
                    const formattedAmount = typeof amount === 'number' ? Math.round(amount) : amount;
                    return `<div>${item}: ${formattedAmount}</div>`;
                })
                .join('');
            
            playerCard.innerHTML = `
                <h3>${player.name || name}</h3>
                <div class="player-stats">
                    <div>Money: $${this.formatNumber(player.money || 0)}</div>
                    <div>Labor: ${(player.labor || 0).toFixed(1)}</div>
                    <div>Production: $${this.formatNumber(player.production_value || 0)}</div>
                    <div>Tech Level: ${(player.technology_level || 1).toFixed(3)}</div>
                </div>
                <div class="player-inventory">
                    <h4>Inventory:</h4>
                    ${inventoryHtml || '<div>Empty</div>'}
                </div>
            `;
            
            playersGrid.appendChild(playerCard);
        });
    }
    
    updateHistories(data) {
        this.updateElement('gdp-history', JSON.stringify(data.gdp_history || []));
        this.updateElement('m2-history', JSON.stringify(data.m2_history || []));
        this.updateElement('inflation-history', JSON.stringify(data.inflation_history || []));
        this.updateElement('employment-history', JSON.stringify(data.employment_history || []));
        this.updateElement('velocity-history', JSON.stringify(data.velocity_history || []));
        this.updateElement('rates-history', JSON.stringify(data.interest_rate_history || []));
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new EconomicDashboard();
});
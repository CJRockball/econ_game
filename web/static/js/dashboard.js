// web/static/js/dashboard.js - REPLACE ENTIRELY
let gdpData = [];
let inflationData = [];
let lastTurn = -1;
let gdpChart;
let ws;

// Initialize WebSocket connection
function initWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        // Ignore heartbeat messages
        if (data.type === 'heartbeat') return;
        
        updateDashboard(data);
    };

    ws.onclose = function() {
        console.log("WebSocket connection closed. Attempting to reconnect...");
        setTimeout(() => {
            initWebSocket();
        }, 3000);
    };

    ws.onerror = function(error) {
        console.log("WebSocket error:", error);
    };
}

function updateDashboard(gameState) {
    // Only update chart when turn actually changes
    if (gameState.turn !== lastTurn) {
        gdpData.push(gameState.gdp);
        inflationData.push(gameState.inflation * 100);
        lastTurn = gameState.turn;
        updateChart();
    }

    // Always update current values with animations
    animateValue('current-turn', gameState.turn);
    animateValue('gdp', '$' + gameState.gdp.toLocaleString());
    animateValue('inflation', (gameState.inflation * 100).toFixed(1) + '%');
    animateValue('employment', gameState.employment.toFixed(1) + '%');
    
    // Update player panels with enhanced data
    updatePlayerPanels(gameState.players);
}

function animateValue(elementId, newValue) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.transform = 'scale(1.05)';
        element.textContent = newValue;
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }
}

function updatePlayerPanels(players) {
    for (const [playerName, playerData] of Object.entries(players)) {
        const panel = document.getElementById(`player-${playerName}`);
        if (panel) {
            // Update money with color coding
            const moneyElement = panel.querySelector('.money');
            const money = playerData.money;
            moneyElement.textContent = '$' + money.toLocaleString();
            moneyElement.style.color = money > 5000 ? '#4CAF50' : money > 1000 ? '#FF9800' : '#f44336';
            
            // Update production with trend indicator
            const productionElement = panel.querySelector('.production');
            productionElement.textContent = '$' + playerData.production_value.toLocaleString();
            
            // Update inventory with better formatting
            const inventoryDiv = panel.querySelector('.inventory-items');
            inventoryDiv.innerHTML = '';
            
            if (Object.keys(playerData.inventory).length === 0) {
                const emptySpan = document.createElement('span');
                emptySpan.className = 'inventory-item';
                emptySpan.textContent = 'No items';
                emptySpan.style.fontStyle = 'italic';
                emptySpan.style.color = '#999';
                inventoryDiv.appendChild(emptySpan);
            } else {
                for (const [item, quantity] of Object.entries(playerData.inventory)) {
                    const span = document.createElement('span');
                    span.className = 'inventory-item';
                    const displayName = item.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    span.textContent = `${displayName}: ${typeof quantity === 'number' ? quantity.toFixed(1) : quantity}`;
                    inventoryDiv.appendChild(span);
                }
            }
        }
    }
}

function startGame() {
    // Add loading state
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
    button.disabled = true;
    
    fetch('/api/game/start', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            console.log('Game started:', data);
            // Clear previous data
            gdpData = [];
            inflationData = [];
            lastTurn = -1;
            updateChart();
            
            // Show success animation
            button.innerHTML = '<i class="fas fa-check"></i> Started!';
            button.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 2000);
        })
        .catch(error => {
            console.error('Error starting game:', error);
            button.innerHTML = originalText;
            button.disabled = false;
        });
}

function advanceTurn() {
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    button.disabled = true;
    
    fetch('/api/game/advance_turn', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            console.log('Turn advanced:', data);
            
            // Show success animation
            button.innerHTML = '<i class="fas fa-check"></i> Advanced!';
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 1000);
        })
        .catch(error => {
            console.error('Error advancing turn:', error);
            button.innerHTML = originalText;
            button.disabled = false;
        });
}

// Initialize chart with better styling
function initChart() {
    const ctx = document.getElementById('gdpChart').getContext('2d');
    gdpChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'GDP ($)',
                data: gdpData,
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'GDP ($)',
                        color: '#666',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        color: '#666',
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Turn',
                        color: '#666',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        color: '#666'
                    }
                }
            },
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function updateChart() {
    if (gdpChart) {
        gdpChart.data.labels = gdpData.map((_, i) => `Turn ${i + 1}`);
        gdpChart.data.datasets[0].data = gdpData;
        gdpChart.update('active');
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    initWebSocket();
    initChart();
    
    // Add smooth transitions to all elements
    document.querySelectorAll('.indicator-card, .player-card').forEach(card => {
        card.style.transition = 'all 0.3s ease';
    });
});

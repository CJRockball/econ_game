// web/static/js/dashboard.js
let gdpData = [];
let inflationData = [];
let lastTurn = -1;
let gdpChart;

// WebSocket connection
let ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = function(event) {
    const gameState = JSON.parse(event.data);
    updateDashboard(gameState);
};

ws.onclose = function() {
    console.log("WebSocket connection closed. Attempting to reconnect...");
    setTimeout(() => {
        ws = new WebSocket(`ws://${window.location.host}/ws`);
    }, 3000);
};

function updateDashboard(gameState) {
    // Only update when turn actually changes
    if (gameState.turn !== lastTurn) {
        gdpData.push(gameState.gdp);
        inflationData.push(gameState.inflation * 100);
        lastTurn = gameState.turn;
        updateChart();
    }

    // Always update current values
    document.getElementById('current-turn').textContent = gameState.turn;
    document.getElementById('gdp').textContent = '$' + gameState.gdp.toLocaleString();
    document.getElementById('inflation').textContent = (gameState.inflation * 100).toFixed(1) + '%';
    
    // Update player panels
    updatePlayerPanels(gameState.players);
}

function updatePlayerPanels(players) {
    // Update each player panel with current data
    for (const [playerName, playerData] of Object.entries(players)) {
        const panel = document.getElementById(`player-${playerName}`);
        if (panel) {
            panel.querySelector('.money').textContent = '$' + playerData.money.toLocaleString();
            panel.querySelector('.production').textContent = '$' + playerData.production_value.toLocaleString();
            
            // Update inventory display
            const inventoryDiv = panel.querySelector('.inventory');
            inventoryDiv.innerHTML = '';
            for (const [item, quantity] of Object.entries(playerData.inventory)) {
                const span = document.createElement('span');
                span.className = 'inventory-item';
                span.textContent = `${item}: ${quantity.toFixed(1)}`;
                inventoryDiv.appendChild(span);
            }
        }
    }
}

function startGame() {
    fetch('/api/game/start', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            console.log('Game started:', data);
            // Clear previous data
            gdpData = [];
            inflationData = [];
            lastTurn = -1;
            updateChart();
        });
}

function advanceTurn() {
    fetch('/api/game/advance_turn', {method: 'POST'})
        .then(response => response.json())
        .then(data => console.log('Turn advanced:', data));
}

// Initialize GDP chart
const ctx = document.getElementById('gdpChart').getContext('2d');
gdpChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'GDP ($)',
            data: gdpData,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            tension: 0.1,
            fill: true
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'GDP ($)'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Turn'
                }
            }
        }
    }
});

function updateChart() {
    gdpChart.data.labels = gdpData.map((_, i) => `Turn ${i + 1}`);
    gdpChart.data.datasets[0].data = gdpData;
    gdpChart.update();
}

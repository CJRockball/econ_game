let gdpData = [];
let ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = function(event) {
    const gameState = JSON.parse(event.data);
    updateDashboard(gameState);
};

function updateDashboard(gameState) {
    document.getElementById('current-turn').textContent = gameState.turn;
    document.getElementById('gdp').textContent = '$' + gameState.gdp.toLocaleString();
    document.getElementById('inflation').textContent = (gameState.inflation * 100).toFixed(1) + '%';
    
    if (gameState.turn !== lastTurn) {
        gdpData.push(gameState.gdp);
        lastTurn = gameState.turn;
    }
    document.getElementById('current-turn').textContent = gameState.turn;
    document.getElementById('gdp').textContent = '$' + gameState.gdp.toLocaleString();
    document.getElementById('inflation').textContent = (gameState.inflation * 100).toFixed(1) + '%';

    updateChart();
}

function startGame() {
    fetch('/api/game/start', {method: 'POST'})
        .then(response => response.json())
        .then(data => console.log('Game started:', data));
}

function advanceTurn() {
    fetch('/api/game/advance_turn', {method: 'POST'})
        .then(response => response.json())
        .then(data => console.log('Turn advanced:', data));
}

// Initialize GDP chart
const ctx = document.getElementById('gdpChart').getContext('2d');
const gdpChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'GDP',
            data: gdpData,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    }
});

function updateChart() {
    gdpChart.data.labels = gdpData.map((_, i) => `Turn ${i + 1}`);
    gdpChart.update();
}

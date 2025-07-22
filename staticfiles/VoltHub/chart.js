const ctx = document.getElementById('energyChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Session 1', 'Session 2', 'Session 3', 'Session 4'],
        datasets: [{
            label: 'Energy (kwh)',
            data: [8, 15, 18, 4],
            backgroundColor:
            'rgba(75, 91, 192, 0.2)',
            borderColor:
            'rgb(87, 75, 192)',
            borderWidth: 1
        
        }]
    },
    options: {
        scales:{
            y:{
                beginAtZero: true
            }
        }
    }
});

async function fetchAnalyticsData() {
    try {
        const response = await fetch('/analytics/');
        if (!response.ok) {
            throw new Error('Failed to fetch analytics data');
        }
        const data = await response.json();
        updateChart(data);
    } catch (error) {
        console.error('Error fetching analytics data:', error);
    }
}

function updateChart(data) {
    const labels = data.map(item => item.station);
    const energyData = data.map(item => item.total_energy_consumed);

    chart.data.labels = labels;
    chart.data.datasets[0].data = energyData;
    chart.update();
}

// Fetch data initially and set an interval for live updates
fetchAnalyticsData();
setInterval(fetchAnalyticsData, 30000); // Update every 30 seconds
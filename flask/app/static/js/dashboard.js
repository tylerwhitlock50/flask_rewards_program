function renderEarningChart(data) {
    const ctx = document.getElementById('topEarnersChart').getContext('2d');

    const labels = data.map(user => user.username);
    const points = data.map(user => user.total_points);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Points Earned',
                data: points,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderPointsByMonthChart(data) {
    const ctx = document.getElementById('pointsByMonthChart').getContext('2d');
    const labels = data.map(entry => entry.month);
    const points = data.map(entry => entry.points);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Points Earned',
                data: points,
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                borderColor: 'rgba(153, 102, 255, 1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderEarningChart(data) {
    const ctx = document.getElementById('topEarnersChart').getContext('2d');

    const labels = data.map(user => user[0]);
    const points = data.map(user => user[1]);

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

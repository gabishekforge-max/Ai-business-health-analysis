document.addEventListener("DOMContentLoaded", function () {
    const revElem = document.getElementById('rev-data');
    if (revElem) {
        const data = JSON.parse(revElem.textContent);
        new Chart(document.getElementById('revChart'), {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Revenue (₹)',
                    data: data.values,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            }
        });
    }

    const catElem = document.getElementById('cat-data');
    if (catElem) {
        const data = JSON.parse(catElem.textContent);
        new Chart(document.getElementById('catChart'), {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#0dcaf0']
                }]
            }
        });
    }

    const forecastElem = document.getElementById('forecast-data');
    if (forecastElem) {
        const data = JSON.parse(forecastElem.textContent);
        const combinedLabels = [...data.dates, ...data.forecast_dates];
        const historicalPoints = [...data.historical, ...Array(data.forecast.length).fill(null)];
        const lastHist = data.historical[data.historical.length - 1];
        const forecastPoints = [...Array(data.historical.length - 1).fill(null), lastHist, ...data.forecast];

        new Chart(document.getElementById('forecastChart'), {
            type: 'line',
            data: {
                labels: combinedLabels,
                datasets: [
                    {
                        label: 'Historical Revenue',
                        data: historicalPoints,
                        borderColor: '#0d6efd',
                        borderWidth: 2
                    },
                    {
                        label: 'Predicted Revenue (ML Model)',
                        data: forecastPoints,
                        borderColor: '#dc3545',
                        borderDash: [5, 5],
                        borderWidth: 2
                    }
                ]
            }
        });
    }

    const marginElem = document.getElementById('cat-margin-data');
    if (marginElem) {
        const data = JSON.parse(marginElem.textContent);
        new Chart(document.getElementById('catMarginChart'), {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Avg Profit Margin (%)',
                    data: data.values,
                    backgroundColor: '#198754'
                }]
            }
        });
    }

    const profElem = document.getElementById('prof-data');
    if (profElem) {
        const data = JSON.parse(profElem.textContent);
        new Chart(document.getElementById('profChart'), {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Profit (₹)',
                    data: data.values,
                    borderColor: '#198754',
                    fill: false
                }]
            }
        });
    }
});
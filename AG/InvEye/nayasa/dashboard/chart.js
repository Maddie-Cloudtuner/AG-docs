// ===================================
// InvEye Nayara Dashboard - Chart Configuration
// Using Chart.js for data visualization
// ===================================

// NOTE: This file requires Chart.js library
// Add to HTML: <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

let fuelChart = null;

// Initialize Fuel Dispensing Chart
function initFuelChart() {
    const ctx = document.getElementById('fuelChart');
    if (!ctx) return;

    // Destroy existing chart if any
    if (fuelChart) {
        fuelChart.destroy();
    }

    const data = mockData.fuelData;

    fuelChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'MS (Petrol)',
                    data: data.ms,
                    borderColor: '#8B5CF6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#8B5CF6',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                },
                {
                    label: 'HSD (Diesel)',
                    data: data.hsd,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#10B981',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false  // We have custom legend in HTML
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#374151',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += new Intl.NumberFormat('en-IN').format(context.parsed.y) + ' L';
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            family: 'Inter',
                            size: 12
                        },
                        color: '#6B7280'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#F3F4F6',
                        borderDash: [5, 5]
                    },
                    ticks: {
                        font: {
                            family: 'Inter',
                            size: 12
                        },
                        color: '#6B7280',
                        callback: function (value) {
                            return new Intl.NumberFormat('en-IN', {
                                notation: 'compact',
                                maximumFractionDigits: 1
                            }).format(value) + 'L';
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Update chart with new data (for real-time updates)
function updateFuelChart(newData) {
    if (!fuelChart) return;

    fuelChart.data.labels = newData.labels;
    fuelChart.data.datasets[0].data = newData.ms;
    fuelChart.data.datasets[1].data = newData.hsd;
    fuelChart.update('none');  // Update without animation for real-time feel
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initFuelChart, updateFuelChart };
}

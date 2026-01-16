/**
 * Employee Analytics Dashboard - CloudTuner/Nayara Edition
 * Chart.js visualizations for 4 key employee compliance KPIs
 */

// ===== 4 Key Employee KPIs (Yellow Highlighted) =====
const kpiData = {
    critical: [
        { name: 'Unauthorized Area', description: 'Entering restricted zone', threshold: 'Any violation', count: 5 },
        { name: 'Workplace Violence', description: 'Physical aggression/threat', threshold: 'Any detection', count: 0 }
    ],
    medium: [
        { name: 'Extended Break', description: 'Break exceeding allowed time', threshold: '>Allowed + 5 min', count: 12 },
        { name: 'Smoking Wrong Area', description: 'Smoking outside designated zone', threshold: 'Any violation', count: 3 }
    ]
};

// ===== Chart Colors =====
const colors = {
    critical: '#DC2626',
    medium: '#D97706',
    low: '#65A30D',
    primary: '#1E3A8A',
    secondary: '#3B82F6',
    grid: '#E2E8F0'
};

// ===== Initialize on Load =====
document.addEventListener('DOMContentLoaded', () => {
    initIncidentsTimeChart();
    initHourlyActivityChart();
    initTableSearch();
    animateKPIValues();
});

// ===== Incidents Over Time Chart (4 KPIs only) =====
function initIncidentsTimeChart() {
    const ctx = document.getElementById('incidentsTimeChart');
    if (!ctx) return;

    // Generate 30-day data for the 4 KPIs
    const days = [];
    const unauthorizedData = [];
    const extendedBreakData = [];
    const smokingData = [];

    for (let i = 30; i >= 1; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

        // Simulated incident counts
        unauthorizedData.push(Math.floor(Math.random() * 6) + 1);
        extendedBreakData.push(Math.floor(Math.random() * 10) + 4);
        smokingData.push(Math.floor(Math.random() * 4) + 1);
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: days,
            datasets: [
                {
                    label: 'Unauthorized Area',
                    data: unauthorizedData,
                    borderColor: colors.critical,
                    backgroundColor: colors.critical + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Extended Break',
                    data: extendedBreakData,
                    borderColor: colors.medium,
                    backgroundColor: colors.medium + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Smoking Wrong Area',
                    data: smokingData,
                    borderColor: '#F59E0B',
                    backgroundColor: '#F59E0B20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    backgroundColor: 'white',
                    titleColor: '#1E293B',
                    bodyColor: '#64748B',
                    borderColor: '#E2E8F0',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 6
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { size: 9 },
                        color: '#94A3B8',
                        maxTicksLimit: 10
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: colors.grid },
                    ticks: {
                        font: { size: 10 },
                        color: '#94A3B8'
                    }
                }
            }
        }
    });
}

// ===== Hourly Activity Chart =====
function initHourlyActivityChart() {
    const ctx = document.getElementById('hourlyActivityChart');
    if (!ctx) return;

    const hours = [];
    const employeeCount = [];
    const violationCount = [];

    for (let i = 0; i < 24; i++) {
        hours.push(`${i.toString().padStart(2, '0')}:00`);

        // Simulate employee presence (peak during work hours)
        let employees = 0;
        if (i >= 6 && i < 9) employees = 50 + (i - 6) * 60;
        else if (i >= 9 && i < 12) employees = 200 + Math.random() * 40;
        else if (i >= 12 && i < 14) employees = 150 + Math.random() * 30; // Lunch
        else if (i >= 14 && i < 17) employees = 220 + Math.random() * 30;
        else if (i >= 17 && i < 20) employees = 220 - (i - 17) * 50;
        else employees = 10 + Math.random() * 15;

        employeeCount.push(Math.round(employees));

        // Violations correlate with employee count
        const violations = Math.max(0, Math.round(employees * 0.015 + Math.random() * 2));
        violationCount.push(violations);
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Employees On-Site',
                    data: employeeCount,
                    borderColor: colors.secondary,
                    backgroundColor: colors.secondary + '30',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 0,
                    yAxisID: 'y'
                },
                {
                    label: 'Violations',
                    data: violationCount,
                    borderColor: colors.critical,
                    backgroundColor: colors.critical + '20',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 0,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    backgroundColor: 'white',
                    titleColor: '#1E293B',
                    bodyColor: '#64748B',
                    borderColor: '#E2E8F0',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 6
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { size: 9 },
                        color: '#94A3B8',
                        maxTicksLimit: 12
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 0,
                    max: 300,
                    grid: { color: colors.grid },
                    ticks: {
                        font: { size: 10 },
                        color: colors.secondary
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 10,
                    grid: { drawOnChartArea: false },
                    ticks: {
                        font: { size: 10 },
                        color: colors.critical
                    }
                }
            }
        }
    });
}

// ===== Table Search =====
function initTableSearch() {
    const searchInput = document.getElementById('searchInput');
    const tableBody = document.getElementById('tableBody');

    if (!searchInput || !tableBody) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const rows = tableBody.querySelectorAll('tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    });
}

// ===== Animate KPI Values =====
function animateKPIValues() {
    const kpiValues = document.querySelectorAll('.kpi-main-value');

    kpiValues.forEach(el => {
        const target = parseInt(el.textContent);
        if (isNaN(target)) return;

        let current = 0;
        const increment = Math.max(1, Math.ceil(target / 20));
        const duration = 800;
        const stepTime = duration / Math.max(1, target / increment);

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                el.textContent = target;
                clearInterval(timer);
            } else {
                el.textContent = current;
            }
        }, stepTime);
    });
}

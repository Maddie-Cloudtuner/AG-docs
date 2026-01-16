/**
 * Detection Analytics Dashboard - CloudTuner/Nayara Edition
 * Chart.js visualizations for detection analysis
 */

// ===== Data from JSON Analysis =====
const detectionData = {
    objects: [
        { name: 'Person', count: 1468, avgConf: 60.35, minConf: 25.17, maxConf: 73.58, lowPct: 1.0, stability: 'stable' },
        { name: 'TV', count: 16189, avgConf: 45.44, minConf: 25.10, maxConf: 77.05, lowPct: 9.5, stability: 'variable' },
        { name: 'Chair', count: 12257, avgConf: 44.82, minConf: 25.02, maxConf: 79.30, lowPct: 18.6, stability: 'variable' },
        { name: 'Laptop', count: 6470, avgConf: 38.71, minConf: 25.10, maxConf: 84.72, lowPct: 31.8, stability: 'variable' },
        { name: 'Clock', count: 2651, avgConf: 38.97, minConf: 25.10, maxConf: 51.95, lowPct: 12.2, stability: 'stable' },
        { name: 'Keyboard', count: 448, avgConf: 28.61, minConf: 25.10, maxConf: 37.21, lowPct: 74.8, stability: 'stable' }
    ],
    totalFrames: 1444,
    totalDetections: 39483
};

// ===== Chart Colors (CloudTuner Theme) =====
const colors = {
    primary: '#1E3A8A',
    secondary: '#3B82F6',
    light: '#60A5FA',
    person: '#EC4899',
    tv: '#3B82F6',
    chair: '#8B5CF6',
    laptop: '#22C55E',
    clock: '#F59E0B',
    keyboard: '#EF4444',
    grid: '#E2E8F0'
};

// ===== Initialize on Load =====
document.addEventListener('DOMContentLoaded', () => {
    initConfidenceTimeChart();
    initTimelineChart();
    initTableSearch();
});

// ===== Confidence by Time Chart =====
function initConfidenceTimeChart() {
    const ctx = document.getElementById('confidenceTimeChart');
    if (!ctx) return;

    // Simulated hourly data based on analysis
    const hours = ['2:00', '5:00', '8:00', '11:00', '14:00', '17:00', '20:00', '23:00'];
    const personConf = [58, 62, 65, 60, 55, 63, 58, 61];
    const tvConf = [42, 48, 46, 44, 43, 47, 45, 44];
    const chairConf = [40, 45, 48, 44, 42, 46, 43, 45];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Person',
                    data: personConf,
                    borderColor: colors.person,
                    backgroundColor: colors.person + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5
                },
                {
                    label: 'TV',
                    data: tvConf,
                    borderColor: colors.tv,
                    backgroundColor: colors.tv + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5
                },
                {
                    label: 'Chair',
                    data: chairConf,
                    borderColor: colors.chair,
                    backgroundColor: colors.chair + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5
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
                    cornerRadius: 6,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: { color: colors.grid },
                    ticks: { font: { size: 10 }, color: '#94A3B8' }
                },
                y: {
                    beginAtZero: false,
                    min: 30,
                    max: 70,
                    grid: { color: colors.grid },
                    ticks: {
                        font: { size: 10 },
                        color: '#94A3B8',
                        callback: (value) => value + '%'
                    }
                }
            }
        }
    });
}

// ===== Timeline Chart (People vs Objects) =====
function initTimelineChart() {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;

    // Generate timeline data
    const frames = [];
    const peopleData = [];
    const objectsData = [];

    for (let i = 0; i < 24; i++) {
        frames.push(`${i}:00`);

        // Person detection (1 per frame average, slight variations)
        let personCount = 18 + Math.sin(i / 3) * 4 + (Math.random() - 0.5) * 2;

        // Objects detection (around 300 per hour on average)
        let objectCount = 280 + Math.cos(i / 2) * 50 + (Math.random() - 0.5) * 30;

        // Add anomaly zones
        if (i >= 14 && i <= 16) {
            personCount = personCount * 0.7; // Low detection zone
            objectCount = objectCount * 0.8;
        }
        if (i >= 12 && i <= 13) {
            objectCount = objectCount * 1.2; // High activity
        }

        peopleData.push(Math.round(personCount));
        objectsData.push(Math.round(objectCount));
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: frames,
            datasets: [
                {
                    label: 'People',
                    data: peopleData,
                    borderColor: colors.person,
                    backgroundColor: colors.person + '30',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    yAxisID: 'y'
                },
                {
                    label: 'Objects',
                    data: objectsData,
                    borderColor: colors.secondary,
                    backgroundColor: colors.secondary + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4,
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
                    ticks: { font: { size: 9 }, color: '#94A3B8', maxTicksLimit: 12 }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 0,
                    max: 24,
                    grid: { color: colors.grid },
                    ticks: {
                        font: { size: 10 },
                        color: colors.person
                    },
                    title: {
                        display: false
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 400,
                    grid: { drawOnChartArea: false },
                    ticks: {
                        font: { size: 10 },
                        color: colors.secondary
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

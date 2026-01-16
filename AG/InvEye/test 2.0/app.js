/**
 * Detection Analytics Dashboard - InvEye CloudTuner.ai
 * Real-time CCTV detection visualization
 */

// ===== Detection Data Store =====
let detectionData = [];
let eventsData = [];
let metricsData = [];
let objectStats = {};
let cameraStats = {};
let timelineData = [];

// ===== Chart.js Colors =====
const colors = {
    critical: '#DC2626',
    medium: '#D97706',
    success: '#22C55E',
    primary: '#1E3A8A',
    secondary: '#3B82F6',
    global: '#7C3AED',
    grid: '#E2E8F0'
};

// ===== Initialize on Load =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadDetectionData();
    processData();
    updateUI();
    initCharts();
    startLiveUpdates();
});

// ===== Load Detection Log =====
async function loadDetectionData() {
    try {
        const response = await fetch('detection_log (1).json');
        detectionData = await response.json();
        console.log(`Loaded ${detectionData.length} detection records`);
    } catch (error) {
        console.error('Error loading detection data:', error);
        // Use sample data if file not found
        detectionData = getSampleData();
    }
}

// ===== Process Detection Data =====
function processData() {
    eventsData = detectionData.filter(d => d.type === 'EVENT');
    metricsData = detectionData.filter(d => d.type === 'METRIC');

    // Reset stats
    objectStats = {};
    cameraStats = {
        'CAFETERIA': { people: 0, count: 0 },
        'EMPLOYEE_AREA': { people: 0, count: 0 },
        'RECEPTION_AREA': { people: 0, count: 0 },
        'BOSS_CABIN': { people: 0, count: 0 }
    };
    timelineData = [];

    // Process metrics
    metricsData.forEach(record => {
        const camId = record.meta.cam_id;
        const peopleCount = record.data?.people_count || 0;
        const detections = record.data?.detections || [];

        // Camera stats
        if (cameraStats[camId]) {
            cameraStats[camId].people += peopleCount;
            cameraStats[camId].count++;
        }

        // Object stats
        detections.forEach(det => {
            const label = det.label;
            if (!objectStats[label]) {
                objectStats[label] = { count: 0, totalConf: 0 };
            }
            objectStats[label].count++;
            objectStats[label].totalConf += det.confidence;
        });

        // Timeline data (last 50 entries)
        timelineData.push({
            ts: new Date(record.meta.ts),
            cam: camId,
            people: peopleCount
        });
    });

    // Keep only last 50 timeline entries
    timelineData = timelineData.slice(-50);
}

// ===== Update UI =====
function updateUI() {
    updateCurrentTime();
    updateStatsBar();
    updateCameraCards();
    updateAlerts();
    updateKPIs();
    updateObjectBars();
    updateTable();
}

// ===== Update Current Time =====
function updateCurrentTime() {
    const timeEl = document.getElementById('currentTime');
    if (timeEl) {
        const now = new Date();
        timeEl.textContent = now.toLocaleString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

// ===== Update Stats Bar =====
function updateStatsBar() {
    // Total cameras
    document.getElementById('totalCameras').textContent = '4';

    // Active events
    const activeEvents = eventsData.length;
    document.getElementById('activeEvents').textContent = activeEvents;

    // Total people detected
    let totalPeople = 0;
    metricsData.forEach(m => { totalPeople += m.data?.people_count || 0; });
    document.getElementById('totalPeople').textContent = totalPeople;

    // Critical alerts
    const criticalAlerts = eventsData.filter(e => e.meta.status === 'CRITICAL').length;
    document.getElementById('criticalAlerts').textContent = criticalAlerts;

    // Safe status count
    const safeCount = metricsData.filter(m => m.meta.status === 'SAFE').length;
    document.getElementById('safeStatus').textContent = safeCount;

    // Average confidence
    let totalConf = 0, confCount = 0;
    metricsData.forEach(m => {
        (m.data?.detections || []).forEach(d => {
            totalConf += d.confidence;
            confCount++;
        });
    });
    const avgConf = confCount > 0 ? Math.round((totalConf / confCount) * 100) : 0;
    document.getElementById('avgConfidence').textContent = avgConf + '%';
}

// ===== Update Camera Cards =====
function updateCameraCards() {
    const cameras = ['CAFETERIA', 'EMPLOYEE_AREA', 'RECEPTION_AREA', 'BOSS_CABIN'];

    cameras.forEach(cam => {
        // Find latest metric for this camera
        const latestMetric = metricsData.filter(m => m.meta.cam_id === cam).pop();
        const latestEvent = eventsData.filter(e => e.meta.cam_id === cam).pop();

        const peopleEl = document.getElementById(`people-${cam}`);
        const statusEl = document.getElementById(`status-${cam}`);

        if (latestMetric) {
            const count = latestMetric.data?.people_count || 0;
            if (peopleEl) peopleEl.textContent = count;
            if (statusEl && latestMetric.meta.status === 'SAFE') {
                statusEl.textContent = '● SAFE';
                statusEl.className = 'cam-status';
            }
        }

        if (latestEvent && latestEvent.meta.status === 'CRITICAL') {
            if (statusEl) {
                statusEl.textContent = '● CRITICAL';
                statusEl.className = 'cam-status critical';
            }
        }
    });
}

// ===== Update Alerts =====
function updateAlerts() {
    const alertsList = document.getElementById('alertsList');
    const alertCountEl = document.getElementById('alertCount');

    if (!alertsList) return;

    // Get last 10 events
    const recentEvents = eventsData.slice(-10).reverse();
    alertCountEl.textContent = `${eventsData.length} Events`;

    alertsList.innerHTML = recentEvents.map(event => {
        const time = new Date(event.meta.ts).toLocaleTimeString();
        const triggers = event.event.triggers?.join(', ') || 'Unknown Event';
        const people = event.event.people_count || 0;

        return `
            <div class="alert-item critical">
                <span class="alert-icon">🚨</span>
                <div class="alert-content">
                    <span class="alert-text">${triggers}</span>
                    <span class="alert-meta">${event.meta.cam_id} • ${people} person(s) detected</span>
                </div>
                <span class="alert-time">${time}</span>
            </div>
        `;
    }).join('');

    if (recentEvents.length === 0) {
        alertsList.innerHTML = `
            <div class="alert-item" style="background: var(--success-bg); border-left-color: var(--success);">
                <span class="alert-icon">✅</span>
                <div class="alert-content">
                    <span class="alert-text">No critical events</span>
                    <span class="alert-meta">All systems operating normally</span>
                </div>
            </div>
        `;
    }
}

// ===== Update KPIs =====
function updateKPIs() {
    // Restricted access violations
    const restrictedCount = eventsData.filter(e =>
        (e.event.triggers || []).some(t => t.includes('RESTRICTED'))
    ).length;
    document.getElementById('kpi-restricted').textContent = restrictedCount;
    document.getElementById('kpi-restricted-today').textContent = restrictedCount;

    // Peak occupancy
    let peakPeople = 0, peakLocation = '-', peakTime = '-';
    metricsData.forEach(m => {
        const count = m.data?.people_count || 0;
        if (count > peakPeople) {
            peakPeople = count;
            peakLocation = m.meta.cam_id;
            peakTime = new Date(m.meta.ts).toLocaleTimeString();
        }
    });
    document.getElementById('kpi-peak').textContent = peakPeople;
    document.getElementById('kpi-peak-location').textContent = peakLocation;
    document.getElementById('kpi-peak-time').textContent = peakTime;

    // Total detections
    let totalDetections = 0, personCount = 0, objectCount = 0;
    metricsData.forEach(m => {
        const dets = m.data?.detections || [];
        totalDetections += dets.length;
        personCount += dets.filter(d => d.label === 'person').length;
        objectCount += dets.filter(d => d.label !== 'person').length;
    });
    document.getElementById('kpi-detections').textContent = totalDetections;
    document.getElementById('kpi-people-count').textContent = personCount;
    document.getElementById('kpi-object-count').textContent = objectCount;
}

// ===== Update Object Bars =====
function updateObjectBars() {
    const container = document.getElementById('objectBars');
    if (!container) return;

    // Sort objects by count
    const sorted = Object.entries(objectStats)
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 8);

    const maxCount = sorted.length > 0 ? sorted[0][1].count : 1;

    container.innerHTML = sorted.map(([label, stats]) => {
        const pct = Math.round((stats.count / maxCount) * 100);
        const avgConf = Math.round((stats.totalConf / stats.count) * 100);
        const barClass = label === 'person' ? 'person' :
            label === 'chair' ? 'chair' :
                label === 'laptop' ? 'laptop' :
                    label === 'tv' ? 'tv' :
                        label === 'potted plant' ? 'potted-plant' : 'other';

        return `
            <div class="bar-item">
                <span class="bar-label">${label}</span>
                <div class="bar-track">
                    <div class="bar-fill ${barClass}" style="width: ${pct}%">
                        ${avgConf}%
                    </div>
                </div>
                <span class="bar-value">${stats.count}</span>
            </div>
        `;
    }).join('');
}

// ===== Update Table =====
function updateTable() {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;

    // Get last 20 records
    const recentRecords = detectionData.slice(-20).reverse();

    tbody.innerHTML = recentRecords.map(record => {
        const isEvent = record.type === 'EVENT';
        const time = new Date(record.meta.ts).toLocaleString();
        const status = record.meta.status;
        const peopleCount = isEvent ? record.event.people_count : (record.data?.people_count || 0);
        const detections = isEvent ? record.event.detections : (record.data?.detections || []);

        // Get top 3 detections
        const topDets = detections.slice(0, 3).map(d => d.label);
        const avgConf = detections.length > 0
            ? Math.round((detections.reduce((s, d) => s + d.confidence, 0) / detections.length) * 100)
            : 0;

        return `
            <tr class="${isEvent ? 'warning-row' : ''}">
                <td>${time}</td>
                <td>${record.meta.cam_id}</td>
                <td><span class="type-badge ${record.type.toLowerCase()}">${record.type}</span></td>
                <td><span class="status-badge ${status.toLowerCase()}">${status}</span></td>
                <td>${peopleCount}</td>
                <td>
                    <div class="detection-tags">
                        ${topDets.map(t => `<span class="detection-tag">${t}</span>`).join('')}
                        ${detections.length > 3 ? `<span class="detection-tag">+${detections.length - 3}</span>` : ''}
                    </div>
                </td>
                <td>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${avgConf}%"></div>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// ===== Initialize Charts =====
function initCharts() {
    initTimelineChart();
    initCameraChart();
    initEventsChart();
}

// ===== Timeline Chart =====
function initTimelineChart() {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;

    const labels = timelineData.map(d => d.ts.toLocaleTimeString());
    const cafeteriaData = timelineData.map(d => d.cam === 'CAFETERIA' ? d.people : null);
    const employeeData = timelineData.map(d => d.cam === 'EMPLOYEE_AREA' ? d.people : null);
    const receptionData = timelineData.map(d => d.cam === 'RECEPTION_AREA' ? d.people : null);
    const bossData = timelineData.map(d => d.cam === 'BOSS_CABIN' ? d.people : null);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'CAFETERIA',
                    data: cafeteriaData,
                    borderColor: '#3B82F6',
                    backgroundColor: '#3B82F620',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 2,
                    spanGaps: true
                },
                {
                    label: 'EMPLOYEE_AREA',
                    data: employeeData,
                    borderColor: '#22C55E',
                    backgroundColor: '#22C55E20',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 2,
                    spanGaps: true
                },
                {
                    label: 'RECEPTION',
                    data: receptionData,
                    borderColor: '#F59E0B',
                    backgroundColor: '#F59E0B20',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 2,
                    spanGaps: true
                },
                {
                    label: 'BOSS_CABIN',
                    data: bossData,
                    borderColor: '#DC2626',
                    backgroundColor: '#DC262620',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 2,
                    spanGaps: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { usePointStyle: true, padding: 15, font: { size: 10 } }
                }
            },
            scales: {
                x: { display: false },
                y: {
                    beginAtZero: true,
                    grid: { color: colors.grid },
                    ticks: { font: { size: 10 }, color: '#94A3B8' }
                }
            }
        }
    });
}

// ===== Camera Distribution Chart =====
function initCameraChart() {
    const ctx = document.getElementById('cameraChart');
    if (!ctx) return;

    const cameras = Object.keys(cameraStats);
    const counts = cameras.map(c => cameraStats[c].count);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: cameras,
            datasets: [{
                data: counts,
                backgroundColor: ['#3B82F6', '#22C55E', '#F59E0B', '#DC2626'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { usePointStyle: true, padding: 15, font: { size: 10 } }
                }
            }
        }
    });
}

// ===== Events Chart =====
function initEventsChart() {
    const ctx = document.getElementById('eventsChart');
    if (!ctx) return;

    // Group events by hour
    const hourCounts = {};
    eventsData.forEach(e => {
        const hour = new Date(e.meta.ts).getHours();
        hourCounts[hour] = (hourCounts[hour] || 0) + 1;
    });

    const labels = Object.keys(hourCounts).map(h => `${h}:00`);
    const data = Object.values(hourCounts);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Events',
                data: data,
                backgroundColor: '#DC262680',
                borderColor: '#DC2626',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: colors.grid } }
            }
        }
    });
}

// ===== Table Search =====
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#tableBody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }
});

// ===== Live Updates =====
function startLiveUpdates() {
    // Update time every second
    setInterval(updateCurrentTime, 1000);
}

// ===== Sample Data (fallback) =====
function getSampleData() {
    return [
        { "type": "METRIC", "meta": { "ts": "2025-12-16T13:37:10.971002Z", "cam_id": "CAFETERIA", "site": "HEAD_OFFICE", "status": "SAFE" }, "data": { "people_count": 8, "detections": [{ "class_id": 0, "label": "person", "confidence": 0.9048 }] } },
        { "type": "METRIC", "meta": { "ts": "2025-12-16T13:37:10.974344Z", "cam_id": "EMPLOYEE_AREA", "site": "HEAD_OFFICE", "status": "SAFE" }, "data": { "people_count": 11, "detections": [{ "class_id": 0, "label": "person", "confidence": 0.9243 }] } },
        { "type": "EVENT", "meta": { "ts": "2025-12-16T13:43:49.138755Z", "cam_id": "BOSS_CABIN", "site": "HEAD_OFFICE", "status": "CRITICAL" }, "event": { "triggers": ["RESTRICTED_ACCESS_BOSS_CABIN"], "people_count": 1, "detections": [{ "class_id": 0, "label": "person", "confidence": 0.4822 }], "capture_triggered": true } }
    ];
}

/**
 * ROBOI DASHBOARD - Main JavaScript
 * Handles tab switching, data loading, chart rendering, and interactions
 */

// ===== STATE =====
let currentTab = 'overview';
let currentPage = 1;
let currentFilters = {
    status: 'ALL',
    camera: '',
    eventType: 'ALL'
};
let currentAlerts = [];
let currentSlide = 0;
let totalSlides = 0;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Roboi Dashboard initializing...');

    // Initialize date range (last 24 hours)
    initializeDateRange();

    // Setup tab navigation
    setupTabNavigation();

    // Setup alert filters
    setupAlertFilters();

    // Load initial data
    await loadAllData();

    // Update last refresh time
    updateLastRefresh();

    console.log('✅ Dashboard initialized');
});

// ===== DATE RANGE =====
function initializeDateRange() {
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    document.getElementById('endDate').value = formatDateForInput(now);
    document.getElementById('startDate').value = formatDateForInput(yesterday);

    // Add change listeners
    document.getElementById('startDate').addEventListener('change', () => loadAllData());
    document.getElementById('endDate').addEventListener('change', () => loadAllData());
}

function formatDateForInput(date) {
    return date.toISOString().slice(0, 16);
}

function getDateRange() {
    const startEl = document.getElementById('startDate');
    const endEl = document.getElementById('endDate');

    return {
        startTime: startEl.value ? Math.floor(new Date(startEl.value).getTime() / 1000) : null,
        endTime: endEl.value ? Math.floor(new Date(endEl.value).getTime() / 1000) : null
    };
}

function updateLastRefresh() {
    const now = new Date();
    document.getElementById('lastRefresh').textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// ===== TAB NAVIGATION =====
function setupTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;

            // Update button states
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`tab-${tab}`).classList.add('active');

            currentTab = tab;
        });
    });
}

// ===== ALERT FILTERS =====
function setupAlertFilters() {
    const filterBtns = document.querySelectorAll('.alert-filters .filter-btn');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            filterAlerts(filter);
        });
    });
}

function filterAlerts(filter) {
    const items = document.querySelectorAll('.alert-item');

    items.forEach(item => {
        if (filter === 'all') {
            item.style.display = 'flex';
        } else {
            item.style.display = item.classList.contains(filter) ? 'flex' : 'none';
        }
    });
}

// ===== DATA LOADING =====
async function loadAllData() {
    const { startTime, endTime } = getDateRange();

    // Load all data in parallel
    await Promise.all([
        loadSummary(startTime, endTime),
        loadEvents(startTime, endTime),
        loadObjectCounts(startTime, endTime),
        loadDetections()
    ]);

    updateLastRefresh();
}

// ===== HEATMAP =====
function updateHeatmap() {
    const camera = document.getElementById('cameraFilter').value;
    const cameraNames = {
        'all': 'All Cameras',
        'd5': 'D5 - Forecourt',
        'd6': 'D6 - Air Station',
        'd7': 'D7 - Employee Area',
        'd8': 'D8 - Entry Gate',
        'd9': 'D9 - Exit Gate'
    };

    // Update detection count based on camera
    const detectionCounts = { 'all': 821, 'd5': 234, 'd6': 156, 'd7': 189, 'd8': 142, 'd9': 100 };
    document.getElementById('detectionCount').textContent = `Detections: ${detectionCounts[camera] || 0}`;

    // Log camera change
    console.log(`🗺️ Heatmap updated for camera: ${cameraNames[camera]}`);
    showNotification(`📍 Heatmap: ${cameraNames[camera]}`, 'info');
}

async function loadSummary(startTime, endTime) {
    try {
        const data = await RoboiAPI.getSummary(startTime, endTime);

        // Update stats cards
        document.getElementById('siteId').textContent = data.siteId?.toUpperCase() || 'R0001';
        document.getElementById('activeCameras').textContent = data.metrics?.activeSensors ?? '-';
        document.getElementById('activeEvents').textContent = data.metrics?.openAlerts ?? '-';
        document.getElementById('criticalAlerts').textContent = data.metrics?.criticalAlerts ?? '-';
        document.getElementById('totalPeople').textContent = data.metrics?.trafficCount ?? '-';
        document.getElementById('peakOccupancy').textContent = data.metrics?.peakDensity ?? '-';

        // Update status indicator
        const statusBadge = document.querySelector('.status-badge');
        if (data.status === 'ONLINE') {
            statusBadge.innerHTML = '<span class="status-dot online"></span> Online • Last Refreshed <span id="lastRefresh">' + new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) + '</span>';
        } else {
            statusBadge.innerHTML = '<span class="status-dot offline"></span> Offline';
        }

        // Update customer tab data
        document.getElementById('footfallToday').textContent = data.metrics?.trafficCount ?? '-';

    } catch (error) {
        console.error('Failed to load summary:', error);
    }
}

async function loadEvents(startTime, endTime) {
    try {
        const data = await RoboiAPI.getEvents(50, startTime, endTime);
        currentAlerts = data.events || [];

        renderAlerts(currentAlerts);

        // Update SOP violations count
        const violations = currentAlerts.filter(e =>
            ['EMERGENCY', 'CRITICAL', 'WARNING'].includes(e.severity)
        ).length;
        document.getElementById('sopViolations').textContent = violations;

        // Update safety stats
        updateSafetyStats(currentAlerts);

    } catch (error) {
        console.error('Failed to load events:', error);
    }
}

function updateSafetyStats(events) {
    const fire = events.filter(e => e.subType?.toLowerCase().includes('fire')).length;
    const smoke = events.filter(e => e.subType?.toLowerCase().includes('smoke')).length;
    const smoking = events.filter(e => e.subType?.toLowerCase().includes('smoking')).length;
    const violence = events.filter(e => e.subType?.toLowerCase().includes('violence') || e.subType?.toLowerCase().includes('fight')).length;

    document.getElementById('fireAlerts').textContent = fire;
    document.getElementById('smokeAlerts').textContent = smoke;
    document.getElementById('smokingAlerts').textContent = smoking;
    document.getElementById('violenceAlerts').textContent = violence;
    document.getElementById('safetyIncidents').textContent = fire + smoke + smoking + violence;
}

function renderAlerts(alerts) {
    const container = document.getElementById('alertsList');

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div class="no-data">No alerts found</div>';
        return;
    }

    container.innerHTML = alerts.map(alert => {
        const severity = alert.severity?.toLowerCase() || 'info';
        const icon = getAlertIcon(alert.type, alert.subType);
        const time = formatTimestamp(alert.timestamp);

        return `
            <div class="alert-item ${severity}" onclick="openAlertModal('${alert.id}')">
                <span class="alert-icon">${icon}</span>
                <div class="alert-content">
                    <div class="alert-title">${alert.subType || alert.type}</div>
                    <div class="alert-meta">
                        <span>${alert.sourceName}</span>
                        <span>${time}</span>
                    </div>
                </div>
                <span class="alert-severity">${alert.severity}</span>
            </div>
        `;
    }).join('');
}

function getAlertIcon(type, subType) {
    const sub = (subType || '').toLowerCase();
    if (sub.includes('fire')) return '🔥';
    if (sub.includes('smoke')) return '💨';
    if (sub.includes('smoking')) return '🚬';
    if (sub.includes('crowd') || sub.includes('mob')) return '👥';
    if (sub.includes('uniform')) return '👔';
    if (sub.includes('violence') || sub.includes('fight')) return '👊';
    if (sub.includes('vehicle')) return '🚗';
    if (type === 'SAFETY') return '🛡️';
    if (type === 'OPERATIONS') return '⚙️';
    return '📊';
}

function formatTimestamp(ts) {
    if (!ts) return '';
    const date = new Date(ts * 1000);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function loadDistribution(startTime, endTime) {
    try {
        const data = await RoboiAPI.getDistribution('24h', startTime, endTime);
        const distribution = Array.isArray(data) ? data : (data.distribution || []);

        renderDistribution(distribution);

    } catch (error) {
        console.error('Failed to load distribution:', error);
    }
}

function renderDistribution(distribution) {
    const container = document.getElementById('distributionList');

    if (!distribution || distribution.length === 0) {
        container.innerHTML = '<div class="no-data">No distribution data</div>';
        return;
    }

    const colors = ['#3A6DC9', '#F89023', '#FF7272', '#39CC2B', '#8B5CF6', '#248CB5'];

    container.innerHTML = distribution.map((item, i) => `
        <div class="distribution-item">
            <span class="distribution-label">${item.label}</span>
            <div class="distribution-bar-container">
                <div class="distribution-bar" style="width: ${item.percentage}%; background: ${colors[i % colors.length]}"></div>
            </div>
            <span class="distribution-value">${item.value}</span>
        </div>
    `).join('');
}

async function loadObjectCounts(startTime, endTime) {
    try {
        const data = await RoboiAPI.getObjectCounts('all', startTime, endTime);
        const counts = data.data || [];

        renderObjectCountChart(counts);

    } catch (error) {
        console.error('Failed to load object counts:', error);
    }
}

function renderObjectCountChart(counts) {
    const ctx = document.getElementById('objectCountChart')?.getContext('2d');
    if (!ctx) return;

    // Process data
    const timestamps = [...new Set(counts.map(c => c.timestamp))].sort();
    const objects = [...new Set(counts.map(c => c.object))];

    const labels = timestamps.map(ts => {
        const d = new Date(ts * 1000);
        return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    });

    const colors = ['#3A6DC9', '#FF7272', '#39CC2B', '#F89023', '#8B5CF6', '#248CB5'];

    const datasets = objects.map((obj, i) => ({
        label: obj.charAt(0).toUpperCase() + obj.slice(1),
        data: timestamps.map(ts => {
            const entry = counts.find(c => c.timestamp === ts && c.object === obj);
            return entry ? entry.count : 0;
        }),
        borderColor: colors[i % colors.length],
        backgroundColor: colors[i % colors.length] + '33',
        fill: true,
        tension: 0.4
    }));

    // Destroy existing chart
    if (window.objectCountChartInstance) {
        window.objectCountChartInstance.destroy();
    }

    window.objectCountChartInstance = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

async function loadDetections() {
    try {
        const data = await RoboiAPI.getDetections(currentPage, 20, currentFilters);

        renderDetectionTable(data.items || []);
        renderPagination(data.page, data.totalPages);

    } catch (error) {
        console.error('Failed to load detections:', error);
    }
}

function renderDetectionTable(detections) {
    const tbody = document.getElementById('detectionTableBody');

    if (!detections || detections.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No detections found</td></tr>';
        return;
    }

    tbody.innerHTML = detections.map(det => {
        const time = formatTimestamp(det.timestamp);
        // Map severity to CSS class - INFO and TRIAGED should show as SAFE (green)
        let statusClass = det.severity?.toLowerCase() || 'safe';
        let statusLabel = det.severity;

        // Show INFO and TRIAGED as SAFE with green styling
        if (det.severity === 'INFO' || det.severity === 'TRIAGED') {
            statusClass = 'safe';
            statusLabel = 'SAFE';
        } else if (det.severity === 'CRITICAL') {
            statusClass = 'critical';
        } else if (det.severity === 'WARNING') {
            statusClass = 'warning';
        } else if (det.severity === 'EMERGENCY') {
            statusClass = 'critical'; // Emergency uses critical styling
        }

        const objects = det.metadata?.detectedObjects?.join(', ') || '-';
        const conf = det.metadata?.confidence ? (det.metadata.confidence * 100).toFixed(0) + '%' : '-';

        return `
            <tr>
                <td>${time}</td>
                <td>${det.sourceName || det.sourceId}</td>
                <td>${det.type}</td>
                <td><span class="status-badge-table ${statusClass}">${statusLabel}</span></td>
                <td>${objects}</td>
                <td>${conf}</td>
            </tr>
        `;
    }).join('');
}

function renderPagination(page, totalPages) {
    const container = document.getElementById('pagination');

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    if (page > 1) {
        html += `<button onclick="goToPage(${page - 1})">← Prev</button>`;
    }

    for (let i = 1; i <= Math.min(totalPages, 5); i++) {
        html += `<button class="${i === page ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }

    if (page < totalPages) {
        html += `<button onclick="goToPage(${page + 1})">Next →</button>`;
    }

    container.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    loadDetections();
}

// ===== FILTERS =====
function toggleFilters() {
    document.getElementById('filtersPanel').classList.toggle('active');
}

function applyFilters() {
    currentFilters = {
        status: document.getElementById('filterStatus').value,
        camera: document.getElementById('filterCamera').value,
        eventType: document.getElementById('filterType').value
    };
    currentPage = 1;
    loadDetections();
}

// ===== REFRESH =====
function refreshData() {
    loadAllData();
}

// ===== ALERT MODAL =====
function openAlertModal(alertId) {
    const alert = currentAlerts.find(a => a.id === alertId);
    if (!alert) return;

    // Parse AI insights
    let insights = null;
    try {
        insights = alert.metadata?.ai_insights ? JSON.parse(alert.metadata.ai_insights) : null;
    } catch (e) {
        console.log('No AI insights available');
    }

    // Update modal header
    document.getElementById('modalIcon').textContent = getAlertIcon(alert.type, alert.subType);
    document.getElementById('modalTitle').textContent = alert.subType || alert.type;
    document.getElementById('modalTags').textContent = alert.metadata?.detectedObjects?.join(', ') || '';

    const severityBadge = document.getElementById('modalSeverity');
    severityBadge.textContent = alert.severity;
    severityBadge.className = `severity-badge ${alert.severity?.toLowerCase()}`;

    // Update evidence carousel
    updateCarousel(alert);

    // Update AI insights
    if (insights) {
        updateAIInsights(insights);
        document.getElementById('aiInsightsSection').style.display = 'block';
    } else {
        document.getElementById('aiInsightsSection').style.display = 'none';
    }

    // Show modal
    document.getElementById('modalOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function updateCarousel(alert) {
    const container = document.getElementById('carouselContainer');
    const baseUrl = 'https://storage.googleapis.com/roboi-events'; // Or your GCP bucket
    const path = alert.metadata?.evidence_path;
    const numImages = alert.metadata?.image_count || 3;

    let slides = [];

    if (path) {
        for (let i = 1; i <= numImages; i++) {
            slides.push(`${baseUrl}/${path}/${i}.jpg`);
        }
    }

    if (slides.length === 0) {
        slides = [
            'https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1612099452927-7fbb6b2b6d42?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1511447333015-45b65e60f6d5?w=800&h=500&fit=crop'
        ];
    }

    totalSlides = slides.length;
    currentSlide = 0;

    container.innerHTML = slides.map((src, i) => `
        <div class="carousel-slide ${i === 0 ? 'active' : ''}">
            <img src="${src}" alt="Evidence ${i + 1}" onerror="this.src='https://via.placeholder.com/800x500?text=Evidence+${i + 1}'">
        </div>
    `).join('');
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    updateSlides();
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    updateSlides();
}

function updateSlides() {
    const slides = document.querySelectorAll('.carousel-slide');
    slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === currentSlide);
    });
}

function updateAIInsights(insights) {
    // KPI Score
    const scoreValue = document.querySelector('#kpiScore .score-value');
    scoreValue.textContent = insights.kpiScore || 0;

    if (insights.kpiScore >= 8) scoreValue.style.color = '#39CC2B';
    else if (insights.kpiScore >= 5) scoreValue.style.color = '#3A6DC9';
    else if (insights.kpiScore >= 3) scoreValue.style.color = '#F89023';
    else scoreValue.style.color = '#FF7272';

    // KPI Scores Grid
    const kpiGrid = document.getElementById('kpiScoresGrid');
    if (insights.kpiScores) {
        const icons = { uniform: '👔', cleanliness: '🧹', safety: '🛡️' };
        kpiGrid.innerHTML = Object.entries(insights.kpiScores).map(([key, val]) => {
            const pct = (val.score / val.max) * 100;
            let color = pct >= 80 ? '#39CC2B' : pct >= 60 ? '#248CB5' : pct >= 40 ? '#F89023' : '#FF7272';
            let label = pct >= 80 ? 'excellent' : pct >= 60 ? 'good' : pct >= 40 ? 'moderate' : 'poor';

            return `
                <div class="kpi-score-item">
                    <span class="kpi-icon">${icons[key] || '📊'}</span>
                    <div class="kpi-details">
                        <span class="kpi-label">${key.charAt(0).toUpperCase() + key.slice(1)}</span>
                        <div class="kpi-bar-container">
                            <div class="kpi-bar" style="width: ${pct}%; background: ${color}"></div>
                        </div>
                        <span class="kpi-value ${label}">${val.score}/${val.max}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Quick Facts
    const quickFacts = document.getElementById('quickFacts');
    if (insights.metrics) {
        const utilClass = insights.utilization === 'low' ? 'low' : insights.utilization === 'high' ? 'high' : 'medium';
        quickFacts.innerHTML = `
            <div class="fact-item">
                <span class="fact-icon">👥</span>
                <span class="fact-label">People</span>
                <span class="fact-value">${insights.metrics.people}</span>
            </div>
            <div class="fact-item">
                <span class="fact-icon">🚗</span>
                <span class="fact-label">Vehicles</span>
                <span class="fact-value">${insights.metrics.vehicles}</span>
            </div>
            <div class="fact-item">
                <span class="fact-icon">👔</span>
                <span class="fact-label">Staff</span>
                <span class="fact-value">${insights.metrics.staff}</span>
            </div>
            <div class="fact-item">
                <span class="fact-icon">📊</span>
                <span class="fact-label">Utilization</span>
                <span class="fact-value ${utilClass}">${(insights.utilization || 'N/A').toUpperCase()}</span>
            </div>
        `;
    }

    // Insight Alerts
    const insightAlerts = document.getElementById('insightAlerts');
    if (insights.alerts && insights.alerts.length > 0) {
        insightAlerts.style.display = 'block';
        insightAlerts.innerHTML = `
            <h4>⚠️ Issues Detected</h4>
            <ul class="alert-list">
                ${insights.alerts.map(a => {
            const isCrit = a.toLowerCase().includes('fire') || a.toLowerCase().includes('critical');
            return `<li class="alert-item-small ${isCrit ? 'critical' : 'warning'}">${a}</li>`;
        }).join('')}
            </ul>
        `;
    } else {
        insightAlerts.style.display = 'none';
    }

    // AI Summary
    const aiSummary = document.getElementById('aiSummary');
    aiSummary.innerHTML = `
        <h4>💬 AI Analysis</h4>
        <div class="summary-sections">
            <div class="summary-block overview">
                <span class="block-label">Overview</span>
                <p>${insights.overview || 'No overview available'}</p>
            </div>
            <div class="summary-block deepdive">
                <span class="block-label">Deep Dive</span>
                <p>${insights.deepdive || 'No detailed analysis available'}</p>
            </div>
            <div class="summary-block insights">
                <span class="block-label">Key Insight</span>
                <p>${insights.insights || 'No insights available'}</p>
            </div>
        </div>
    `;

    // TL;DR
    document.getElementById('tldrSection').innerHTML = `
        <span class="tldr-label">🎯 TL;DR:</span>
        <span class="tldr-text">${insights.tldr || insights.verdict || 'Analysis complete'}</span>
    `;
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
    document.body.style.overflow = 'auto';
}

// ===== CONFIG MODAL =====
function openConfig() {
    document.getElementById('apiUrl').value = API_CONFIG.baseUrl;
    document.getElementById('apiKey').value = API_CONFIG.apiKey;
    document.getElementById('configSiteId').value = API_CONFIG.siteId;
    document.getElementById('configModal').classList.add('active');
}

function closeConfig() {
    document.getElementById('configModal').classList.remove('active');
}

function saveConfig() {
    const config = {
        baseUrl: document.getElementById('apiUrl').value,
        apiKey: document.getElementById('apiKey').value,
        siteId: document.getElementById('configSiteId').value
    };

    saveApiConfig(config);
    closeConfig();

    // Reload data with new config
    loadAllData();

    showNotification('✅ Configuration saved!', 'success');
}

// ===== ACTIONS =====
function downloadReport() {
    showNotification('📥 Generating report...', 'info');
    setTimeout(() => {
        showNotification('✅ Report downloaded!', 'success');
    }, 2000);
}

function shareToTelegram() {
    showNotification('📤 Sending to Telegram...', 'info');
    setTimeout(() => {
        showNotification('✅ Alert shared!', 'success');
    }, 1500);
}

function markAsRead() {
    showNotification('✅ Marked as read', 'success');
    setTimeout(closeModal, 1000);
}

// ===== NOTIFICATIONS =====
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 14px 20px;
        background: ${type === 'success' ? '#39CC2B' : type === 'error' ? '#FF7272' : '#3A6DC9'};
        color: white;
        border-radius: 10px;
        font-weight: 500;
        z-index: 3000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
    .no-data { padding: 40px; text-align: center; color: #9F9F9F; }
`;
document.head.appendChild(style);

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        closeConfig();
    }

    if (document.getElementById('modalOverlay').classList.contains('active')) {
        if (e.key === 'ArrowLeft') prevSlide();
        if (e.key === 'ArrowRight') nextSlide();
    }
});

// ===== INIT CHARTS =====
function initCharts() {
    // SOP Radar Chart - Using KPIs from AI_KPI_DOCUMENTATION
    const radarCtx = document.getElementById('sopRadarChart')?.getContext('2d');
    if (radarCtx) {
        new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['Uniform (1-5)', 'Cleanliness (1-5)', 'Safety (1-5)', 'Greeting', 'Zero Display', 'FSM Attend'],
                datasets: [{
                    label: 'Score',
                    data: [80, 90, 100, 65, 100, 100], // Uniform 4/5, Clean 4.5/5, Safety 5/5, Greeting 65%, Zero 100%, FSM 100%
                    backgroundColor: 'rgba(36, 140, 181, 0.2)',
                    borderColor: '#248CB5',
                    pointBackgroundColor: '#248CB5',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20 },
                        grid: { color: 'rgba(0,0,0,0.05)' },
                        pointLabels: { font: { size: 10 } }
                    }
                }
            }
        });
    }

    // Cleanliness Line Chart
    const cleanCtx = document.getElementById('cleanlinessChart')?.getContext('2d');
    if (cleanCtx) {
        new Chart(cleanCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Score',
                    data: [78, 82, 80, 85, 88, 82, 86],
                    borderColor: '#39CC2B',
                    backgroundColor: 'rgba(57, 204, 43, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: false, min: 60, max: 100 }
                }
            }
        });
    }
}

// Initialize charts after DOM load
setTimeout(initCharts, 500);

console.log('📊 Roboi Dashboard script loaded');

// ===================================
// InvEye Nayara Dashboard - Main App
// Real-time Dashboard Updates & Interactions
// ===================================

// Initialize Dashboard on Page Load
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 InvEye Nayara Dashboard Initializing...');

    // Initialize Components
    initDashboard();

    // Set up real-time updates
    startRealTimeUpdates();

    // Setup event listeners
    setupEventListeners();

    console.log('✅ Dashboard Loaded Successfully');
});

// Main Dashboard Initialization
function initDashboard() {
    // Render CCTV Grid
    renderCCTVGrid();

    // Render Alerts
    renderAlerts();

    // Initialize Chart
    if (typeof Chart !== 'undefined') {
        initFuelChart();
    } else {
        console.warn('⚠️ Chart.js not loaded. Add: <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>');
    }

    // Update Dynamic Values
    updateDynamicValues();
}

// Render CCTV Camera Grid
function renderCCTVGrid() {
    const cctvGrid = document.getElementById('cctvGrid');
    if (!cctvGrid) return;

    cctvGrid.innerHTML = '';

    mockData.cctvFeeds.forEach(feed => {
        const feedElement = document.createElement('div');
        feedElement.className = 'cctv-feed';
        feedElement.innerHTML = `
            <div class="cctv-overlay">
                <div class="cctv-info">
                    <div class="cctv-name">${feed.name}</div>
                    <div class="cctv-location">${feed.location}</div>
                </div>
                <div class="cctv-status">
                    <span class="cctv-status-dot"></span>
                    ${feed.status}
                </div>
            </div>
        `;

        // Add click handler for fullscreen (future enhancement)
        feedElement.addEventListener('click', () => {
            console.log(`📹 Expanding camera: ${feed.name}`);
            // Future: Open fullscreen modal
        });

        cctvGrid.appendChild(feedElement);
    });
}

// Render Real-Time Alerts
function renderAlerts() {
    const alertsContainer = document.getElementById('alertsContainer');
    if (!alertsContainer) return;

    alertsContainer.innerHTML = '';

    // Show first 8 alerts
    const visibleAlerts = mockData.alerts.slice(0, 8);

    visibleAlerts.forEach(alert => {
        const alertElement = document.createElement('div');
        alertElement.className = `alert-item severity-${alert.severity}`;
        alertElement.innerHTML = `
            <div class="alert-header">
                <span class="alert-severity ${alert.severity}">
                    ${alert.severity === 'red' ? '🔥 VERY CRITICAL' :
                alert.severity === 'orange' ? '⚠️ CRITICAL' : '🟡 MODERATE'}
                </span>
            </div>
            <div class="alert-title">${alert.title}</div>
            <div class="alert-details">
                📍 ${alert.location} ${alert.camera ? `• 📹 ${alert.camera}` : ''}
            </div>
            <div class="alert-time">🕒 ${alert.time}</div>
        `;

        // Add click handler
        alertElement.addEventListener('click', () => {
            console.log(`🚨 Alert clicked: ${alert.title}`);
            showAlertDetails(alert);
        });

        alertsContainer.appendChild(alertElement);
    });
}

// Show Alert Details (future enhancement)
function showAlertDetails(alert) {
    // Future: Open modal with full alert details, CCTV snapshot, and action buttons
    alert(`Alert Details:\n\n${alert.title}\n\nLocation: ${alert.location}\nCamera: ${alert.camera || 'N/A'}\nTime: ${alert.time}\n\n${alert.description}`);
}

// Update Dynamic Dashboard Values
function updateDynamicValues() {
    const data = mockData;

    // Update counts (already in HTML, but can be animated)
    animateValue('footfallCount', 0, data.operations.customersServed, 1000);
    animateValue('revenueValue', 0, data.operations.totalRevenue, 1000);
}

// Animate Number Count-Up
function animateValue(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const range = end - start;
    const increment = range / (duration / 16);  // 60 FPS
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString('en-IN');
    }, 16);
}

// Real-Time Updates Simulation
function startRealTimeUpdates() {
    // Simulate real-time alert additions every 30 seconds
    setInterval(() => {
        // In production, this would be WebSocket connection
        console.log('🔄 Checking for new alerts...');
        // renderAlerts() would be called when new data arrives
    }, 30000);

    // Update chart every 5 minutes (simulate new hourly data)
    setInterval(() => {
        console.log('📊 Updating fuel chart data...');
        // updateFuelChart(newData) would be called with fresh data
    }, 300000);

    // Update time-based elements (e.g., "2 min ago" → "3 min ago")
    setInterval(() => {
        updateTimeAgo();
    }, 60000);  // Every minute
}

// Update "time ago" for alerts
function updateTimeAgo() {
    const alerts = document.querySelectorAll('.alert-time');
    alerts.forEach((alert, index) => {
        const originalTime = mockData.alerts[index]?.time;
        if (originalTime) {
            // In production, calculate from actual timestamp
            // For now, just refresh the display
            alert.textContent = `🕒 ${originalTime}`;
        }
    });
}

// Setup Event Listeners
function setupEventListeners() {
    // Location Selector
    const locationSelect = document.getElementById('locationSelect');
    if (locationSelect) {
        locationSelect.addEventListener('change', (e) => {
            console.log(`📍 Station changed to: ${e.target.value}`);
            // In production: fetch new station data and reload dashboard
            showLoadingState();
            setTimeout(() => {
                hideLoadingState();
                initDashboard();
            }, 1000);
        });
    }

    // Date Range Selector
    const dateSelect = document.getElementById('dateSelect');
    if (dateSelect) {
        dateSelect.addEventListener('change', (e) => {
            console.log(`📅 Date range changed to: ${e.target.value}`);
            // In production: fetch historical data for selected range
        });
    }

    // Expand Cameras Button
    const expandBtn = document.getElementById('expandCameras');
    if (expandBtn) {
        expandBtn.addEventListener('click', () => {
            console.log('🖼 Expanding CCTV grid...');
            // Future: Open full-screen camera grid modal
            alert('Full-screen CCTV view coming soon!');
        });
    }

    // Notification Button
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', () => {
            console.log('🔔 Opening notifications...');
            // Future: Open notifications panel
            alert(`You have ${mockData.kpis.redAlerts + mockData.kpis.orangeAlerts + mockData.kpis.yellowAlerts} active alerts`);
        });
    }
}

// Loading State Helpers
function showLoadingState() {
    document.body.style.opacity = '0.6';
    document.body.style.pointerEvents = 'none';
}

function hideLoadingState() {
    document.body.style.opacity = '1';
    document.body.style.pointerEvents = 'auto';
}

// Utility: Format time difference
function getTimeDifference(timestamp) {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now - then;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

// Export for testing/debugging
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initDashboard,
        renderCCTVGrid,
        renderAlerts,
        updateDynamicValues
    };
}

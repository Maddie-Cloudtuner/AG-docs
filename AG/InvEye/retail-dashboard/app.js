// ===================================
// InvEye Retail Dashboard - Main Application
// ===================================

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    startRealTimeUpdates();
});

// ===================================
// Initialize Dashboard
// ===================================

function initializeDashboard() {
    renderCCTVFeeds();
    renderAlerts();
    renderTopProducts();
    renderChart();
    updateKPIs();
    setupEventListeners();
}

// ===================================
// CCTV Feeds Rendering
// ===================================

function renderCCTVFeeds() {
    const cctvGrid = document.getElementById('cctvGrid');

    cctvGrid.innerHTML = dashboardData.cctvFeeds.map(feed => `
        <div class="cctv-feed" data-camera-id="${feed.id}">
            <img src="${feed.thumbnail}" alt="${feed.name} - ${feed.location}">
            <div class="cctv-overlay">
                <div class="cctv-info">
                    <div class="cctv-name">${feed.name}</div>
                    <div class="cctv-location">${feed.location}</div>
                </div>
                <div class="cctv-status">
                    <span class="cctv-status-dot"></span>
                    <span>LIVE</span>
                </div>
            </div>
        </div>
    `).join('');
}

// ===================================
// Alerts Rendering
// ===================================

function renderAlerts() {
    const alertsContainer = document.getElementById('alertsContainer');

    alertsContainer.innerHTML = dashboardData.alerts.map(alert => `
        <div class="alert-item ${alert.severity}" data-alert-id="${alert.id}">
            <div class="alert-header">
                <div class="alert-icon">${alert.icon}</div>
                <div class="alert-content">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-details">${alert.description}</div>
                    <div class="alert-details">Location: ${alert.location}</div>
                    <div class="alert-time">${alert.time}</div>
                </div>
            </div>
            <div class="alert-actions">
                <button class="alert-btn" onclick="viewAlert(${alert.id})">View CCTV</button>
                <button class="alert-btn" onclick="dismissAlert(${alert.id})">Dismiss</button>
            </div>
        </div>
    `).join('');
}

// ===================================
// Top Products Rendering
// ===================================

function renderTopProducts() {
    const topProductsList = document.getElementById('topProductsList');

    topProductsList.innerHTML = dashboardData.topProducts.map(product => `
        <div class="employee-item product-item" data-product-id="${product.id}">
            <div class="employee-avatar product-icon">${product.icon}</div>
            <div class="employee-info">
                <div class="employee-name">${product.name}</div>
                <div class="employee-id">${product.category} • ${product.sales} sold</div>
            </div>
            <div class="product-revenue">
                <span class="revenue-value">${product.revenue}</span>
            </div>
        </div>
    `).join('');
}

// ===================================
// Chart Rendering
// ===================================

function renderChart() {
    new SimpleChart('customerFlowChart', {
        type: 'line',
        data: dashboardData.customerFlowData
    });
}

// ===================================
// Update KPIs
// ===================================

function updateKPIs() {
    const { footfallCount, revenueToday, conversionRate, avgBasketValue, storeCapacity } = dashboardData.kpis;

    document.getElementById('footfallCount').textContent = footfallCount.toLocaleString();
    document.getElementById('revenueToday').textContent = revenueToday;
    document.getElementById('conversionRate').textContent = `${conversionRate}%`;
    document.getElementById('avgBasketValue').textContent = avgBasketValue;
    document.getElementById('storeCapacity').textContent = `${storeCapacity}%`;
}

// ===================================
// Event Listeners
// ===================================

function setupEventListeners() {
    // Location selector
    const locationSelect = document.getElementById('locationSelect');
    locationSelect.addEventListener('change', (e) => {
        console.log('Location changed:', e.target.value);
        // In production, this would fetch data for the selected location
    });

    // Date selector
    const dateSelect = document.getElementById('dateSelect');
    dateSelect.addEventListener('change', (e) => {
        console.log('Date range changed:', e.target.value);
        // In production, this would fetch data for the selected date range
    });

    // Product item click
    document.querySelectorAll('.product-item').forEach(item => {
        item.addEventListener('click', () => {
            const productId = item.dataset.productId;
            viewProductDetails(productId);
        });
    });

    // CCTV feed click
    document.querySelectorAll('.cctv-feed').forEach(feed => {
        feed.addEventListener('click', () => {
            const cameraId = feed.dataset.cameraId;
            expandCamera(cameraId);
        });
    });

    // Expand cameras button
    const expandBtn = document.getElementById('expandCameras');
    if (expandBtn) {
        expandBtn.addEventListener('click', () => {
            toggleCameraGrid();
        });
    }
}

// ===================================
// Alert Actions
// ===================================

function viewAlert(alertId) {
    console.log('Viewing alert:', alertId);
    const alert = dashboardData.alerts.find(a => a.id === alertId);
    if (alert) {
        window.alert(`🎥 Opening CCTV footage\n\n${alert.title}\n${alert.description}\nLocation: ${alert.location}\nTime: ${alert.time}`);
    }
}

function dismissAlert(alertId) {
    console.log('Dismissing alert:', alertId);

    // Remove from data
    const alertIndex = dashboardData.alerts.findIndex(a => a.id === alertId);
    if (alertIndex !== -1) {
        dashboardData.alerts.splice(alertIndex, 1);
    }

    // Update UI
    renderAlerts();

    // Update notification badge
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
        notificationBadge.textContent = dashboardData.alerts.length;
    }
}

// ===================================
// Product Details
// ===================================

function viewProductDetails(productId) {
    console.log('Viewing product details:', productId);
    const product = dashboardData.topProducts.find(p => p.id === productId);
    if (product) {
        window.alert(`📊 Product Performance\n\n${product.name}\nCategory: ${product.category}\nSales Today: ${product.sales} units\nRevenue: ${product.revenue}\n\nIn production, this would show:\n- Hourly sales trend\n- Customer demographics\n- Stock levels\n- Related product recommendations\n- Price history`);
    }
}

// ===================================
// Camera Expansion
// ===================================

function expandCamera(cameraId) {
    console.log('Expanding camera:', cameraId);
    const camera = dashboardData.cctvFeeds.find(c => c.id == cameraId);
    if (camera) {
        window.alert(`🎥 Fullscreen Camera View\n\nCAM ${cameraId} - ${camera.location}\nStatus: LIVE\n\nIn production, this would show:\n- Full HD live feed\n- AI detection overlays\n- Recording controls\n- Incident tagging`);
    }
}

function toggleCameraGrid() {
    console.log('Toggling camera grid');
    window.alert('📹 Expanding to show all 12 cameras\n\nIn production, this would display:\n- Grid view with all store cameras\n- Zone selection filters\n- Multi-camera tracking\n- Incident replay');
}

// ===================================
// Real-Time Updates Simulation
// ===================================

function startRealTimeUpdates() {
    // Simulate real-time data updates every 6 seconds
    setInterval(() => {
        // Update footfall count
        const change = Math.floor(Math.random() * 20) - 5;
        dashboardData.kpis.footfallCount = Math.max(2500, dashboardData.kpis.footfallCount + change);

        // Update conversion rate slightly
        const conversionChange = (Math.random() * 0.4 - 0.2).toFixed(1);
        dashboardData.kpis.conversionRate = Math.max(30, Math.min(40, parseFloat((dashboardData.kpis.conversionRate + parseFloat(conversionChange)).toFixed(1))));

        // Update store capacity
        const capacityChange = Math.floor(Math.random() * 6) - 3;
        dashboardData.kpis.storeCapacity = Math.max(45, Math.min(85, dashboardData.kpis.storeCapacity + capacityChange));

        // Update KPIs
        updateKPIs();

        console.log('Real-time update:', new Date().toLocaleTimeString());
    }, 6000);
}

// ===================================
// Utility Functions
// ===================================

function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function getTimeAgo(timestamp) {
    const now = new Date();
    const diff = Math.floor((now - timestamp) / 1000); // seconds

    if (diff < 60) return `${diff} sec ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hr ago`;
    return `${Math.floor(diff / 86400)} days ago`;
}

// ===================================
// Export for other modules
// ===================================

window.retailDashboardAPI = {
    refreshData: initializeDashboard,
    viewProduct: viewProductDetails,
    dismissAlert: dismissAlert,
    viewAlert: viewAlert,
    expandCamera: expandCamera
};

console.log('InvEye Retail Dashboard initialized successfully');

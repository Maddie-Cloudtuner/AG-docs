// ===================================
// InvEye Dashboard - Main Application
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
    renderEmployeeList();
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
                    <div class="alert-details">Employee: ${alert.employee}</div>
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
// Employee List Rendering
// ===================================

function renderEmployeeList() {
    const employeeList = document.getElementById('employeeList');

    employeeList.innerHTML = dashboardData.employees.map(employee => `
        <div class="employee-item" data-employee-id="${employee.id}">
            <div class="employee-avatar">${employee.initials}</div>
            <div class="employee-info">
                <div class="employee-name">${employee.name}</div>
                <div class="employee-id">${employee.id} • ${employee.department}</div>
            </div>
            <div class="employee-status ${employee.status}">
                <span class="status-dot"></span>
                <span>${employee.status === 'on-site' ? 'On Site' : 'On Break'}</span>
            </div>
        </div>
    `).join('');
}

// ===================================
// Chart Rendering
// ===================================

function renderChart() {
    new SimpleChart('attendanceChart', {
        type: 'line',
        data: dashboardData.attendanceData
    });
}

// ===================================
// Update KPIs
// ===================================

function updateKPIs() {
    const { presentCount, complianceRate, activeAlerts, avgTime } = dashboardData.kpis;

    document.getElementById('presentCount').textContent = presentCount;
    document.getElementById('complianceRate').textContent = `${complianceRate}%`;
    document.getElementById('activeAlerts').textContent = activeAlerts;
    document.getElementById('avgTime').textContent = avgTime;
}

// ===================================
// Event Listeners
// ===================================

function setupEventListeners() {
    // Employee search
    const searchInput = document.getElementById('employeeSearch');
    searchInput.addEventListener('input', (e) => {
        filterEmployees(e.target.value);
    });

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

    // Employee item click
    document.querySelectorAll('.employee-item').forEach(item => {
        item.addEventListener('click', () => {
            const employeeId = item.dataset.employeeId;
            viewEmployeeProfile(employeeId);
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
// Filter Employees
// ===================================

function filterEmployees(searchTerm) {
    const filteredEmployees = dashboardData.employees.filter(employee =>
        employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        employee.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        employee.department.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const employeeList = document.getElementById('employeeList');

    if (filteredEmployees.length === 0) {
        employeeList.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #6B7280;">
                No employees found matching "${searchTerm}"
            </div>
        `;
        return;
    }

    employeeList.innerHTML = filteredEmployees.map(employee => `
        <div class="employee-item" data-employee-id="${employee.id}">
            <div class="employee-avatar">${employee.initials}</div>
            <div class="employee-info">
                <div class="employee-name">${employee.name}</div>
                <div class="employee-id">${employee.id} • ${employee.department}</div>
            </div>
            <div class="employee-status ${employee.status}">
                <span class="status-dot"></span>
                <span>${employee.status === 'on-site' ? 'On Site' : 'On Break'}</span>
            </div>
        </div>
    `).join('');

    // Reattach event listeners
    document.querySelectorAll('.employee-item').forEach(item => {
        item.addEventListener('click', () => {
            const employeeId = item.dataset.employeeId;
            viewEmployeeProfile(employeeId);
        });
    });
}

// ===================================
// Alert Actions
// ===================================

function viewAlert(alertId) {
    console.log('Viewing alert:', alertId);
    // In production, this would open a modal with CCTV footage
    alert(`Opening CCTV footage for alert #${alertId}`);
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

    // Update alert count
    dashboardData.kpis.activeAlerts = dashboardData.alerts.length;
    document.getElementById('activeAlerts').textContent = dashboardData.kpis.activeAlerts;

    // Update notification badge
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
        notificationBadge.textContent = dashboardData.alerts.length;
    }
}

// ===================================
// Employee Profile
// ===================================

function viewEmployeeProfile(employeeId) {
    console.log('Viewing profile for employee:', employeeId);
    // In production, this would navigate to employee detail page
    alert(`Opening profile for ${employeeId}\n\nIn production, this would show:\n- Today's timeline\n- Attendance history\n- Compliance scores\n- Productivity metrics\n- Incident log`);
}

// ===================================
// Camera Expansion
// ===================================

function expandCamera(cameraId) {
    console.log('Expanding camera:', cameraId);
    // In production, this would open fullscreen camera view
    alert(`Opening fullscreen view for CAM ${cameraId}`);
}

function toggleCameraGrid() {
    console.log('Toggling camera grid');
    // In production, this would expand to show all 16 cameras
    alert('Expanding to show all 16 cameras');
}

// ===================================
// Real-Time Updates Simulation
// ===================================

function startRealTimeUpdates() {
    // Simulate real-time data updates every 5 seconds
    setInterval(() => {
        // Randomly update employee count
        const change = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
        dashboardData.kpis.presentCount = Math.max(140, Math.min(150, dashboardData.kpis.presentCount + change));

        // Update compliance rate slightly
        const complianceChange = (Math.random() * 2 - 1).toFixed(0);
        dashboardData.kpis.complianceRate = Math.max(88, Math.min(98, parseInt(dashboardData.kpis.complianceRate) + parseInt(complianceChange)));

        // Update KPIs in UI
        updateKPIs();

        console.log('Real-time update:', new Date().toLocaleTimeString());
    }, 5000);
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

window.dashboardAPI = {
    refreshData: initializeDashboard,
    viewEmployee: viewEmployeeProfile,
    dismissAlert: dismissAlert,
    viewAlert: viewAlert
};

console.log('InvEye Dashboard initialized successfully');

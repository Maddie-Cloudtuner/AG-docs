/**
 * ROBOI PETROL PUMP DASHBOARD
 * Multi-page data with backend schema alignment
 */

// ===== MOCK DATA ALIGNED WITH BACKEND SCHEMA =====
// Based on: roboi-backend/schema_doc.md and app/models/schemas.py

const mockData = {
    // Site Summary (from /api/v1/sites/{siteId}/summary)
    siteSummary: {
        siteId: "RO001",
        status: "ONLINE",
        metrics: {
            activeSensors: 5,
            openAlerts: 3,
            trafficCount: 156,
            peakDensity: 8,
            criticalAlerts: 1,
            complianceScore: 82
        }
    },

    // Events (from /api/v1/sites/{siteId}/events)
    events: [
        {
            id: "evt-001",
            timestamp: Date.now() / 1000 - 120,
            sourceId: "1",
            sourceName: "Pump 1 Camera",
            type: "SAFETY",
            subType: "MOBILE_PHONE_USAGE",
            severity: "WARNING",
            metadata: {
                detectedObjects: ["person", "cell_phone"],
                confidence: 0.87,
                ai_insights: "Customer using mobile phone while refueling at Pump 1. Staff should intervene.",
                evidence_path: "/captures/RO001/D1/2026-01-12/capture_093245.jpg"
            }
        },
        {
            id: "evt-002",
            timestamp: Date.now() / 1000 - 900,
            sourceId: "2",
            sourceName: "Pump 2 Camera",
            type: "OPERATIONS",
            subType: "UNIFORM_VIOLATION",
            severity: "WARNING",
            metadata: {
                detectedObjects: ["person", "uniform"],
                confidence: 0.92,
                ai_insights: "Staff member at Pump 2 not wearing cap. Uniform score: 3/5",
                triaged_by: null
            }
        },
        {
            id: "evt-003",
            timestamp: Date.now() / 1000 - 3600,
            sourceId: "3",
            sourceName: "Entry Camera",
            type: "SECURITY",
            subType: "CROWD_GATHERING",
            severity: "INFO",
            metadata: {
                detectedObjects: ["person", "person", "person", "person", "car"],
                confidence: 0.78,
                ai_insights: "4 people gathered near entry. Normal activity - appears to be customers."
            }
        }
    ],

    // Staff Data (from recognition data in events)
    staff: [
        {
            id: "STF001",
            name: "Ramesh Kumar",
            role: "Pump Operator",
            photo: null,
            shift: "Morning (6 AM - 2 PM)",
            currentLocation: "Pump 1",
            uniformCompliance: true,
            vehiclesServed: 32,
            greetingRate: 85,
            zeroDisplayRate: 72,
            identity_id: 1001
        },
        {
            id: "STF002",
            name: "Suresh Patel",
            role: "Pump Operator",
            shift: "Morning (6 AM - 2 PM)",
            currentLocation: "Pump 2",
            uniformCompliance: false,
            uniformIssue: "Missing cap",
            vehiclesServed: 28,
            greetingRate: 70,
            zeroDisplayRate: 55,
            identity_id: 1002
        },
        {
            id: "STF003",
            name: "Amit Joshi",
            role: "FSM (Manager)",
            shift: "Morning (6 AM - 2 PM)",
            currentLocation: "Office",
            uniformCompliance: true,
            floorRounds: 8,
            identity_id: 1003
        },
        {
            id: "STF004",
            name: "Vikram Singh",
            role: "Air Station Operator",
            shift: "Morning (6 AM - 2 PM)",
            currentLocation: "Air Station",
            uniformCompliance: true,
            vehiclesServed: 34,
            identity_id: 1004
        }
    ],

    // Vehicles (from license plate detections)
    vehicles: [
        {
            plate: "GJ05AB7890",
            type: "car",
            make: "Maruti Swift",
            color: "White",
            pump: 1,
            fuelType: "Petrol",
            liters: 42.5,
            amount: 4250,
            timestamp: Date.now() / 1000 - 120,
            staff: "Ramesh Kumar"
        },
        {
            plate: "GJ01XX1234",
            type: "motorcycle",
            make: "Honda Activa",
            color: "Red",
            pump: 2,
            fuelType: "Petrol",
            liters: 5.2,
            amount: 520,
            timestamp: Date.now() / 1000 - 480,
            staff: "Suresh Patel"
        },
        {
            plate: "MH12CD5678",
            type: "truck",
            make: "Tata LPT",
            color: "Blue",
            pump: 3,
            fuelType: "Diesel",
            liters: 120,
            amount: 10800,
            timestamp: Date.now() / 1000 - 900,
            staff: "Ramesh Kumar"
        },
        {
            plate: "GJ18WX9999",
            type: "car",
            make: "Hyundai Creta",
            color: "Silver",
            pump: 1,
            fuelType: "Petrol",
            liters: 35,
            amount: 3500,
            timestamp: Date.now() / 1000 - 1320,
            staff: "Ramesh Kumar"
        },
        {
            plate: "GJ03KL4567",
            type: "car",
            make: "Tata Nexon",
            color: "Red",
            pump: 4,
            fuelType: "Diesel",
            liters: 28,
            amount: 2520,
            timestamp: Date.now() / 1000 - 1800,
            staff: "Suresh Patel"
        }
    ],

    // Cameras (based on cam_id, cam_name from schema)
    cameras: [
        {
            cam_id: 1,
            cam_name: "D1 - Pump 1 Camera",
            status: "online",
            location: "Dispenser Island 1",
            resolution: "1080p",
            fps: 15,
            lastEvent: Date.now() / 1000 - 120,
            detectionCount: 156,
            alertCount: 2
        },
        {
            cam_id: 2,
            cam_name: "D2 - Pump 2 Camera",
            status: "online",
            location: "Dispenser Island 2",
            resolution: "1080p",
            fps: 15,
            lastEvent: Date.now() / 1000 - 900,
            detectionCount: 142,
            alertCount: 1
        },
        {
            cam_id: 3,
            cam_name: "D3 - Pump 3 & 4 Camera",
            status: "online",
            location: "Dispenser Island 3-4",
            resolution: "1080p",
            fps: 15,
            lastEvent: Date.now() / 1000 - 600,
            detectionCount: 98,
            alertCount: 0
        },
        {
            cam_id: 4,
            cam_name: "Entry Camera",
            status: "online",
            location: "Main Entry Gate",
            resolution: "720p",
            fps: 10,
            lastEvent: Date.now() / 1000 - 3600,
            detectionCount: 234,
            alertCount: 0
        },
        {
            cam_id: 5,
            cam_name: "Air Station Camera",
            status: "online",
            location: "Air/Water Station",
            resolution: "720p",
            fps: 10,
            lastEvent: Date.now() / 1000 - 1800,
            detectionCount: 87,
            alertCount: 0
        }
    ],

    // Safety/Compliance Checks
    safetyChecks: {
        fire: { detected: false, lastCheck: Date.now() / 1000 - 120 },
        smoke: { detected: false, lastCheck: Date.now() / 1000 - 120 },
        smoking: { detected: false, incidents24h: 0 },
        mobilePhone: { detected: false, incidents24h: 3 },
        duCovers: { allClosed: true, openCount: 0 },
        manholes: { allCovered: true, openCount: 0 },
        plasticFill: { detected: false, incidents24h: 0 },
        cleanliness: { score: 5, issues: [] }
    },

    // Analytics (from /api/v1/sites/{siteId}/analytics)
    analytics: {
        distribution: [
            { label: "car", value: 89, percentage: 57.1 },
            { label: "motorcycle", value: 42, percentage: 26.9 },
            { label: "truck", value: 18, percentage: 11.5 },
            { label: "auto", value: 7, percentage: 4.5 }
        ],
        hourlyTraffic: {
            timestamps: [6, 7, 8, 9, 10, 11, 12, 13, 14],
            series: [
                { key: "vehicles", data: [8, 12, 18, 22, 15, 19, 28, 24, 10] },
                { key: "people", data: [12, 18, 25, 30, 22, 26, 38, 32, 15] }
            ]
        },
        peakOccupancy: [
            { location: "Pump 1", hour: 12, count: 8 },
            { location: "Pump 2", hour: 12, count: 6 },
            { location: "Entry", hour: 13, count: 5 }
        ]
    }
};

// ===== PAGE STATE =====
let currentPage = 'dashboard';

// ===== PAGE RENDER FUNCTIONS =====
const pageRenderers = {
    dashboard: renderDashboard,
    compliance: renderCompliancePage,
    safety: renderSafetyPage,
    vehicles: renderVehiclesPage,
    staff: renderStaffPage,
    cameras: renderCamerasPage
};

function renderDashboard() {
    return `
        <!-- Metrics Overview -->
        <section class="metrics-row">
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-label">Today's Revenue</span>
                    <span class="metric-trend up">+12.5%</span>
                </div>
                <div class="metric-value">₹2,34,500</div>
                <div class="metric-comparison">vs ₹2,08,400 yesterday</div>
            </div>
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-label">Vehicles Served</span>
                    <span class="metric-trend up">+8%</span>
                </div>
                <div class="metric-value">${mockData.siteSummary.metrics.trafficCount}</div>
                <div class="metric-comparison">128 fueled • 28 air/water only</div>
            </div>
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-label">Compliance Score</span>
                    <span class="metric-badge good">Good</span>
                </div>
                <div class="metric-value">${(mockData.siteSummary.metrics.complianceScore / 10).toFixed(1)}<span class="metric-unit">/10</span></div>
                <div class="metric-comparison">Target: 9.0 • Gap: ${(9 - mockData.siteSummary.metrics.complianceScore / 10).toFixed(1)} points</div>
            </div>
            <div class="metric-card alert">
                <div class="metric-header">
                    <span class="metric-label">Open Issues</span>
                    <span class="metric-badge warning">Action Needed</span>
                </div>
                <div class="metric-value">${mockData.siteSummary.metrics.openAlerts}</div>
                <div class="metric-comparison">${mockData.siteSummary.metrics.criticalAlerts} critical • ${mockData.siteSummary.metrics.openAlerts - mockData.siteSummary.metrics.criticalAlerts} warning</div>
            </div>
        </section>

        <!-- Main Grid -->
        <div class="grid-container">
            <div class="grid-column left">
                ${renderLiveOperations()}
                ${renderStaffSummary()}
            </div>
            <div class="grid-column right">
                ${renderSafetyGrid()}
                ${renderActionItems()}
                ${renderRecentVehicles()}
            </div>
        </div>
    `;
}

function renderLiveOperations() {
    const pumps = [
        { id: 1, status: 'active', vehicle: mockData.vehicles[0], staff: mockData.staff[0], timer: 154 },
        { id: 2, status: 'active', vehicle: mockData.vehicles[1], staff: mockData.staff[1], timer: 72 },
        { id: 3, status: 'idle', lastUsed: 4 },
        { id: 4, status: 'queued', vehicle: mockData.vehicles[2], waitTime: 3 }
    ];

    return `
        <section class="card operations-card">
            <div class="card-header">
                <h3>Live Operations</h3>
                <span class="live-indicator">● LIVE</span>
            </div>
            <div class="pump-grid">
                ${pumps.map(pump => {
        if (pump.status === 'active') {
            return `
                            <div class="pump-item active">
                                <div class="pump-number">${pump.id}</div>
                                <div class="pump-details">
                                    <span class="pump-status">Fueling</span>
                                    <span class="pump-vehicle">${pump.vehicle.color} ${pump.vehicle.make} • ${pump.vehicle.plate}</span>
                                    <span class="pump-staff">${pump.staff.name}</span>
                                </div>
                                <div class="pump-timer" data-pump="${pump.id}">${formatTime(pump.timer)}</div>
                            </div>
                        `;
        } else if (pump.status === 'idle') {
            return `
                            <div class="pump-item idle">
                                <div class="pump-number">${pump.id}</div>
                                <div class="pump-details">
                                    <span class="pump-status">Available</span>
                                    <span class="pump-info">Last used ${pump.lastUsed} min ago</span>
                                </div>
                            </div>
                        `;
        } else {
            return `
                            <div class="pump-item queued">
                                <div class="pump-number">${pump.id}</div>
                                <div class="pump-details">
                                    <span class="pump-status">1 vehicle waiting</span>
                                    <span class="pump-vehicle">${pump.vehicle.color} ${pump.vehicle.make} • ${pump.vehicle.plate}</span>
                                </div>
                                <div class="pump-wait">~${pump.waitTime} min wait</div>
                            </div>
                        `;
        }
    }).join('')}
            </div>
            <div class="card-footer">
                <span>Avg. service time: 3.2 min</span>
                <span>Peak hour: 12:00 - 1:00 PM</span>
            </div>
        </section>
    `;
}

function renderStaffSummary() {
    const onDutyStaff = mockData.staff.filter(s => s.shift.includes('Morning'));

    return `
        <section class="card staff-card">
            <div class="card-header">
                <h3>Staff on Duty</h3>
                <span class="shift-info">Morning Shift • 6 AM - 2 PM</span>
            </div>
            <div class="staff-list">
                ${onDutyStaff.slice(0, 3).map(staff => `
                    <div class="staff-item" data-staff-id="${staff.id}">
                        <div class="staff-avatar">${staff.name.split(' ').map(n => n[0]).join('')}</div>
                        <div class="staff-info">
                            <span class="staff-name">${staff.name}</span>
                            <span class="staff-role">${staff.role}</span>
                        </div>
                        <div class="staff-metrics">
                            <span class="staff-served">${staff.vehiclesServed ? staff.vehiclesServed + ' served' : staff.currentLocation}</span>
                            <div class="staff-compliance ${staff.uniformCompliance ? 'ok' : 'warning'}">
                                <span>${staff.uniformCompliance ? 'Uniform ✓' : staff.uniformIssue}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="staff-summary">
                <div class="summary-item">
                    <span class="summary-value">${Math.round(onDutyStaff.reduce((sum, s) => sum + (s.greetingRate || 0), 0) / 3)}%</span>
                    <span class="summary-label">Greeting rate</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value">${Math.round(onDutyStaff.reduce((sum, s) => sum + (s.zeroDisplayRate || 0), 0) / 3)}%</span>
                    <span class="summary-label">Zero display</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value">18/22</span>
                    <span class="summary-label">5L tests done</span>
                </div>
            </div>
        </section>
    `;
}

function renderSafetyGrid() {
    const checks = mockData.safetyChecks;

    return `
        <section class="card safety-card">
            <div class="card-header">
                <h3>Safety & Compliance</h3>
                <span class="last-check">Last AI scan: ${getTimeAgo(checks.fire.lastCheck)}</span>
            </div>
            <div class="safety-grid">
                <div class="safety-item ${checks.fire.detected ? 'danger' : 'ok'}">
                    <div class="safety-icon">🔥</div>
                    <div class="safety-info">
                        <span class="safety-label">Fire/Smoke</span>
                        <span class="safety-status">${checks.fire.detected ? 'DETECTED!' : 'Clear'}</span>
                    </div>
                </div>
                <div class="safety-item ${checks.smoking.incidents24h > 0 ? 'warning' : 'ok'}">
                    <div class="safety-icon">🚬</div>
                    <div class="safety-info">
                        <span class="safety-label">Smoking</span>
                        <span class="safety-status">${checks.smoking.incidents24h > 0 ? checks.smoking.incidents24h + ' incidents today' : 'None detected'}</span>
                    </div>
                </div>
                <div class="safety-item ${checks.duCovers.allClosed ? 'ok' : 'warning'}">
                    <div class="safety-icon">⛽</div>
                    <div class="safety-info">
                        <span class="safety-label">DU Covers</span>
                        <span class="safety-status">${checks.duCovers.allClosed ? 'All closed' : checks.duCovers.openCount + ' open'}</span>
                    </div>
                </div>
                <div class="safety-item ${checks.mobilePhone.incidents24h > 0 ? 'warning' : 'ok'}">
                    <div class="safety-icon">📱</div>
                    <div class="safety-info">
                        <span class="safety-label">Mobile Usage</span>
                        <span class="safety-status">${checks.mobilePhone.incidents24h > 0 ? checks.mobilePhone.incidents24h + ' incidents today' : 'None'}</span>
                    </div>
                </div>
                <div class="safety-item ${checks.manholes.allCovered ? 'ok' : 'danger'}">
                    <div class="safety-icon">🕳️</div>
                    <div class="safety-info">
                        <span class="safety-label">Manholes</span>
                        <span class="safety-status">${checks.manholes.allCovered ? 'All covered' : checks.manholes.openCount + ' open!'}</span>
                    </div>
                </div>
                <div class="safety-item ok">
                    <div class="safety-icon">🧹</div>
                    <div class="safety-info">
                        <span class="safety-label">Cleanliness</span>
                        <span class="safety-status">Good (${checks.cleanliness.score}/5)</span>
                    </div>
                </div>
            </div>
        </section>
    `;
}

function renderActionItems() {
    const issues = mockData.events.filter(e => e.severity !== 'INFO').slice(0, 3);

    return `
        <section class="card issues-card">
            <div class="card-header">
                <h3>Action Items</h3>
                <span class="issues-count">${issues.length} open</span>
            </div>
            <div class="issues-list">
                ${issues.map((issue, idx) => {
        const priority = issue.severity === 'CRITICAL' ? 'high' : issue.severity === 'WARNING' ? 'medium' : 'low';
        return `
                        <div class="issue-item ${priority}" data-event-id="${issue.id}">
                            <div class="issue-priority">${priority === 'high' ? '!' : priority === 'medium' ? '●' : '○'}</div>
                            <div class="issue-content">
                                <span class="issue-title">${formatSubType(issue.subType)}</span>
                                <span class="issue-desc">${issue.metadata.ai_insights?.substring(0, 80) || 'No details'}</span>
                                <span class="issue-time">Detected ${getTimeAgo(issue.timestamp)} • ${issue.sourceName}</span>
                            </div>
                            <button class="issue-action" data-action="resolve">${issue.metadata.triaged_by ? 'Resolved' : 'Resolve'}</button>
                        </div>
                    `;
    }).join('')}
            </div>
        </section>
    `;
}

function renderRecentVehicles() {
    return `
        <section class="card transactions-card">
            <div class="card-header">
                <h3>Recent Vehicles</h3>
                <a href="#" class="view-all" data-page="vehicles">View all →</a>
            </div>
            <div class="transactions-list">
                ${mockData.vehicles.slice(0, 4).map(v => `
                    <div class="transaction-item" data-plate="${v.plate}">
                        <div class="transaction-plate">${v.plate}</div>
                        <div class="transaction-details">
                            <span>${v.color} ${v.make}</span>
                            <span>Pump ${v.pump} • ${v.liters}L ${v.fuelType}</span>
                        </div>
                        <div class="transaction-time">${getTimeAgo(v.timestamp)}</div>
                    </div>
                `).join('')}
            </div>
            <div class="card-footer">
                <span>Plate recognition: 94% accurate today</span>
            </div>
        </section>
    `;
}

// ===== COMPLIANCE PAGE =====
function renderCompliancePage() {
    return `
        <section class="page-header">
            <h2>Compliance Dashboard</h2>
            <p>Track uniform, greeting, zero display, and 5L testing compliance</p>
        </section>
        
        <section class="metrics-row">
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">Uniform Compliance</span></div>
                <div class="metric-value">75<span class="metric-unit">%</span></div>
                <div class="metric-comparison">3 of 4 staff compliant</div>
            </div>
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">Greeting Rate</span></div>
                <div class="metric-value">78<span class="metric-unit">%</span></div>
                <div class="metric-comparison">Target: 90%</div>
            </div>
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">Zero Display</span></div>
                <div class="metric-value warning">62<span class="metric-unit">%</span></div>
                <div class="metric-comparison">Target: 80% • Action needed</div>
            </div>
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">5L Testing</span></div>
                <div class="metric-value">82<span class="metric-unit">%</span></div>
                <div class="metric-comparison">18 of 22 completed</div>
            </div>
        </section>
        
        <section class="card full-width">
            <div class="card-header"><h3>Staff Compliance Details</h3></div>
            <div class="data-table">
                <table>
                    <thead>
                        <tr>
                            <th>Staff</th>
                            <th>Role</th>
                            <th>Uniform</th>
                            <th>Greeting</th>
                            <th>Zero Display</th>
                            <th>Issues</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${mockData.staff.map(s => `
                            <tr>
                                <td><strong>${s.name}</strong></td>
                                <td>${s.role}</td>
                                <td class="${s.uniformCompliance ? 'status-ok' : 'status-warning'}">${s.uniformCompliance ? '✓ Compliant' : '⚠ Violation'}</td>
                                <td>${s.greetingRate || '-'}%</td>
                                <td>${s.zeroDisplayRate || '-'}%</td>
                                <td>${s.uniformIssue || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </section>
    `;
}

// ===== SAFETY PAGE =====
function renderSafetyPage() {
    const checks = mockData.safetyChecks;

    return `
        <section class="page-header">
            <h2>Safety Monitoring</h2>
            <p>Real-time safety event detection and alerts</p>
        </section>
        
        <section class="metrics-row">
            <div class="metric-card ${checks.fire.detected ? 'danger' : ''}">
                <div class="metric-header"><span class="metric-label">Fire/Smoke</span></div>
                <div class="metric-value">${checks.fire.detected ? '⚠️' : '✓'}</div>
                <div class="metric-comparison">${checks.fire.detected ? 'ALERT! Fire detected' : 'All clear'}</div>
            </div>
            <div class="metric-card ${checks.mobilePhone.incidents24h > 2 ? 'alert' : ''}">
                <div class="metric-header"><span class="metric-label">Mobile Usage</span></div>
                <div class="metric-value">${checks.mobilePhone.incidents24h}</div>
                <div class="metric-comparison">Incidents today (near pumps)</div>
            </div>
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">DU Covers</span></div>
                <div class="metric-value">${checks.duCovers.allClosed ? '✓' : checks.duCovers.openCount}</div>
                <div class="metric-comparison">${checks.duCovers.allClosed ? 'All closed' : 'Cover open!'}</div>
            </div>
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">Manholes</span></div>
                <div class="metric-value">${checks.manholes.allCovered ? '✓' : checks.manholes.openCount}</div>
                <div class="metric-comparison">${checks.manholes.allCovered ? 'All covered' : 'Cover missing!'}</div>
            </div>
        </section>
        
        <section class="card full-width">
            <div class="card-header"><h3>Safety Events (Last 24 Hours)</h3></div>
            <div class="data-table">
                <table>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Event</th>
                            <th>Location</th>
                            <th>Severity</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${mockData.events.filter(e => e.type === 'SAFETY').map(e => `
                            <tr>
                                <td>${new Date(e.timestamp * 1000).toLocaleTimeString()}</td>
                                <td>${formatSubType(e.subType)}</td>
                                <td>${e.sourceName}</td>
                                <td class="severity-${e.severity.toLowerCase()}">${e.severity}</td>
                                <td>${e.metadata.triaged_by ? 'Resolved' : 'Open'}</td>
                                <td><button class="btn-small">View</button></td>
                            </tr>
                        `).join('')}
                        ${mockData.events.filter(e => e.type === 'SAFETY').length === 0 ? '<tr><td colspan="6" class="empty-state">No safety events in last 24 hours ✓</td></tr>' : ''}
                    </tbody>
                </table>
            </div>
        </section>
    `;
}

// ===== VEHICLES PAGE =====
function renderVehiclesPage() {
    return `
        <section class="page-header">
            <h2>Vehicle Tracking</h2>
            <p>License plate recognition and transaction history</p>
        </section>
        
        <section class="metrics-row">
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">Vehicles Today</span></div>
                <div class="metric-value">${mockData.vehicles.length * 25}</div>
                <div class="metric-comparison">+8% vs yesterday</div>
            </div>
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">Plates Recognized</span></div>
                <div class="metric-value">94<span class="metric-unit">%</span></div>
                <div class="metric-comparison">High accuracy</div>
            </div>
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">Avg. Fuel Volume</span></div>
                <div class="metric-value">28<span class="metric-unit">L</span></div>
                <div class="metric-comparison">Per vehicle</div>
            </div>
            <div class="metric-card">
                <div class="metric-header"><span class="metric-label">Total Revenue</span></div>
                <div class="metric-value">₹2.3<span class="metric-unit">L</span></div>
                <div class="metric-comparison">Today</div>
            </div>
        </section>
        
        <section class="card full-width">
            <div class="card-header"><h3>Recent Transactions</h3></div>
            <div class="data-table">
                <table>
                    <thead>
                        <tr>
                            <th>License Plate</th>
                            <th>Vehicle</th>
                            <th>Pump</th>
                            <th>Fuel</th>
                            <th>Amount</th>
                            <th>Staff</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${mockData.vehicles.map(v => `
                            <tr>
                                <td><code class="plate">${v.plate}</code></td>
                                <td>${v.color} ${v.make}</td>
                                <td>Pump ${v.pump}</td>
                                <td>${v.liters}L ${v.fuelType}</td>
                                <td>₹${v.amount.toLocaleString()}</td>
                                <td>${v.staff}</td>
                                <td>${getTimeAgo(v.timestamp)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </section>
    `;
}

// ===== STAFF PAGE =====
function renderStaffPage() {
    return `
        <section class="page-header">
            <h2>Staff Management</h2>
            <p>Track staff performance, attendance, and compliance</p>
        </section>
        
        <section class="staff-grid-page">
            ${mockData.staff.map(s => `
                <div class="staff-profile-card">
                    <div class="profile-header">
                        <div class="profile-avatar">${s.name.split(' ').map(n => n[0]).join('')}</div>
                        <div class="profile-info">
                            <h4>${s.name}</h4>
                            <span class="role-badge">${s.role}</span>
                        </div>
                        <div class="profile-status ${s.uniformCompliance ? 'ok' : 'warning'}">
                            ${s.uniformCompliance ? '✓' : '⚠'}
                        </div>
                    </div>
                    <div class="profile-details">
                        <div class="detail-row">
                            <span>Current Location</span>
                            <strong>${s.currentLocation}</strong>
                        </div>
                        <div class="detail-row">
                            <span>Shift</span>
                            <strong>${s.shift}</strong>
                        </div>
                        ${s.vehiclesServed ? `
                            <div class="detail-row">
                                <span>Vehicles Served</span>
                                <strong>${s.vehiclesServed}</strong>
                            </div>
                        ` : ''}
                        ${s.greetingRate ? `
                            <div class="detail-row">
                                <span>Greeting Rate</span>
                                <strong>${s.greetingRate}%</strong>
                            </div>
                        ` : ''}
                        ${s.uniformIssue ? `
                            <div class="detail-row warning">
                                <span>Issue</span>
                                <strong>${s.uniformIssue}</strong>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
        </section>
    `;
}

// ===== CAMERAS PAGE =====
function renderCamerasPage() {
    return `
        <section class="page-header">
            <h2>Camera Status</h2>
            <p>Monitor all connected cameras and their detection activity</p>
        </section>
        
        <section class="cameras-grid">
            ${mockData.cameras.map(cam => `
                <div class="camera-card">
                    <div class="camera-preview">
                        <div class="camera-placeholder">
                            <span>📹</span>
                            <span class="cam-status ${cam.status}">${cam.status.toUpperCase()}</span>
                        </div>
                    </div>
                    <div class="camera-info">
                        <h4>${cam.cam_name}</h4>
                        <span class="camera-location">${cam.location}</span>
                        <div class="camera-stats">
                            <span>${cam.resolution} @ ${cam.fps}fps</span>
                            <span>${cam.detectionCount} detections</span>
                            <span>${cam.alertCount} alerts</span>
                        </div>
                        <div class="camera-last-event">
                            Last event: ${getTimeAgo(cam.lastEvent)}
                        </div>
                    </div>
                </div>
            `).join('')}
        </section>
    `;
}

// ===== HELPER FUNCTIONS =====
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function getTimeAgo(timestamp) {
    const now = Date.now() / 1000;
    const diff = now - timestamp;

    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return `${Math.floor(diff / 86400)} days ago`;
}

function formatSubType(subType) {
    return subType.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
}

// ===== NAVIGATION HANDLER =====
function navigateTo(page) {
    currentPage = page;

    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === page) {
            item.classList.add('active');
        }
    });

    // Update content
    const contentArea = document.querySelector('.content-area');
    if (contentArea && pageRenderers[page]) {
        contentArea.innerHTML = pageRenderers[page]();
        attachEventListeners();
    }

    showToast(`Navigating to ${page.charAt(0).toUpperCase() + page.slice(1)}`, 'info');
}

// ===== EVENT LISTENERS =====
function attachEventListeners() {
    // Nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            if (page) navigateTo(page);
        });
    });

    // View all links
    document.querySelectorAll('.view-all').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            if (page) navigateTo(page);
        });
    });

    // Issue actions
    document.querySelectorAll('.issue-action').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const issueItem = btn.closest('.issue-item');
            issueItem.style.opacity = '0.5';
            btn.textContent = 'Resolved';
            showToast('Issue marked as resolved', 'success');
        });
    });

    // Clickable items
    document.querySelectorAll('.staff-item, .transaction-item, .pump-item').forEach(item => {
        item.style.cursor = 'pointer';
        item.addEventListener('click', () => {
            showToast('Opening details...', 'info');
        });
    });

    // Refresh button
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
        showToast('Dashboard refreshed', 'success');
    });
}

// ===== TOAST NOTIFICATION =====
function showToast(message, type = 'info') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    const colors = { success: '#22c55e', error: '#dc2626', warning: '#eab308', info: '#d97706' };

    toast.style.cssText = `
        position: fixed; bottom: 24px; right: 24px; padding: 14px 24px;
        background: ${colors[type]}; color: white; border-radius: 10px;
        font-size: 13px; font-weight: 500; z-index: 1000;
        animation: slideUp 0.3s ease; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    `;

    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
`;
document.head.appendChild(style);

// ===== TIMER UPDATE =====
let pumpTimers = { 1: 154, 2: 72 };
setInterval(() => {
    Object.keys(pumpTimers).forEach(pumpId => {
        pumpTimers[pumpId]++;
        const timerEl = document.querySelector(`[data-pump="${pumpId}"]`);
        if (timerEl) timerEl.textContent = formatTime(pumpTimers[pumpId]);
    });
}, 1000);

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    attachEventListeners();
    console.log('🚀 Roboi Dashboard loaded with', Object.keys(mockData).length, 'data sources');
});

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
    initCameraSelector();  // Initialize camera dropdown
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

// ===== Delta Tracking Stats =====
let deltaStats = {
    uniquePeople: 0,
    uniqueObjects: 0,
    objectTypeCounts: {},  // { 'person': 5, 'chair': 2, ... }
    totalFrames: 0
};

// Calculate IoU (Intersection over Union) for bounding boxes
function calculateIoU(box1, box2) {
    const x1 = Math.max(box1.left, box2.left);
    const y1 = Math.max(box1.top, box2.top);
    const x2 = Math.min(box1.left + box1.width, box2.left + box2.width);
    const y2 = Math.min(box1.top + box1.height, box2.top + box2.height);

    const intersection = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
    const area1 = box1.width * box1.height;
    const area2 = box2.width * box2.height;
    const union = area1 + area2 - intersection;

    return union > 0 ? intersection / union : 0;
}

// ===== Process Detection Data with Delta Tracking =====
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

    // Delta tracking - track unique objects per camera
    const cameraTrackers = {};  // { 'CAFETERIA': { prevDetections: [], uniqueIds: Set } }
    deltaStats = {
        uniquePeople: 0,
        uniqueObjects: 0,
        objectTypeCounts: {},
        totalFrames: metricsData.length
    };

    // Sort metrics by timestamp
    const sortedMetrics = [...metricsData].sort((a, b) =>
        new Date(a.meta.ts) - new Date(b.meta.ts)
    );

    // Process metrics with delta tracking
    sortedMetrics.forEach((record, frameIndex) => {
        const camId = record.meta.cam_id;
        const peopleCount = record.data?.people_count || 0;
        const detections = record.data?.detections || [];

        // Initialize camera tracker
        if (!cameraTrackers[camId]) {
            cameraTrackers[camId] = {
                prevDetections: [],
                objectIds: {},  // { 'person': Set(), 'chair': Set() }
                nextId: {}      // { 'person': 1, 'chair': 1 }
            };
        }

        const tracker = cameraTrackers[camId];
        const currentDetections = [];

        // Match current detections to previous frame
        detections.forEach(det => {
            const label = det.label;
            const bbox = det.bbox;

            // Initialize tracking for this object type
            if (!tracker.objectIds[label]) {
                tracker.objectIds[label] = new Set();
                tracker.nextId[label] = 1;
            }

            // Try to match with previous frame using IoU
            let matched = false;
            let matchedId = null;
            const IOU_THRESHOLD = 0.3;  // Objects with >30% overlap are same

            for (const prevDet of tracker.prevDetections) {
                if (prevDet.label === label && prevDet.bbox) {
                    const iou = calculateIoU(bbox, prevDet.bbox);
                    if (iou >= IOU_THRESHOLD) {
                        matched = true;
                        matchedId = prevDet.trackId;
                        break;
                    }
                }
            }

            // Assign ID
            let trackId;
            if (matched && matchedId) {
                trackId = matchedId;  // Same object
            } else {
                // New object - assign new ID
                trackId = `${camId}_${label}_${tracker.nextId[label]++}`;
                tracker.objectIds[label].add(trackId);
            }

            currentDetections.push({
                ...det,
                trackId: trackId
            });

            // Update cumulative objectStats (for bars display)
            if (!objectStats[label]) {
                objectStats[label] = { count: 0, totalConf: 0 };
            }
            objectStats[label].count++;
            objectStats[label].totalConf += det.confidence;
        });

        // Update previous detections for next frame
        tracker.prevDetections = currentDetections;

        // Camera stats
        if (cameraStats[camId]) {
            cameraStats[camId].people += peopleCount;
            cameraStats[camId].count++;
        }

        // Timeline data
        timelineData.push({
            ts: new Date(record.meta.ts),
            cam: camId,
            people: peopleCount
        });
    });

    // Calculate unique counts from all camera trackers
    Object.values(cameraTrackers).forEach(tracker => {
        Object.entries(tracker.objectIds).forEach(([label, ids]) => {
            if (!deltaStats.objectTypeCounts[label]) {
                deltaStats.objectTypeCounts[label] = 0;
            }
            deltaStats.objectTypeCounts[label] += ids.size;

            if (label === 'person') {
                deltaStats.uniquePeople += ids.size;
            } else {
                deltaStats.uniqueObjects += ids.size;
            }
        });
    });

    // Keep only last 50 timeline entries
    timelineData = timelineData.slice(-50);

    console.log('Delta Stats:', deltaStats);

    // Sync data to localStorage for other pages (report.html, alerts.html)
    syncToLocalStorage();
}

// ===== Sync Data to LocalStorage =====
function syncToLocalStorage() {
    try {
        localStorage.setItem('deltaStats', JSON.stringify(deltaStats));
        localStorage.setItem('eventsData', JSON.stringify(eventsData));
        localStorage.setItem('cameraStats', JSON.stringify(cameraStats));
        localStorage.setItem('objectStats', JSON.stringify(objectStats));
    } catch (e) {
        console.warn('Failed to sync to localStorage:', e);
    }
}

// ===== Update UI =====
function updateUI() {
    updateCurrentTime();
    updateStatsBar();
    updateSelectedCamera();  // New single camera
    updateDetectedObjects(); // New detection panel
    updateAlerts();
    updateKPIs();
    updateObjectBars();
    updateTable();
    updateObjectTypesCount();
}

// ===== Camera Selection =====
let selectedCamera = 'CAFETERIA';

function initCameraSelector() {
    const selector = document.getElementById('cameraSelect');
    if (selector) {
        selector.addEventListener('change', (e) => {
            selectedCamera = e.target.value;
            updateSelectedCamera();
            updateDetectedObjects();
        });
    }
}

// ===== Update Selected Camera =====
function updateSelectedCamera() {
    const latestMetric = metricsData.filter(m => m.meta.cam_id === selectedCamera).pop();
    const latestEvent = eventsData.filter(e => e.meta.cam_id === selectedCamera).pop();

    // Update camera name
    const camName = document.getElementById('selectedCamName');
    const camLabel = document.getElementById('selectedCamLabel');
    const camStatus = document.getElementById('selectedCamStatus');
    const camPeople = document.getElementById('selectedCamPeople');

    if (camName) camName.textContent = selectedCamera;
    if (camLabel) camLabel.textContent = selectedCamera;

    if (latestMetric) {
        const count = latestMetric.data?.people_count || 0;
        if (camPeople) camPeople.textContent = count;
        if (camStatus) {
            camStatus.textContent = '● ' + latestMetric.meta.status;
            camStatus.className = 'cam-status' + (latestMetric.meta.status === 'CRITICAL' ? ' critical' : '');
        }
    }

    if (latestEvent && latestEvent.meta.status === 'CRITICAL') {
        if (camStatus) {
            camStatus.textContent = '● CRITICAL';
            camStatus.className = 'cam-status critical';
        }
    }
}

// ===== Update Detected Objects Panel =====
function updateDetectedObjects() {
    const container = document.getElementById('detectedObjectsList');
    if (!container) return;

    // Get latest detections for selected camera
    const latestMetric = metricsData.filter(m => m.meta.cam_id === selectedCamera).pop();
    const detections = latestMetric?.data?.detections || [];

    // Group by label
    const grouped = {};
    detections.forEach(det => {
        if (!grouped[det.label]) {
            grouped[det.label] = { count: 0, totalConf: 0 };
        }
        grouped[det.label].count++;
        grouped[det.label].totalConf += det.confidence;
    });

    // Sort by count
    const sorted = Object.entries(grouped).sort((a, b) => b[1].count - a[1].count);

    container.innerHTML = sorted.map(([label, stats]) => {
        const config = getObjectConfig(label);
        const avgConf = Math.round((stats.totalConf / stats.count) * 100);

        return `
            <div class="detection-object-item">
                <span class="detection-object-icon">${config.icon}</span>
                <div class="detection-object-info">
                    <span class="detection-object-label">${label}</span>
                    <span class="detection-object-conf">${avgConf}% avg conf</span>
                </div>
                <span class="detection-object-count">${stats.count}</span>
            </div>
        `;
    }).join('');

    if (sorted.length === 0) {
        container.innerHTML = '<div style="padding: 1rem; color: var(--text-muted); text-align: center;">No objects detected</div>';
    }
}

// ===== Update Object Types Count =====
function updateObjectTypesCount() {
    const el = document.getElementById('objectTypesCount');
    if (el) {
        const count = Object.keys(objectStats).length;
        el.textContent = `${count} Types`;
    }
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

    // Detection stats - USE DELTA STATS (IoU-based unique tracking)
    const uniqueObjectTypes = Object.keys(deltaStats.objectTypeCounts).length;

    // Display delta-tracked unique counts
    document.getElementById('kpi-detections').textContent = uniqueObjectTypes;
    document.getElementById('kpi-people-count').textContent = deltaStats.uniquePeople;
    document.getElementById('kpi-object-count').textContent = deltaStats.uniqueObjects;

    // Frame count
    const frameCountEl = document.getElementById('kpi-frame-count');
    if (frameCountEl) {
        frameCountEl.textContent = deltaStats.totalFrames;
    }
}

// ===== Object Icons & Colors Configuration =====
const OBJECT_CONFIG = {
    // Core COCO classes with icons and colors
    'person': { icon: '👤', color: '#3B82F6', class: 'person' },
    'bicycle': { icon: '🚲', color: '#8B5CF6', class: 'vehicle' },
    'car': { icon: '🚗', color: '#6366F1', class: 'vehicle' },
    'motorcycle': { icon: '🏍️', color: '#8B5CF6', class: 'vehicle' },
    'bus': { icon: '🚌', color: '#6366F1', class: 'vehicle' },
    'truck': { icon: '🚚', color: '#6366F1', class: 'vehicle' },
    'backpack': { icon: '🎒', color: '#F59E0B', class: 'accessory' },
    'umbrella': { icon: '☂️', color: '#EC4899', class: 'accessory' },
    'handbag': { icon: '👜', color: '#EC4899', class: 'accessory' },
    'suitcase': { icon: '🧳', color: '#F59E0B', class: 'accessory' },
    'bottle': { icon: '🍼', color: '#10B981', class: 'object' },
    'wine glass': { icon: '🍷', color: '#EF4444', class: 'object' },
    'cup': { icon: '☕', color: '#F59E0B', class: 'object' },
    'fork': { icon: '🍴', color: '#6B7280', class: 'object' },
    'knife': { icon: '🔪', color: '#EF4444', class: 'danger' },
    'spoon': { icon: '🥄', color: '#6B7280', class: 'object' },
    'bowl': { icon: '🥣', color: '#10B981', class: 'object' },
    'banana': { icon: '🍌', color: '#FBBF24', class: 'food' },
    'apple': { icon: '🍎', color: '#EF4444', class: 'food' },
    'sandwich': { icon: '🥪', color: '#F59E0B', class: 'food' },
    'orange': { icon: '🍊', color: '#F97316', class: 'food' },
    'pizza': { icon: '🍕', color: '#F59E0B', class: 'food' },
    'donut': { icon: '🍩', color: '#EC4899', class: 'food' },
    'cake': { icon: '🎂', color: '#EC4899', class: 'food' },
    'chair': { icon: '🪑', color: '#22C55E', class: 'chair' },
    'couch': { icon: '🛋️', color: '#22C55E', class: 'furniture' },
    'potted plant': { icon: '🪴', color: '#22C55E', class: 'potted-plant' },
    'bed': { icon: '🛏️', color: '#8B5CF6', class: 'furniture' },
    'dining table': { icon: '🍽️', color: '#6B7280', class: 'furniture' },
    'toilet': { icon: '🚽', color: '#6B7280', class: 'object' },
    'tv': { icon: '📺', color: '#7C3AED', class: 'tv' },
    'laptop': { icon: '💻', color: '#0EA5E9', class: 'laptop' },
    'mouse': { icon: '🖱️', color: '#6B7280', class: 'electronics' },
    'remote': { icon: '📱', color: '#6B7280', class: 'electronics' },
    'keyboard': { icon: '⌨️', color: '#6B7280', class: 'electronics' },
    'cell phone': { icon: '📱', color: '#0EA5E9', class: 'electronics' },
    'microwave': { icon: '📦', color: '#F59E0B', class: 'appliance' },
    'oven': { icon: '🔥', color: '#EF4444', class: 'appliance' },
    'toaster': { icon: '🍞', color: '#F59E0B', class: 'appliance' },
    'sink': { icon: '🚰', color: '#0EA5E9', class: 'object' },
    'refrigerator': { icon: '🧊', color: '#0EA5E9', class: 'appliance' },
    'book': { icon: '📚', color: '#8B5CF6', class: 'object' },
    'clock': { icon: '⏰', color: '#F59E0B', class: 'clock' },
    'vase': { icon: '🏺', color: '#EC4899', class: 'object' },
    'scissors': { icon: '✂️', color: '#EF4444', class: 'danger' },
    'teddy bear': { icon: '🧸', color: '#EC4899', class: 'object' },
    // Fire/Smoke/Fighting (custom classes)
    'fire': { icon: '🔥', color: '#DC2626', class: 'danger' },
    'smoke': { icon: '💨', color: '#6B7280', class: 'danger' },
    'fighting': { icon: '👊', color: '#DC2626', class: 'danger' },
    'violence': { icon: '⚠️', color: '#DC2626', class: 'danger' },
    'weapon': { icon: '🔫', color: '#DC2626', class: 'danger' }
};

// Get object configuration with fallback
function getObjectConfig(label) {
    return OBJECT_CONFIG[label] || { icon: '📦', color: '#6B7280', class: 'other' };
}

// ===== Update Object Bars (using delta-tracked unique counts) =====
function updateObjectBars() {
    const container = document.getElementById('objectBars');
    if (!container) return;

    // Use deltaStats for UNIQUE object counts
    const uniqueCounts = deltaStats.objectTypeCounts || {};

    // Sort objects by unique count
    const sorted = Object.entries(uniqueCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);  // Show top 10 objects

    const maxCount = sorted.length > 0 ? sorted[0][1] : 1;

    container.innerHTML = sorted.map(([label, uniqueCount]) => {
        const pct = Math.round((uniqueCount / maxCount) * 100);
        const config = getObjectConfig(label);

        // Get average confidence from objectStats if available
        const cumStats = objectStats[label] || { count: 1, totalConf: 0.8 };
        const avgConf = Math.round((cumStats.totalConf / cumStats.count) * 100);

        return `
            <div class="bar-item">
                <span class="bar-label">
                    <span class="object-icon">${config.icon}</span>
                    ${label}
                </span>
                <div class="bar-track">
                    <div class="bar-fill ${config.class}" style="width: ${pct}%; background-color: ${config.color}">
                        ${avgConf}%
                    </div>
                </div>
                <span class="bar-value">${uniqueCount}</span>
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

        // Get top 3 unique detection types with icons
        const uniqueLabels = [...new Set(detections.map(d => d.label))].slice(0, 4);
        const avgConf = detections.length > 0
            ? Math.round((detections.reduce((s, d) => s + d.confidence, 0) / detections.length) * 100)
            : 0;

        // Confidence bar color based on value
        const confColor = avgConf >= 70 ? '#22C55E' : avgConf >= 40 ? '#F59E0B' : '#DC2626';

        return `
            <tr class="${isEvent ? 'warning-row' : ''}">
                <td>${time}</td>
                <td>${record.meta.cam_id}</td>
                <td><span class="type-badge ${record.type.toLowerCase()}">${record.type}</span></td>
                <td><span class="status-badge ${status.toLowerCase()}">${status}</span></td>
                <td>${peopleCount}</td>
                <td>
                    <div class="detection-tags">
                        ${uniqueLabels.map(label => {
            const config = getObjectConfig(label);
            const count = detections.filter(d => d.label === label).length;
            return `<span class="detection-tag" title="${label}">${config.icon} ${count > 1 ? count : ''}</span>`;
        }).join('')}
                        ${uniqueLabels.length < [...new Set(detections.map(d => d.label))].length
                ? `<span class="detection-tag">+${[...new Set(detections.map(d => d.label))].length - uniqueLabels.length}</span>`
                : ''}
                    </div>
                </td>
                <td>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${avgConf}%; background-color: ${confColor}"></div>
                        <span class="conf-value">${avgConf}%</span>
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
let timelineChartInstance = null;

function initTimelineChart() {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;

    // Destroy existing chart if any
    if (timelineChartInstance) {
        timelineChartInstance.destroy();
    }

    // Format timestamps for display (include date if spans multiple days)
    const labels = timelineData.map(d => {
        const date = d.ts;
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const timeStr = date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
        return `${timeStr}`;
    });

    const cafeteriaData = timelineData.map(d => d.cam === 'CAFETERIA' ? d.people : null);
    const employeeData = timelineData.map(d => d.cam === 'EMPLOYEE_AREA' ? d.people : null);
    const receptionData = timelineData.map(d => d.cam === 'RECEPTION_AREA' ? d.people : null);
    const bossData = timelineData.map(d => d.cam === 'BOSS_CABIN' ? d.people : null);

    timelineChartInstance = new Chart(ctx, {
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
                },
                tooltip: {
                    callbacks: {
                        title: (items) => `Time: ${items[0].label}`,
                        label: (item) => `${item.dataset.label}: ${item.raw} people`
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: { display: false },
                    ticks: {
                        font: { size: 9 },
                        color: '#94A3B8',
                        maxRotation: 45,
                        minRotation: 45,
                        maxTicksLimit: 10
                    },
                    title: {
                        display: true,
                        text: 'Timestamp',
                        font: { size: 10, weight: 'bold' },
                        color: '#64748B'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: colors.grid },
                    ticks: { font: { size: 10 }, color: '#94A3B8' },
                    title: {
                        display: true,
                        text: 'People Count',
                        font: { size: 10, weight: 'bold' },
                        color: '#64748B'
                    }
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

// ===== Sample Data (fallback) - Extended with all object types =====
function getSampleData() {
    return [
        // METRIC example - CAFETERIA with multiple objects
        {
            "type": "METRIC",
            "meta": {
                "ts": "2025-12-16T13:37:10.971002Z",
                "cam_id": "CAFETERIA",
                "site": "HEAD_OFFICE",
                "status": "SAFE"
            },
            "data": {
                "people_count": 8,
                "detections": [
                    { "class_id": 0, "label": "person", "confidence": 0.9048, "bbox": { "top": 132, "left": 227, "width": 90, "height": 242 } },
                    { "class_id": 0, "label": "person", "confidence": 0.8989, "bbox": { "top": 136, "left": 328, "width": 87, "height": 245 } },
                    { "class_id": 0, "label": "person", "confidence": 0.8604, "bbox": { "top": 154, "left": 412, "width": 106, "height": 227 } },
                    { "class_id": 0, "label": "person", "confidence": 0.8462, "bbox": { "top": 129, "left": 498, "width": 68, "height": 226 } },
                    { "class_id": 0, "label": "person", "confidence": 0.729, "bbox": { "top": 117, "left": 472, "width": 37, "height": 89 } },
                    { "class_id": 39, "label": "bottle", "confidence": 0.3008, "bbox": { "top": 123, "left": 330, "width": 8, "height": 28 } },
                    { "class_id": 56, "label": "chair", "confidence": 0.363, "bbox": { "top": 252, "left": 388, "width": 48, "height": 130 } },
                    { "class_id": 68, "label": "microwave", "confidence": 0.3684, "bbox": { "top": 110, "left": 206, "width": 79, "height": 69 } }
                ]
            }
        },
        // METRIC example - EMPLOYEE_AREA with many objects
        {
            "type": "METRIC",
            "meta": {
                "ts": "2025-12-16T13:37:10.974344Z",
                "cam_id": "EMPLOYEE_AREA",
                "site": "HEAD_OFFICE",
                "status": "SAFE"
            },
            "data": {
                "people_count": 11,
                "detections": [
                    { "class_id": 0, "label": "person", "confidence": 0.9243, "bbox": { "top": 81, "left": 309, "width": 69, "height": 250 } },
                    { "class_id": 0, "label": "person", "confidence": 0.8071, "bbox": { "top": 83, "left": 238, "width": 56, "height": 110 } },
                    { "class_id": 0, "label": "person", "confidence": 0.6963, "bbox": { "top": 185, "left": 52, "width": 78, "height": 133 } },
                    { "class_id": 24, "label": "backpack", "confidence": 0.6284, "bbox": { "top": 209, "left": 6, "width": 31, "height": 43 } },
                    { "class_id": 56, "label": "chair", "confidence": 0.8042, "bbox": { "top": 217, "left": 30, "width": 100, "height": 140 } },
                    { "class_id": 56, "label": "chair", "confidence": 0.7056, "bbox": { "top": 124, "left": 421, "width": 58, "height": 68 } },
                    { "class_id": 60, "label": "dining table", "confidence": 0.3303, "bbox": { "top": 204, "left": 100, "width": 161, "height": 156 } },
                    { "class_id": 62, "label": "tv", "confidence": 0.8232, "bbox": { "top": 41, "left": 248, "width": 24, "height": 18 } },
                    { "class_id": 62, "label": "tv", "confidence": 0.6943, "bbox": { "top": 48, "left": 207, "width": 24, "height": 19 } },
                    { "class_id": 63, "label": "laptop", "confidence": 0.626, "bbox": { "top": 197, "left": 113, "width": 40, "height": 59 } },
                    { "class_id": 63, "label": "laptop", "confidence": 0.5488, "bbox": { "top": 156, "left": 172, "width": 37, "height": 22 } },
                    { "class_id": 74, "label": "clock", "confidence": 0.5698, "bbox": { "top": 10, "left": 137, "width": 16, "height": 17 } }
                ]
            }
        },
        // EVENT example - BOSS_CABIN restricted access
        {
            "type": "EVENT",
            "meta": {
                "ts": "2025-12-16T13:43:49.138755Z",
                "cam_id": "BOSS_CABIN",
                "site": "HEAD_OFFICE",
                "status": "CRITICAL"
            },
            "event": {
                "triggers": ["RESTRICTED_ACCESS_BOSS_CABIN"],
                "people_count": 1,
                "detections": [
                    { "class_id": 0, "label": "person", "confidence": 0.4822, "bbox": { "top": 32, "left": 10, "width": 77, "height": 98 } }
                ],
                "capture_triggered": true
            }
        },
        // Additional METRIC - RECEPTION_AREA
        {
            "type": "METRIC",
            "meta": {
                "ts": "2025-12-16T13:38:10.000000Z",
                "cam_id": "RECEPTION_AREA",
                "site": "HEAD_OFFICE",
                "status": "SAFE"
            },
            "data": {
                "people_count": 3,
                "detections": [
                    { "class_id": 0, "label": "person", "confidence": 0.88, "bbox": { "top": 100, "left": 200, "width": 80, "height": 200 } },
                    { "class_id": 0, "label": "person", "confidence": 0.75, "bbox": { "top": 110, "left": 350, "width": 70, "height": 180 } },
                    { "class_id": 56, "label": "chair", "confidence": 0.65, "bbox": { "top": 250, "left": 150, "width": 60, "height": 100 } },
                    { "class_id": 73, "label": "potted plant", "confidence": 0.55, "bbox": { "top": 50, "left": 400, "width": 40, "height": 80 } }
                ]
            }
        }
    ];
}

// ===== Critical Alert Banner =====
let dismissedAlerts = new Set();
let currentAlertId = null;

function updateCriticalAlertBanner() {
    const banner = document.getElementById('criticalAlertBanner');
    if (!banner) return;

    // Find the most recent CRITICAL event that hasn't been dismissed
    const criticalEvents = eventsData.filter(e =>
        e.meta.status === 'CRITICAL' &&
        !dismissedAlerts.has(e.meta.ts)
    );

    const latestCritical = criticalEvents[criticalEvents.length - 1];

    if (latestCritical) {
        currentAlertId = latestCritical.meta.ts;
        const triggers = latestCritical.event.triggers?.join(', ') || 'Critical Event Detected';
        const time = new Date(latestCritical.meta.ts);
        const timeAgo = getTimeAgo(time);

        document.getElementById('alertBannerTitle').textContent = 'CRITICAL ALERT';
        document.getElementById('alertBannerMessage').textContent = triggers.replace(/_/g, ' ');
        document.getElementById('alertBannerMeta').textContent = `${latestCritical.meta.cam_id} • ${timeAgo}`;

        banner.style.display = 'flex';
        document.body.classList.add('has-alert');
    } else {
        banner.style.display = 'none';
        document.body.classList.remove('has-alert');
        currentAlertId = null;
    }
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return date.toLocaleDateString();
}

function takeAlertAction() {
    if (!currentAlertId) return;

    // Find the alert details
    const alert = eventsData.find(e => e.meta.ts === currentAlertId);
    if (alert) {
        // Switch to the camera where the alert occurred
        selectedCamera = alert.meta.cam_id;
        const selector = document.getElementById('cameraSelect');
        if (selector) {
            selector.value = selectedCamera;
        }
        updateSelectedCamera();
        updateDetectedObjects();

        // Scroll to camera feed
        const cameraSection = document.querySelector('.single-camera-container');
        if (cameraSection) {
            cameraSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    // Dismiss after taking action
    dismissAlert();
}

function dismissAlert() {
    if (currentAlertId) {
        dismissedAlerts.add(currentAlertId);
    }
    updateCriticalAlertBanner();
}

// Update the updateUI function to include alert banner
const originalUpdateUI = updateUI;
updateUI = function () {
    originalUpdateUI();
    updateCriticalAlertBanner();
};

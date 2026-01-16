/**
 * ROBOI API Service Layer
 * Connects to the roboi-backend FastAPI server
 */

// Default configuration - can be overridden via UI
let API_CONFIG = {
    baseUrl: 'http://localhost:8000',
    apiKey: 'default_unsafe_key',
    siteId: 'ro001'
};

// Load saved config from localStorage
function loadConfig() {
    const saved = localStorage.getItem('roboi_config');
    if (saved) {
        API_CONFIG = { ...API_CONFIG, ...JSON.parse(saved) };
    }
}

// Save config to localStorage
function saveApiConfig(config) {
    API_CONFIG = { ...API_CONFIG, ...config };
    localStorage.setItem('roboi_config', JSON.stringify(API_CONFIG));
}

// Get API headers with authentication
function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'X-API-Key': API_CONFIG.apiKey
    };
}

// Generic fetch wrapper with error handling
async function apiFetch(endpoint, options = {}) {
    const url = `${API_CONFIG.baseUrl}/api/v1${endpoint}`;

    try {
        const response = await fetch(url, {
            ...options,
            headers: { ...getHeaders(), ...options.headers }
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        throw error;
    }
}

// ===== API ENDPOINTS =====

const API = {
    /**
     * Get site summary metrics
     * @param {number} startTime - Unix timestamp (optional)
     * @param {number} endTime - Unix timestamp (optional)
     */
    getSummary: async (startTime, endTime) => {
        let params = new URLSearchParams();
        if (startTime) params.append('startTime', startTime);
        if (endTime) params.append('endTime', endTime);

        const query = params.toString() ? `?${params}` : '';
        return apiFetch(`/sites/${API_CONFIG.siteId}/summary${query}`);
    },

    /**
     * Get site events/alerts
     * @param {number} limit - Max number of events (default 50)
     * @param {number} startTime - Unix timestamp (optional)
     * @param {number} endTime - Unix timestamp (optional)
     * @param {string} severity - CRITICAL, WARNING, INFO (optional)
     */
    getEvents: async (limit = 50, startTime, endTime, severity) => {
        let params = new URLSearchParams({ limit: limit.toString() });
        if (startTime) params.append('startTime', startTime);
        if (endTime) params.append('endTime', endTime);
        if (severity) params.append('severity', severity);

        return apiFetch(`/sites/${API_CONFIG.siteId}/events?${params}`);
    },

    /**
     * Get analytics distribution (object types breakdown)
     * @param {string} range - 12h, 24h, 7d, 30d, all
     * @param {number} startTime - Unix timestamp (optional)
     * @param {number} endTime - Unix timestamp (optional)
     */
    getDistribution: async (range = '24h', startTime, endTime) => {
        let params = new URLSearchParams({ range, viewType: 'distribution' });
        if (startTime) params.append('startTime', startTime);
        if (endTime) params.append('endTime', endTime);

        return apiFetch(`/sites/${API_CONFIG.siteId}/analytics?${params}`);
    },

    /**
     * Get object counts over time
     * @param {string} range - 12h, 24h, 7d, 30d, all
     * @param {number} startTime - Unix timestamp (optional)
     * @param {number} endTime - Unix timestamp (optional)
     */
    getObjectCounts: async (range = 'all', startTime, endTime) => {
        let params = new URLSearchParams({ range });
        if (startTime) params.append('startTime', startTime);
        if (endTime) params.append('endTime', endTime);

        return apiFetch(`/sites/${API_CONFIG.siteId}/analytics/object-counts?${params}`);
    },

    /**
     * Get detections with pagination and filters
     * @param {number} page - Page number (default 1)
     * @param {number} pageSize - Items per page (default 20)
     * @param {object} filters - { status, camera, minConfidence, startTime, endTime, eventType }
     */
    getDetections: async (page = 1, pageSize = 20, filters = {}) => {
        let params = new URLSearchParams({ page, pageSize });

        if (filters.status && filters.status !== 'ALL') params.append('status', filters.status);
        if (filters.camera) params.append('camera', filters.camera);
        if (filters.minConfidence) params.append('minConfidence', filters.minConfidence);
        if (filters.startTime) params.append('startTime', filters.startTime);
        if (filters.endTime) params.append('endTime', filters.endTime);
        if (filters.eventType && filters.eventType !== 'ALL') params.append('eventType', filters.eventType);

        return apiFetch(`/sites/${API_CONFIG.siteId}/detections?${params}`);
    },

    /**
     * Get heatmap data
     * @param {string} range - 12h, 24h, 7d, 30d, all
     */
    getHeatmap: async (range = '24h') => {
        return apiFetch(`/sites/${API_CONFIG.siteId}/analytics/heatmap?range=${range}`);
    },

    /**
     * Get peak occupancy data
     */
    getPeakOccupancy: async () => {
        return apiFetch(`/sites/${API_CONFIG.siteId}/analytics/peak-occupancy`);
    },

    /**
     * Health check
     */
    health: async () => {
        return apiFetch('/health');
    }
};

// ===== MOCK DATA FOR OFFLINE/DEMO MODE =====

const MOCK_DATA = {
    summary: {
        siteId: 'ro001',
        status: 'ONLINE',
        metrics: {
            activeSensors: 5,
            openAlerts: 30,
            trafficCount: 897,
            peakDensity: 8,
            criticalAlerts: 30,
            complianceScore: 82
        }
    },

    events: {
        events: [
            {
                id: 'evt_001',
                timestamp: Date.now() / 1000 - 300,
                sourceId: 'cam_d7',
                sourceName: 'D7-Employee Area',
                type: 'SAFETY',
                subType: 'Fire Detected',
                severity: 'CRITICAL',
                metadata: {
                    detectedObjects: ['fire', 'person', 'motorcycle'],
                    confidence: 0.89,
                    snapshotUrl: null,
                    ai_insights: JSON.stringify({
                        verdict: "CRITICAL ALERT - Fire/smoke detected near pump area",
                        kpiScore: 3,
                        kpiScores: { uniform: { score: 3, max: 5 }, cleanliness: { score: 4, max: 5 }, safety: { score: 1, max: 5 } },
                        utilization: 'medium',
                        metrics: { people: 2, vehicles: 1, staff: 1 },
                        alerts: ['Fire/Smoke Detected', 'Immediate Evacuation Required'],
                        overview: 'CRITICAL: Smoke/fire detected near fuel pump 3. One motorcycle present. Two people in vicinity.',
                        deepdive: 'Smoke visible near motorcycle exhaust area. Could be vehicle exhaust or actual fire.',
                        insights: 'Potential fire hazard detected. Staff should investigate immediately.',
                        tldr: 'CRITICAL | Safety: 1/5 | FIRE/SMOKE AT PUMP 3'
                    }),
                    image_count: 5,
                    video_count: 1,
                    evidence_path: 'india_gujarat_ahmedabad_ro001_forecourt_1767447005'
                }
            },
            {
                id: 'evt_002',
                timestamp: Date.now() / 1000 - 600,
                sourceId: 'cam_d5',
                sourceName: 'D5-Forecourt',
                type: 'OPERATIONS',
                subType: 'Crowd Policy Violation',
                severity: 'WARNING',
                metadata: {
                    detectedObjects: ['car', 'truck', 'person'],
                    confidence: 0.75,
                    snapshotUrl: null,
                    ai_insights: JSON.stringify({
                        verdict: "KPI Analysis - 7/10 compliance. 1 issue found.",
                        kpiScore: 7,
                        kpiScores: { uniform: { score: 1, max: 5 }, cleanliness: { score: 5, max: 5 }, safety: { score: 5, max: 5 } },
                        utilization: 'low',
                        metrics: { people: 1, vehicles: 3, staff: 0 },
                        alerts: ['No Uniformed Staff Visible'],
                        overview: 'Petrol pump premises during daylight hours. Vehicles: 3. Staff: 0 uniformed.',
                        deepdive: 'One white car parked in foreground. A white SUV near fuel pumps. Truck visible in background.',
                        insights: 'No uniformed staff is visible at the pump. Premises appear clean.',
                        tldr: 'KPI: 7/10 | Uniform: 1/5 | No uniformed staff visible'
                    }),
                    image_count: 3,
                    video_count: 0,
                    evidence_path: 'india_gujarat_ahmedabad_ro001_forecourt_1767447305'
                }
            },
            {
                id: 'evt_003',
                timestamp: Date.now() / 1000 - 900,
                sourceId: 'cam_d7',
                sourceName: 'D7-Employee Area',
                type: 'OPERATIONS',
                subType: 'Uniform Violation',
                severity: 'WARNING',
                metadata: {
                    detectedObjects: ['person', 'staff'],
                    confidence: 0.82,
                    snapshotUrl: null,
                    ai_insights: JSON.stringify({
                        verdict: "KPI Analysis - 6/10 compliance. 2 issues found.",
                        kpiScore: 6,
                        kpiScores: { uniform: { score: 2, max: 5 }, cleanliness: { score: 4, max: 5 }, safety: { score: 5, max: 5 } },
                        utilization: 'medium',
                        metrics: { people: 3, vehicles: 2, staff: 2 },
                        alerts: ['Staff Missing Cap', 'Improper Footwear'],
                        overview: 'Active fueling operations. 2 staff members visible. Uniform compliance issues.',
                        deepdive: 'Staff at pump 1 not wearing cap. Second staff wearing sandals.',
                        insights: 'Two uniform violations detected. Reminder needed about uniform requirements.',
                        tldr: 'KPI: 6/10 | Uniform: 2/5 | 2 uniform issues detected'
                    }),
                    image_count: 2,
                    video_count: 0,
                    evidence_path: null
                }
            },
            {
                id: 'evt_004',
                timestamp: Date.now() / 1000 - 1200,
                sourceId: 'cam_d5',
                sourceName: 'D5-Forecourt',
                type: 'OPERATIONS',
                subType: 'KPI Analysis Complete',
                severity: 'INFO',
                metadata: {
                    detectedObjects: ['car', 'person'],
                    confidence: 0.95,
                    snapshotUrl: null,
                    ai_insights: JSON.stringify({
                        verdict: "KPI Analysis - 10/10 compliance. 0 issues found.",
                        kpiScore: 10,
                        kpiScores: { uniform: { score: 5, max: 5 }, cleanliness: { score: 5, max: 5 }, safety: { score: 5, max: 5 } },
                        utilization: 'high',
                        metrics: { people: 5, vehicles: 4, staff: 2 },
                        alerts: [],
                        overview: 'Active petrol pump with excellent operations. All KPIs compliant.',
                        deepdive: 'Four vehicles being served. Staff wearing complete uniform.',
                        insights: 'Excellent operations. All staff in proper uniform. Area clean and organized.',
                        tldr: 'KPI: 10/10 | Excellent operations'
                    }),
                    image_count: 4,
                    video_count: 1,
                    evidence_path: null
                }
            }
        ]
    },

    distribution: [
        { label: 'Person', value: 450, percentage: 50.2 },
        { label: 'Car', value: 180, percentage: 20.1 },
        { label: 'Motorcycle', value: 120, percentage: 13.4 },
        { label: 'Truck', value: 80, percentage: 8.9 },
        { label: 'Staff', value: 45, percentage: 5.0 },
        { label: 'Other', value: 22, percentage: 2.4 }
    ],

    objectCounts: {
        data: [
            { timestamp: Date.now() / 1000 - 7200, object: 'person', count: 45 },
            { timestamp: Date.now() / 1000 - 7200, object: 'car', count: 12 },
            { timestamp: Date.now() / 1000 - 3600, object: 'person', count: 67 },
            { timestamp: Date.now() / 1000 - 3600, object: 'car', count: 18 },
            { timestamp: Date.now() / 1000, object: 'person', count: 52 },
            { timestamp: Date.now() / 1000, object: 'car', count: 15 }
        ]
    },

    detections: {
        items: [],
        total: 100,
        page: 1,
        pageSize: 20,
        totalPages: 5
    }
};

// Populate mock detections
for (let i = 0; i < 20; i++) {
    MOCK_DATA.detections.items.push({
        id: `det_${i}`,
        timestamp: Date.now() / 1000 - (i * 180),
        sourceId: `cam_d${5 + (i % 4)}`,
        sourceName: `D${5 + (i % 4)}-Camera`,
        type: i % 3 === 0 ? 'SAFETY' : 'OPERATIONS',
        subType: ['Person Detected', 'Vehicle Entry', 'Uniform Check', 'Crowd Analysis'][i % 4],
        severity: ['CRITICAL', 'WARNING', 'INFO', 'TRIAGED'][i % 4],
        metadata: {
            detectedObjects: ['person', 'car', 'truck'].slice(0, (i % 3) + 1),
            confidence: 0.7 + (Math.random() * 0.25)
        }
    });
}

// ===== API WRAPPER WITH FALLBACK TO MOCK =====

const RoboiAPI = {
    getSummary: async (...args) => {
        try {
            return await API.getSummary(...args);
        } catch {
            console.log('Using mock summary data');
            return MOCK_DATA.summary;
        }
    },

    getEvents: async (...args) => {
        try {
            return await API.getEvents(...args);
        } catch {
            console.log('Using mock events data');
            return MOCK_DATA.events;
        }
    },

    getDistribution: async (...args) => {
        try {
            return await API.getDistribution(...args);
        } catch {
            console.log('Using mock distribution data');
            return MOCK_DATA.distribution;
        }
    },

    getObjectCounts: async (...args) => {
        try {
            return await API.getObjectCounts(...args);
        } catch {
            console.log('Using mock object counts');
            return MOCK_DATA.objectCounts;
        }
    },

    getDetections: async (...args) => {
        try {
            return await API.getDetections(...args);
        } catch {
            console.log('Using mock detections');
            return MOCK_DATA.detections;
        }
    },

    getHeatmap: async (...args) => {
        try {
            return await API.getHeatmap(...args);
        } catch {
            console.log('Using mock heatmap');
            return { data: [] };
        }
    }
};

// Initialize config on load
loadConfig();

console.log('🔌 Roboi API loaded. Config:', API_CONFIG);

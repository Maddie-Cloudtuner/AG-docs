// ===================================
// InvEye Nayara Dashboard - Mock Data
// ===================================

const mockData = {
    // Real-time Alerts with Severity
    alerts: [
        {
            id: 1,
            severity: 'red',
            title: 'No Smoking Violation',
            location: 'DU Island 3',
            camera: 'Camera #12',
            time: '2 min ago',
            description: 'Person detected smoking near fuel dispensing area'
        },
        {
            id: 2,
            severity: 'red',
            title: 'Static Discharge Not Followed',
            location: 'Tanker Unloading Bay',
            camera: 'Camera #18',
            time: '8 min ago',
            description: 'Grounding cable not connected before unloading'
        },
        {
            id: 3,
            severity: 'orange',
            title: 'PPE Non-Compliance',
            location: 'DU Island 2',
            camera: 'Camera #8',
            time: '12 min ago',
            description: 'Staff not wearing safety helmet during fueling'
        },
        {
            id: 4,
            severity: 'orange',
            title: 'Queue Wait Time Exceeded',
            location: 'DU Island 1',
            camera: 'Camera #4',
            time: '18 min ago',
            description: 'Customer wait time: 11 min (Target: < 5 min)'
        },
        {
            id: 5,
            severity: 'orange',
            title: 'Uniform Compliance Issue',
            location: 'Forecourt',
            camera: 'Camera #6',
            time: '25 min ago',
            description: 'Staff uniform not properly worn'
        },
        {
            id: 6,
            severity: 'yellow',
            title: 'Housekeeping Below Standard',
            location: 'Forecourt Area',
            camera: 'Camera #3',
            time: '1 hour ago',
            description: 'Forecourt cleanliness score: 76% (Target: ≥ 80%)'
        },
        {
            id: 7,
            severity: 'yellow',
            title: 'Daily Checklist Not Updated',
            location: 'Office',
            camera: 'N/A',
            time: '2 hours ago',
            description: 'Morning shift checklist incomplete'
        },
        {
            id: 8,
            severity: 'yellow',
            title: 'Restroom Cleanliness',
            location: 'Customer Restroom',
            camera: 'Camera #22',
            time: '3 hours ago',
            description: 'Cleaning required'
        }
    ],

    // CCTV Camera Feeds
    cctvFeeds: [
        {
            id: 1,
            name: 'Forecourt Entry',
            location: 'Main Gate',
            status: 'LIVE',
            //  Placeholder image (dark gradient)
            image: null
        },
        {
            id: 2,
            name: 'DU Island 1-2',
            location: 'Dispensing Area',
            status: 'LIVE',
            image: null
        },
        {
            id: 3,
            name: 'DU Island 3-4',
            location: 'Dispensing Area',
            status: 'LIVE',
            image: null
        },
        {
            id: 4,
            name: 'Tanker Bay',
            location: 'Unloading Zone',
            status: 'LIVE',
            image: null
        },
        {
            id: 5,
            name: 'Cash Counter',
            location: 'Shop Area',
            status: 'LIVE',
            image: null
        },
        {
            id: 6,
            name: 'Perimeter',
            location: 'Tank Farm',
            status: 'LIVE',
            image: null
        }
    ],

    // Hourly Fuel Dispensing Data for Chart
    fuelData: {
        labels: ['6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM'],
        ms: [420, 580, 720, 890, 1050, 1180, 1340, 1520, 1680, 1420, 1180, 950],  // MS (Petrol) in liters
        hsd: [680, 890, 1120, 1340, 1580, 1720, 1890, 2050, 2180, 1920, 1680, 1450]  // HSD (Diesel) in liters
    },

    // Compliance by Category
    compliance: {
        'Safety & Compliance': 88,
        'Fuel Quality & Quantity': 100,
        'Equipment & Asset': 95,
        'Operational Efficiency': 78,
        'Regulatory & Licensing': 100
    },

    // Fuel Tank Status
    tanks: {
        ms: {
            product: 'MS (Petrol)',
            currentLevel: 12485,  // liters
            capacity: 18350,  // liters
            density: 738.2,  // kg/m³
            targetDensity: 738.0,
            tolerance: 0.5,
            waterLevel: 5,  // mm
            maxWater: 10,  // mm
            temperature: 28.5,  // °C
            status: 'good'
        },
        hsd: {
            product: 'HSD (Diesel)',
            currentLevel: 8920,  // liters
            capacity: 20000,  // liters
            density: 834.1,  // kg/m³
            targetDensity: 834.0,
            tolerance: 0.5,
            waterLevel: 3,  // mm
            maxWater: 10,  // mm
            temperature: 29.1,  // °C
            status: 'good'
        }
    },

    // Today's Operations Summary
    operations: {
        customersServed: 487,
        totalRevenue: 482150,  // INR
        msDispensed: 6840,  // liters
        hsdDispensed: 8920,  // liters
        avgTransactionValue: 990,  // INR
        peakHour: '2:00-4:00 PM',
        activeDUs: 4,
        totalDUs: 4
    },

    // KPI Summary
    kpis: {
        redAlerts: 2,
        orangeAlerts: 7,
        yellowAlerts: 14,
        compliantKPIs: 50,
        totalKPIs: 73,
        complianceScore: 91,
        cctvUptime: 95,
        ppeCompliance: 92,
        fuelQuality: 100
    },

    // Regulatory Certificates
    certificates: [
        {
            id: 1,
            name: 'PESO License',
            authority: 'Petroleum & Explosives Safety Organization',
            issueDate: '2023-06-15',
            expiryDate: '2025-06-15',
            status: 'valid',
            daysToExpiry: 189
        },
        {
            id: 2,
            name: 'Fire NOC',
            authority: 'Fire Department',
            issueDate: '2023-08-22',
            expiryDate: '2025-08-22',
            status: 'valid',
            daysToExpiry: 257
        },
        {
            id: 3,
            name: 'Weights & Measures',
            authority: 'Legal Metrology Department',
            issueDate: '2023-12-18',
            expiryDate: '2024-12-18',
            status: 'expiring',
            daysToExpiry: 10
        },
        {
            id: 4,
            name: 'Pollution Control',
            authority: 'State Pollution Control Board',
            issueDate: '2024-03-10',
            expiryDate: '2025-03-10',
            status: 'valid',
            daysToExpiry: 92
        }
    ]
};

// Helper Functions
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount).replace('₹', '₹');
};

const formatNumber = (num) => {
    return new Intl.NumberFormat('en-IN').format(num);
};

const getTimeAgo = (minutes) => {
    if (minutes < 60) return `${minutes} min ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { mockData, formatCurrency, formatNumber, getTimeAgo };
}

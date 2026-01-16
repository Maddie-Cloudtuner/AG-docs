// ===================================
// InvEye Retail Dashboard - Sample Data
// ===================================

const dashboardData = {
    // CCTV Feeds
    cctvFeeds: [
        {
            id: 1,
            name: "CAM 1",
            location: "Main Entrance",
            status: "live",
            thumbnail: "data:image/svg+xml,%3Csvg width='640' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='640' height='360' fill='%231F2937'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='%239CA3AF'%3EEntrance%3C/text%3E%3C/svg%3E"
        },
        {
            id: 2,
            name: "CAM 2",
            location: "Electronics Section",
            status: "live",
            thumbnail: "data:image/svg+xml,%3Csvg width='640' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='640' height='360' fill='%231F2937'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='%239CA3AF'%3EElectronics%3C/text%3E%3C/svg%3E"
        },
        {
            id: 3,
            name: "CAM 3",
            location: "Checkout Area",
            status: "live",
            thumbnail: "data:image/svg+xml,%3Csvg width='640' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='640' height='360' fill='%231F2937'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='%239CA3AF'%3ECheckout%3C/text%3E%3C/svg%3E"
        },
        {
            id: 4,
            name: "CAM 4",
            location: "Fashion Department",
            status: "live",
            thumbnail: "data:image/svg+xml,%3Csvg width='640' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='640' height='360' fill='%231F2937'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='%239CA3AF'%3EFashion%3C/text%3E%3C/svg%3E"
        }
    ],

    // Security Alerts
    alerts: [
        {
            id: 1,
            severity: "critical",
            title: "Suspicious Behavior Detected",
            description: "Person loitering near high-value items",
            location: "Electronics (CAM #2)",
            time: "3 min ago",
            icon: "🚨"
        },
        {
            id: 2,
            severity: "high",
            title: "Possible Shoplifting",
            description: "Concealment action detected",
            location: "Fashion Area (CAM #4)",
            time: "8 min ago",
            icon: "⚠️"
        },
        {
            id: 3,
            severity: "medium",
            title: "Spill Detected",
            description: "Floor hazard in aisle 5",
            location: "Groceries Section",
            time: "15 min ago",
            icon: "🧹"
        },
        {
            id: 4,
            severity: "high",
            title: "Unauthorized Access",
            description: "Customer in staff-only area",
            location: "Storage Room (CAM #7)",
            time: "20 min ago",
            icon: "🚪"
        },
        {
            id: 5,
            severity: "medium",
            title: "Stock Alert",
            description: "Low inventory detected on shelf",
            location: "Electronics Section",
            time: "25 min ago",
            icon: "📦"
        }
    ],

    // Top Selling Products
    topProducts: [
        {
            id: "PRD-001",
            name: "iPhone 15 Pro",
            category: "Electronics",
            sales: 23,
            revenue: "₹2.76L",
            icon: "📱"
        },
        {
            id: "PRD-002",
            name: "Nike Air Max Shoes",
            category: "Fashion",
            sales: 18,
            revenue: "₹1.44L",
            icon: "👟"
        },
        {
            id: "PRD-003",
            name: "Samsung 4K TV 55\"",
            category: "Electronics",
            sales: 12,
            revenue: "₹4.8L",
            icon: "📺"
        },
        {
            id: "PRD-004",
            name: "Levi's Jeans",
            category: "Fashion",
            sales: 34,
            revenue: "₹1.36L",
            icon: "👖"
        },
        {
            id: "PRD-005",
            name: "Apple Watch Series 9",
            category: "Electronics",
            sales: 15,
            revenue: "₹5.25L",
            icon: "⌚"
        }
    ],

    // Customer Flow Data (Today's hourly breakdown)
    customerFlowData: {
        labels: ['9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm'],
        datasets: [
            {
                label: 'Visitors',
                data: [145, 234, 312, 487, 456, 512, 423, 389, 267],
                borderColor: '#8B5CF6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Purchases',
                data: [52, 89, 124, 178, 167, 189, 156, 142, 97],
                borderColor: '#10B981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }
        ]
    },

    // KPI Values
    kpis: {
        footfallCount: 2847,
        revenueToday: "₹3.64L",
        conversionRate: 34.2,
        avgBasketValue: "₹1,247",
        storeCapacity: 68
    }
};

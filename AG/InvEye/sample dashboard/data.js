// ===================================
// InvEye Dashboard - Sample Data
// ===================================

const dashboardData = {
    // CCTV Feeds
    cctvFeeds: [
        {
            id: 1,
            name: "CAM 1",
            location: "Main Gate - Entry",
            status: "live",
            thumbnail: "data:image/svg+xml,%3Csvg width='640' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='640' height='360' fill='%231F2937'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='%239CA3AF'%3EMain Gate%3C/text%3E%3C/svg%3E"
        },
        {
            id: 2,
            name: "CAM 2",
            location: "Production Floor B",
            status: "live",
            thumbnail: "data:image/svg+xml,%3Csvg width='640' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='640' height='360' fill='%231F2937'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='%239CA3AF'%3EFloor B%3C/text%3E%3C/svg%3E"
        },
        {
            id: 3,
            name: "CAM 3",
            location: "Break Room A",
            status: "live",
            thumbnail: "data:image/svg+xml,%3Csvg width='640' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='640' height='360' fill='%231F2937'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='%239CA3AF'%3EBreak Room%3C/text%3E%3C/svg%3E"
        },
        {
            id: 4,
            name: "CAM 4",
            location: "Exit C - Parking",
            status: "live",
            thumbnail: "data:image/svg+xml,%3Csvg width='640' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='640' height='360' fill='%231F2937'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='%239CA3AF'%3EExit Parking%3C/text%3E%3C/svg%3E"
        }
    ],

    // Real-time Alerts
    alerts: [
        {
            id: 1,
            severity: "critical",
            title: "Restricted Area Breach",
            employee: "Unknown Person",
            location: "Server Room (CAM #8)",
            time: "2 min ago",
            icon: "⚠️"
        },
        {
            id: 2,
            severity: "high",
            title: "No PPE Detected",
            employee: "John Doe (#EMP-1234)",
            location: "Production Floor (CAM #12)",
            time: "5 min ago",
            icon: "🦺"
        },
        {
            id: 3,
            severity: "medium",
            title: "Unauthorized Phone Use",
            employee: "Sarah Lee (#EMP-789)",
            location: "Workstation B-15",
            time: "15 min ago",
            icon: "📱"
        }
    ],

    // Employee List
    employees: [
        {
            id: "EMP-1234",
            name: "John Doe",
            initials: "JD",
            status: "on-site",
            department: "Production",
            clockIn: "9:02 AM"
        },
        {
            id: "EMP-5678",
            name: "Sarah Lee",
            initials: "SL",
            status: "on-break",
            department: "Quality Control",
            clockIn: "8:58 AM"
        },
        {
            id: "EMP-9012",
            name: "Mike Johnson",
            initials: "MJ",
            status: "on-site",
            department: "Assembly",
            clockIn: "9:05 AM"
        },
        {
            id: "EMP-3456",
            name: "Emily Chen",
            initials: "EC",
            status: "on-site",
            department: "Packaging",
            clockIn: "9:00 AM"
        },
        {
            id: "EMP-7890",
            name: "David Wilson",
            initials: "DW",
            status: "on-site",
            department: "Production",
            clockIn: "9:10 AM"
        },
        {
            id: "EMP-2345",
            name: "Lisa Anderson",
            initials: "LA",
            status: "on-break",
            department: "Quality Control",
            clockIn: "9:03 AM"
        },
        {
            id: "EMP-6789",
            name: "Robert Brown",
            initials: "RB",
            status: "on-site",
            department: "Assembly",
            clockIn: "8:55 AM"
        },
        {
            id: "EMP-0123",
            name: "Jennifer Martinez",
            initials: "JM",
            status: "on-site",
            department: "Packaging",
            clockIn: "9:08 AM"
        }
    ],

    // Attendance Chart Data (Last 7 days)
    attendanceData: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
            {
                label: 'Present',
                data: [142, 138, 145, 150, 145, 0, 0],
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Target',
                data: [150, 150, 150, 150, 150, 0, 0],
                borderColor: '#8B5CF6',
                backgroundColor: 'transparent',
                borderDash: [5, 5],
                tension: 0,
                fill: false
            }
        ]
    },

    // KPI Values
    kpis: {
        presentCount: 145,
        complianceRate: 92,
        activeAlerts: 3,
        avgTime: "7.2h"
    }
};

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AutomationDashboard = () => {
    const [stats, setStats] = useState(null);
    const [schedulerStatus, setSchedulerStatus] = useState(null);
    const [jobHistory, setJobHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [triggering, setTriggering] = useState(false);

    useEffect(() => {
        fetchData();
        // Refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            // Fetch auto-tagger stats
            const autoTaggerResponse = await axios.get('http://localhost:8000/api/ml/stats');
            setStats(autoTaggerResponse.data);

            // Fetch scheduler status
            const schedulerResponse = await axios.get('http://localhost:8000/api/scheduler/status');
            setSchedulerStatus(schedulerResponse.data);

            // Fetch job history
            const jobsResponse = await axios.get('http://localhost:8000/api/scheduler/jobs?limit=10');
            setJobHistory(jobsResponse.data.jobs || []);

            setLoading(false);
        } catch (error) {
            console.error('Error fetching automation data:', error);
            setLoading(false);
        }
    };

    const triggerDiscovery = async () => {
        setTriggering(true);
        try {
            await axios.post('http://localhost:8000/api/scheduler/trigger', { job: 'discovery' });
            alert('Discovery job triggered successfully!');
            // Refresh data after a short delay
            setTimeout(fetchData, 2000);
        } catch (error) {
            console.error('Error triggering discovery:', error);
            alert('Failed to trigger discovery job');
        } finally {
            setTriggering(false);
        }
    };

    if (loading) {
        return (
            <div className="p-8">
                <h1 className="text-3xl font-bold mb-6">🤖 Automation Dashboard</h1>
                <p className="text-gray-600">Loading automation statistics...</p>
            </div>
        );
    }

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">🤖 Automation Dashboard</h1>
                <p className="text-gray-600">Monitor and control automated virtual tag Application</p>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <div className="text-blue-600 text-sm font-semibold mb-2">ML INFERENCES</div>
                    <div className="text-3xl font-bold text-blue-900">{stats?.total_inferences || 0}</div>
                    <div className="text-sm text-blue-700 mt-2">Total predictions made</div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <div className="text-green-600 text-sm font-semibold mb-2">AUTO-TAGGED</div>
                    <div className="text-3xl font-bold text-green-900">{stats?.auto_applied_tags || 0}</div>
                    <div className="text-sm text-green-700 mt-2">Tags applied automatically</div>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                    <div className="text-purple-600 text-sm font-semibold mb-2">MODEL VERSION</div>
                    <div className="text-2xl font-bold text-purple-900">{stats?.model_version || 'N/A'}</div>
                    <div className="text-sm text-purple-700 mt-2">Current ML model</div>
                </div>

                <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
                    <div className="text-orange-600 text-sm font-semibold mb-2">ACTIVE JOBS</div>
                    <div className="text-3xl font-bold text-orange-900">{schedulerStatus?.active_jobs || 0}</div>
                    <div className="text-sm text-orange-700 mt-2">Scheduled cron jobs</div>
                </div>
            </div>

            {/* Scheduler Controls */}
            <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
                <h2 className="text-xl font-bold text-gray-800 mb-4">⚡ Scheduler Controls</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="border border-gray-200 rounded p-4">
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-semibold text-gray-700">Resource Discovery</span>
                            <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                                ACTIVE
                            </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                            Interval: {schedulerStatus?.intervals?.discovery || '*/5 * * * *'}
                        </p>
                        <p className="text-xs text-gray-500">
                            Last run: {schedulerStatus?.job_stats?.discovery?.lastRun
                                ? new Date(schedulerStatus.job_stats.discovery.lastRun).toLocaleString()
                                : 'Not yet'}
                        </p>
                    </div>

                    <div className="border border-gray-200 rounded p-4">
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-semibold text-gray-700">Tag Re-evaluation</span>
                            <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                                ACTIVE
                            </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                            Interval: {schedulerStatus?.intervals?.reEvaluation || '0 * * * *'}
                        </p>
                        <p className="text-xs text-gray-500">
                            Last run: {schedulerStatus?.job_stats?.reEvaluation?.lastRun
                                ? new Date(schedulerStatus.job_stats.reEvaluation.lastRun).toLocaleString()
                                : 'Not yet'}
                        </p>
                    </div>
                </div>

                <button
                    onClick={triggerDiscovery}
                    disabled={triggering}
                    className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${triggering
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700'
                        }`}
                >
                    {triggering ? '⏳ Triggering...' : '🔍 Trigger Discovery Now'}
                </button>
            </div>

            {/* Job History */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">📋 Recent Job Executions</h2>

                {jobHistory.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No job executions yet. Wait for the first cron cycle or trigger manually.</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Job Name</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Started At</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Resources</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Tags Applied</th>
                                </tr>
                            </thead>
                            <tbody>
                                {jobHistory.map((job, index) => (
                                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="py-3 px-4 text-sm">{job.job_name}</td>
                                        <td className="py-3 px-4">
                                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${job.status === 'COMPLETED'
                                                ? 'bg-green-100 text-green-800'
                                                : job.status === 'RUNNING'
                                                    ? 'bg-blue-100 text-blue-800'
                                                    : 'bg-red-100 text-red-800'
                                                }`}>
                                                {job.status}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-600">
                                            {new Date(job.started_at).toLocaleString()}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-center">{job.resources_processed || '-'}</td>
                                        <td className="py-3 px-4 text-sm text-center font-semibold text-green-600">
                                            {job.tags_applied || 0}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Configuration Info */}
            <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-2">⚙️ Configuration</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                        <span className="text-gray-600">Auto-apply threshold:</span>
                        <span className="ml-2 font-semibold">{stats?.auto_apply_threshold * 100}%</span>
                    </div>
                    <div>
                        <span className="text-gray-600">Manual review threshold:</span>
                        <span className="ml-2 font-semibold">{stats?.manual_review_threshold * 100}%</span>
                    </div>
                    <div>
                        <span className="text-gray-600">Scheduler status:</span>
                        <span className="ml-2 font-semibold text-green-600">
                            {schedulerStatus?.enabled ? 'Enabled' : 'Disabled'}
                        </span>
                    </div>
                    <div>
                        <span className="text-gray-600">Discovery runs:</span>
                        <span className="ml-2 font-semibold">
                            {schedulerStatus?.job_stats?.discovery?.totalRuns || 0}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AutomationDashboard;

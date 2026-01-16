import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ApprovalsPage = () => {
    const [pendingTags, setPendingTags] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedTags, setSelectedTags] = useState(new Set());
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        fetchPendingApprovals();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchPendingApprovals, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchPendingApprovals = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/approvals/pending');
            setPendingTags(response.data.pending_approvals || []);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching pending approvals:', error);
            setLoading(false);
        }
    };

    const handleApprove = async (tagId) => {
        setProcessing(true);
        try {
            await axios.post('http://localhost:8000/api/approvals/approve', {
                tag_id: tagId,
                action: 'APPROVED',
                user: 'admin'
            });
            alert('Tag approved successfully!');
            fetchPendingApprovals();
            setSelectedTags(new Set());
        } catch (error) {
            console.error('Error approving tag:', error);
            alert('Failed to approve tag');
        } finally {
            setProcessing(false);
        }
    };

    const handleDeny = async (tagId) => {
        setProcessing(true);
        try {
            await axios.post('http://localhost:8000/api/approvals/approve', {
                tag_id: tagId,
                action: 'DENIED',
                user: 'admin'
            });
            alert('Tag denied successfully!');
            fetchPendingApprovals();
            setSelectedTags(new Set());
        } catch (error) {
            console.error('Error denying tag:', error);
            alert('Failed to deny tag');
        } finally {
            setProcessing(false);
        }
    };

    const handleSelectTag = (tagId) => {
        const newSelected = new Set(selectedTags);
        if (newSelected.has(tagId)) {
            newSelected.delete(tagId);
        } else {
            newSelected.add(tagId);
        }
        setSelectedTags(newSelected);
    };

    const handleSelectAll = () => {
        if (selectedTags.size === pendingTags.length) {
            setSelectedTags(new Set());
        } else {
            setSelectedTags(new Set(pendingTags.map(tag => tag.id)));
        }
    };

    const handleBulkApprove = async () => {
        if (selectedTags.size === 0) {
            alert('Please select at least one tag');
            return;
        }

        setProcessing(true);
        try {
            await axios.post('http://localhost:8000/api/approvals/bulk', {
                tag_ids: Array.from(selectedTags),
                action: 'APPROVED',
                user: 'admin'
            });
            alert(`${selectedTags.size} tags approved successfully!`);
            fetchPendingApprovals();
            setSelectedTags(new Set());
        } catch (error) {
            console.error('Error bulk approving:', error);
            alert('Failed to approve tags');
        } finally {
            setProcessing(false);
        }
    };

    const handleBulkDeny = async () => {
        if (selectedTags.size === 0) {
            alert('Please select at least one tag');
            return;
        }

        setProcessing(true);
        try {
            await axios.post('http://localhost:8000/api/approvals/bulk', {
                tag_ids: Array.from(selectedTags),
                action: 'DENIED',
                user: 'admin'
            });
            alert(`${selectedTags.size} tags denied successfully!`);
            fetchPendingApprovals();
            setSelectedTags(new Set());
        } catch (error) {
            console.error('Error bulk denying:', error);
            alert('Failed to deny tags');
        } finally {
            setProcessing(false);
        }
    };

    const getConfidenceBadge = (confidence) => {
        if (confidence >= 0.95) return 'bg-green-100 text-green-800';
        if (confidence >= 0.90) return 'bg-blue-100 text-blue-800';
        return 'bg-yellow-100 text-yellow-800';
    };

    if (loading) {
        return (
            <div className="p-8">
                <h1 className="text-3xl font-bold mb-6">✅ Tag Approvals</h1>
                <p className="text-gray-600">Loading pending approvals...</p>
            </div>
        );
    }

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">✅ Tag Approvals</h1>
                <p className="text-gray-600">Review and approve or deny auto-applied virtual tags</p>
            </div>

            {/* Summary Card */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-semibold text-blue-900">
                            {pendingTags.length} Tags Pending Approval
                        </h2>
                        <p className="text-sm text-blue-700 mt-1">
                            {selectedTags.size} selected
                        </p>
                    </div>
                    {selectedTags.size > 0 && (
                        <div className="flex gap-3">
                            <button
                                onClick={handleBulkApprove}
                                disabled={processing}
                                className="px-6 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                ✓ Approve Selected ({selectedTags.size})
                            </button>
                            <button
                                onClick={handleBulkDeny}
                                disabled={processing}
                                className="px-6 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                ✗ Deny Selected ({selectedTags.size})
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Tags Table */}
            {pendingTags.length === 0 ? (
                <div className="text-center py-12 bg-white border border-gray-200 rounded-lg">
                    <div className="text-6xl mb-4">🎉</div>
                    <p className="text-xl font-semibold text-gray-800 mb-2">All Caught Up!</p>
                    <p className="text-gray-600">No pending tag approvals at the moment.</p>
                </div>
            ) : (
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="py-3 px-4 text-left">
                                        <input
                                            type="checkbox"
                                            checked={selectedTags.size === pendingTags.length && pendingTags.length > 0}
                                            onChange={handleSelectAll}
                                            className="w-4 h-4"
                                        />
                                    </th>
                                    <th className="py-3 px-4 text-left font-semibold text-gray-700">Resource</th>
                                    <th className="py-3 px-4 text-left font-semibold text-gray-700">Cloud</th>
                                    <th className="py-3 px-4 text-left font-semibold text-gray-700">Tag Key</th>
                                    <th className="py-3 px-4 text-left font-semibold text-gray-700">Tag Value</th>
                                    <th className="py-3 px-4 text-left font-semibold text-gray-700">Source</th>
                                    <th className="py-3 px-4 text-left font-semibold text-gray-700">Confidence</th>
                                    <th className="py-3 px-4 text-left font-semibold text-gray-700">Created</th>
                                    <th className="py-3 px-4 text-center font-semibold text-gray-700">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pendingTags.map((tag) => (
                                    <tr key={tag.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="py-3 px-4">
                                            <input
                                                type="checkbox"
                                                checked={selectedTags.has(tag.id)}
                                                onChange={() => handleSelectTag(tag.id)}
                                                className="w-4 h-4"
                                            />
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="font-medium text-gray-900">{tag.resource_name}</div>
                                            <div className="text-xs text-gray-500">{tag.resource_type}</div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`px-2 py-1 text-xs font-semibold rounded ${tag.cloud === 'AWS' ? 'bg-orange-100 text-orange-800' :
                                                    tag.cloud === 'GCP' ? 'bg-blue-100 text-blue-800' :
                                                        'bg-cyan-100 text-cyan-800'
                                                }`}>
                                                {tag.cloud}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 font-mono text-sm text-gray-700">{tag.tag_key}</td>
                                        <td className="py-3 px-4 font-mono text-sm text-gray-700">{tag.tag_value}</td>
                                        <td className="py-3 px-4">
                                            <span className="px-2 py-1 text-xs font-semibold rounded bg-purple-100 text-purple-800">
                                                {tag.source}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`px-2 py-1 text-xs font-semibold rounded ${getConfidenceBadge(tag.confidence)}`}>
                                                {(tag.confidence * 100).toFixed(0)}%
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-600">
                                            {new Date(tag.created_at).toLocaleString()}
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="flex gap-2 justify-center">
                                                <button
                                                    onClick={() => handleApprove(tag.id)}
                                                    disabled={processing}
                                                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
                                                >
                                                    ✓ Approve
                                                </button>
                                                <button
                                                    onClick={() => handleDeny(tag.id)}
                                                    disabled={processing}
                                                    className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:opacity-50"
                                                >
                                                    ✗ Deny
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Refresh Button */}
            <div className="mt-6 flex justify-center">
                <button
                    onClick={fetchPendingApprovals}
                    className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
                >
                    🔄 Refresh
                </button>
            </div>
        </div>
    );
};

export default ApprovalsPage;

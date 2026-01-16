import React, { useState } from 'react';
import axios from 'axios';

const CSVImportPage = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState(null);
    const [exporting, setExporting] = useState(false);

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file && file.name.endsWith('.csv')) {
            setSelectedFile(file);
            setUploadResult(null);
        } else {
            alert('Please select a CSV file');
            event.target.value = null;
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            alert('Please select a file first');
            return;
        }

        setUploading(true);
        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            const response = await axios.post('http://localhost:8000/api/csv/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setUploadResult(response.data);
            alert(`Upload successful! ${response.data.stats.tags_created} tags created, ${response.data.stats.tags_updated} tags updated`);
            setSelectedFile(null);
            document.getElementById('fileInput').value = null;
        } catch (error) {
            console.error('Upload error:', error);
            alert('Upload failed: ' + (error.response?.data?.error || error.message));
        } finally {
            setUploading(false);
        }
    };

    const handleExport = async () => {
        setExporting(true);
        try {
            const response = await axios.get('http://localhost:8000/api/csv/export', {
                responseType: 'blob'
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'virtual_tags_export.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            alert('Export successful!');
        } catch (error) {
            console.error('Export error:', error);
            alert('Export failed: ' + (error.response?.data?.error || error.message));
        } finally {
            setExporting(false);
        }
    };

    const downloadTemplate = () => {
        const template = `resource_name,tag_key,tag_value,confidence
prod-api-server-001,environment,production,1.0
prod-api-server-001,team,backend,1.0
prod-api-server-001,cost-center,engineering,1.0
staging-db-instance-002,environment,staging,0.95
staging-db-instance-002,team,backend,0.95
staging-db-instance-002,cost-center,engineering,0.95`;

        const blob = new Blob([template], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'tag_import_template.csv');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    };

    return (
        <div className="p-8 max-w-5xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">📤 CSV Import/Export</h1>
                <p className="text-gray-600">Bulk import or export virtual tags using CSV files</p>
            </div>

            {/* Import Section */}
            <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">📥 Import Tags from CSV</h2>

                <div className="mb-6">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                        <h3 className="font-semibold text-blue-900 mb-2">CSV Format Requirements:</h3>
                        <ul className="text-sm text-blue-800 list-disc list-inside space-y-1">
                            <li>Required columns: <code className="bg-blue-100 px-1 rounded">resource_name</code>, <code className="bg-blue-100 px-1 rounded">tag_key</code>, <code className="bg-blue-100 px-1 rounded">tag_value</code></li>
                            <li>Optional column: <code className="bg-blue-100 px-1 rounded">confidence</code> (defaults to 1.0)</li>
                            <li>Resource name can be partial match (case-insensitive)</li>
                            <li>Tags are automatically marked as APPROVED</li>
                        </ul>
                    </div>

                    <button
                        onClick={downloadTemplate}
                        className="mb-4 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
                    >
                        📄 Download Template CSV
                    </button>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Select CSV File
                        </label>
                        <input
                            id="fileInput"
                            type="file"
                            accept=".csv"
                            onChange={handleFileSelect}
                            className="block w-full text-sm text-gray-500
                                file:mr-4 file:py-2 file:px-4
                                file:rounded-lg file:border-0
                                file:text-sm file:font-semibold
                                file:bg-blue-50 file:text-blue-700
                                hover:file:bg-blue-100
                                cursor-pointer"
                        />
                    </div>

                    {selectedFile && (
                        <div className="bg-gray-50 border border-gray-200 rounded p-3">
                            <p className="text-sm text-gray-700">
                                <span className="font-semibold">Selected:</span> {selectedFile.name}
                                <span className="text-gray-500 ml-2">({(selectedFile.size / 1024).toFixed(2)} KB)</span>
                            </p>
                        </div>
                    )}

                    <button
                        onClick={handleUpload}
                        disabled={!selectedFile || uploading}
                        className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${!selectedFile || uploading
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700'
                            }`}
                    >
                        {uploading ? '⏳ Uploading...' : '🚀 Upload and Import Tags'}
                    </button>
                </div>

                {/* Upload Results */}
                {uploadResult && (
                    <div className="mt-6 border-t border-gray-200 pt-4">
                        <h3 className="font-semibold text-gray-800 mb-3">Import Results</h3>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                            <div className="bg-blue-50 rounded-lg p-3">
                                <div className="text-sm text-blue-600 font-semibold">Total Rows</div>
                                <div className="text-2xl font-bold text-blue-900">{uploadResult.stats.total_rows}</div>
                            </div>
                            <div className="bg-green-50 rounded-lg p-3">
                                <div className="text-sm text-green-600 font-semibold">Tags Created</div>
                                <div className="text-2xl font-bold text-green-900">{uploadResult.stats.tags_created}</div>
                            </div>
                            <div className="bg-yellow-50 rounded-lg p-3">
                                <div className="text-sm text-yellow-600 font-semibold">Tags Updated</div>
                                <div className="text-2xl font-bold text-yellow-900">{uploadResult.stats.tags_updated}</div>
                            </div>
                            <div className="bg-red-50 rounded-lg p-3">
                                <div className="text-sm text-red-600 font-semibold">Errors</div>
                                <div className="text-2xl font-bold text-red-900">{uploadResult.stats.errors.length}</div>
                            </div>
                        </div>

                        {uploadResult.stats.errors.length > 0 && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <h4 className="font-semibold text-red-800 mb-2">Errors ({uploadResult.stats.errors.length}):</h4>
                                <div className="max-h-40 overflow-y-auto">
                                    {uploadResult.stats.errors.map((error, idx) => (
                                        <div key={idx} className="text-sm text-red-700 mb-1">• {error}</div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Export Section */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">📤 Export Tags to CSV</h2>

                <p className="text-gray-600 mb-4">
                    Download all current virtual tags as a CSV file. Includes resource details, tag values, confidence scores, and approval status.
                </p>

                <button
                    onClick={handleExport}
                    disabled={exporting}
                    className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${exporting
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-green-600 hover:bg-green-700'
                        }`}
                >
                    {exporting ? '⏳ Exporting...' : '💾 Export All Tags'}
                </button>
            </div>

            {/* Info Section */}
            <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-2">💡 Tips</h3>
                <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                    <li>CSV imports are faster than manual tagging for bulk operations</li>
                    <li>Resource names support partial matching (e.g., "api-server" matches "prod-api-server-001")</li>
                    <li>Imported tags bypass approval workflow and are immediately active</li>
                    <li>Existing tags will be updated with new values from CSV</li>
                    <li>Use Export to backup your current tag configuration</li>
                </ul>
            </div>
        </div>
    );
};

export default CSVImportPage;

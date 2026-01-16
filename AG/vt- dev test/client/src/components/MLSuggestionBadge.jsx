import React from 'react';
import axios from 'axios';

const MLSuggestionBadge = ({ suggestion, resourceId, onAccept }) => {
    const [accepting, setAccepting] = React.useState(false);

    const handleAccept = async () => {
        setAccepting(true);
        try {
            // Apply the suggested tag
            await axios.post('http://localhost:5000/api/virtual-tags', {
                resource_id: resourceId,
                tag_key: suggestion.tag_key,
                tag_value: suggestion.predicted_value,
                source: 'USER_CONFIRMED'
            });

            // Send feedback to ML
            await axios.post('http://localhost:5000/api/ml/feedback', {
                resource_id: resourceId,
                prediction: suggestion,
                accepted: true
            });

            alert(`Tag "${suggestion.tag_key}: ${suggestion.predicted_value}" applied successfully!`);
            if (onAccept) onAccept();
        } catch (error) {
            console.error('Error accepting suggestion:', error);
            alert('Failed to apply tag');
        } finally {
            setAccepting(false);
        }
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.90) return 'bg-green-100 text-green-800 border-green-300';
        if (confidence >= 0.70) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
        return 'bg-gray-100 text-gray-800 border-gray-300';
    };

    return (
        <div className={`border rounded-lg p-3 ${getConfidenceColor(suggestion.confidence)}`}>
            <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                    <div className="font-semibold text-sm mb-1">
                        ✨ AI Suggestion: {suggestion.tag_key}
                    </div>
                    <div className="text-lg font-bold">
                        {suggestion.predicted_value}
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-xs font-semibold mb-1">
                        Confidence
                    </div>
                    <div className="text-2xl font-bold">
                        {(suggestion.confidence * 100).toFixed(0)}%
                    </div>
                </div>
            </div>

            {suggestion.reasoning && (
                <div className="text-xs mb-3 opacity-80">
                    💡 {suggestion.reasoning}
                </div>
            )}

            <button
                onClick={handleAccept}
                disabled={accepting}
                className={`w-full px-3 py-2 text-sm font-semibold rounded transition-colors ${accepting
                        ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                        : 'bg-white text-gray-800 hover:bg-gray-50 border border-current'
                    }`}
            >
                {accepting ? '⏳ Applying...' : '✓ Accept This Tag'}
            </button>
        </div>
    );
};

export default MLSuggestionBadge;

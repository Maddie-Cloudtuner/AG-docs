const RuleCard = ({ rule }) => {
  const getScopeColor = (scope) => {
    switch (scope?.toUpperCase()) {
      case 'AWS': return 'bg-orange-100 text-orange-800';
      case 'GCP': return 'bg-red-100 text-red-800';
      case 'AZURE': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    if (priority >= 3) return 'bg-red-100 text-red-800';
    if (priority >= 2) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-800">{rule.rule_name}</h3>
            <span className={`px-2 py-1 text-xs rounded-full font-medium ${getScopeColor(rule.scope)}`}>
              {rule.scope}
            </span>
            <span className={`px-2 py-1 text-xs rounded-full font-medium ${getPriorityColor(rule.priority)}`}>
              Priority {rule.priority}
            </span>
          </div>
          
          <div className="text-sm text-gray-600 mb-3">
            Created by <span className="font-medium">{rule.created_by}</span> on{' '}
            {new Date(rule.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-700 mb-2">📋 Condition</h4>
          <code className="text-sm bg-gray-100 px-2 py-1 rounded text-gray-800 break-all">
            {rule.condition}
          </code>
        </div>

        <div className="bg-purple-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-700 mb-2">🏷️ Applied Tag</h4>
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 text-sm bg-purple-100 text-purple-800 rounded-full font-medium border border-purple-200">
              🧩 {rule.tag_key}: {rule.tag_value}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            This rule will apply the tag <strong>{rule.tag_key}: {rule.tag_value}</strong> to all{' '}
            <strong>{rule.scope}</strong> resources where <strong>{rule.condition}</strong>
          </span>
        </div>
      </div>
    </div>
  );
};

export default RuleCard;
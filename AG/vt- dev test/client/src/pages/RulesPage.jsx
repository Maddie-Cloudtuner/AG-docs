import { useState, useEffect } from 'react';
import { rulesApi } from '../services/api';
import RuleCard from '../components/RuleCard';
import AddRuleModal from '../components/AddRuleModal';

const RulesPage = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddRuleModal, setShowAddRuleModal] = useState(false);
  const [applyingRules, setApplyingRules] = useState(false);
  const [applyResult, setApplyResult] = useState(null);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await rulesApi.getAll();
      setRules(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch rules');
      console.error('Error fetching rules:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleAddRule = async (ruleData) => {
    try {
      await rulesApi.create(ruleData);
      fetchRules(); // Refresh the list
      setShowAddRuleModal(false);
    } catch (err) {
      console.error('Error adding rule:', err);
      alert('Failed to add rule');
    }
  };

  const handleApplyRules = async () => {
    try {
      setApplyingRules(true);
      const response = await rulesApi.apply();
      setApplyResult(response.data);
      setTimeout(() => setApplyResult(null), 5000); // Hide after 5 seconds
    } catch (err) {
      console.error('Error applying rules:', err);
      alert('Failed to apply rules');
    } finally {
      setApplyingRules(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading rules...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">⚠️ {error}</div>
        <button 
          onClick={fetchRules}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Tagging Rules</h1>
          <p className="text-gray-600 mt-2">
            Create intelligent rules to automatically apply virtual tags to your resources
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleApplyRules}
            disabled={applyingRules || rules.length === 0}
            className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {applyingRules ? 'Applying...' : '⚡ Apply Rules'}
          </button>
          <button
            onClick={() => setShowAddRuleModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            + Create Rule
          </button>
        </div>
      </div>

      {applyResult && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-green-800 mb-2">✅ Rules Applied Successfully!</h3>
          <p className="text-green-700 text-sm">{applyResult.message}</p>
          {applyResult.details && applyResult.details.length > 0 && (
            <details className="mt-2">
              <summary className="text-green-700 text-sm cursor-pointer hover:text-green-800">
                View Details ({applyResult.details.length} tags applied)
              </summary>
              <div className="mt-2 space-y-1">
                {applyResult.details.slice(0, 10).map((detail, index) => (
                  <div key={index} className="text-xs text-green-600 bg-green-100 p-2 rounded">
                    <strong>{detail.resourceName}</strong> → {detail.tagKey}: {detail.tagValue} (via {detail.ruleName})
                  </div>
                ))}
                {applyResult.details.length > 10 && (
                  <p className="text-xs text-green-600">...and {applyResult.details.length - 10} more</p>
                )}
              </div>
            </details>
          )}
        </div>
      )}

      <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-800 mb-2">🎯 How Rules Work</h3>
        <ul className="text-blue-700 text-sm space-y-1">
          <li>• Rules automatically apply virtual tags based on resource properties</li>
          <li>• Supported conditions: CONTAINS, STARTS_WITH, EQUALS</li>
          <li>• Example: <code className="bg-blue-100 px-1 rounded">name CONTAINS 'prod'</code> → Environment: Production</li>
          <li>• Click "Apply Rules" to process all resources with current rules</li>
        </ul>
      </div>

      {rules.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No rules created yet</p>
          <button
            onClick={() => setShowAddRuleModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Create Your First Rule
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {rules.map((rule) => (
            <RuleCard key={rule.id} rule={rule} />
          ))}
        </div>
      )}

      {showAddRuleModal && (
        <AddRuleModal
          onAdd={handleAddRule}
          onClose={() => setShowAddRuleModal(false)}
        />
      )}
    </div>
  );
};

export default RulesPage;
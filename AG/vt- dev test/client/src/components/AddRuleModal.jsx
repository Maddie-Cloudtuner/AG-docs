import { useState } from 'react';

const AddRuleModal = ({ onAdd, onClose }) => {
  const [formData, setFormData] = useState({
    ruleName: '',
    condition: '',
    tagKey: '',
    tagValue: '',
    scope: 'All',
    priority: 1,
    createdBy: 'manual'
  });

  const [conditionBuilder, setConditionBuilder] = useState({
    field: 'name',
    operator: 'CONTAINS',
    value: ''
  });

  const [useBuilder, setUseBuilder] = useState(true);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleConditionBuilderChange = (e) => {
    const newBuilder = {
      ...conditionBuilder,
      [e.target.name]: e.target.value
    };
    setConditionBuilder(newBuilder);
    
    // Auto-update condition string
    if (newBuilder.field && newBuilder.operator && newBuilder.value) {
      setFormData({
        ...formData,
        condition: `${newBuilder.field} ${newBuilder.operator} '${newBuilder.value}'`
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.ruleName && formData.condition && formData.tagKey && formData.tagValue) {
      onAdd(formData);
    }
  };

  const exampleConditions = [
    "name CONTAINS 'prod'",
    "name STARTS_WITH 'web'",
    "cloud EQUALS 'AWS'",
    "name CONTAINS 'staging'"
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Create New Rule</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rule Name *
            </label>
            <input
              type="text"
              name="ruleName"
              value={formData.ruleName}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Production Environment Tagging"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Condition *
            </label>
            
            <div className="mb-2">
              <div className="flex gap-2 text-sm">
                <button
                  type="button"
                  onClick={() => setUseBuilder(true)}
                  className={`px-3 py-1 rounded ${useBuilder ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
                >
                  Builder
                </button>
                <button
                  type="button"
                  onClick={() => setUseBuilder(false)}
                  className={`px-3 py-1 rounded ${!useBuilder ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
                >
                  Manual
                </button>
              </div>
            </div>

            {useBuilder ? (
              <div className="grid grid-cols-3 gap-2 mb-2">
                <select
                  name="field"
                  value={conditionBuilder.field}
                  onChange={handleConditionBuilderChange}
                  className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="name">name</option>
                  <option value="cloud">cloud</option>
                  <option value="account_id">account_id</option>
                </select>
                
                <select
                  name="operator"
                  value={conditionBuilder.operator}
                  onChange={handleConditionBuilderChange}
                  className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="CONTAINS">CONTAINS</option>
                  <option value="STARTS_WITH">STARTS_WITH</option>
                  <option value="EQUALS">EQUALS</option>
                </select>
                
                <input
                  type="text"
                  name="value"
                  value={conditionBuilder.value}
                  onChange={handleConditionBuilderChange}
                  className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="value"
                />
              </div>
            ) : null}

            <input
              type="text"
              name="condition"
              value={formData.condition}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              placeholder="e.g., name CONTAINS 'prod'"
              required
              readOnly={useBuilder}
            />

            <div className="text-xs text-gray-500 mt-1">
              Examples: {exampleConditions.map((ex, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setFormData({...formData, condition: ex})}
                  className="text-blue-600 hover:text-blue-800 mr-2"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tag Key *
              </label>
              <input
                type="text"
                name="tagKey"
                value={formData.tagKey}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Environment"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tag Value *
              </label>
              <input
                type="text"
                name="tagValue"
                value={formData.tagValue}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Production"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cloud Scope
              </label>
              <select
                name="scope"
                value={formData.scope}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="All">All Clouds</option>
                <option value="AWS">AWS Only</option>
                <option value="GCP">GCP Only</option>
                <option value="Azure">Azure Only</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>1 (Low)</option>
                <option value={2}>2 (Medium)</option>
                <option value={3}>3 (High)</option>
              </select>
            </div>
          </div>

          <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-800">
              💡 <strong>Preview:</strong> This rule will apply tag{' '}
              <code className="bg-blue-100 px-1 rounded">{formData.tagKey || 'TagKey'}: {formData.tagValue || 'TagValue'}</code>{' '}
              to all <strong>{formData.scope}</strong> resources where{' '}
              <code className="bg-blue-100 px-1 rounded">{formData.condition || 'condition'}</code>
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
            >
              Create Rule
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddRuleModal;
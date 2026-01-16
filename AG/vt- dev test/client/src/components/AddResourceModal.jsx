import { useState } from 'react';

const AddResourceModal = ({ onAdd, onClose }) => {
  const [formData, setFormData] = useState({
    resourceId: '',
    name: '',
    cloud: 'AWS',
    accountId: '',
    nativeTags: {}
  });
  const [tagKey, setTagKey] = useState('');
  const [tagValue, setTagValue] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const addNativeTag = () => {
    if (tagKey && tagValue) {
      setFormData({
        ...formData,
        nativeTags: {
          ...formData.nativeTags,
          [tagKey]: tagValue
        }
      });
      setTagKey('');
      setTagValue('');
    }
  };

  const removeNativeTag = (key) => {
    const newTags = { ...formData.nativeTags };
    delete newTags[key];
    setFormData({
      ...formData,
      nativeTags: newTags
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.resourceId && formData.name && formData.accountId) {
      onAdd(formData);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Add New Resource</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Resource ID *
            </label>
            <input
              type="text"
              name="resourceId"
              value={formData.resourceId}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., aws-ec2-i-1234567890abcdef0"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Resource Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., prod-web-server-01"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cloud Provider *
            </label>
            <select
              name="cloud"
              value={formData.cloud}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="AWS">AWS</option>
              <option value="GCP">Google Cloud</option>
              <option value="Azure">Azure</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Account ID *
            </label>
            <input
              type="text"
              name="accountId"
              value={formData.accountId}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 123456789012"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Native Tags
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={tagKey}
                onChange={(e) => setTagKey(e.target.value)}
                className="flex-1 border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Key"
              />
              <input
                type="text"
                value={tagValue}
                onChange={(e) => setTagValue(e.target.value)}
                className="flex-1 border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Value"
              />
              <button
                type="button"
                onClick={addNativeTag}
                className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
              >
                +
              </button>
            </div>
            
            {Object.keys(formData.nativeTags).length > 0 && (
              <div className="space-y-1">
                {Object.entries(formData.nativeTags).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between bg-gray-50 px-2 py-1 rounded text-sm">
                    <span>{key}: {value}</span>
                    <button
                      type="button"
                      onClick={() => removeNativeTag(key)}
                      className="text-red-500 hover:text-red-700"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
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
              Add Resource
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddResourceModal;
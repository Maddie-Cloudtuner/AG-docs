const ResourceCard = ({ resource, onAddVirtualTag }) => {
  const getCloudIcon = (cloud) => {
    switch (cloud?.toUpperCase()) {
      case "AWS":
        return "🟠";
      case "GCP":
        return "🔴";
      case "AZURE":
        return "🔵";
      default:
        return "☁️";
    }
  };

  const getCloudColor = (cloud) => {
    switch (cloud?.toUpperCase()) {
      case "AWS":
        return "bg-orange-100 text-orange-800";
      case "GCP":
        return "bg-red-100 text-red-800";
      case "AZURE":
        return "bg-blue-100 text-blue-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const renderTags = (tags, isVirtual = false) => {
    if (!tags || Object.keys(tags).length === 0) {
      return <span className="text-gray-400 text-sm">No tags</span>;
    }

    return (
      <div className="flex flex-wrap gap-2">
        {Object.entries(tags).map(([key, value]) => (
          <span
            key={key}
            className={`px-2 py-1 text-xs rounded-full font-medium ${
              isVirtual
                ? "bg-purple-100 text-purple-800 border border-purple-200"
                : "bg-gray-100 text-gray-700"
            }`}
          >
            {isVirtual && "🧩 "}
            {key}: {value}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl">{getCloudIcon(resource.cloud)}</span>
            <h3 className="text-xl font-semibold text-gray-800">
              {resource.name}
            </h3>
            <span
              className={`px-2 py-1 text-xs rounded-full font-medium ${getCloudColor(
                resource.cloud
              )}`}
            >
              {resource.cloud}
            </span>
          </div>
          <p className="text-sm text-gray-500 mb-1">
            Resource ID:{" "}
            <code className="bg-gray-100 px-1 rounded">
              {resource.resource_id}
            </code>
          </p>
          <p className="text-sm text-gray-500">
            Account:{" "}
            <code className="bg-gray-100 px-1 rounded">
              {resource.account_id}
            </code>
          </p>
        </div>

        <button
          onClick={onAddVirtualTag}
          className="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700 transition-colors"
        >
          + Virtual Tag
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Native Tags
          </h4>
          {renderTags(resource.native_tags)}
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Virtual Tags
            <span className="text-xs text-purple-600 font-normal ml-1">
              (🧩 Virtual)
            </span>
          </h4>
          {renderTags(resource.virtualTags, true)}
        </div>
      </div>
    </div>
  );
};

export default ResourceCard;

import { useState, useEffect } from "react";
import { resourcesApi, virtualTagsApi } from "../services/api";
import ResourceCard from "../components/ResourceCard";
import AddResourceModal from "../components/AddResourceModal";
import AddVirtualTagModal from "../components/AddVirtualTagModal";

const ResourcesPage = () => {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddResourceModal, setShowAddResourceModal] = useState(false);
  const [showAddTagModal, setShowAddTagModal] = useState(false);
  const [selectedResource, setSelectedResource] = useState(null);

  const fetchResources = async () => {
    try {
      setLoading(true);
      const response = await resourcesApi.getAll();
      // Handle both old format (array) and new format (object with resources array)
      const resourcesData = response.data.resources || response.data;
      setResources(resourcesData);
      setError(null);
    } catch (err) {
      setError("Failed to fetch resources");
      console.error("Error fetching resources:", err);
    } finally {
      setLoading(false);
    }
  };

  console.log("ResourcesPage render: ", { resources, loading, error });
  useEffect(() => {
    fetchResources();
  }, []);

  const handleAddResource = async (resourceData) => {
    try {
      await resourcesApi.create(resourceData);
      fetchResources(); // Refresh the list
      setShowAddResourceModal(false);
    } catch (err) {
      console.error("Error adding resource:", err);
      alert("Failed to add resource");
    }
  };

  const handleAddVirtualTag = async (tagData) => {
    try {
      await virtualTagsApi.create({
        ...tagData,
        resourceId: selectedResource.resource_id,
      });
      fetchResources(); // Refresh the list
      setShowAddTagModal(false);
      setSelectedResource(null);
    } catch (err) {
      console.error("Error adding virtual tag:", err);
      alert("Failed to add virtual tag");
    }
  };

  const openAddTagModal = (resource) => {
    setSelectedResource(resource);
    setShowAddTagModal(true);
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading resources...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">⚠️ {error}</div>
        <button
          onClick={fetchResources}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
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
          <h1 className="text-3xl font-bold text-gray-800">Cloud Resources</h1>
          <p className="text-gray-600 mt-2">
            Manage your cloud resources and virtual tags across AWS, GCP, and
            Azure
          </p>
        </div>
        <button
          onClick={() => setShowAddResourceModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          + Add Resource
        </button>
      </div>

      {resources.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No resources found</p>
          <button
            onClick={() => setShowAddResourceModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Add Your First Resource
          </button>
        </div>
      ) : (
        <div className="grid gap-6">
          {resources.map((resource) => (
            <ResourceCard
              key={resource.resource_id}
              resource={resource}
              onAddVirtualTag={() => openAddTagModal(resource)}
            />
          ))}
        </div>
      )}

      {showAddResourceModal && (
        <AddResourceModal
          onAdd={handleAddResource}
          onClose={() => setShowAddResourceModal(false)}
        />
      )}

      {showAddTagModal && (
        <AddVirtualTagModal
          resource={selectedResource}
          onAdd={handleAddVirtualTag}
          onClose={() => {
            setShowAddTagModal(false);
            setSelectedResource(null);
          }}
        />
      )}
    </div>
  );
};

export default ResourcesPage;

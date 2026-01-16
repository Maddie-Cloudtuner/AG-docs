import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="text-center max-w-4xl mx-auto">
      <div className="mb-12">
        <h1 className="text-5xl font-bold text-gray-800 mb-6">
          🏷️ Virtual Tagging Prototype
        </h1>
        <p className="text-xl text-gray-600 mb-8 leading-relaxed">
          Simulate tagging and cost allocation without touching your cloud resources.
          <br />
          Create virtual tags, define rules, and visualize resource organization across AWS, GCP, and Azure.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">
            ⚡ Quick Start
          </h3>
          <p className="text-gray-600 mb-6">
            View and manage your cloud resources with virtual tagging capabilities.
          </p>
          <Link 
            to="/resources" 
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            View Resources
          </Link>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-md">
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">
            🎯 Rule Engine
          </h3>
          <p className="text-gray-600 mb-6">
            Create intelligent tagging rules to automatically organize your resources.
          </p>
          <Link 
            to="/rules" 
            className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            Manage Rules
          </Link>
        </div>
      </div>

      <div className="bg-gray-100 p-8 rounded-lg">
        <h3 className="text-2xl font-semibold text-gray-800 mb-4">
          🚀 Features
        </h3>
        <div className="grid md:grid-cols-3 gap-6 text-left">
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Multi-Cloud Support</h4>
            <p className="text-gray-600 text-sm">
              Works with AWS, Google Cloud, and Azure resources
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Rule-Based Tagging</h4>
            <p className="text-gray-600 text-sm">
              Automatically apply tags based on resource properties
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Virtual Tags</h4>
            <p className="text-gray-600 text-sm">
              Tag simulation without modifying actual cloud resources
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import ResourcesPage from './pages/ResourcesPage';
import RulesPage from './pages/RulesPage';
import AutomationDashboard from './pages/AutomationDashboard';
import ApprovalsPage from './pages/ApprovalsPage';
import CSVImportPage from './pages/CSVImportPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/resources" element={<ResourcesPage />} />
            <Route path="/rules" element={<RulesPage />} />
            <Route path="/automation" element={<AutomationDashboard />} />
            <Route path="/approvals" element={<ApprovalsPage />} />
            <Route path="/csv-import" element={<CSVImportPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
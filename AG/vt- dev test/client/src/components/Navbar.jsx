import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          <Link to="/" className="text-xl font-bold">
            🏷️ Virtual Tagging
          </Link>

          <div className="flex space-x-6">
            <Link
              to="/"
              className={`hover:text-blue-200 transition-colors ${isActive('/') ? 'text-blue-200 font-semibold' : ''
                }`}
            >
              Home
            </Link>
            <Link
              to="/resources"
              className={`hover:text-blue-200 transition-colors ${isActive('/resources') ? 'text-blue-200 font-semibold' : ''
                }`}
            >
              Resources
            </Link>
            <Link
              to="/rules"
              className={`hover:text-blue-200 transition-colors ${isActive('/rules') ? 'text-blue-200 font-semibold' : ''
                }`}
            >
              Rules
            </Link>
            <Link
              to="/automation"
              className={`hover:text-blue-200 transition-colors ${isActive('/automation') ? 'text-blue-200 font-semibold' : ''
                }`}
            >
              🤖 Automation
            </Link>
            <Link
              to="/approvals"
              className={`hover:text-blue-200 transition-colors ${isActive('/approvals') ? 'text-blue-200 font-semibold' : ''
                }`}
            >
              ✅ Approvals
            </Link>
            <Link
              to="/csv-import"
              className={`hover:text-blue-200 transition-colors ${isActive('/csv-import') ? 'text-blue-200 font-semibold' : ''
                }`}
            >
              📤 CSV Import
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
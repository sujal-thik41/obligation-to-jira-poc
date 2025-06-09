import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path ? 'bg-indigo-700' : '';
  };

  return (
    <nav className="bg-indigo-600 text-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <span className="text-xl font-bold">Obligation Manager</span>
            </Link>
          </div>
          <div className="flex space-x-4">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 ${isActive('/')}`}
            >
              Upload Document
            </Link>
            <Link
              to="/obligations"
              className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 ${isActive('/obligations')}`}
            >
              Obligations
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

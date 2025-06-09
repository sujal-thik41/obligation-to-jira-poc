import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useObligations } from '../context/ObligationContext';

const ObligationsList = () => {
  const { 
    obligations, 
    fetchObligations, 
    loading, 
    error, 
    pagination,
    deleteObligation,
    createIssue,
    createIssuesForMultiple
  } = useObligations();
  
  const [selectedObligations, setSelectedObligations] = useState([]);
  const [partyFilter, setPartyFilter] = useState('');
  const [isCreatingIssues, setIsCreatingIssues] = useState(false);

  useEffect(() => {
    fetchObligations(pagination.page, pagination.pageSize);
  }, []);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages) {
      fetchObligations(newPage, pagination.pageSize, partyFilter || null);
    }
  };

  const handlePartyFilterChange = (e) => {
    setPartyFilter(e.target.value);
  };

  const handleApplyFilter = () => {
    fetchObligations(1, pagination.pageSize, partyFilter || null);
  };

  const handleClearFilter = () => {
    setPartyFilter('');
    fetchObligations(1, pagination.pageSize);
  };

  const handleSelectObligation = (id) => {
    setSelectedObligations(prev => {
      if (prev.includes(id)) {
        return prev.filter(item => item !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedObligations.length === obligations.length) {
      setSelectedObligations([]);
    } else {
      setSelectedObligations(obligations.map(ob => ob.id));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this obligation?')) {
      try {
        await deleteObligation(id);
      } catch (err) {
        console.error('Failed to delete obligation:', err);
      }
    }
  };

  const handleCreateIssue = async (id) => {
    try {
      await createIssue(id);
    } catch (err) {
      console.error('Failed to create Jira issue:', err);
    }
  };

  const handleCreateMultipleIssues = async () => {
    if (selectedObligations.length === 0) return;
    
    setIsCreatingIssues(true);
    try {
      await createIssuesForMultiple(selectedObligations);
      setSelectedObligations([]);
    } catch (err) {
      console.error('Failed to create Jira issues:', err);
    } finally {
      setIsCreatingIssues(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Obligations</h1>
        
        <div className="flex space-x-2">
          {selectedObligations.length > 0 && (
            <button
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              onClick={handleCreateMultipleIssues}
              disabled={isCreatingIssues || selectedObligations.length === 0}
            >
              {isCreatingIssues ? 'Creating...' : `Create Jira Issues (${selectedObligations.length})`}
            </button>
          )}
        </div>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
        <div className="p-4 border-b">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4">
              <div className="flex items-center">
                <label htmlFor="party-filter" className="mr-2 text-sm font-medium text-gray-700">
                  Party Name:
                </label>
                <input
                  type="text"
                  id="party-filter"
                  className="border rounded-md px-3 py-1 text-sm"
                  value={partyFilter}
                  onChange={handlePartyFilterChange}
                  placeholder="Filter by party name"
                />
              </div>
              
              <div className="flex space-x-2">
                <button
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md text-sm hover:bg-gray-200"
                  onClick={handleApplyFilter}
                >
                  Apply Filter
                </button>
                <button
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md text-sm hover:bg-gray-200"
                  onClick={handleClearFilter}
                >
                  Clear
                </button>
              </div>
            </div>
            
            <div className="text-sm text-gray-500">
              Showing {obligations.length} of {pagination.total} obligations
            </div>
          </div>
        </div>

        {loading && !obligations.length ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading obligations...</p>
          </div>
        ) : error ? (
          <div className="p-6 text-center text-red-600">
            <p>Error loading obligations: {error}</p>
          </div>
        ) : obligations.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <p>No obligations found. Upload a document to extract obligations.</p>
            <Link to="/" className="mt-2 inline-block text-indigo-600 hover:underline">
              Go to Upload
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-4 py-3 text-left">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                        checked={selectedObligations.length === obligations.length && obligations.length > 0}
                        onChange={handleSelectAll}
                      />
                    </div>
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Obligation
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Party
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Deadline
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Section
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Jira
                  </th>
                  <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {obligations.map((obligation) => (
                  <tr key={obligation.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                        checked={selectedObligations.includes(obligation.id)}
                        onChange={() => handleSelectObligation(obligation.id)}
                      />
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-sm text-gray-900 line-clamp-2">
                        {obligation.obligation_text}
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{obligation.party_name || 'N/A'}</div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{obligation.deadline || 'N/A'}</div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{obligation.section || 'N/A'}</div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      {obligation.jira_issue_id ? (
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                          {obligation.jira_issue_id}
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                          Not created
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <Link
                          to={`/obligations/${obligation.id}`}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Edit
                        </Link>
                        {!obligation.jira_issue_id && (
                          <button
                            onClick={() => handleCreateIssue(obligation.id)}
                            className="text-green-600 hover:text-green-900"
                          >
                            Create Issue
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(obligation.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {obligations.length > 0 && (
          <div className="px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={pagination.page === 1}
                className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                  pagination.page === 1 ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Previous
              </button>
              <button
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={pagination.page === pagination.totalPages}
                className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                  pagination.page === pagination.totalPages ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(pagination.page - 1) * pagination.pageSize + 1}</span> to{' '}
                  <span className="font-medium">
                    {Math.min(pagination.page * pagination.pageSize, pagination.total)}
                  </span>{' '}
                  of <span className="font-medium">{pagination.total}</span> results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page === 1}
                    className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium ${
                      pagination.page === 1 ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    <span className="sr-only">Previous</span>
                    <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </button>
                  
                  {/* Page numbers */}
                  {[...Array(pagination.totalPages).keys()].map((page) => {
                    const pageNumber = page + 1;
                    // Show only a window of pages around current page
                    if (
                      pageNumber === 1 ||
                      pageNumber === pagination.totalPages ||
                      (pageNumber >= pagination.page - 1 && pageNumber <= pagination.page + 1)
                    ) {
                      return (
                        <button
                          key={pageNumber}
                          onClick={() => handlePageChange(pageNumber)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            pagination.page === pageNumber
                              ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {pageNumber}
                        </button>
                      );
                    } else if (
                      pageNumber === pagination.page - 2 ||
                      pageNumber === pagination.page + 2
                    ) {
                      return (
                        <span
                          key={pageNumber}
                          className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
                        >
                          ...
                        </span>
                      );
                    }
                    return null;
                  })}
                  
                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page === pagination.totalPages}
                    className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium ${
                      pagination.page === pagination.totalPages ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    <span className="sr-only">Next</span>
                    <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ObligationsList;

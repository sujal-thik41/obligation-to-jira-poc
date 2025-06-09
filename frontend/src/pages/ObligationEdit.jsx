import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useObligations } from '../context/ObligationContext';

const ObligationEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { fetchObligation, updateObligation, deleteObligation, createIssue, loading, error, currentObligation } = useObligations();
  
  const [formData, setFormData] = useState({
    obligation_text: '',
    party_name: '',
    deadline: '',
    section: '',
    priority: 'Medium',
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const loadObligation = async () => {
      try {
        await fetchObligation(id);
      } catch (err) {
        console.error('Error fetching obligation:', err);
      }
    };
    
    loadObligation();
  }, [id]);

  useEffect(() => {
    if (currentObligation) {
      setFormData({
        obligation_text: currentObligation.obligation_text || '',
        party_name: currentObligation.party_name || '',
        deadline: currentObligation.deadline || '',
        section: currentObligation.section || '',
        priority: currentObligation.priority || 'Medium',
      });
    }
  }, [currentObligation]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFormError('');
    setSuccessMessage('');
    
    try {
      await updateObligation(id, formData);
      setSuccessMessage('Obligation updated successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Error updating obligation');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this obligation?')) {
      try {
        await deleteObligation(id);
        navigate('/obligations');
      } catch (err) {
        setFormError(err.response?.data?.detail || 'Error deleting obligation');
      }
    }
  };

  const handleCreateIssue = async () => {
    try {
      await createIssue(id);
      setSuccessMessage('Jira issue created successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Error creating Jira issue');
    }
  };

  if (loading && !currentObligation) {
    return (
      <div className="max-w-3xl mx-auto p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading obligation details...</p>
      </div>
    );
  }

  if (error && !currentObligation) {
    return (
      <div className="max-w-3xl mx-auto p-8">
        <div className="bg-red-50 p-4 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
        <button
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          onClick={() => navigate('/obligations')}
        >
          Back to Obligations
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Edit Obligation</h1>
        <button
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          onClick={() => navigate('/obligations')}
        >
          Back to List
        </button>
      </div>

      {successMessage && (
        <div className="mb-4 bg-green-50 p-4 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">{successMessage}</p>
            </div>
          </div>
        </div>
      )}

      {formError && (
        <div className="mb-4 bg-red-50 p-4 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{formError}</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <div className="flex justify-between items-center mb-1">
              <label htmlFor="obligation_text" className="block text-sm font-medium text-gray-700">
                Obligation Text
              </label>
              {currentObligation?.jira_issue_id && (
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                  Locked - Jira Issue Created
                </span>
              )}
            </div>
            <textarea
              id="obligation_text"
              name="obligation_text"
              rows={4}
              className={`w-full px-3 py-2 border ${currentObligation?.jira_issue_id ? 'bg-gray-100 border-gray-200' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500`}
              value={formData.obligation_text}
              onChange={handleChange}
              required
              disabled={currentObligation?.jira_issue_id}
              title={currentObligation?.jira_issue_id ? 'Description cannot be changed after Jira issue is created' : ''}
            />
          </div>

          <div>
            <label htmlFor="party_name" className="block text-sm font-medium text-gray-700 mb-1">
              Party Name
            </label>
            <input
              type="text"
              id="party_name"
              name="party_name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={formData.party_name}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="deadline" className="block text-sm font-medium text-gray-700 mb-1">
              Deadline
            </label>
            <input
              type="text"
              id="deadline"
              name="deadline"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={formData.deadline}
              onChange={handleChange}
              placeholder="e.g., 30 days, January 15, 2025"
            />
          </div>

          <div>
            <label htmlFor="section" className="block text-sm font-medium text-gray-700 mb-1">
              Section
            </label>
            <input
              type="text"
              id="section"
              name="section"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={formData.section}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              id="priority"
              name="priority"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={formData.priority}
              onChange={handleChange}
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>

          {currentObligation && (
            <div className="pt-2 border-t">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Source Document: {currentObligation.source_document || 'N/A'}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Created: {new Date(currentObligation.created_at).toLocaleString()}
                  </p>
                </div>
                {currentObligation.jira_issue_id && (
                  <div className="bg-green-100 px-3 py-1 rounded-full flex items-center">
                    <svg className="h-4 w-4 text-green-600 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <p className="text-sm text-green-800">Jira Issue: {currentObligation.jira_issue_id}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="flex justify-between pt-4">
            <div className="space-x-2">
              <button
                type="button"
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                onClick={handleDelete}
                disabled={isSubmitting}
              >
                Delete
              </button>
              {currentObligation && !currentObligation.jira_issue_id && (
                <button
                  type="button"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  onClick={handleCreateIssue}
                  disabled={isSubmitting}
                >
                  Create Jira Issue
                </button>
              )}
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ObligationEdit;

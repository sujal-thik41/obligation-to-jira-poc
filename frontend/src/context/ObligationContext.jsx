import React, { createContext, useState, useContext } from 'react';
import * as api from '../services/api';

// Create context
const ObligationContext = createContext();

// Custom hook to use the obligation context
export const useObligations = () => useContext(ObligationContext);

export const ObligationProvider = ({ children }) => {
  const [obligations, setObligations] = useState([]);
  const [currentObligation, setCurrentObligation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0,
  });

  // Upload document and extract obligations
  const uploadDocument = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.uploadDocument(file);
      setObligations(response.obligations || []);
      setPagination({
        page: response.current_page || 1,
        pageSize: response.page_size || 10,
        total: response.total_obligations || 0,
        totalPages: response.total_pages || 0,
      });
      return response;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading document');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch obligations with pagination
  const fetchObligations = async (page = 1, pageSize = 10, partyName = null) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getObligations(page, pageSize, partyName);
      setObligations(response.obligations || []);
      setPagination({
        page: response.page || 1,
        pageSize: response.page_size || 10,
        total: response.total || 0,
        totalPages: response.total_pages || 0,
      });
      return response;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching obligations');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch a single obligation by ID
  const fetchObligation = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const obligation = await api.getObligation(id);
      setCurrentObligation(obligation);
      return obligation;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching obligation');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Update an obligation
  const updateObligation = async (id, data) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await api.updateObligation(id, data);
      
      // Update in local state
      setObligations(obligations.map(ob => 
        ob.id === id ? { ...ob, ...updated } : ob
      ));
      
      if (currentObligation && currentObligation.id === id) {
        setCurrentObligation({ ...currentObligation, ...updated });
      }
      
      return updated;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error updating obligation');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Delete an obligation
  const deleteObligation = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.deleteObligation(id);
      
      // Remove from local state
      setObligations(obligations.filter(ob => ob.id !== id));
      
      if (currentObligation && currentObligation.id === id) {
        setCurrentObligation(null);
      }
      
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error deleting obligation');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Create Jira issue for a single obligation
  const createIssue = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.createIssueForObligation(id);
      
      // Update the obligation in local state with the Jira issue ID
      if (result.success && result.issue_id) {
        setObligations(obligations.map(ob => 
          ob.id === id ? { ...ob, jira_issue_id: result.issue_id } : ob
        ));
        
        if (currentObligation && currentObligation.id === id) {
          setCurrentObligation({ ...currentObligation, jira_issue_id: result.issue_id });
        }
      }
      
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creating Jira issue');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Create Jira issues for multiple obligations
  const createIssuesForMultiple = async (obligationIds) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.createIssuesForObligations(obligationIds);
      
      // Refresh obligations after creating issues
      await fetchObligations(pagination.page, pagination.pageSize);
      
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creating Jira issues');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Clear all state (used when navigating away)
  const clearState = () => {
    setObligations([]);
    setCurrentObligation(null);
    setError(null);
    setPagination({
      page: 1,
      pageSize: 10,
      total: 0,
      totalPages: 0,
    });
  };

  const value = {
    obligations,
    currentObligation,
    loading,
    error,
    pagination,
    uploadDocument,
    fetchObligations,
    fetchObligation,
    updateObligation,
    deleteObligation,
    createIssue,
    createIssuesForMultiple,
    clearState,
  };

  return (
    <ObligationContext.Provider value={value}>
      {children}
    </ObligationContext.Provider>
  );
};

export default ObligationContext;

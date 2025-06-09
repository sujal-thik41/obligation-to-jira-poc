import axios from 'axios';

const API_URL = '/api';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Document upload and obligation extraction
export const uploadDocument = async (file, page = 1, pageSize = 10) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(`/upload-document?page=${page}&page_size=${pageSize}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Get all obligations with pagination
export const getObligations = async (page = 1, pageSize = 10, partyName = null) => {
  let url = `/obligations?page=${page}&page_size=${pageSize}`;
  if (partyName) {
    url += `&party_name=${encodeURIComponent(partyName)}`;
  }
  
  const response = await api.get(url);
  return response.data;
};

// Get a single obligation by ID
export const getObligation = async (id) => {
  const response = await api.get(`/obligations/${id}`);
  return response.data;
};

// Update an obligation
export const updateObligation = async (id, data) => {
  const response = await api.put(`/obligations/${id}`, data);
  return response.data;
};

// Delete an obligation
export const deleteObligation = async (id) => {
  const response = await api.delete(`/obligations/${id}`);
  return response.data;
};

// Create Jira issue for a single obligation
export const createIssueForObligation = async (id) => {
  const response = await api.post(`/obligations/${id}/create-issue`);
  return response.data;
};

// Create Jira issues for multiple obligations
export const createIssuesForObligations = async (obligationIds) => {
  const response = await api.post('/obligations/create-issues', obligationIds);
  return response.data;
};

export default api;

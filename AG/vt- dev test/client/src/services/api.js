import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Resources API
export const resourcesApi = {
  getAll: () => api.get('/resources'),
  create: (data) => api.post('/resources', data),
};

// Virtual Tags API
export const virtualTagsApi = {
  getByResourceId: (resourceId) => api.get(`/virtual-tags/${resourceId}`),
  create: (data) => api.post('/virtual-tags', data),
};

// Rules API
export const rulesApi = {
  getAll: () => api.get('/rules'),
  create: (data) => api.post('/rules', data),
  apply: () => api.post('/rules/apply'),
};

// Health check
export const healthApi = {
  check: () => api.get('/health'),
};

export default api;
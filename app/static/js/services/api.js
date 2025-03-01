import axios from 'axios';

const api = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API
export const authAPI = {
  login: () => window.location.href = '/auth/login',
  checkAuth: () => api.get('/auth/test'),
  getEmails: () => api.get('/auth/emails'),
  getEmailById: (id) => api.get(`/auth/emails/${id}`),
  getThreads: () => api.get('/auth/threads'),
  getThreadById: (id) => api.get(`/auth/threads/${id}`),
};

// Email API
export const emailAPI = {
  processEmails: (maxEmails = 10) => api.post('/api/emails/process', { max_emails: maxEmails }),
  getEmailById: (id) => api.get(`/api/emails/${id}`),
  getThreadEmails: (threadId) => api.get(`/api/emails/thread/${threadId}`),
};

// Capsule API (to be implemented on the backend)
export const capsuleAPI = {
  getCapsules: () => api.get('/api/capsules'),
  getCapsuleById: (id) => api.get(`/api/capsules/${id}`),
  createCapsule: (data) => api.post('/api/capsules', data),
  updateCapsule: (id, data) => api.put(`/api/capsules/${id}`, data),
  deleteCapsule: (id) => api.delete(`/api/capsules/${id}`),
};

export default api; 
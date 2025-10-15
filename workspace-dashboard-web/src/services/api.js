/**
 * API Client Service
 *
 * Handles all communication with the backend API
 */

const API_BASE_URL = 'http://localhost:8000';

// Helper function for making API requests
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

// Session API
export const sessionAPI = {
  // Get all sessions
  getAll: () => request('/api/sessions'),

  // Get a specific session
  get: (sessionId) => request(`/api/sessions/${sessionId}`),

  // Create a new session
  create: (sessionData) => request('/api/sessions', {
    method: 'POST',
    body: JSON.stringify(sessionData),
  }),

  // Update a session
  update: (sessionId, updates) => request(`/api/sessions/${sessionId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  }),

  // Delete a session
  delete: (sessionId) => request(`/api/sessions/${sessionId}`, {
    method: 'DELETE',
  }),

  // Fork a session
  fork: (sessionId) => request(`/api/sessions/${sessionId}/fork`, {
    method: 'POST',
  }),
};

// Project API
export const projectAPI = {
  // Get all unique project names
  getAll: () => request('/api/projects'),
};

// Layout API
export const layoutAPI = {
  // Get saved layouts
  get: () => request('/api/layouts'),

  // Save layout configuration
  save: (layouts) => request('/api/layouts', {
    method: 'PUT',
    body: JSON.stringify(layouts),
  }),
};

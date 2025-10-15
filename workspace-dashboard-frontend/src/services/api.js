import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Session API calls
export const sessionAPI = {
  create: async (projectName, taskName, metadata = {}) => {
    const response = await api.post('/sessions', {
      project_name: projectName,
      task_name: taskName,
      metadata,
    });
    return response.data;
  },

  get: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  list: async () => {
    const response = await api.get('/sessions');
    return response.data;
  },

  update: async (sessionId, updates) => {
    const response = await api.put(`/sessions/${sessionId}`, updates);
    return response.data;
  },

  delete: async (sessionId) => {
    const response = await api.delete(`/sessions/${sessionId}`);
    return response.data;
  },

  getOutputs: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}/outputs`);
    return response.data;
  },
};

// Dashboard API calls
export const dashboardAPI = {
  getLayouts: async () => {
    const response = await api.get('/dashboard/layouts');
    return response.data;
  },

  saveLayouts: async (layouts) => {
    const response = await api.put('/dashboard/layouts', { layouts });
    return response.data;
  },
};

// SSE Connection
export class SSEClient {
  constructor(onMessage, onError) {
    this.eventSource = null;
    this.onMessage = onMessage;
    this.onError = onError;
    this.reconnectTimeout = null;
    this.reconnectDelay = 3000;
  }

  connect() {
    if (this.eventSource) {
      this.disconnect();
    }

    this.eventSource = new EventSource('/events');

    // Handle different event types
    this.eventSource.addEventListener('session.status.changed', (event) => {
      this.handleMessage('session.status.changed', event.data);
    });

    this.eventSource.addEventListener('session.task.completed', (event) => {
      this.handleMessage('session.task.completed', event.data);
    });

    this.eventSource.addEventListener('session.outputs.created', (event) => {
      this.handleMessage('session.outputs.created', event.data);
    });

    this.eventSource.addEventListener('session.error', (event) => {
      this.handleMessage('session.error', event.data);
    });

    this.eventSource.addEventListener('heartbeat', (event) => {
      this.handleMessage('heartbeat', event.data);
    });

    this.eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      if (this.onError) {
        this.onError(error);
      }
      this.scheduleReconnect();
    };

    this.eventSource.onopen = () => {
      console.log('SSE Connected');
      this.clearReconnectTimeout();
    };
  }

  handleMessage(eventType, data) {
    try {
      const parsedData = JSON.parse(data);
      if (this.onMessage) {
        this.onMessage(eventType, parsedData);
      }
    } catch (error) {
      console.error('Error parsing SSE message:', error);
    }
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.clearReconnectTimeout();
  }

  scheduleReconnect() {
    this.clearReconnectTimeout();
    this.reconnectTimeout = setTimeout(() => {
      console.log('Attempting SSE reconnection...');
      this.connect();
    }, this.reconnectDelay);
  }

  clearReconnectTimeout() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }
}

export default api;
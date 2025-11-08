import axios from 'axios';

// Base API URL - update this based on your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Canvas API
export const canvasAPI = {
  authenticate: async (canvasUrl, accessToken) => {
    const response = await api.post('/canvas/authenticate', {
      canvas_url: canvasUrl,
      access_token: accessToken,
    });
    return response.data;
  },

  getAssignments: async () => {
    try {
      const response = await api.get('/canvas/assignments');
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        // Clear authentication if we get 401
        localStorage.removeItem('canvas_auth');
        throw new Error('Canvas authentication expired. Please reconnect.');
      }
      throw error;
    }
  },

  getCourseAssignments: async (courseId) => {
    try {
      const response = await api.get(`/canvas/assignments/${courseId}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        localStorage.removeItem('canvas_auth');
        throw new Error('Canvas authentication expired. Please reconnect.');
      }
      throw error;
    }
  },

  getCourses: async () => {
    try {
      const response = await api.get('/canvas/courses');
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        localStorage.removeItem('canvas_auth');
        throw new Error('Canvas authentication expired. Please reconnect.');
      }
      throw error;
    }
  },
};

// Study Plan API
export const studyPlanAPI = {
  generatePlan: async (assignments, preferences = null) => {
    const response = await api.post('/study-plan/generate', {
      assignments,
      preferences,
    });
    return response.data;
  },

  completePlan: async () => {
    const response = await api.post('/study-plan/complete');
    return response.data;
  },
};

// Google Calendar API
export const calendarAPI = {
  authenticate: async (credentials) => {
    const response = await api.post('/google/authenticate', {
      credentials,
    });
    return response.data;
  },

  createEvents: async (tasks) => {
    const response = await api.post('/calendar/create-events', tasks);
    return response.data;
  },

  getFreeSlots: async (startDate, endDate) => {
    const response = await api.get('/calendar/free-slots', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  deleteEvent: async (eventId) => {
    const response = await api.delete(`/calendar/event/${eventId}`);
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/');
  return response.data;
};

export default api;

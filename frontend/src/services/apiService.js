import { authService } from './authService';

// Get API endpoint from environment or use a default
const API_ENDPOINT = process.env.REACT_APP_API_ENDPOINT || 'http://localhost:3001';

export const apiService = {
  // Get current crossings
  getDashboardData: async (filters = {}) => {
    try {
      // Get current auth session
      const tokens = authService.getStoredUser();
      if (!tokens) {
        throw new Error('Not authenticated');
      }

      // Build query parameters
      const params = new URLSearchParams();
      params.append('type', 'crossings');
      
      if (filters.direction) params.append('direction', filters.direction);
      if (filters.min_price) params.append('min_price', filters.min_price);
      if (filters.min_volume_ratio) params.append('min_volume_ratio', filters.min_volume_ratio);
      if (filters.adr_pct_min) params.append('adr_pct_min', filters.adr_pct_min);
      if (filters.adr_pct_max) params.append('adr_pct_max', filters.adr_pct_max);

      console.log('Fetching dashboard data from:', `${API_ENDPOINT}/dashboard?${params}`);

      const response = await fetch(`${API_ENDPOINT}/dashboard?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.accessToken || ''}`,
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Dashboard data received:', data);
      return data;
    } catch (err) {
      console.error('getDashboardData error:', err);
      throw err;
    }
  },

  // Get scan history
  getScanHistory: async (days = 7) => {
    try {
      const tokens = authService.getStoredUser();
      if (!tokens) {
        throw new Error('Not authenticated');
      }

      const params = new URLSearchParams();
      params.append('type', 'history');
      params.append('days', days);

      const response = await fetch(`${API_ENDPOINT}/dashboard?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.accessToken || ''}`,
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('getScanHistory error:', err);
      throw err;
    }
  },

  // Get user settings
  getUserSettings: async (userId) => {
    try {
      const tokens = authService.getStoredUser();
      if (!tokens) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_ENDPOINT}/settings/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.accessToken || ''}`,
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('getUserSettings error:', err);
      throw err;
    }
  },

  // Update user settings
  updateUserSettings: async (userId, settings) => {
    try {
      const tokens = authService.getStoredUser();
      if (!tokens) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_ENDPOINT}/settings/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.accessToken || ''}`,
        },
        body: JSON.stringify(settings),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('updateUserSettings error:', err);
      throw err;
    }
  },

  // Set API endpoint (for dynamic configuration)
  setApiEndpoint: (endpoint) => {
    console.log('API endpoint set to:', endpoint);
  },
};

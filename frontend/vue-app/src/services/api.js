import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // Your backend API URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  // OLD: getBotsForTenant(tenantId) { return apiClient.get(`/bots/tenant/${tenantId}`); }
  // NEW: (Backend endpoint is now GET /api/v1/bots which gets tenant_id from token)
  getBots() {
    return apiClient.get('/api/v1/bots');
  },
  // OLD: createBot(tenantId, botConfig) { return apiClient.post(`/bots/${tenantId}`, botConfig); }
  // NEW: (Backend endpoint is now POST /api/v1/bots which gets tenant_id from token)
  createBot(botConfig) {
    return apiClient.post('/api/v1/bots', botConfig);
  },
  getBotLogs(botId, tail = 100) {
    return apiClient.get(`/bots/${botId}/logs`, { params: { tail } });
  },
  login(credentials) { // credentials: { username: email, password: password }
    // FastAPI's OAuth2PasswordRequestForm expects form data
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return apiClient.post('/api/v1/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  register(userData) { // userData: { email, password, full_name }
    return apiClient.post('/api/v1/auth/register', userData);
  },
  // Method to set Authorization header after login
  setAuthHeader(token) {
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
    }
  }
  // Add getBot(botId), deleteBot(botId) later
};
